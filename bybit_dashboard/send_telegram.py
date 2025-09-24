#!/usr/bin/env python3
"""
Script para enviar mensagens de trading para o Telegram
Uso: python3 send_telegram.py [chat_id]
"""
import os
import sys
import requests
from dotenv import load_dotenv
from bybit_api import connect_bybit, get_price, get_balance
from strategy import get_entry_levels
from datetime import datetime

# Carrega variáveis do .env
load_dotenv()

def send_trading_alert(chat_id):
    """Envia alerta de trading para o chat especificado"""
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ Token do Telegram não encontrado no .env")
        return False
    
    try:
        # Conecta com a API da Bybit
        session = connect_bybit()
        
        # Obtém dados de mercado
        price = get_price(session, 'BTCUSDT')
        balance = get_balance(session)
        
        # Calcula níveis de entrada
        entry_levels = get_entry_levels(price)
        
        # Monta mensagem formatada
        message = f"""
🤖 <b>BYBIT TRADING ALERT</b>
⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

💰 <b>Dados de Mercado:</b>
• Preço BTC/USDT: <code>{price:,.2f}</code>
• Saldo USDT: <code>{balance:.2f}</code>

🎯 <b>Níveis de Entrada Sugeridos:</b>
• Entrada 1: <code>{entry_levels[0]:,.2f}</code> (0%)
• Entrada 2: <code>{entry_levels[1]:,.2f}</code> (-1.5%)
• Entrada 3: <code>{entry_levels[2]:,.2f}</code> (-3.5%)

📊 <b>Status:</b> ✅ API funcionando
🔧 <b>Modo:</b> Apenas sugestões

<i>Bot configurado e operacional!</i>
        """
        
        # Envia mensagem
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message.strip(),
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Alerta de trading enviado com sucesso!")
            print(f"📱 Chat ID: {chat_id}")
            return True
        else:
            print(f"❌ Erro ao enviar: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def get_bot_info():
    """Obtém informações do bot"""
    token = os.getenv('TELEGRAM_TOKEN')
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url)
        
        if response.status_code == 200:
            bot_info = response.json()
            print("🤖 Informações do bot:")
            print(f"   Nome: {bot_info['result']['first_name']}")
            print(f"   Username: @{bot_info['result']['username']}")
            print(f"   ID: {bot_info['result']['id']}")
            return True
        else:
            print(f"❌ Erro ao obter informações: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        chat_id = sys.argv[1]
        print(f"📤 Enviando alerta para chat_id: {chat_id}")
        send_trading_alert(chat_id)
    else:
        print("🤖 Bot do Telegram - Bybit Trading")
        print("=" * 40)
        get_bot_info()
        print("\n📝 Como usar:")
        print("1. Procure por @FlowBybit_bot no Telegram")
        print("2. Inicie uma conversa com /start")
        print("3. Envie qualquer mensagem para obter seu chat_id")
        print("4. Execute: python3 send_telegram.py [seu_chat_id]")
        print("\n💡 Dica: Use @userinfobot no Telegram para obter seu chat_id")

if __name__ == "__main__":
    main()
