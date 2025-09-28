#!/usr/bin/env python3
"""
📱 TELEGRAM SNIPER BOT NEØ - INTEGRAÇÃO COMPLETA
Bot para análise sob demanda via Telegram
"""

import os
import json
import requests
from dotenv import load_dotenv
from sniper_system import SniperSystem
from datetime import datetime

load_dotenv()

class TelegramSniperBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.sniper = SniperSystem()
        self.last_update_id = 0
        
    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Envia mensagem para Telegram"""
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")
            return False
    
    def get_updates(self):
        """Obtém atualizações do Telegram"""
        url = f"https://api.telegram.org/bot{self.token}/getUpdates"
        
        params = {
            'offset': self.last_update_id + 1,
            'timeout': 30
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Erro ao obter updates: {e}")
        
        return None
    
    def handle_command(self, chat_id, command, args=""):
        """Processa comandos do Telegram"""
        
        if command == '/start':
            message = """
🥷 <b>SNIPER NEØ - BOT DE TRADING</b>

<b>Comandos disponíveis:</b>
/analyze - Análise completa (6 ativos)
/analyze BTCUSDT,ETHUSDT - Análise específica
/ranking - TOP 6 ativos ranqueados
/rank - TOP 6 ativos ranqueados
/ranki - TOP 6 ativos ranqueados
/status - Status do sistema
/help - Ajuda

<b>Exemplo:</b>
/analyze BTCUSDT,ETHUSDT
/ranking
            """
            return self.send_message(chat_id, message)
        
        elif command == '/analyze':
            # Análise completa com scan dinâmico
            symbols = args.split(',') if args else None
            
            # Envia mensagem de processamento
            self.send_message(chat_id, "🔍 <b>SCAN DINÂMICO COMPLETO</b>\n📊 Varrendo TODOS os ativos de futuros...\n⏳ Aguarde alguns segundos...")
            
            # Executa análise
            try:
                # Força atualização da lista de ativos se não especificado
                if not symbols:
                    self.sniper.assets = self.sniper.get_all_futures_symbols()
                
                ranking = self.sniper.analyze_on_demand(symbols)
                
                if not ranking:
                    return self.send_message(chat_id, "❌ <b>Erro na análise</b>\nTente novamente em alguns segundos.")
                
                # Formata resultado
                message = f"🏆 <b>TOP {min(6, len(ranking))} ATIVOS RANQUEADOS</b>\n"
                message += f"📊 Total analisado: {len(self.sniper.assets)} ativos\n\n"
                
                for i, ativo in enumerate(ranking[:6], 1):
                    emoji = "🟢" if ativo['direcao'] == "LONG" else "🔴"
                    frenzy_emoji = "🚨" if ativo['score'] >= 8 else ""
                    message += f"{i}º {emoji}{frenzy_emoji} <b>{ativo['ativo']}</b> {ativo['direcao']}\n"
                    message += f"   Score: <b>{ativo['score']}/10</b>\n"
                    message += f"   RSI: {ativo['dados']['rsi']} | MACD: {ativo['dados']['macd']}\n"
                    message += f"   Volume: {ativo['dados']['volume']} | Funding: {ativo['dados']['funding']}\n"
                    
                    # Mostra combo patterns se existirem
                    combo_patterns = ativo['dados'].get('combo_patterns_long' if ativo['direcao'] == 'LONG' else 'combo_patterns_short', [])
                    if combo_patterns:
                        message += f"   🔥 Combos: {', '.join(combo_patterns)}\n"
                    
                    # Mostra ajustes cirúrgicos
                    volatility_mult = ativo['dados'].get('volatility_mult', 1.0)
                    capital_weight = ativo['dados'].get('capital_weight', 1.0)
                    message += f"   ⚡ Vol: {volatility_mult}x | Cap: {capital_weight}x\n\n"
                
                # Verifica se há alvo
                best = ranking[0]
                if best['score'] >= self.sniper.threshold:
                    message += f"🎯 <b>ALVO IDENTIFICADO!</b>\n"
                    message += f"<b>{best['ativo']}</b> {best['direcao']} - Score: {best['score']}/10"
                else:
                    message += f"⏳ Nenhum alvo acima do threshold {self.sniper.threshold}/10"
                
                return self.send_message(chat_id, message)
                
            except Exception as e:
                return self.send_message(chat_id, f"❌ <b>Erro na análise:</b> {str(e)}")
        
        elif command in ['/ranking', '/rank', '/ranki']:
            # Ranking rápido com scan dinâmico
            try:
                # Força atualização da lista de ativos
                self.sniper.assets = self.sniper.get_all_futures_symbols()
                ranking = self.sniper.get_full_ranking()
                
                message = f"🏆 <b>TOP 6 ATIVOS RANQUEADOS</b>\n"
                message += f"📊 Total analisado: {len(self.sniper.assets)} ativos\n\n"
                
                for i, ativo in enumerate(ranking[:6], 1):
                    emoji = "🟢" if ativo['direcao'] == "LONG" else "🔴"
                    message += f"{i}º {emoji} <b>{ativo['ativo']}</b> {ativo['direcao']} - {ativo['score']}/10\n"
                
                return self.send_message(chat_id, message)
                
            except Exception as e:
                return self.send_message(chat_id, f"❌ <b>Erro no ranking:</b> {str(e)}")
        
        elif command == '/status':
            # Status do sistema
            try:
                # Testa API
                from bybit_api import connect_bybit, get_futures_price
                session = connect_bybit()
                price_data = get_futures_price(session, 'BTCUSDT')
                
                message = f"""
🟢 <b>SISTEMA SNIPER NEØ - ONLINE</b>

<b>Status:</b>
✅ API Bybit: Conectada
✅ Preço BTC: ${price_data['price']:,.2f}
✅ Threshold: {self.sniper.threshold}/10
✅ Ativos: {len(self.sniper.assets)}

<b>Última atualização:</b> {datetime.now().strftime('%H:%M:%S')}
                """
                
                return self.send_message(chat_id, message)
                
            except Exception as e:
                return self.send_message(chat_id, f"❌ <b>Sistema offline:</b> {str(e)}")
        
        elif command == '/help':
            message = """
🥷 <b>SNIPER NEØ - AJUDA</b>

<b>Comandos:</b>
/analyze - Análise completa
/analyze BTCUSDT,ETHUSDT - Análise específica
/ranking - TOP 6 ativos
/rank - TOP 6 ativos (alternativo)
/ranki - TOP 6 ativos (alternativo)
/status - Status do sistema

<b>Exemplos:</b>
/analyze BTCUSDT
/analyze BTCUSDT,ETHUSDT,SOLUSDT
/ranking
/ranki

<b>Fluxo recomendado:</b>
1. /status - Verifica se está online
2. /analyze - Análise completa
3. /ranking - Ver TOP 6
4. Operar na Bybit com base no resultado
            """
            return self.send_message(chat_id, message)
        
        else:
            return self.send_message(chat_id, "❌ <b>Comando não reconhecido</b>\nUse /help para ver os comandos disponíveis.")
    
    def process_updates(self):
        """Processa atualizações do Telegram"""
        updates = self.get_updates()
        
        if not updates or not updates.get('ok'):
            return
        
        for update in updates.get('result', []):
            self.last_update_id = update['update_id']
            
            if 'message' in update:
                message = update['message']
                chat_id = message['chat']['id']
                text = message.get('text', '')
                
                # Processa comando
                if text.startswith('/'):
                    parts = text.split(' ', 1)
                    command = parts[0]
                    args = parts[1] if len(parts) > 1 else ""
                    
                    print(f"📱 Comando recebido: {command} {args}")
                    self.handle_command(chat_id, command, args)
    
    def run(self):
        """Executa o bot"""
        print("🤖 TELEGRAM SNIPER BOT NEØ INICIADO")
        print("=" * 50)
        print("📱 Envie /start para começar")
        print("⏹️  Pressione Ctrl+C para parar")
        
        try:
            while True:
                self.process_updates()
        except KeyboardInterrupt:
            print("\n🛑 Bot parado pelo usuário")

def main():
    """Função principal"""
    bot = TelegramSniperBot()
    bot.run()

if __name__ == "__main__":
    main()
