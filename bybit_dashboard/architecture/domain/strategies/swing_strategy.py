#!/usr/bin/env python3
"""
🎯 SWING STRATEGY NEØ - ESTRATÉGIA DE SWING
Estratégia de trading de médio prazo para movimentos maiores
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_strategy import BaseStrategy, StrategySignal, StrategyParameters

class SwingStrategy(BaseStrategy):
    """
    Estratégia Swing - Foco em movimentos de médio prazo
    """
    
    def __init__(self, parameters: Optional[StrategyParameters] = None):
        # Parâmetros específicos do Swing
        swing_params = StrategyParameters(
            rsi_oversold=20,  # Muito restritivo
            rsi_overbought=80,  # Muito restritivo
            macd_threshold=0.002,  # Menos sensível
            volume_threshold=5000000,  # Volume muito alto
            funding_threshold=0.01,  # Funding muito restritivo
            min_score=9.0,  # Score mínimo muito alto
            max_leverage=3,  # Leverage muito conservador
            stop_loss_pct=5.0,  # Stop loss largo
            take_profit_pct=10.0  # Take profit grande
        )
        
        if parameters:
            # Mescla parâmetros customizados
            for key, value in parameters.__dict__.items():
                setattr(swing_params, key, value)
        
        super().__init__(swing_params)
    
    def get_name(self) -> str:
        return "Swing Strategy"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    async def analyze(self, data: Dict[str, Any]) -> StrategySignal:
        """
        Análise específica da estratégia Swing
        Foca em sinais de alta qualidade com movimentos maiores
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
        
        # 1. Análise RSI (peso muito alto)
        rsi_signal = self.calculate_rsi_signal(rsi)
        rsi_signal['symbol'] = symbol
        signals.append(rsi_signal)
        
        # 2. Análise MACD (peso alto)
        macd_signal_data = self.calculate_macd_signal(macd_line, macd_signal)
        macd_signal_data['symbol'] = symbol
        signals.append(macd_signal_data)
        
        # 3. Análise de Volume (peso muito alto)
        volume_signal = self.calculate_volume_signal(volume)
        volume_signal['symbol'] = symbol
        signals.append(volume_signal)
        
        # 4. Análise de Funding (peso alto)
        funding_signal = self.calculate_funding_signal(funding_rate)
        funding_signal['symbol'] = symbol
        signals.append(funding_signal)
        
        # Combina todos os sinais
        final_signal = self.combine_signals(signals)
        
        # Aplica filtros específicos do Swing
        final_signal = self._apply_swing_filters(final_signal, data)
        
        # Calcula níveis de entrada, stop loss e take profit
        if final_signal.direction != 'NEUTRAL' and final_signal.strength >= self.parameters.min_score:
            final_signal.entry_price = price
            final_signal.stop_loss = self.calculate_stop_loss(price, final_signal.direction)
            final_signal.take_profit = self.calculate_take_profit(price, final_signal.direction)
            final_signal.leverage = min(self.parameters.max_leverage, int(final_signal.strength / 3))
        
        return final_signal
    
    def _apply_swing_filters(self, signal: StrategySignal, data: Dict[str, Any]) -> StrategySignal:
        """Aplica filtros específicos da estratégia Swing"""
        
        # Filtro 1: Volume mínimo (muito restritivo)
        volume = data.get('volume', 0)
        if volume < self.parameters.volume_threshold:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning='Volume insuficiente para Swing'
            )
        
        # Filtro 2: Score mínimo (muito restritivo)
        if signal.strength < self.parameters.min_score:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Score insuficiente: {signal.strength:.1f} < {self.parameters.min_score}'
            )
        
        # Filtro 3: Confiança mínima (muito restritiva)
        if signal.confidence < 0.9:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Confiança insuficiente: {signal.confidence:.2f} < 0.9'
            )
        
        # Filtro 4: Verificação de tendência de longo prazo
        trend = data.get('trend_7d', 0)
        if abs(trend) < 10:  # Tendência fraca
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Tendência fraca: {trend:.1f}%'
            )
        
        # Se passou em todos os filtros, ajusta confiança
        signal.confidence = min(signal.confidence * 1.2, 1.0)  # Bonus maior
        signal.reasoning += " [SWING APPROVED]"
        
        return signal
    
    def get_strategy_description(self) -> str:
        """Retorna descrição da estratégia"""
        return """
        🎯 SWING STRATEGY - ESTRATÉGIA DE MÉDIO PRAZO
        
        Esta estratégia foca em identificar oportunidades de trading de médio prazo,
        com alta precisão e movimentos maiores.
        
        CARACTERÍSTICAS:
        - RSI muito restritivo (20/80)
        - MACD menos sensível (0.002)
        - Volume mínimo muito alto (5M+)
        - Score mínimo muito alto (9.0+)
        - Leverage muito conservador (máx 3x)
        - Stop loss largo (5.0%)
        - Take profit grande (10.0%)
        
        FILTROS APLICADOS:
        ✅ Volume mínimo muito alto
        ✅ Score mínimo muito alto
        ✅ Confiança mínima (90%+)
        ✅ Tendência de longo prazo
        
        OBJETIVO: Identificar trades de alta qualidade com movimentos maiores.
        """
