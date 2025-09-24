#!/usr/bin/env python3
"""
Adiciona OPENAI_ASSISTANT_ID ao .env
"""

import os
from dotenv import load_dotenv, set_key

def add_assistant_id():
    """Adiciona Assistant ID ao .env"""
    
    print("🔧 ADICIONANDO OPENAI_ASSISTANT_ID AO .ENV")
    print("=" * 50)
    
    # Carrega .env existente
    load_dotenv()
    
    # Verifica se já existe
    existing_id = os.getenv("OPENAI_ASSISTANT_ID")
    if existing_id:
        print(f"✅ OPENAI_ASSISTANT_ID já existe: {existing_id}")
        return existing_id
    
    print("📝 Para obter o Assistant ID:")
    print("1. Acesse: https://platform.openai.com/playground")
    print("2. Clique em 'Assistants' no menu lateral")
    print("3. Crie um novo Assistant")
    print("4. Use este prompt:")
    print()
    print("PROMPT DO ASSISTANT:")
    print("-" * 40)
    print("""
Você é um analista técnico especializado em criptomoedas e trading. Sua função é analisar dados de gráficos e indicadores técnicos para validar sinais de trading.

DADOS DE ENTRADA:
- Símbolo do ativo (ex: BTCUSDT)
- Preço atual e variação 24h
- Volatilidade do mercado
- Indicadores técnicos (RSI, MACD, Volume, Funding, OI)
- Score do sistema (0-10)
- Dados históricos OHLCV

ANÁLISE SOLICITADA:
1. Análise técnica detalhada do gráfico
2. Confirmação ou refutação do sinal
3. Nível de confiança (1-10)
4. Recomendações de entrada/saída
5. Stop-loss e take-profit sugeridos
6. Riscos identificados

FORMATO DE RESPOSTA:
Sempre responda em JSON estruturado:
{
    "analysis": "Análise técnica detalhada",
    "signal_confirmation": true/false,
    "confidence_level": 1-10,
    "entry_recommendation": "LONG/SHORT/HOLD",
    "stop_loss": "Preço sugerido",
    "take_profit": "Preço sugerido",
    "risks": ["Lista de riscos"],
    "reasoning": "Explicação da decisão"
}

REGRAS:
- Seja objetivo e técnico
- Baseie decisões em dados concretos
- Identifique padrões de gráfico
- Considere contexto de mercado
- Seja conservador com confiança baixa
    """)
    print("-" * 40)
    print()
    
    # Adiciona um Assistant ID de exemplo (você pode substituir)
    example_id = "asst_example123"
    print(f"📝 Adicionando Assistant ID de exemplo: {example_id}")
    print("⚠️  Substitua por seu Assistant ID real no arquivo .env")
    
    # Adiciona ao .env
    set_key(".env", "OPENAI_ASSISTANT_ID", example_id)
    print(f"✅ OPENAI_ASSISTANT_ID adicionado ao .env")
    
    return example_id

def show_current_config():
    """Mostra configuração atual"""
    
    print("\n📋 CONFIGURAÇÃO ATUAL:")
    print("=" * 30)
    
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_SECRET_KEY")
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    
    print(f"OPENAI_SECRET_KEY: {'✅' if openai_key else '❌'}")
    print(f"OPENAI_ASSISTANT_ID: {'✅' if assistant_id else '❌'}")
    print(f"TELEGRAM_TOKEN: {'✅' if telegram_token else '❌'}")
    
    if openai_key and assistant_id and telegram_token:
        print("\n✅ TODAS AS CONFIGURAÇÕES OK!")
        print("🎯 Sistema pronto para uso!")
        return True
    else:
        print("\n❌ CONFIGURAÇÕES INCOMPLETAS!")
        return False

def main():
    """Função principal"""
    
    print("🥷 SNIPER NEØ + OPENAI ASSISTANT")
    print("=" * 50)
    
    # Adiciona Assistant ID
    assistant_id = add_assistant_id()
    
    # Mostra configuração
    show_current_config()
    
    print("\n🚀 PRÓXIMOS PASSOS:")
    print("1. Substitua o Assistant ID no .env pelo seu real")
    print("2. Execute: python test_openai_integration.py")
    print("3. Execute: python telegram_ai_bot.py")

if __name__ == "__main__":
    main()
