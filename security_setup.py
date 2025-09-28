#!/usr/bin/env python3
"""
🔒 SECURITY SETUP NEØ - CONFIGURAÇÃO DE SEGURANÇA
Script para configurar ambiente seguro do SNIPER NEØ
"""

import os
import shutil
from pathlib import Path

def create_env_file():
    """Cria arquivo .env com configurações seguras"""
    
    env_content = """# 🔒 CONFIGURAÇÃO DE SEGURANÇA CRÍTICA - SNIPER NEØ
# ⚠️ CONFIGURE SUAS CHAVES REAIS AQUI

# ===========================================
# 🚨 CONFIGURAÇÃO DE AMBIENTE (CRÍTICO)
# ===========================================

# Modo de operação - MUDANÇA CRÍTICA DE SEGURANÇA
# true = Testnet (simulado) | false = Produção (dinheiro real)
TESTNET_MODE=true

# Confirmação para produção (apenas se TESTNET_MODE=false)
# Deve ser explicitamente definido como true para operar com dinheiro real
PRODUCTION_MODE=false
PRODUCTION_CONFIRMED=false

# ===========================================
# 🔑 CHAVES DE API BYBIT
# ===========================================

# Suas chaves de API da Bybit
# Obtenha em: https://www.bybit.com/app/user/api-management
API_KEY=sua_api_key_aqui
API_SECRET=sua_api_secret_aqui

# ===========================================
# 📱 CONFIGURAÇÃO TELEGRAM
# ===========================================

# Token do bot Telegram
# Obtenha com @BotFather no Telegram
TELEGRAM_TOKEN=seu_telegram_token_aqui

# Chat ID para receber alertas
# Use get_chat_id.py para descobrir seu chat ID
TELEGRAM_CHAT_ID=seu_chat_id_aqui

# ===========================================
# 🤖 CONFIGURAÇÃO OPENAI (OPCIONAL)
# ===========================================

# Chave da API OpenAI
# Obtenha em: https://platform.openai.com/api-keys
OPENAI_API_KEY=sua_openai_api_key_aqui
OPENAI_SECRET_KEY=sua_openai_secret_key_aqui

# ID do Assistant OpenAI
# Crie um assistant no playground OpenAI
OPENAI_ASSISTANT_ID=seu_assistant_id_aqui

# ===========================================
# ⚙️ CONFIGURAÇÕES AVANÇADAS
# ===========================================

# Intervalo entre análises (em minutos)
ANALYSIS_INTERVAL=15

# Threshold mínimo para alertas (0-10)
DEFAULT_THRESHOLD=7.0

# Modo de debug (true/false)
DEBUG_MODE=false

# ===========================================
# 🛡️ CONFIGURAÇÕES DE SEGURANÇA
# ===========================================

# Tamanho máximo de posição (USDT)
MAX_POSITION_SIZE=1000.0

# Número máximo de trades por dia
MAX_DAILY_TRADES=10

# Requer confirmação para trades (true/false)
REQUIRE_CONFIRMATION=true
"""
    
    # Verifica se .env já existe
    if os.path.exists('.env'):
        backup_name = '.env.backup'
        counter = 1
        while os.path.exists(f'{backup_name}.{counter}'):
            counter += 1
        backup_name = f'{backup_name}.{counter}'
        
        shutil.copy2('.env', backup_name)
        print(f"✅ Backup do .env criado: {backup_name}")
    
    # Cria novo .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Arquivo .env criado com configurações seguras")
    print("⚠️  Configure suas chaves reais no arquivo .env")

def create_security_config():
    """Cria arquivo de configuração de segurança"""
    from security_validator import create_security_config_file
    create_security_config_file()

def validate_current_setup():
    """Valida configuração atual"""
    print("\n🔍 VALIDANDO CONFIGURAÇÃO ATUAL...")
    
    try:
        from security_validator import SecurityValidator
        validator = SecurityValidator()
        
        # Testa validação de ambiente
        validator.validate_environment()
        print("✅ Ambiente validado com sucesso")
        
        # Mostra status
        status = validator.get_security_status()
        print(f"📊 Status: {status['environment']}")
        print(f"📊 Trades hoje: {status['daily_trades']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def show_security_warnings():
    """Mostra avisos de segurança importantes"""
    warnings = """
🚨 AVISOS DE SEGURANÇA CRÍTICOS:

1. 🔴 OPERAÇÕES COM DINHEIRO REAL:
   - Configure TESTNET_MODE=false
   - Configure PRODUCTION_MODE=true  
   - Configure PRODUCTION_CONFIRMED=true
   - Configure limites de segurança adequados

2. 🟡 TESTE PRIMEIRO:
   - Use TESTNET_MODE=true para testes
   - Valide todas as funcionalidades
   - Configure limites baixos inicialmente

3. 🛡️ SEGURANÇA:
   - Mantenha suas chaves seguras
   - Use IP whitelist na Bybit
   - Monitore logs de segurança
   - Configure alertas de segurança

4. 📋 CHECKLIST DE SEGURANÇA:
   ✅ Arquivo .env configurado
   ✅ Chaves de API válidas
   ✅ Modo testnet ativado
   ✅ Limites de segurança configurados
   ✅ Logs de segurança ativos
"""
    print(warnings)

def main():
    """Função principal de configuração"""
    print("🔒 CONFIGURAÇÃO DE SEGURANÇA - SNIPER NEØ")
    print("=" * 50)
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Criar arquivo .env seguro")
        print("2. Criar configuração de segurança")
        print("3. Validar configuração atual")
        print("4. Mostrar avisos de segurança")
        print("5. Executar configuração completa")
        print("0. Sair")
        
        choice = input("\nOpção: ").strip()
        
        if choice == "1":
            create_env_file()
            
        elif choice == "2":
            create_security_config()
            
        elif choice == "3":
            validate_current_setup()
            
        elif choice == "4":
            show_security_warnings()
            
        elif choice == "5":
            print("\n🚀 EXECUTANDO CONFIGURAÇÃO COMPLETA...")
            create_env_file()
            create_security_config()
            validate_current_setup()
            show_security_warnings()
            print("\n✅ CONFIGURAÇÃO COMPLETA!")
            
        elif choice == "0":
            print("👋 Até logo!")
            break
            
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()
