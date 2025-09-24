#!/usr/bin/env python3
"""
SNIPER NEØ + OpenAI Assistant Integration
Sistema híbrido com validação de IA para análise de gráficos
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from sniper_system import SniperSystem
from openai_assistant_integration import OpenAIAssistantNode

class SniperAIEnhanced(SniperSystem):
    """
    SNIPER NEØ com integração OpenAI Assistant
    Adiciona validação de IA para análise de gráficos
    """
    
    def __init__(self, openai_api_key: str, openai_assistant_id: str):
        """
        Inicializa SNIPER com validação de IA
        
        Args:
            openai_api_key: Chave da API OpenAI
            openai_assistant_id: ID do assistant criado no playground
        """
        super().__init__()
        
        # Inicializa node de IA
        self.ai_node = OpenAIAssistantNode(openai_api_key, openai_assistant_id)
        
        # Configurações de IA
        self.ai_enabled = True
        self.ai_confidence_threshold = 7.0  # Mínimo para confiar na IA
        self.ai_analysis_cache = {}  # Cache para evitar análises repetidas
        
    def find_best_trade_with_ai(self, threshold: float = 7.0) -> Dict:
        """
        Encontra melhor trade com validação de IA
        
        Args:
            threshold: Score mínimo para análise
            
        Returns:
            Dict com trade + validação de IA
        """
        # Busca melhor trade normalmente
        best_trade = self.find_best_trade()
        
        if not best_trade or best_trade.get('symbol') is None:
            return {
                "status": "no_target",
                "message": "Nenhum alvo encontrado",
                "ai_analysis": None
            }
        
        # Se encontrou alvo, valida com IA
        if self.ai_enabled:
            ai_analysis = self._validate_with_ai(best_trade)
            
            # Adiciona análise de IA ao resultado
            best_trade['ai_analysis'] = ai_analysis
            best_trade['ai_enhanced'] = True
            
            # Ajusta confiança baseado na IA
            if ai_analysis.get('confidence_level', 0) >= self.ai_confidence_threshold:
                best_trade['ai_confirmed'] = True
                best_trade['final_confidence'] = ai_analysis.get('confidence_level', 0)
            else:
                best_trade['ai_confirmed'] = False
                best_trade['final_confidence'] = ai_analysis.get('confidence_level', 0)
        
        return best_trade
    
    def _validate_with_ai(self, trade_data: Dict) -> Dict:
        """
        Valida trade com OpenAI Assistant
        
        Args:
            trade_data: Dados do trade encontrado
            
        Returns:
            Dict com análise da IA
        """
        symbol = trade_data['symbol']
        
        # Verifica cache
        cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d%H%M')}"
        if cache_key in self.ai_analysis_cache:
            return self.ai_analysis_cache[cache_key]
        
        try:
            # Busca dados históricos para análise
            df = self.get_klines(symbol, "15", 50)
            if df is None or len(df) < 20:
                return {"error": "Dados insuficientes para análise"}
            
            # Prepara indicadores
            indicators = {
                'rsi': trade_data.get('rsi', 0),
                'macd_signal': trade_data.get('macd', 'neutral'),
                'volume_ratio': trade_data.get('volume_ratio', 1.0),
                'funding_rate': trade_data.get('funding_rate', 0),
                'oi_trend': trade_data.get('oi_trend', 'neutral')
            }
            
            # Analisa com IA
            ai_analysis = self.ai_node.analyze_chart_data(
                symbol=symbol,
                df=df,
                indicators=indicators,
                score=trade_data.get('score', 0)
            )
            
            # Cacheia resultado
            self.ai_analysis_cache[cache_key] = ai_analysis
            
            return ai_analysis
            
        except Exception as e:
            return {"error": f"Erro na análise de IA: {str(e)}"}
    
    def generate_ai_enhanced_alert(self, trade_data: Dict) -> str:
        """
        Gera alerta aprimorado com validação de IA
        
        Args:
            trade_data: Dados do trade com análise de IA
            
        Returns:
            String com alerta formatado
        """
        if not trade_data.get('ai_analysis'):
            return self.generate_sniper_alert(trade_data)
        
        ai_analysis = trade_data['ai_analysis']
        
        # Gera alerta aprimorado
        enhanced_alert = self.ai_node.generate_enhanced_alert(
            symbol=trade_data['symbol'],
            original_alert=trade_data,
            ai_analysis=ai_analysis
        )
        
        return enhanced_alert
    
    def get_ai_performance_stats(self) -> Dict:
        """
        Retorna estatísticas de performance da IA
        
        Returns:
            Dict com métricas de IA
        """
        if not hasattr(self, 'ai_analysis_cache'):
            return {"error": "IA não habilitada"}
        
        total_analyses = len(self.ai_analysis_cache)
        confirmed_signals = sum(1 for analysis in self.ai_analysis_cache.values() 
                               if analysis.get('signal_confirmation', False))
        
        avg_confidence = sum(analysis.get('confidence_level', 0) 
                           for analysis in self.ai_analysis_cache.values()) / total_analyses if total_analyses > 0 else 0
        
        return {
            "total_analyses": total_analyses,
            "confirmed_signals": confirmed_signals,
            "confirmation_rate": (confirmed_signals / total_analyses * 100) if total_analyses > 0 else 0,
            "avg_confidence": avg_confidence,
            "ai_enabled": self.ai_enabled
        }
    
    def toggle_ai(self, enabled: bool = None) -> bool:
        """
        Liga/desliga validação de IA
        
        Args:
            enabled: True para ligar, False para desligar, None para alternar
            
        Returns:
            Status atual da IA
        """
        if enabled is None:
            self.ai_enabled = not self.ai_enabled
        else:
            self.ai_enabled = enabled
        
        return self.ai_enabled
    
    def set_ai_confidence_threshold(self, threshold: float) -> None:
        """
        Define threshold de confiança da IA
        
        Args:
            threshold: Valor entre 1-10
        """
        self.ai_confidence_threshold = max(1, min(10, threshold))

# Exemplo de uso
def test_sniper_ai():
    """Testa SNIPER com IA"""
    
    # Configuração
    OPENAI_API_KEY = "sua_api_key_openai"
    OPENAI_ASSISTANT_ID = "seu_assistant_id"
    
    # Cria instância
    sniper_ai = SniperAIEnhanced(OPENAI_API_KEY, OPENAI_ASSISTANT_ID)
    
    # Testa busca com IA
    print("🔍 Buscando melhor trade com validação de IA...")
    result = sniper_ai.find_best_trade_with_ai(threshold=7.0)
    
    if result.get('status') == 'no_target':
        print("❌ Nenhum alvo encontrado")
    else:
        print("✅ Alvo encontrado!")
        print(f"Ativo: {result['symbol']}")
        print(f"Score: {result['score']}/10")
        print(f"IA Confirmado: {result.get('ai_confirmed', False)}")
        print(f"Confiança IA: {result.get('final_confidence', 0)}/10")
        
        # Gera alerta aprimorado
        alert = sniper_ai.generate_ai_enhanced_alert(result)
        print("\n" + "="*50)
        print("ALERTA APRIMORADO COM IA:")
        print("="*50)
        print(alert)
    
    # Mostra estatísticas
    stats = sniper_ai.get_ai_performance_stats()
    print(f"\n📊 Estatísticas IA: {stats}")

if __name__ == "__main__":
    test_sniper_ai()
