#!/usr/bin/env python3
"""
📱 ENVIAR ANÁLISE VIA TELEGRAM - SNIPER NEØ
Script para enviar análise sob demanda via Telegram
"""

import sys
import os
import requests
from dotenv import load_dotenv
from sniper_system import SniperSystem

load_dotenv()

def send_telegram_message(chat_id, message):
    """Envia mensagem para Telegram"""
    token = os.getenv('TELEGRAM_TOKEN')
    
    if not token:
        print("❌ Token do Telegram não encontrado")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("✅ Análise enviada para o Telegram!")
            return True
        else:
            print(f"❌ Erro ao enviar: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def format_analysis_result(ranking, threshold):
    """Formata resultado da análise para Telegram"""
    if not ranking:
        return "❌ <b>Erro na análise</b>\nTente novamente em alguns segundos."
    
    message = f"🏆 <b>TOP {min(6, len(ranking))} ATIVOS RANQUEADOS</b>\n\n"
    
    for i, ativo in enumerate(ranking[:6], 1):
        emoji = "🟢" if ativo['direcao'] == "LONG" else "🔴"
        message += f"{i}º {emoji} <b>{ativo['ativo']}</b> {ativo['direcao']}\n"
        message += f"   Score: <b>{ativo['score']}/10</b>\n"
        message += f"   RSI: {ativo['dados']['rsi']} | MACD: {ativo['dados']['macd']}\n"
        message += f"   Volume: {ativo['dados']['volume']} | Funding: {ativo['dados']['funding']}\n\n"
    
    # Verifica se há alvo
    best = ranking[0]
    if best['score'] >= threshold:
        message += f"🎯 <b>ALVO IDENTIFICADO!</b>\n"
        message += f"<b>{best['ativo']}</b> {best['direcao']} - Score: {best['score']}/10"
    else:
        message += f"⏳ Nenhum alvo acima do threshold {threshold}/10"
    
    return message

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python3 send_analysis_telegram.py <chat_id> [símbolos]")
        print("Exemplo: python3 send_analysis_telegram.py 6582122066")
        print("Exemplo: python3 send_analysis_telegram.py 6582122066 BTCUSDT,ETHUSDT")
        return
    
    chat_id = sys.argv[1]
    symbols = sys.argv[2].split(',') if len(sys.argv) > 2 else None
    
    print("🔍 SNIPER NEØ - ANÁLISE VIA TELEGRAM")
    print("=" * 50)
    
    # Executa análise
    sniper = SniperSystem()
    
    if symbols:
        print(f"📊 Analisando símbolos específicos: {', '.join(symbols)}")
        ranking = sniper.analyze_on_demand(symbols)
    else:
        print("📊 Analisando todos os ativos padrão")
        ranking = sniper.analyze_on_demand()
    
    # Formata resultado
    message = format_analysis_result(ranking, sniper.threshold)
    
    # Envia para Telegram
    success = send_telegram_message(chat_id, message)
    
    if success:
        print("🎯 Análise enviada com sucesso!")
    else:
        print("❌ Falha ao enviar análise")

if __name__ == "__main__":
    main()
