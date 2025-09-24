#!/usr/bin/env python3
"""
🔑 CONFIGURAÇÃO AUTOMÁTICA DE CHAVES REAIS - SNIPER NEØ
Script para configurar suas chaves reais de TESTNET
"""

import os
import re

def set_real_keys(api_key, api_secret, telegram_token=None):
    """
    Configura chaves reais no arquivo .env
    
    Args:
        api_key: Sua API Key de TESTNET
        api_secret: Sua API Secret de TESTNET
        telegram_token: Token do Telegram (opcional)
    """
    
    print("🔑 CONFIGURAÇÃO DE CHAVES REAIS DE TESTNET")
    print("=" * 50)
    
    # Valida chaves
    if not api_key or len(api_key) < 20:
        print("❌ API Key inválida ou muito curta")
        return False
    
    if not api_secret or len(api_secret) < 20:
        print("❌ API Secret inválida ou muito curta")
        return False
    
    print("✅ Chaves válidas!")
    
    # Lê arquivo atual
    with open('.env', 'r') as f:
        content = f.read()
    
    # Substitui chaves
    content = re.sub(r'API_KEY=.*', f'API_KEY={api_key}', content)
    content = re.sub(r'API_SECRET=.*', f'API_SECRET={api_secret}', content)
    
    # Substitui token do Telegram se fornecido
    if telegram_token:
        content = re.sub(r'TELEGRAM_TOKEN=.*', f'TELEGRAM_TOKEN={telegram_token}', content)
    
    # Salva arquivo atualizado
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Arquivo .env atualizado com chaves reais!")
    return True

def test_connection():
    """Testa conexão com as novas chaves"""
    
    print("\n🔌 Testando conexão...")
    
    try:
        from bybit_api import connect_bybit
        session = connect_bybit()
        print("✅ Conexão estabelecida com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def main():
    """
    Função principal - EDITE AQUI SUAS CHAVES
    """
    
    # 🔑 EDITE AQUI SUAS CHAVES DE TESTNET
    API_KEY = "SUA_API_KEY_AQUI"
    API_SECRET = "SUA_API_SECRET_AQUI"
    TELEGRAM_TOKEN = "SEU_TELEGRAM_TOKEN_AQUI"  # Opcional
    
    print("🔑 CONFIGURAÇÃO DE CHAVES REAIS - SNIPER NEØ")
    print("=" * 50)
    print()
    print("⚠️  IMPORTANTE:")
    print("1. Edite este arquivo e substitua as chaves acima")
    print("2. Use APENAS chaves de TESTNET")
    print("3. NUNCA use chaves de produção")
    print()
    
    # Verifica se as chaves foram editadas
    if API_KEY == "SUA_API_KEY_AQUI" or API_SECRET == "SUA_API_SECRET_AQUI":
        print("❌ ERRO: Você precisa editar este arquivo e configurar suas chaves!")
        print()
        print("📝 COMO CONFIGURAR:")
        print("1. Abra este arquivo: set_real_keys.py")
        print("2. Substitua 'SUA_API_KEY_AQUI' pela sua API Key")
        print("3. Substitua 'SUA_API_SECRET_AQUI' pela sua API Secret")
        print("4. Execute novamente: python set_real_keys.py")
        print()
        print("🔗 OBTENHA SUAS CHAVES EM: https://testnet.bybit.com")
        return
    
    try:
        # Configura chaves
        if set_real_keys(API_KEY, API_SECRET, TELEGRAM_TOKEN):
            # Testa conexão
            if test_connection():
                print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
                print("✅ Chaves reais configuradas com sucesso")
                print("🚀 Agora você pode executar o sistema:")
                print("   python sniper_dashboard.py")
                print("   python telegram_sniper_enhanced.py")
            else:
                print("\n❌ ERRO na conexão")
                print("💡 Verifique se as chaves estão corretas")
        else:
            print("\n❌ ERRO na configuração")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
