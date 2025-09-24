#!/usr/bin/env python3
"""
🔧 CORREÇÃO DA CHAVE OPENAI - SNIPER NEØ
Script para configurar a chave do OpenAI
"""

import os
import re

def add_openai_key():
    """Adiciona chave do OpenAI ao arquivo .env"""
    
    print("🔧 CORREÇÃO DA CHAVE OPENAI - SNIPER NEØ")
    print("=" * 50)
    print()
    print("⚠️  ERRO: OPENAI_SECRET_KEY não configurada")
    print("💡 SOLUÇÃO: Configure sua chave do OpenAI")
    print()
    
    # Lê arquivo atual
    with open('.env', 'r') as f:
        content = f.read()
    
    # Verifica se já existe
    if 'OPENAI_SECRET_KEY' in content:
        print("✅ OPENAI_SECRET_KEY já existe no arquivo .env")
        return
    
    # Adiciona chave do OpenAI
    openai_config = """
# 🤖 CONFIGURAÇÕES OPENAI
OPENAI_SECRET_KEY=your_openai_api_key_here
OPENAI_ASSISTANT_ID=your_assistant_id_here
"""
    
    # Adiciona ao final do arquivo
    content += openai_config
    
    # Salva arquivo atualizado
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✅ OPENAI_SECRET_KEY adicionada ao arquivo .env")
    print("📝 EDITE o arquivo .env e configure sua chave do OpenAI")

def show_instructions():
    """Mostra instruções para obter chave do OpenAI"""
    
    print("\n📋 COMO OBTER SUA CHAVE DO OPENAI:")
    print("1. Acesse: https://platform.openai.com/api-keys")
    print("2. Faça login na sua conta OpenAI")
    print("3. Clique em: Create new secret key")
    print("4. Copie a chave gerada")
    print("5. Edite o arquivo .env e substitua 'your_openai_api_key_here'")
    print()
    print("📋 COMO OBTER ASSISTANT ID:")
    print("1. Acesse: https://platform.openai.com/assistants")
    print("2. Crie um novo Assistant ou use um existente")
    print("3. Copie o Assistant ID")
    print("4. Edite o arquivo .env e substitua 'your_assistant_id_here'")

def analyze_flow():
    """Analisa o fluxo de análise dupla"""
    
    print("\n🔍 ANÁLISE DO FLUXO ATUAL:")
    print("=" * 40)
    print()
    print("📊 FLUXO DE ANÁLISE DUPLA:")
    print("1. 🎯 SNIPER NEØ analisa 413 ativos")
    print("2. 📈 Identifica TOP 6 melhores oportunidades")
    print("3. 🤖 OpenAI Assistant analisa apenas os TOP 6")
    print("4. 💡 Gera análise avançada e sugestões")
    print()
    print("✅ VANTAGENS:")
    print("- Filtro eficiente: API faz triagem inicial")
    print("- Análise focada: IA analisa apenas os melhores")
    print("- Economia de tokens: Não analisa todos os 413")
    print("- Qualidade: Dupla validação")
    print()
    print("⚠️  CONSIDERAÇÕES:")
    print("- Latência: Dupla análise demora mais")
    print("- Custo: Tokens do OpenAI para cada análise")
    print("- Complexidade: Mais pontos de falha")
    print()
    print("🎯 RECOMENDAÇÃO:")
    print("O fluxo está BEM OTIMIZADO!")
    print("- API faz triagem rápida (413 → TOP 6)")
    print("- IA analisa apenas os melhores (6 ativos)")
    print("- Resultado: Análise de qualidade com eficiência")

def main():
    """Função principal"""
    try:
        add_openai_key()
        show_instructions()
        analyze_flow()
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Configure sua chave do OpenAI no arquivo .env")
        print("2. Configure seu Assistant ID no arquivo .env")
        print("3. Execute: python telegram_sniper_enhanced.py")
        print("4. Teste o comando /analyze no Telegram")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
