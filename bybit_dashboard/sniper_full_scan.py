#!/usr/bin/env python3
"""
🎯 SNIPER FULL SCAN - VARREDURA COMPLETA DO MERCADO
Varre TODOS os ativos de futuros da Bybit
"""

import sys
from sniper_system import SniperSystem

def main():
    """Executa varredura completa do mercado"""
    print("🎯 SNIPER NEØ - VARREDURA COMPLETA DO MERCADO")
    print("=" * 60)
    
    # Configura threshold
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 5.0
    
    # Inicia sniper
    sniper = SniperSystem()
    sniper.threshold = threshold
    
    print(f"📊 Threshold: {threshold}/10")
    print(f"🎯 Ativos a analisar: {len(sniper.assets)}")
    print()
    
    # Executa varredura completa
    result = sniper.run_sniper_scan()
    
    print("\n" + "=" * 60)
    print("🎯 VARREDURA COMPLETA FINALIZADA!")
    
    if result["status"] == "TARGET":
        print("✅ ALVO IDENTIFICADO!")
    else:
        print("⏳ Nenhum alvo encontrado")

if __name__ == "__main__":
    main()
