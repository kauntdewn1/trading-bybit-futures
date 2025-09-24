#!/usr/bin/env python3
"""
🔄 MUDANÇA PARA MODO PRODUÇÃO - SNIPER NEØ
Script para mudar do modo testnet para produção
"""

import os
import re

def switch_to_production():
    """Muda configuração para modo produção"""
    
    print("🔄 MUDANÇA PARA MODO PRODUÇÃO - SNIPER NEØ")
    print("=" * 50)
    print()
    print("⚠️  ATENÇÃO: Sua chave é de PRODUÇÃO!")
    print("⚠️  Operações serão REAIS com dinheiro REAL!")
    print("⚠️  IP restrito: 181.192.114.64 (muito seguro)")
    print()
    
    # Lê arquivo atual
    with open('.env', 'r') as f:
        content = f.read()
    
    # Substitui configurações
    content = re.sub(r'TESTNET_MODE=.*', 'TESTNET_MODE=false', content)
    content = re.sub(r'PRODUCTION_MODE=.*', 'PRODUCTION_MODE=true', content)
    content = re.sub(r'PRODUCTION_CONFIRMED=.*', 'PRODUCTION_CONFIRMED=true', content)
    content = re.sub(r'BASE_URL=.*', 'BASE_URL=https://api.bybit.com', content)
    content = re.sub(r'WS_URL=.*', 'WS_URL=wss://stream.bybit.com', content)
    
    # Salva arquivo atualizado
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ Configuração alterada para PRODUÇÃO!")
    print("🔒 IP restrito: 181.192.114.64")
    print("⚠️  OPERAÇÕES REAIS - USE COM CUIDADO!")

def test_connection():
    """Testa conexão em modo produção"""
    
    print("\n🔌 Testando conexão em modo PRODUÇÃO...")
    
    try:
        from bybit_api import connect_bybit
        session = connect_bybit()
        print("✅ Conexão estabelecida com sucesso!")
        print("🎉 Sua chave está funcionando em PRODUÇÃO!")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return False

def main():
    """Função principal"""
    try:
        switch_to_production()
        
        # Testa conexão
        if test_connection():
            print("\n🎉 CONFIGURAÇÃO CONCLUÍDA!")
            print("✅ Sistema configurado para PRODUÇÃO")
            print("🔒 IP restrito: 181.192.114.64 (muito seguro!)")
            print("⚠️  OPERAÇÕES REAIS - USE COM CUIDADO!")
            print("🚀 Agora você pode executar o sistema:")
            print("   python sniper_dashboard.py")
            print("   python telegram_sniper_enhanced.py")
        else:
            print("\n❌ ERRO na conexão")
            print("💡 Verifique se a chave está correta")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
