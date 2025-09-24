#!/usr/bin/env python3
"""
Script para descobrir o Chat ID do Telegram
"""
import os
import requests
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

def get_chat_id():
    """Obtém o chat_id das mensagens recebidas"""
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ Token do Telegram não encontrado no .env")
        return
    
    url = f"https://api.telegram.org/bot{token}/getUpdates"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get('ok'):
            updates = data['result']
            
            if not updates:
                print("📱 Nenhuma mensagem recebida ainda.")
                print("\n💡 Para descobrir seu chat_id:")
                print("1. Procure por @FlowBybit_bot no Telegram")
                print("2. Envie /start ou qualquer mensagem")
                print("3. Execute este script novamente")
                return
            
            print("📨 Mensagens recebidas:")
            print("=" * 40)
            
            for update in updates:
                if 'message' in update:
                    message = update['message']
                    chat = message['chat']
                    user = message.get('from', {})
                    
                    print(f"🆔 Chat ID: {chat['id']}")
                    print(f"👤 Nome: {user.get('first_name', 'N/A')}")
                    print(f"📝 Mensagem: {message.get('text', 'N/A')}")
                    print(f"⏰ Data: {message.get('date', 'N/A')}")
                    print("-" * 40)
            
            # Pega o último chat_id
            last_update = updates[-1]
            if 'message' in last_update:
                chat_id = last_update['message']['chat']['id']
                print(f"\n✅ Seu Chat ID é: {chat_id}")
                print(f"\n💡 Para enviar alertas:")
                print(f"   python3 send_telegram.py {chat_id}")
                print(f"   python3 test_telegram.py {chat_id}")
        
        else:
            print(f"❌ Erro: {data.get('description', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🔍 DESCOBRINDO CHAT ID DO TELEGRAM")
    print("=" * 40)
    get_chat_id()

if __name__ == "__main__":
    main()
