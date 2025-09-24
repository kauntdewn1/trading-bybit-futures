#!/usr/bin/env python3
"""
Bot do Telegram para Bybit Trading
Responde a comandos e envia alertas de trading
"""
import os
import requests
import json
from dotenv import load_dotenv
from bybit_api import connect_bybit, get_price, get_balance, get_klines
from strategy import get_entry_levels
from datetime import datetime

# Carrega variáveis do .env
load_dotenv()

class BybitTelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_TOKEN')
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        
    def get_updates(self, offset=None):
        """Obtém mensagens não lidas"""
        url = f"{self.base_url}/getUpdates"
        params = {'offset': offset} if offset else {}
        
        try:
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Erro ao obter updates: {e}")
            return None
    
    def send_message(self, chat_id, text, parse_mode='HTML'):
        """Envia mensagem para o chat"""
        url = f"{self.base_url}/sendMessage"
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
    
    def get_trading_data(self):
        """Obtém dados de trading da Bybit"""
        try:
            session = connect_bybit()
            price = get_price(session, 'BTCUSDT')
            balance = get_balance(session)
            entry_levels = get_entry_levels(price)
            
            return {
                'price': price,
                'balance': balance,
                'entry_levels': entry_levels,
                'timestamp': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def format_trading_alert(self, data):
        """Formata alerta de trading"""
        if 'error' in data:
            return f"❌ Erro ao obter dados: {data['error']}"
        
        return f"""
🤖 <b>BYBIT TRADING ALERT</b>
⏰ {data['timestamp']}

💰 <b>Dados de Mercado:</b>
• Preço BTC/USDT: <code>{data['price']:,.2f}</code>
• Saldo USDT: <code>{data['balance']:.2f}</code>

🎯 <b>Níveis de Entrada Sugeridos:</b>
• Entrada 1: <code>{data['entry_levels'][0]:,.2f}</code> (0%)
• Entrada 2: <code>{data['entry_levels'][1]:,.2f}</code> (-1.5%)
• Entrada 3: <code>{data['entry_levels'][2]:,.2f}</code> (-3.5%)

📊 <b>Status:</b> ✅ API funcionando
🔧 <b>Modo:</b> Apenas sugestões

<i>Bot configurado e operacional!</i>
        """
    
    def handle_command(self, chat_id, command):
        """Processa comandos recebidos"""
        command = command.lower().strip()
        
        if command == '/start':
            welcome = """
🤖 <b>Bem-vindo ao Bybit Trading Bot!</b>

<b>Comandos disponíveis:</b>
/price - Preço atual do BTC
/balance - Saldo da conta
/levels - Níveis de entrada sugeridos
/alert - Alerta completo de trading
/getchatid - Mostra seu Chat ID
/help - Mostra esta ajuda

<i>Bot configurado e operacional!</i>
            """
            return self.send_message(chat_id, welcome)
        
        elif command == '/help':
            help_text = """
📚 <b>Comandos do Bot:</b>

/price - Preço atual BTC/USDT
/balance - Saldo USDT da conta
/levels - Níveis de entrada sugeridos
/alert - Alerta completo de trading
/getchatid - Mostra seu Chat ID
/help - Mostra esta ajuda

<i>Digite qualquer comando para começar!</i>
            """
            return self.send_message(chat_id, help_text)
        
        elif command == '/price':
            data = self.get_trading_data()
            if 'error' not in data:
                price_text = f"💰 <b>Preço BTC/USDT:</b> <code>{data['price']:,.2f}</code>"
                return self.send_message(chat_id, price_text)
            else:
                return self.send_message(chat_id, f"❌ Erro: {data['error']}")
        
        elif command == '/balance':
            data = self.get_trading_data()
            if 'error' not in data:
                balance_text = f"💳 <b>Saldo USDT:</b> <code>{data['balance']:.2f}</code>"
                return self.send_message(chat_id, balance_text)
            else:
                return self.send_message(chat_id, f"❌ Erro: {data['error']}")
        
        elif command == '/levels':
            data = self.get_trading_data()
            if 'error' not in data:
                levels_text = f"""
🎯 <b>Níveis de Entrada Sugeridos:</b>
• Entrada 1: <code>{data['entry_levels'][0]:,.2f}</code> (0%)
• Entrada 2: <code>{data['entry_levels'][1]:,.2f}</code> (-1.5%)
• Entrada 3: <code>{data['entry_levels'][2]:,.2f}</code> (-3.5%)
                """
                return self.send_message(chat_id, levels_text)
            else:
                return self.send_message(chat_id, f"❌ Erro: {data['error']}")
        
        elif command == '/alert':
            data = self.get_trading_data()
            alert_text = self.format_trading_alert(data)
            return self.send_message(chat_id, alert_text)
        
        elif command == '/getchatid':
            chat_info = f"""
🆔 <b>Informações do Chat:</b>
• Chat ID: <code>{chat_id}</code>
• Tipo: {message.get('chat', {}).get('type', 'N/A')}
• Nome: {message.get('chat', {}).get('first_name', 'N/A')}

💡 <b>Como usar:</b>
• Para enviar alertas: <code>python3 send_telegram.py {chat_id}</code>
• Para testar: <code>python3 test_telegram.py {chat_id}</code>
            """
            return self.send_message(chat_id, chat_info)
        
        else:
            unknown_text = """
❓ <b>Comando não reconhecido!</b>

Digite /help para ver os comandos disponíveis.
            """
            return self.send_message(chat_id, unknown_text)
    
    def run(self):
        """Executa o bot em loop"""
        print("🤖 Iniciando bot do Telegram...")
        print("📱 Bot: @FlowBybit_bot")
        print("⏹️  Pressione Ctrl+C para parar")
        
        offset = None
        
        try:
            while True:
                updates = self.get_updates(offset)
                
                if updates and updates.get('ok'):
                    for update in updates['result']:
                        if 'message' in update:
                            message = update['message']
                            chat_id = message['chat']['id']
                            text = message.get('text', '')
                            
                            print(f"📨 Mensagem recebida de {chat_id}: {text}")
                            
                            # Processa comando
                            self.handle_command(chat_id, text)
                            
                            # Atualiza offset
                            offset = update['update_id'] + 1
                
                # Aguarda 1 segundo antes da próxima verificação
                import time
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️  Bot parado pelo usuário")
        except Exception as e:
            print(f"❌ Erro no bot: {e}")

def main():
    """Função principal"""
    bot = BybitTelegramBot()
    bot.run()

if __name__ == "__main__":
    main()
