#!/usr/bin/env python3
"""
Sniper Telegram Bot - Dispara alertas de precisão
"""
import os
import json
import requests
from dotenv import load_dotenv
from sniper_system import SniperSystem

load_dotenv()

def send_sniper_alert(chat_id, alert_data):
    """Envia alerta sniper para Telegram"""
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ Token do Telegram não encontrado")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    # Se alert_data é string, usa diretamente; se é dict, pega a chave 'alert'
    if isinstance(alert_data, str):
        message_text = alert_data
    else:
        message_text = alert_data.get("alert", str(alert_data))
    
    data = {
        'chat_id': chat_id,
        'text': message_text,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Alerta sniper enviado!")
            return True
        else:
            print(f"❌ Erro ao enviar: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def run_sniper_scan_and_alert(chat_id):
    """Executa scan sniper e envia alerta"""
    print("🥷 EXECUTANDO SCAN SNIPER...")
    
    # Executa sistema sniper
    sniper = SniperSystem()
    result = sniper.run_sniper_scan()
    
    # Se encontrou alvo, envia alerta
    if result["status"] == "TARGET":
        print("🎯 ALVO ENCONTRADO - ENVIANDO ALERTA!")
        send_sniper_alert(chat_id, result)
    else:
        print("⏳ Nenhum alvo encontrado - Aguardando próximo scan")
    
    return result

def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) > 1:
        chat_id = sys.argv[1]
        print(f"🎯 Enviando para chat_id: {chat_id}")
        run_sniper_scan_and_alert(chat_id)
    else:
        print("🥷 SNIPER TELEGRAM BOT")
        print("Uso: python3 sniper_telegram.py [chat_id]")
        print("Exemplo: python3 sniper_telegram.py 6582122066")

if __name__ == "__main__":
    main()
