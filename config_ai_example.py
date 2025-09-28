#!/usr/bin/env python3
"""
Configuração e exemplo de uso - SNIPER NEØ + OpenAI Assistant
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sua_api_key_openai")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID", "seu_assistant_id")

# Configurações Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "seu_telegram_token")

# Configurações Bybit
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "sua_bybit_api_key")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "sua_bybit_api_secret")

def setup_environment():
    """Configura variáveis de ambiente"""
    
    print("🔧 CONFIGURAÇÃO SNIPER NEØ + AI")
    print("=" * 50)
    
    # Verifica se arquivo .env existe
    if not os.path.exists('.env'):
        print("❌ Arquivo .env não encontrado!")
        print("📝 Criando arquivo .env...")
        
        env_content = f"""
# OpenAI Configuration
OPENAI_API_KEY={OPENAI_API_KEY}
OPENAI_ASSISTANT_ID={OPENAI_ASSISTANT_ID}

# Telegram Configuration
TELEGRAM_TOKEN={TELEGRAM_TOKEN}

# Bybit Configuration
BYBIT_API_KEY={BYBIT_API_KEY}
BYBIT_API_SECRET={BYBIT_API_SECRET}
        """
        
        with open('.env', 'w') as f:
            f.write(env_content.strip())
        
        print("✅ Arquivo .env criado!")
        print("⚠️  Configure suas chaves no arquivo .env")
    else:
        print("✅ Arquivo .env encontrado!")
    
    print("\n📋 CONFIGURAÇÕES NECESSÁRIAS:")
    print("1. OpenAI API Key: https://platform.openai.com/api-keys")
    print("2. OpenAI Assistant ID: https://platform.openai.com/playground")
    print("3. Telegram Bot Token: @BotFather")
    print("4. Bybit API Keys: https://www.bybit.com/app/user/api-management")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Configure as chaves no arquivo .env")
    print("2. Crie um Assistant no OpenAI Playground")
    print("3. Execute: python telegram_ai_bot.py")

def test_integration():
    """Testa integração com OpenAI Assistant"""
    
    print("\n🧪 TESTE DE INTEGRAÇÃO")
    print("=" * 30)
    
    try:
        from sniper_ai_enhanced import SniperAIEnhanced
        
        # Cria instância
        sniper_ai = SniperAIEnhanced(OPENAI_API_KEY, OPENAI_ASSISTANT_ID)
        
        print("✅ SNIPER AI criado com sucesso!")
        
        # Testa busca com IA
        print("🔍 Testando busca com IA...")
        result = sniper_ai.find_best_trade_with_ai(threshold=7.0)
        
        if result.get('status') == 'no_target':
            print("❌ Nenhum alvo encontrado (normal em teste)")
        else:
            print("✅ Alvo encontrado!")
            print(f"   Ativo: {result['symbol']}")
            print(f"   Score: {result['score']}/10")
            print(f"   IA Confirmado: {result.get('ai_confirmed', False)}")
        
        # Testa estatísticas
        stats = sniper_ai.get_ai_performance_stats()
        print(f"📊 Estatísticas IA: {stats}")
        
        print("✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        print("⚠️  Verifique suas configurações no arquivo .env")

def run_telegram_bot():
    """Executa bot do Telegram com IA"""
    
    print("\n🤖 EXECUTANDO BOT TELEGRAM + AI")
    print("=" * 40)
    
    try:
        from telegram_ai_bot import SniperAITelegramBot
        
        # Cria e executa bot
        bot = SniperAITelegramBot(TELEGRAM_TOKEN, OPENAI_API_KEY, OPENAI_ASSISTANT_ID)
        bot.run_bot()
        
    except Exception as e:
        print(f"❌ Erro ao executar bot: {str(e)}")
        print("⚠️  Verifique suas configurações no arquivo .env")

def main():
    """Função principal"""
    
    print("🥷 SNIPER NEØ + OPENAI ASSISTANT")
    print("=" * 50)
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Configurar ambiente")
        print("2. Testar integração")
        print("3. Executar bot Telegram")
        print("4. Sair")
        
        choice = input("\nOpção: ").strip()
        
        if choice == "1":
            setup_environment()
        elif choice == "2":
            test_integration()
        elif choice == "3":
            run_telegram_bot()
        elif choice == "4":
            print("👋 Até logo!")
            break
        else:
            print("❌ Opção inválida!")

if __name__ == "__main__":
    main()
