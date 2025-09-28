#!/usr/bin/env python3
"""
🎯 SNIPER STRATEGY NEØ - ESTRATÉGIA SNIPER
Estratégia de trading de alta precisão para identificação de oportunidades
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .base_strategy import BaseStrategy, StrategySignal, StrategyParameters

class SniperStrategy(BaseStrategy):
    """
    Estratégia Sniper - Foco em precisão e timing perfeito
    """
    
    def __init__(self, parameters: Optional[StrategyParameters] = None):
        # Parâmetros específicos do Sniper
        sniper_params = StrategyParameters(
            rsi_oversold=25,  # Mais restritivo
            rsi_overbought=75,  # Mais restritivo
            macd_threshold=0.0005,  # Mais sensível
            volume_threshold=2000000,  # Volume alto obrigatório
            funding_threshold=0.005,  # Funding mais restritivo
            min_score=8.0,  # Score mínimo alto
            max_leverage=5,  # Leverage conservador
            stop_loss_pct=1.5,  # Stop loss apertado
            take_profit_pct=3.0  # Take profit moderado
        )
        
        if parameters:
            # Mescla parâmetros customizados
            for key, value in parameters.__dict__.items():
                setattr(sniper_params, key, value)
        
        super().__init__(sniper_params)
    
    def get_name(self) -> str:
        return "Sniper Strategy"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    async def analyze(self, data: Dict[str, Any]) -> StrategySignal:
        """
        Análise específica da estratégia Sniper
        Foca em sinais de alta qualidade com múltiplas confirmações
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
        open_interest = data.get('open_interest', 0)
        
        signals = []
        
        # 1. Análise RSI (peso alto)
        rsi_signal = self.calculate_rsi_signal(rsi)
        rsi_signal['symbol'] = symbol
        signals.append(rsi_signal)
        
        # 2. Análise MACD (peso alto)
        macd_signal_data = self.calculate_macd_signal(macd_line, macd_signal)
        macd_signal_data['symbol'] = symbol
        signals.append(macd_signal_data)
        
        # 3. Análise de Volume (peso médio)
        volume_signal = self.calculate_volume_signal(volume)
        volume_signal['symbol'] = symbol
        signals.append(volume_signal)
        
        # 4. Análise de Funding (peso médio)
        funding_signal = self.calculate_funding_signal(funding_rate)
        funding_signal['symbol'] = symbol
        signals.append(funding_signal)
        
        # 5. Análise de Open Interest (peso baixo)
        oi_signal = self._calculate_oi_signal(open_interest)
        oi_signal['symbol'] = symbol
        signals.append(oi_signal)
        
        # 6. Análise de Momentum (peso médio)
        momentum_signal = self._calculate_momentum_signal(data)
        momentum_signal['symbol'] = symbol
        signals.append(momentum_signal)
        
        # Combina todos os sinais
        final_signal = self.combine_signals(signals)
        
        # Aplica filtros específicos do Sniper
        final_signal = self._apply_sniper_filters(final_signal, data)
        
        # Calcula níveis de entrada, stop loss e take profit
        if final_signal.direction != 'NEUTRAL' and final_signal.strength >= self.parameters.min_score:
            final_signal.entry_price = price
            final_signal.stop_loss = self.calculate_stop_loss(price, final_signal.direction)
            final_signal.take_profit = self.calculate_take_profit(price, final_signal.direction)
            final_signal.leverage = min(self.parameters.max_leverage, int(final_signal.strength))
        
        return final_signal
    
    def _calculate_oi_signal(self, open_interest: float) -> Dict[str, Any]:
        """Calcula sinal baseado no Open Interest"""
        if open_interest > 5000000:  # OI alto
            return {
                'direction': 'OI_HIGH',
                'strength': 1,
                'reasoning': f'High OI: {open_interest:,.0f}'
            }
        elif open_interest < 1000000:  # OI baixo
            return {
                'direction': 'OI_LOW',
                'strength': 0,
                'reasoning': f'Low OI: {open_interest:,.0f}'
            }
        else:
            return {
                'direction': 'OI_NORMAL',
                'strength': 0.5,
                'reasoning': f'Normal OI: {open_interest:,.0f}'
            }
    
    def _calculate_momentum_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula sinal de momentum"""
        # Simula cálculo de momentum baseado em dados históricos
        price_change = data.get('price_change_24h', 0)
        volume_change = data.get('volume_change_24h', 0)
        
        momentum_score = 0
        reasoning_parts = []
        
        # Análise de mudança de preço
        if abs(price_change) > 5:  # Mudança significativa
            if price_change > 0:
                momentum_score += 2
                reasoning_parts.append(f'Price up: {price_change:.1f}%')
            else:
                momentum_score += 2
                reasoning_parts.append(f'Price down: {price_change:.1f}%')
        
        # Análise de mudança de volume
        if abs(volume_change) > 50:  # Mudança significativa no volume
            momentum_score += 1
            reasoning_parts.append(f'Volume change: {volume_change:.1f}%')
        
        if momentum_score > 0:
            direction = 'MOMENTUM_HIGH' if momentum_score >= 2 else 'MOMENTUM_MEDIUM'
            return {
                'direction': direction,
                'strength': min(momentum_score, 3),
                'reasoning': '; '.join(reasoning_parts)
            }
        else:
            return {
                'direction': 'MOMENTUM_LOW',
                'strength': 0,
                'reasoning': 'Low momentum'
            }
    
    def _apply_sniper_filters(self, signal: StrategySignal, data: Dict[str, Any]) -> StrategySignal:
        """Aplica filtros específicos da estratégia Sniper"""
        
        # Filtro 1: Volume mínimo obrigatório
        volume = data.get('volume', 0)
        if volume < self.parameters.volume_threshold:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning='Volume insuficiente para Sniper'
            )
        
        # Filtro 2: Score mínimo obrigatório
        if signal.strength < self.parameters.min_score:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Score insuficiente: {signal.strength:.1f} < {self.parameters.min_score}'
            )
        
        # Filtro 3: Confiança mínima
        if signal.confidence < 0.7:
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Confiança insuficiente: {signal.confidence:.2f} < 0.7'
            )
        
        # Filtro 4: Verificação de volatilidade
        volatility = data.get('volatility_24h', 0)
        if volatility > 20:  # Volatilidade muito alta
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Volatilidade muito alta: {volatility:.1f}%'
            )
        
        # Filtro 5: Verificação de spread
        spread = data.get('spread', 0)
        if spread > 0.1:  # Spread muito alto
            return StrategySignal(
                symbol=signal.symbol,
                direction='NEUTRAL',
                strength=0,
                confidence=0,
                reasoning=f'Spread muito alto: {spread:.3f}'
            )
        
        # Se passou em todos os filtros, ajusta confiança
        signal.confidence = min(signal.confidence * 1.1, 1.0)  # Bonus de confiança
        signal.reasoning += " [SNIPER APPROVED]"
        
        return signal
    
    def get_strategy_description(self) -> str:
        """Retorna descrição da estratégia"""
        return """
        🎯 SNIPER STRATEGY - ESTRATÉGIA DE ALTA PRECISÃO
        
        Esta estratégia foca em identificar oportunidades de trading com máxima precisão,
        utilizando múltiplas confirmações técnicas e filtros rigorosos.
        
        CARACTERÍSTICAS:
        - RSI mais restritivo (25/75)
        - MACD mais sensível (0.0005)
        - Volume mínimo alto (2M+)
        - Score mínimo elevado (8.0+)
        - Leverage conservador (máx 5x)
        - Stop loss apertado (1.5%)
        - Take profit moderado (3.0%)
        
        FILTROS APLICADOS:
        ✅ Volume mínimo obrigatório
        ✅ Score mínimo elevado
        ✅ Confiança mínima (70%+)
        ✅ Volatilidade controlada
        ✅ Spread aceitável
        
        OBJETIVO: Identificar trades de alta qualidade com máxima precisão.
        """
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance da estratégia"""
        return {
            'strategy_name': self.get_name(),
            'version': self.get_version(),
            'total_runs': self.run_count,
            'successful_runs': self.success_count,
            'success_rate': self.get_success_rate(),
            'is_active': self.is_active,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'parameters': self.get_parameters(),
            'description': self.get_strategy_description()
        }
