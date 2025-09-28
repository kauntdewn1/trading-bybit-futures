#!/usr/bin/env python3
"""
🔑 CONFIGURAÇÃO DA SUA CHAVE REAL - SNIPER NEØ
Script para configurar sua chave de API da Bybit
"""

import os
import re

def configure_real_key(api_key, api_secret, telegram_token=None):
    """
    Configura sua chave real no arquivo .env
    
    Args:
        api_key: Sua API Key real da Bybit
        api_secret: Sua API Secret real da Bybit
        telegram_token: Token do Telegram (opcional)
    """
    
    print("🔑 CONFIGURAÇÃO DA SUA CHAVE REAL - SNIPER NEØ")
    print("=" * 55)
    
    # Valida chaves (Bybit usa chaves de 18+ caracteres)
    if not api_key or len(api_key) < 18:
        print("❌ API Key inválida ou muito curta")
        return False
    
    if not api_secret or len(api_secret) < 20:
        print("❌ API Secret inválida ou muito curta")
        return False
    
    print("✅ Chaves válidas!")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-5:]}")
    print(f"🔑 API Secret: {api_secret[:10]}...{api_secret[-5:]}")
    
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
    
    print("✅ Arquivo .env atualizado com sua chave real!")
    return True

def test_connection():
    """Testa conexão com sua chave real"""
    
    print("\n🔌 Testando conexão com sua chave...")
    
    try:
        from bybit_api import connect_bybit
        session = connect_bybit()
        print("✅ Conexão estabelecida com sucesso!")
        print("🎉 Sua chave está funcionando perfeitamente!")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def main():
    """
    Função principal - EDITE AQUI SUA CHAVE REAL
    """
    
    # 🔑 EDITE AQUI SUA CHAVE REAL DA BYBIT
    API_KEY = "1blelhM2aNRINYK8Mt"
    API_SECRET = "ivXB3yH3VmoIm1oLxdJRPbAVo2mQkVS7Nruw"
    TELEGRAM_TOKEN = "7563910031:AAF5oYor5ba35yAdRnyKSnTZJewN7FojTqc"  # Opcional
    
    print("🔑 CONFIGURAÇÃO DA SUA CHAVE REAL - SNIPER NEØ")
    print("=" * 55)
    print()
    print("📋 INSTRUÇÕES:")
    print("1. Edite este arquivo e substitua as chaves acima")
    print("2. Use sua chave real da Bybit (não testnet)")
    print("3. Sua chave já tem IP restrito: 181.192.114.64")
    print()
    
    # Verifica se as chaves foram editadas
    if API_KEY == "SUA_API_KEY_REAL_AQUI" or API_SECRET == "SUA_API_SECRET_REAL_AQUI":
        print("❌ ERRO: Você precisa editar este arquivo e configurar sua chave!")
        print()
        print("📝 COMO CONFIGURAR:")
        print("1. Abra este arquivo: configure_your_key.py")
        print("2. Substitua 'SUA_API_KEY_REAL_AQUI' pela sua API Key")
        print("3. Substitua 'SUA_API_SECRET_REAL_AQUI' pela sua API Secret")
        print("4. Execute novamente: python configure_your_key.py")
        print()
        print("🔗 SUA CHAVE JÁ TEM IP RESTRITO: 181.192.114.64")
        print("✅ Isso é muito seguro!")
        return
    
    try:
        # Configura chave
        if configure_real_key(API_KEY, API_SECRET, TELEGRAM_TOKEN):
            # Testa conexão
            if test_connection():
                print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
                print("✅ Sua chave real configurada com sucesso")
                print("🔒 IP restrito: 181.192.114.64 (muito seguro!)")
                print("🚀 Agora você pode executar o sistema:")
                print("   python sniper_dashboard.py")
                print("   python telegram_sniper_enhanced.py")
            else:
                print("\n❌ ERRO na conexão")
                print("💡 Verifique se a chave está correta")
        else:
            print("\n❌ ERRO na configuração")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
