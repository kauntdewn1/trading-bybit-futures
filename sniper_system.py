#!/usr/bin/env python3
"""
SNIPER SYSTEM - Protocolo NΞØ
Sistema de precisão para identificar O MELHOR trade do momento
"""
import json
import pandas as pd
import time
from bybit_api import connect_bybit, get_futures_price, get_klines
from futures_strategy import calculate_liquidation_price
from ta.momentum import RSIIndicator
from ta.trend import MACD
from datetime import datetime
from combo_patterns import ComboPatterns
from tracker import Tracker

class SniperSystem:
    def __init__(self):
        self.session = connect_bybit()
        self.assets = self.get_all_futures_symbols()  # Todos os ativos de futuros
        self.threshold = 7.0  # Threshold mínimo para trade
        self.combo_patterns = ComboPatterns()  # Sistema de combo patterns
        self.tracker = Tracker()  # Sistema de auto-learning
    
    def get_all_futures_symbols(self):
        """Obtém todos os símbolos de futuros USDT Perp via API Bybit"""
        try:
            import requests
            
            # Endpoint oficial da Bybit para listar todos os instrumentos de futuros
            url = "https://api.bybit.com/v5/market/instruments-info?category=linear"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ HTTP Error: {response.status_code}")
                return self._get_fallback_symbols()
                
            data = response.json()
            
            if data.get("retCode") == 0 and data.get("result"):
                # Filtra apenas símbolos USDT Perp válidos para trading
                symbols = [
                    item["symbol"] for item in data["result"]["list"]
                    if item["symbol"].endswith("USDT") and 
                       item["status"] == "Trading" and
                       item.get("contractType") == "LinearPerpetual" and
                       len(item["symbol"]) <= 12 and  # Evita símbolos muito longos/estranhos
                       not any(x in item["symbol"] for x in ["1000000", "10000", "1000"])  # Evita multiplicadores
                ]
                
                print(f"🎯 SNIPER NEØ - VARRENDO {len(symbols)} ATIVOS DE FUTUROS PELA API")
                print(f"📊 Primeiros 10: {symbols[:10]}")
                return symbols
            else:
                print(f"❌ Erro na API Bybit: {data.get('retMsg', 'Unknown error')}")
                return self._get_fallback_symbols()
                
        except Exception as e:
            print(f"❌ Erro ao obter símbolos Bybit via API: {e}")
            return self._get_fallback_symbols()
    
    def _get_fallback_symbols(self):
        """Lista básica de fallback"""
        fallback = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "SOLUSDT",
            "DOGEUSDT", "DOTUSDT", "AVAXUSDT", "MATICUSDT", "LTCUSDT", "UNIUSDT",
            "LINKUSDT", "ATOMUSDT", "XLMUSDT", "BCHUSDT", "FILUSDT", "TRXUSDT",
            "ETCUSDT", "XMRUSDT", "EOSUSDT", "AAVEUSDT", "ALGOUSDT", "COMPUSDT",
            "MKRUSDT", "SNXUSDT", "YFIUSDT", "SUSHIUSDT", "CRVUSDT", "1INCHUSDT",
            "BALUSDT", "LRCUSDT", "ZRXUSDT", "KNCUSDT", "RENUSDT", "NEARUSDT",
            "FTMUSDT", "ICPUSDT", "VETUSDT", "HBARUSDT", "THETAUSDT", "EGLDUSDT",
            "FLOWUSDT", "MANAUSDT", "SANDUSDT", "AXSUSDT", "GALAUSDT", "ENJUSDT",
            "CHZUSDT", "ARUSDT", "STORJUSDT", "SCUSDT", "ANKRUSDT", "SKLUSDT",
            "ZECUSDT", "DASHUSDT", "ZENUSDT", "FTTUSDT", "OKBUSDT"
        ]
        print(f"⚠️ Usando lista fallback com {len(fallback)} símbolos")
        return fallback
        
    def calculate_volatility_multiplier(self, df):
        """Calcula multiplicador de volatilidade baseado na volatilidade recente"""
        try:
            # Calcula volatilidade dos últimos 20 períodos
            returns = df["close"].pct_change().dropna()
            volatility = returns.rolling(window=20).std().iloc[-1]
            
            # Normaliza volatilidade (0.01 = 1%, 0.05 = 5%)
            if volatility < 0.01:  # Muito baixa volatilidade
                return 0.5  # Reduz score pela metade
            elif volatility < 0.02:  # Baixa volatilidade
                return 0.8
            elif volatility < 0.04:  # Volatilidade normal
                return 1.0
            elif volatility < 0.06:  # Alta volatilidade
                return 1.3
            else:  # Volatilidade extrema
                return 1.5
        except:
            return 1.0  # Fallback para volatilidade normal
    
    def calculate_capital_weighting(self, symbol, volume_24h):
        """Calcula peso baseado no capital movimentado"""
        try:
            # Volume em USDT (aproximado)
            volume_usdt = volume_24h
            
            # Categorias de volume
            if volume_usdt > 100_000_000:  # > 100M USDT
                return 1.5  # Mega cap
            elif volume_usdt > 50_000_000:  # > 50M USDT
                return 1.3  # Large cap
            elif volume_usdt > 10_000_000:  # > 10M USDT
                return 1.1  # Mid cap
            elif volume_usdt > 1_000_000:  # > 1M USDT
                return 1.0  # Small cap
            else:  # < 1M USDT
                return 0.7  # Micro cap (penaliza)
        except:
            return 1.0  # Fallback neutro

    def calculate_score(self, symbol, timeframe="15"):
        """Calcula score baseado na lógica de ranking otimizada com ajustes cirúrgicos"""
        try:
            # Obtém dados
            futures_data = get_futures_price(self.session, symbol)
            if not futures_data:
                return {"long": 0, "short": 0, "data": None}
                
            df = get_klines(self.session, symbol, timeframe, 50)
            
            if len(df) < 20:
                return {"long": 0, "short": 0, "data": None}
            
            # Calcula indicadores
            rsi = RSIIndicator(close=df["close"], window=14).rsi().iloc[-1]
            macd = MACD(close=df["close"])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            histogram = macd_line - signal_line
            
            # Volume
            volume_sma = df["volume"].rolling(window=20).mean().iloc[-1]
            current_volume = df["volume"].iloc[-1]
            volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1
            
            # Funding e Open Interest
            funding_rate = futures_data["funding_rate"]
            open_interest = futures_data["open_interest"]
            price = futures_data["price"]
            volume_24h = futures_data["volume_24h"]
            
            # Determina status dos indicadores
            macd_status = "bullish" if macd_line > signal_line else "bearish"
            volume_status = "high" if volume_ratio > 1.5 else "low"
            oi_status = "up" if open_interest > 1000000 else "down"
            
            # AJUSTES CIRÚRGICOS
            volatility_mult = self.calculate_volatility_multiplier(df)
            capital_weight = self.calculate_capital_weighting(symbol, volume_24h)
            
            # Calcula scores baseado na lógica especificada
            score_long = 0
            score_short = 0
            
            # Regras LONG com ajustes dinâmicos
            if rsi < 35: 
                score_long += 3 * volatility_mult  # RSI extremo em alta volatilidade vale mais
            if macd_status == "bullish": 
                score_long += 2 * capital_weight  # MACD bullish em ativo com volume vale mais
            if funding_rate < 0: 
                score_long += 1
            if volume_status == "high": 
                score_long += 1 * capital_weight  # Volume alto em ativo com capital vale mais
            if oi_status == "up": 
                score_long += 1
            
            # Regras SHORT com ajustes dinâmicos
            if rsi > 70: 
                score_short += 3 * volatility_mult  # RSI extremo em alta volatilidade vale mais
            if macd_status == "bearish": 
                score_short += 2 * capital_weight  # MACD bearish em ativo com volume vale mais
            if funding_rate > 0: 
                score_short += 1
            if volume_status == "high": 
                score_short += 1 * capital_weight  # Volume alto em ativo com capital vale mais
            if oi_status == "down": 
                score_short += 1
            
            # COMBO PATTERNS - BÔNUS DE CONFLUÊNCIA
            data_for_combo = {
                "rsi": rsi,
                "macd": macd_status,
                "volume_ratio": volume_ratio,
                "funding": funding_rate,
                "oi": oi_status
            }
            
            # Calcula bônus de combo patterns
            combo_bonus_long, combo_patterns_long = self.combo_patterns.calculate_combo_bonus(data_for_combo, "LONG")
            combo_bonus_short, combo_patterns_short = self.combo_patterns.calculate_combo_bonus(data_for_combo, "SHORT")
            
            # Aplica bônus de combo
            score_long += combo_bonus_long
            score_short += combo_bonus_short
            
            # AUTO-LEARNING - Ajustes baseados no histórico
            asset_preference = self.tracker.get_asset_preference(symbol)
            
            # Converte combo patterns de dict para string
            combo_patterns_long_names = [p["name"] for p in combo_patterns_long] if combo_patterns_long else []
            combo_patterns_short_names = [p["name"] for p in combo_patterns_short] if combo_patterns_short else []
            
            pattern_preference_long = self.tracker.get_pattern_preference(combo_patterns_long_names)
            pattern_preference_short = self.tracker.get_pattern_preference(combo_patterns_short_names)
            
            # Aplica preferências de auto-learning
            score_long *= asset_preference * pattern_preference_long
            score_short *= asset_preference * pattern_preference_short
            
            return {
                "long": round(score_long, 1),
                "short": round(score_short, 1),
                "data": {
                    "symbol": symbol,
                    "price": price,
                    "rsi": round(rsi, 1),
                    "macd": macd_status,
                    "volume": volume_status,
                    "funding": round(funding_rate, 4),
                    "oi": oi_status,
                    "volume_ratio": round(volume_ratio, 2),
                    "volatility_mult": round(volatility_mult, 2),
                    "capital_weight": round(capital_weight, 2),
                    "volume_24h": volume_24h,
                    "combo_bonus_long": round(combo_bonus_long, 1),
                    "combo_bonus_short": round(combo_bonus_short, 1),
                    "combo_patterns_long": combo_patterns_long_names,
                    "combo_patterns_short": combo_patterns_short_names,
                    "asset_preference": round(asset_preference, 2),
                    "pattern_preference_long": round(pattern_preference_long, 2),
                    "pattern_preference_short": round(pattern_preference_short, 2)
                }
            }
            
        except Exception as e:
            print(f"Erro ao calcular score para {symbol}: {e}")
            import traceback
            traceback.print_exc()
            return {"long": 0, "short": 0, "data": None}
    
    def find_best_trade(self):
        """Encontra O MELHOR trade varrendo TODOS os ativos de futuros"""
        print("🔍 SNIPER SCANNING - VARRENDO MERCADO COMPLETO...")
        print(f"📊 Analisando {len(self.assets)} ativos de futuros...")
        
        # Lista para ranking
        ranking = []
        processed = 0
        frenzy_count = 0  # Contador para modo raiva total
        
        for i, asset in enumerate(self.assets, 1):
            print(f"📊 Analisando {asset}... ({i}/{len(self.assets)})")
            
            # Delay para respeitar rate limit
            if i > 1:
                time.sleep(0.1)  # 100ms entre requests
            
            result = self.calculate_score(asset)
            
            if result["data"] is None:
                continue
            
            # Determina melhor direção e score
            long_score = result["long"]
            short_score = result["short"]
            
            if long_score > short_score:
                melhor_direcao = "LONG"
                melhor_score = long_score
            else:
                melhor_direcao = "SHORT"
                melhor_score = short_score
            
            # Adiciona ao ranking
            ranking.append({
                "ativo": asset,
                "direcao": melhor_direcao,
                "score": melhor_score,
                "dados": result["data"]
            })
            
            processed += 1
            if melhor_score >= 5:  # Só mostra scores altos
                print(f"   ✅ {asset} {melhor_direcao}: {melhor_score}/10")
            
            # Conta ativos em modo raiva total (score 8+)
            if melhor_score >= 8:
                frenzy_count += 1
        
        # Ordena pelo score (maior primeiro)
        ranking.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"\n🎯 VARREDURA COMPLETA: {processed} ativos analisados")
        
        # MODO RAIVA TOTAL - 3+ ativos com score 8+
        if frenzy_count >= 3:
            print(f"\n🚨🚨🚨 MODO RAIVA TOTAL ATIVADO! 🚨🚨🚨")
            print(f"🔥 {frenzy_count} ATIVOS DISPARARAM SCORE 8+ SIMULTANEAMENTE!")
            print(f"💀 É AGORA OU VOLTA PRA CLT! 💀")
            print(f"⚡ MOMENTO DE MÁXIMA OPORTUNIDADE! ⚡")
        
        # Mostra TOP 6 sempre
        print(f"\n🔥 TOP 6 FUTUROS – Bybit")
        for i, ativo in enumerate(ranking[:6], 1):
            emoji = "🟢" if ativo['direcao'] == "LONG" else "🔴"
            frenzy_emoji = "🚨" if ativo['score'] >= 8 else ""
            print(f"{i}️⃣ {emoji}{frenzy_emoji} {ativo['ativo']} – Direção: {ativo['direcao']} – Score: {ativo['score']}/10")
            print(f"     Motivo: RSI {ativo['dados']['rsi']}, MACD {ativo['dados']['macd']}, Volume {ativo['dados']['volume']}")
        
        # Seleciona melhor ativo acima do threshold
        melhor = next((r for r in ranking if r["score"] >= self.threshold), None)
        
        if melhor:
            print(f"\n🎯 MELHOR ALVO: {melhor['ativo']} {melhor['direcao']} - Score: {melhor['score']}/10")
            return {
                "symbol": melhor["ativo"],
                "direction": melhor["direcao"],
                "score": melhor["score"],
                "data": melhor["dados"],
                "frenzy_count": frenzy_count
            }
        else:
            print(f"\n⏳ Nenhum ativo acima do threshold {self.threshold}/10")
            return None
    
    def get_full_ranking(self):
        """Retorna ranking completo de todos os ativos com cache"""
        ranking = []
        
        # Cache para evitar requests duplicados
        cache_time = 30  # 30 segundos de cache
        current_time = time.time()
        
        for asset in self.assets:
            # Verifica cache
            cache_key = f"{asset}_data"
            if (hasattr(self, '_cache') and 
                cache_key in self._cache and 
                current_time - self._cache[cache_key]['timestamp'] < cache_time):
                
                result = self._cache[cache_key]['data']
            else:
                # Faz request com delay para respeitar rate limit
                time.sleep(0.1)  # 100ms entre requests
                result = self.calculate_score(asset)
                
                # Salva no cache
                if not hasattr(self, '_cache'):
                    self._cache = {}
                self._cache[cache_key] = {
                    'data': result,
                    'timestamp': current_time
                }
            
            if result["data"] is None:
                continue
            
            # Determina melhor direção e score
            long_score = result["long"]
            short_score = result["short"]
            
            if long_score > short_score:
                melhor_direcao = "LONG"
                melhor_score = long_score
            else:
                melhor_direcao = "SHORT"
                melhor_score = short_score
            
            # Adiciona ao ranking
            ranking.append({
                "symbol": asset,
                "direction": melhor_direcao,
                "score": melhor_score,
                "rsi": result["data"]["rsi"],
                "macd": result["data"]["macd"],
                "volume": result["data"]["volume"],
                "funding_rate": result["data"]["funding"],
                "oi_trend": result["data"]["oi"],
                "price": result["data"]["price"]
            })
        
        # Ordena pelo score (maior primeiro)
        ranking.sort(key=lambda x: x["score"], reverse=True)
        
        return ranking
    
    def analyze_on_demand(self, symbols=None):
        """Análise sob demanda - só quando você pedir"""
        if symbols is None:
            symbols = self.assets
        
        print(f"🔍 ANÁLISE SOB DEMANDA - {len(symbols)} ativos")
        print("=" * 50)
        
        ranking = []
        
        for i, asset in enumerate(symbols):
            print(f"📊 Analisando {asset}... ({i+1}/{len(symbols)})")
            
            # Delay entre requests para respeitar rate limit
            if i > 0:
                time.sleep(0.2)  # 200ms entre requests
            
            result = self.calculate_score(asset)
            
            if result["data"] is None:
                print(f"   ❌ {asset}: Sem dados")
                continue
            
            # Determina melhor direção e score
            long_score = result["long"]
            short_score = result["short"]
            
            if long_score > short_score:
                melhor_direcao = "LONG"
                melhor_score = long_score
            else:
                melhor_direcao = "SHORT"
                melhor_score = short_score
            
            print(f"   ✅ {asset} {melhor_direcao}: {melhor_score}/10")
            
            # Adiciona ao ranking
            ranking.append({
                "ativo": asset,
                "direcao": melhor_direcao,
                "score": melhor_score,
                "dados": result["data"]
            })
        
        # Ordena pelo score (maior primeiro)
        ranking.sort(key=lambda x: x["score"], reverse=True)
        
        print(f"\n🏆 TOP {min(6, len(ranking))} ATIVOS:")
        for i, ativo in enumerate(ranking[:6], 1):
            print(f"   {i}º {ativo['ativo']} {ativo['direcao']} - Score: {ativo['score']}/10")
        
        return ranking
    
    def generate_sniper_alert(self, trade_data, direction, score, frenzy_count=0):
        """Gera payload Telegram otimizado"""
        if trade_data is None:
            return {
                "status": "WAIT",
                "alert": "⚠️ Nenhuma oportunidade de trade futuro com edge real neste momento.\nAguarde o próximo sinal do Node NΞØ. Proteja seu capital.",
                "timestamp": datetime.now().strftime("%H:%M")
            }
        
        # Registra alerta no tracker para auto-learning
        combo_patterns = trade_data.get("combo_patterns_long" if direction == "LONG" else "combo_patterns_short", [])
        alert_id = self.tracker.record_alert(
            symbol=trade_data["symbol"],
            direction=direction,
            score=score,
            data=trade_data,
            combo_patterns=combo_patterns
        )
        
        # Monta payload no formato especificado
        ativo = trade_data["symbol"]
        dados = trade_data
        
        # MODO RAIVA TOTAL - Alerta prioritário
        if frenzy_count >= 3:
            payload = f"""🚨🚨🚨 MODO RAIVA TOTAL ATIVADO! 🚨🚨🚨

🔥 {frenzy_count} ATIVOS DISPARARAM SCORE 8+ SIMULTANEAMENTE!
💀 É AGORA OU VOLTA PRA CLT! 💀

🎯 MELHOR ALVO: {ativo}
⚡ DIREÇÃO: {direction}
📊 MOTIVO:
   - RSI: {dados['rsi']}
   - MACD: {dados['macd']}
   - Volume: {dados['volume']}
   - Funding: {dados['funding']}
   - Open Interest: {dados['oi']}

🟢 Score de Qualidade: {score}/10
🚨 COMBO PATTERNS: {', '.join(combo_patterns) if combo_patterns else 'Nenhum'}

⚡ MOMENTO DE MÁXIMA OPORTUNIDADE!
🔥 ENTRADA IMEDIATA - STOP CURTO!
💀 NÃO PERCA ESTA OPORTUNIDADE!

⏱️ Atualização automática Node NΞØ"""
        else:
            payload = f"""🔥 MELHOR OPORTUNIDADE FUTUROS AGORA – Node NΞØ

🎯 ATIVO: {ativo}
⚡ DIREÇÃO: {direction}
📊 MOTIVO:
   - RSI: {dados['rsi']}
   - MACD: {dados['macd']}
   - Volume: {dados['volume']}
   - Funding: {dados['funding']}
   - Open Interest: {dados['oi']}

🟢 Score de Qualidade: {score}/10
🔥 COMBO PATTERNS: {', '.join(combo_patterns) if combo_patterns else 'Nenhum'}

🟡 Sugestão: Entrada rápida e stop curto. Valide no painel antes de operar pesado.

⏱️ Atualização automática Node NΞØ"""
        
        return {
            "status": "TARGET",
            "alert": payload,
            "alert_id": alert_id,  # ID para tracking
            "data": {
                "symbol": ativo,
                "direction": direction,
                "score": score,
                "rsi": dados['rsi'],
                "macd": dados['macd'],
                "volume": dados['volume'],
                "funding": dados['funding'],
                "oi": dados['oi'],
                "combo_patterns": combo_patterns,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def run_sniper_scan(self):
        """Executa scan sniper completo"""
        print("🥷 SNIPER SYSTEM - PROTOCOLO NΞØ")
        print("=" * 50)
        
        best_trade, direction, score, frenzy_count = self.find_best_trade()
        alert = self.generate_sniper_alert(best_trade, direction, score, frenzy_count)
        
        if alert["status"] == "TARGET":
            print("\n🎯 ALVO IDENTIFICADO!")
            print(alert["alert"])
        else:
            print(f"\n⏳ {alert['alert']}")
        
        return alert

def main():
    """Executa o sistema sniper"""
    sniper = SniperSystem()
    result = sniper.run_sniper_scan()
    
    # Salva resultado para Telegram
    with open("sniper_result.json", "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result

if __name__ == "__main__":
    main()
