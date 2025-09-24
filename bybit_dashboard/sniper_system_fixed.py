#!/usr/bin/env python3
"""
🥷 SNIPER SYSTEM FIXED - VERSÃO CORRIGIDA
Implementa todas as correções identificadas na análise
"""

import json
import pandas as pd
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from bybit_api import connect_bybit, get_futures_price, get_klines
from futures_strategy import calculate_liquidation_price
from ta.momentum import RSIIndicator
from ta.trend import MACD
from combo_patterns import ComboPatterns
from tracker import Tracker

@dataclass
class ValidationResult:
    """Resultado de validação de indicadores"""
    valid: bool
    errors: List[str]
    warnings: List[str]

class RateLimiter:
    """Rate limiter inteligente com backoff adaptativo"""
    
    def __init__(self, max_requests: int = 100, per_minute: int = 60):
        self.max_requests = max_requests
        self.per_minute = per_minute
        self.requests = []
        self.success_rate = 1.0
        self.adaptive_delay = 0.1
        self.retry_count = 0
        
    def make_request(self, func, *args, **kwargs):
        """Faz request com rate limiting inteligente"""
        # Limpa requests antigos
        now = time.time()
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        # Verifica rate limit
        if len(self.requests) >= self.max_requests:
            sleep_time = 60 - (now - self.requests[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Ajusta delay baseado na taxa de sucesso
        if self.success_rate < 0.9:
            self.adaptive_delay = min(self.adaptive_delay * 1.2, 2.0)
        elif self.success_rate > 0.95:
            self.adaptive_delay = max(self.adaptive_delay * 0.9, 0.05)
            
        time.sleep(self.adaptive_delay)
        
        try:
            result = func(*args, **kwargs)
            self.requests.append(now)
            self.success_rate = 0.9 * self.success_rate + 0.1
            self.retry_count = 0
            return result
        except Exception as e:
            self.success_rate = 0.9 * self.success_rate
            if "rate limit" in str(e).lower():
                self.retry_count += 1
                backoff_time = min(2 ** self.retry_count, 30)
                time.sleep(backoff_time)
            raise e

class SecureSniperSystem:
    """Sistema Sniper com correções de segurança e performance"""
    
    def __init__(self):
        self.setup_logging()
        self.session = connect_bybit()
        self.assets = self.get_all_futures_symbols()
        self.threshold = 7.0
        self.combo_patterns = ComboPatterns()
        self.tracker = Tracker()
        self.rate_limiter = RateLimiter()
        self.valid_symbols = set()
        self.cache = {}
        self.cache_ttl = 300  # 5 minutos
        
    def setup_logging(self):
        """Configura logging estruturado"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sniper_audit.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def validate_indicators(self, df: pd.DataFrame, min_periods: int = 20) -> ValidationResult:
        """Validação robusta de indicadores"""
        validation_result = ValidationResult(valid=True, errors=[], warnings=[])
        
        # Verifica dados mínimos
        if len(df) < min_periods:
            validation_result.valid = False
            validation_result.errors.append(f"Dados insuficientes: {len(df)} < {min_periods}")
            return validation_result
        
        # Verifica se há dados válidos
        if df.empty or df.isnull().all().any():
            validation_result.valid = False
            validation_result.errors.append("DataFrame vazio ou com colunas nulas")
            return validation_result
        
        # Verifica RSI
        try:
            rsi = RSIIndicator(close=df["close"], window=14).rsi()
            if rsi.isna().any():
                validation_result.valid = False
                validation_result.errors.append("RSI contém valores NaN")
        except Exception as e:
            validation_result.valid = False
            validation_result.errors.append(f"Erro ao calcular RSI: {e}")
        
        # Verifica MACD
        try:
            macd = MACD(close=df["close"])
            if macd.macd().isna().any() or macd.macd_signal().isna().any():
                validation_result.valid = False
                validation_result.errors.append("MACD contém valores NaN")
        except Exception as e:
            validation_result.valid = False
            validation_result.errors.append(f"Erro ao calcular MACD: {e}")
        
        # Verifica volume
        if df["volume"].sum() == 0:
            validation_result.warnings.append("Volume zero detectado")
        
        return validation_result
    
    def validate_symbol(self, symbol: str) -> bool:
        """Valida se símbolo existe na Bybit"""
        if symbol in self.valid_symbols:
            return True
            
        try:
            test_data = self.rate_limiter.make_request(
                get_futures_price, self.session, symbol
            )
            if test_data:
                self.valid_symbols.add(symbol)
                return True
            return False
        except Exception as e:
            self.logger.warning(f"Símbolo inválido {symbol}: {e}")
            return False
    
    def safe_api_call(self, func, *args, **kwargs):
        """Chamada de API com tratamento de erros robusto"""
        try:
            return self.rate_limiter.make_request(func, *args, **kwargs)
        except Exception as e:
            self.logger.error(f"Erro na API: {e}")
            return None
    
    def calculate_volatility_multiplier(self, df: pd.DataFrame) -> float:
        """Calcula multiplicador de volatilidade com validação"""
        try:
            if len(df) < 20:
                return 1.0
                
            returns = df["close"].pct_change().dropna()
            if len(returns) < 10:
                return 1.0
                
            volatility = returns.rolling(window=20).std().iloc[-1]
            
            if pd.isna(volatility) or volatility <= 0:
                return 1.0
            
            # Normaliza volatilidade
            if volatility < 0.01:
                return 0.5
            elif volatility < 0.02:
                return 0.8
            elif volatility < 0.04:
                return 1.0
            elif volatility < 0.06:
                return 1.3
            else:
                return 1.5
        except Exception as e:
            self.logger.warning(f"Erro ao calcular volatilidade: {e}")
            return 1.0
    
    def calculate_capital_weighting(self, symbol: str, volume_24h: float) -> float:
        """Calcula peso de capital com validação"""
        try:
            if not volume_24h or volume_24h <= 0:
                return 1.0
                
            if volume_24h > 100_000_000:
                return 1.5
            elif volume_24h > 50_000_000:
                return 1.3
            elif volume_24h > 10_000_000:
                return 1.1
            elif volume_24h > 1_000_000:
                return 1.0
            else:
                return 0.7
        except Exception as e:
            self.logger.warning(f"Erro ao calcular capital weighting: {e}")
            return 1.0
    
    def calculate_adaptive_threshold(self) -> float:
        """Threshold adaptativo baseado no contexto"""
        base = self.threshold
        
        # Ajuste por horário
        hour = datetime.now().hour
        if 14 <= hour <= 16:  # Horário de alta liquidez
            base *= 0.9
        elif 22 <= hour <= 6:  # Horário de baixa liquidez
            base *= 1.1
        
        return min(max(base, 3.0), 10.0)
    
    def calculate_score_safe(self, symbol: str, timeframe: str = "15") -> Dict:
        """Calcula score com validação robusta"""
        try:
            # Valida símbolo
            if not self.validate_symbol(symbol):
                return {"long": 0, "short": 0, "data": None}
            
            # Obtém dados com rate limiting
            futures_data = self.safe_api_call(get_futures_price, self.session, symbol)
            if not futures_data:
                return {"long": 0, "short": 0, "data": None}
                
            df = self.safe_api_call(get_klines, self.session, symbol, timeframe, 50)
            if df is None or len(df) < 20:
                return {"long": 0, "short": 0, "data": None}
            
            # Valida indicadores
            validation = self.validate_indicators(df)
            if not validation.valid:
                self.logger.warning(f"Indicadores inválidos para {symbol}: {validation.errors}")
                return {"long": 0, "short": 0, "data": None}
            
            # Calcula indicadores com validação
            rsi = RSIIndicator(close=df["close"], window=14).rsi().iloc[-1]
            macd = MACD(close=df["close"])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            
            # Validação adicional
            if pd.isna(rsi) or pd.isna(macd_line) or pd.isna(signal_line):
                return {"long": 0, "short": 0, "data": None}
            
            # Volume com validação
            volume_sma = df["volume"].rolling(window=20).mean().iloc[-1]
            current_volume = df["volume"].iloc[-1]
            
            if pd.isna(volume_sma) or volume_sma <= 0:
                volume_ratio = 1.0
            else:
                volume_ratio = current_volume / volume_sma
            
            # Dados de futuros
            funding_rate = futures_data.get("funding_rate", 0)
            open_interest = futures_data.get("open_interest", 0)
            price = futures_data.get("price", 0)
            volume_24h = futures_data.get("volume_24h", 0)
            
            # Status dos indicadores
            macd_status = "bullish" if macd_line > signal_line else "bearish"
            volume_status = "high" if volume_ratio > 1.5 else "low"
            oi_status = "up" if open_interest > 1000000 else "down"
            
            # Ajustes cirúrgicos
            volatility_mult = self.calculate_volatility_multiplier(df)
            capital_weight = self.calculate_capital_weighting(symbol, volume_24h)
            
            # Calcula scores
            score_long = 0
            score_short = 0
            
            # Regras LONG
            if rsi < 35:
                score_long += 3 * volatility_mult
            if macd_status == "bullish":
                score_long += 2 * capital_weight
            if funding_rate < 0:
                score_long += 1
            if volume_status == "high":
                score_long += 1 * capital_weight
            if oi_status == "up":
                score_long += 1
            
            # Regras SHORT
            if rsi > 70:
                score_short += 3 * volatility_mult
            if macd_status == "bearish":
                score_short += 2 * capital_weight
            if funding_rate > 0:
                score_short += 1
            if volume_status == "high":
                score_short += 1 * capital_weight
            if oi_status == "down":
                score_short += 1
            
            # Combo patterns
            data_for_combo = {
                "rsi": rsi,
                "macd": macd_status,
                "volume_ratio": volume_ratio,
                "funding": funding_rate,
                "oi": oi_status
            }
            
            combo_bonus_long, combo_patterns_long = self.combo_patterns.calculate_combo_bonus(data_for_combo, "LONG")
            combo_bonus_short, combo_patterns_short = self.combo_patterns.calculate_combo_bonus(data_for_combo, "SHORT")
            
            score_long += combo_bonus_long
            score_short += combo_bonus_short
            
            # Auto-learning com validação
            try:
                asset_preference = self.tracker.get_asset_preference(symbol)
                pattern_preference_long = self.tracker.get_pattern_preference(combo_patterns_long)
                pattern_preference_short = self.tracker.get_pattern_preference(combo_patterns_short)
                
                score_long *= asset_preference * pattern_preference_long
                score_short *= asset_preference * pattern_preference_short
            except Exception as e:
                self.logger.warning(f"Erro no auto-learning para {symbol}: {e}")
            
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
                    "combo_patterns_long": [p["name"] for p in combo_patterns_long],
                    "combo_patterns_short": [p["name"] for p in combo_patterns_short],
                    "asset_preference": round(asset_preference, 2),
                    "pattern_preference_long": round(pattern_preference_long, 2),
                    "pattern_preference_short": round(pattern_preference_short, 2)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular score para {symbol}: {e}")
            return {"long": 0, "short": 0, "data": None}
    
    def get_all_futures_symbols(self) -> List[str]:
        """Obtém símbolos com validação"""
        try:
            import requests
            
            url = "https://api.bybit.com/v5/market/instruments-info?category=linear"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                self.logger.error(f"HTTP Error: {response.status_code}")
                return self._get_fallback_symbols()
                
            data = response.json()
            
            if data.get("retCode") == 0 and data.get("result"):
                symbols = [
                    item["symbol"] for item in data["result"]["list"]
                    if item["symbol"].endswith("USDT") and 
                       item["status"] == "Trading" and
                       item.get("contractType") == "LinearPerpetual" and
                       len(item["symbol"]) <= 12
                ]
                
                self.logger.info(f"Obtidos {len(symbols)} símbolos de futuros")
                return symbols
            else:
                self.logger.error(f"Erro na API Bybit: {data.get('retMsg', 'Unknown error')}")
                return self._get_fallback_symbols()
                
        except Exception as e:
            self.logger.error(f"Erro ao obter símbolos: {e}")
            return self._get_fallback_symbols()
    
    def _get_fallback_symbols(self) -> List[str]:
        """Lista de fallback para símbolos"""
        return [
            "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "SOLUSDT",
            "DOGEUSDT", "DOTUSDT", "AVAXUSDT", "MATICUSDT", "LTCUSDT", "UNIUSDT"
        ]
    
    def find_best_trade_safe(self) -> Tuple[Optional[Dict], Optional[str], float, int]:
        """Encontra melhor trade com validação robusta"""
        self.logger.info("Iniciando análise segura de mercado")
        
        ranking = []
        processed = 0
        frenzy_count = 0
        errors = 0
        
        for i, asset in enumerate(self.assets, 1):
            try:
                self.logger.debug(f"Analisando {asset} ({i}/{len(self.assets)})")
                
                result = self.calculate_score_safe(asset)
                
                if result["data"] is None:
                    errors += 1
                    continue
                
                long_score = result["long"]
                short_score = result["short"]
                
                if long_score > short_score:
                    melhor_direcao = "LONG"
                    melhor_score = long_score
                else:
                    melhor_direcao = "SHORT"
                    melhor_score = short_score
                
                ranking.append({
                    "ativo": asset,
                    "direcao": melhor_direcao,
                    "score": melhor_score,
                    "dados": result["data"]
                })
                
                processed += 1
                
                if melhor_score >= 8:
                    frenzy_count += 1
                
                if melhor_score >= 5:
                    self.logger.info(f"{asset} {melhor_direcao}: {melhor_score}/10")
                    
            except Exception as e:
                self.logger.error(f"Erro ao processar {asset}: {e}")
                errors += 1
                continue
        
        # Ordena ranking
        ranking.sort(key=lambda x: x["score"], reverse=True)
        
        self.logger.info(f"Análise concluída: {processed} processados, {errors} erros, {frenzy_count} em modo raiva")
        
        # Seleciona melhor
        adaptive_threshold = self.calculate_adaptive_threshold()
        melhor = next((r for r in ranking if r["score"] >= adaptive_threshold), None)
        
        if melhor:
            return melhor["dados"], melhor["direcao"], melhor["score"], frenzy_count
        else:
            return None, None, 0, frenzy_count

def main():
    """Teste do sistema corrigido"""
    sniper = SecureSniperSystem()
    
    print("🧪 TESTE DO SISTEMA CORRIGIDO")
    print("=" * 50)
    
    # Teste de validação
    print("1. Testando validação de indicadores...")
    test_data = pd.DataFrame({
        'close': [100, 101, 102, 103, 104] * 10,
        'volume': [1000, 1100, 1200, 1300, 1400] * 10
    })
    
    validation = sniper.validate_indicators(test_data)
    print(f"   Validação: {'✅' if validation.valid else '❌'}")
    if validation.errors:
        print(f"   Erros: {validation.errors}")
    
    # Teste de rate limiting
    print("2. Testando rate limiting...")
    start_time = time.time()
    for i in range(5):
        result = sniper.safe_api_call(get_futures_price, sniper.session, "BTCUSDT")
        print(f"   Request {i+1}: {'✅' if result else '❌'}")
    end_time = time.time()
    print(f"   Tempo total: {end_time - start_time:.2f}s")
    
    # Teste de análise
    print("3. Testando análise segura...")
    best_trade, direction, score, frenzy = sniper.find_best_trade_safe()
    if best_trade:
        print(f"   Melhor trade: {best_trade['symbol']} {direction} - {score}/10")
    else:
        print("   Nenhum trade encontrado")
    
    print("✅ Teste concluído!")

if __name__ == "__main__":
    main()
