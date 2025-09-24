#!/usr/bin/env python3
"""
🎯 SCALPING STRATEGY NEØ - ESTRATÉGIA DE SCALPING
Estratégia de trading de alta frequência para lucros rápidos
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_strategy import BaseStrategy, StrategySignal, StrategyParameters

class ScalpingStrategy(BaseStrategy):
    """
    Estratégia Scalping - Foco em lucros rápidos e alta frequência
    """
    
    def __init__(self, parameters: Optional[StrategyParameters] = None):
        # Parâmetros específicos do Scalping
        scalping_params = StrategyParameters(
            rsi_oversold=40,  # Menos restritivo
            rsi_overbought=60,  # Menos restritivo
            macd_threshold=0.0001,  # Mais sensível
            volume_threshold=500000,  # Volume menor aceito
            funding_threshold=0.002,  # Funding menos restritivo
            min_score=5.0,  # Score mínimo menor
            max_leverage=20,  # Leverage maior
            stop_loss_pct=0.5,  # Stop loss muito apertado
            take_profit_pct=1.0  # Take profit pequeno
        )
        
        if parameters:
            # Mescla parâmetros customizados
            for key, value in parameters.__dict__.items():
                setattr(scalping_params, key, value)
        
        super().__init__(scalping_params)
    
    def get_name(self) -> str:
        return "Scalping Strategy"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    async def analyze(self, data: Dict[str, Any]) -> StrategySignal:
        """
        Análise específica da estratégia Scalping
        Foca em sinais rápidos com menor precisão mas maior frequência
        """
        if not self.validate_data(data):
            return StrategySignal(
                symbol=data.get('symbol', ''),
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning='Dados inválidos'
            )
        
        symbol = data['symbol']
        price = data['price']
        rsi = data['rsi']
        macd_line = data['macd_line']
        macd_signal = data['macd_signal']
        volume = data['volume']
        funding_rate = data.get('funding_rate', 0)
        
        signals = []
        
        # 1. Análise RSI (peso médio)
        rsi_signal = self.calculate_rsi_signal(rsi)
        rsi_signal['symbol'] = symbol
        signals.append(rsi_signal)
        
        # 2. Análise MACD (peso alto)
        macd_signal_data = self.calculate_macd_signal(macd_line, macd_signal)
        macd_signal_data['symbol'] = symbol
        signals.append(macd_signal_data)
        
        # 3. Análise de Volume (peso baixo)
        volume_signal = self.calculate_volume_signal(volume)
        volume_signal['symbol'] = symbol
        signals.append(volume_signal)
        
        # 4. Análise de Funding (peso baixo)
        funding_signal = self.calculate_funding_signal(funding_rate)
        funding_signal['symbol'] = symbol
        signals.append(funding_signal)
        
        # Combina todos os sinais
        final_signal = self.combine_signals(signals)
        
        # Aplica filtros específicos do Scalping
        final_signal = self._apply_scalping_filters(final_signal, data)
        
        # Calcula níveis de entrada, stop loss e take profit
        if final_signal.direction != 'NEUTRAL' and final_signal.strength >= self.parameters.min_score:
            final_signal.entry_price = price
            final_signal.stop_loss = self.calculate_stop_loss(price, final_signal.direction)
            final_signal.take_profit = self.calculate_take_profit(price, final_signal.direction)
            final_signal.leverage = min(self.parameters.max_leverage, int(final_signal.strength * 2))
        
        return final_signal
    
    def _apply_scalping_filters(self, signal: StrategySignal, data: Dict[str, Any]) -> StrategySignal:
        """Aplica filtros específicos da estratégia Scalping"""
        
        # Filtro 1: Volume mínimo (menos restritivo)
        volume = data.get('volume', 0)
        if volume < self.parameters.volume_threshold:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning='Volume insuficiente para Scalping'
            )
        
        # Filtro 2: Score mínimo (menos restritivo)
        if signal.strength < self.parameters.min_score:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Score insuficiente: {signal.strength:.1f} < {self.parameters.min_score}'
            )
        
        # Filtro 3: Confiança mínima (menos restritiva)
        if signal.confidence < 0.5:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Confiança insuficiente: {signal.confidence:.2f} < 0.5'
            )
        
        # Se passou em todos os filtros, ajusta confiança
        signal.confidence = min(signal.confidence * 1.05, 1.0)  # Bonus menor
        signal.reasoning += " [SCALPING APPROVED]"
        
        return signal
    
    def get_strategy_description(self) -> str:
        """Retorna descrição da estratégia"""
        return """
        🎯 SCALPING STRATEGY - ESTRATÉGIA DE ALTA FREQUÊNCIA
        
        Esta estratégia foca em identificar oportunidades de trading rápidas,
        com menor precisão mas maior frequência de sinais.
        
        CARACTERÍSTICAS:
        - RSI menos restritivo (40/60)
        - MACD mais sensível (0.0001)
        - Volume mínimo menor (500K+)
        - Score mínimo menor (5.0+)
        - Leverage maior (máx 20x)
        - Stop loss muito apertado (0.5%)
        - Take profit pequeno (1.0%)
        
        FILTROS APLICADOS:
        ✅ Volume mínimo (menos restritivo)
        ✅ Score mínimo menor
        ✅ Confiança mínima (50%+)
        
        OBJETIVO: Identificar trades rápidos com lucros pequenos mas frequentes.
        """
