#!/usr/bin/env python3
"""
🔍 ANÁLISE SOB DEMANDA - SNIPER NEØ
Só analisa quando você pedir - protege API da Bybit
"""

import sys
from sniper_system import SniperSystem

def main():
    """Análise sob demanda"""
    print("🔍 SNIPER NEØ - ANÁLISE SOB DEMANDA")
    print("=" * 50)
    
    # Verifica se símbolos foram fornecidos
    if len(sys.argv) > 1:
        symbols = sys.argv[1].split(',')
        print(f"📊 Analisando símbolos específicos: {', '.join(symbols)}")
    else:
        symbols = None
        print("📊 Analisando todos os ativos padrão")
    
    # Executa análise
    sniper = SniperSystem()
    ranking = sniper.analyze_on_demand(symbols)
    
    # Mostra resultado
    if ranking:
        print(f"\n✅ Análise concluída - {len(ranking)} ativos analisados")
        
        # Verifica se há alvo acima do threshold
        best = ranking[0]
        if best['score'] >= sniper.threshold:
            print(f"\n🎯 ALVO IDENTIFICADO: {best['ativo']} {best['direcao']} - Score: {best['score']}/10")
        else:
            print(f"\n⏳ Nenhum alvo acima do threshold {sniper.threshold}/10")
    else:
        print("\n❌ Nenhum ativo analisado com sucesso")

if __name__ == "__main__":
    main()
