#!/usr/bin/env python3
"""
Setup OpenAI Assistant ID - SNIPER NEØ
"""

import os
from dotenv import load_dotenv, set_key

def setup_openai_assistant():
    """Configura OpenAI Assistant ID"""
    
    print("🔧 CONFIGURAÇÃO OPENAI ASSISTANT")
    print("=" * 40)
    
    # Carrega .env existente
    load_dotenv()
    
    # Verifica se já existe
    existing_id = os.getenv("OPENAI_ASSISTANT_ID")
    if existing_id:
        print(f"✅ OPENAI_ASSISTANT_ID já configurado: {existing_id}")
        return existing_id
    
    print("📝 Para configurar o OpenAI Assistant:")
    print("1. Acesse: https://platform.openai.com/playground")
    print("2. Clique em 'Assistants' no menu lateral")
    print("3. Crie um novo Assistant com o prompt abaixo")
    print("4. Copie o Assistant ID (ex: asst_abc123...)")
    print()
    
    # Prompt do Assistant
    prompt = """
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
    """
    
    print("📋 PROMPT DO ASSISTANT:")
    print("-" * 40)
    print(prompt)
    print("-" * 40)
    print()
    
    # Solicita Assistant ID
    assistant_id = input("Cole o Assistant ID aqui: ").strip()
    
    if assistant_id and assistant_id.startswith("asst_"):
        # Adiciona ao .env
        set_key(".env", "OPENAI_ASSISTANT_ID", assistant_id)
        print(f"✅ OPENAI_ASSISTANT_ID configurado: {assistant_id}")
        return assistant_id
    else:
        print("❌ Assistant ID inválido! Deve começar com 'asst_'")
        return None

def test_configuration():
    """Testa configuração"""
    
    print("\n🧪 TESTANDO CONFIGURAÇÃO")
    print("=" * 30)
    
    # Carrega .env
    load_dotenv()
    
    # Verifica chaves
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
    
    print("🥷 SNIPER NEØ + OPENAI ASSISTANT SETUP")
    print("=" * 50)
    
    # Configura Assistant ID
    assistant_id = setup_openai_assistant()
    
    if assistant_id:
        # Testa configuração
        if test_configuration():
            print("\n🚀 PRÓXIMOS PASSOS:")
            print("1. Execute: python test_openai_integration.py")
            print("2. Execute: python telegram_ai_bot.py")
        else:
            print("\n⚠️  Configure as chaves faltantes no .env")
    else:
        print("\n❌ Configuração cancelada!")

if __name__ == "__main__":
    main()
