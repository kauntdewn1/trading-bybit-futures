#!/usr/bin/env python3
"""
🎯 BASE STRATEGY NEØ - ESTRATÉGIA BASE
Classe base para todas as estratégias de trading
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from ...core.interfaces import IStrategy
from ...core.entities import AnalysisResult, TechnicalIndicators, MarketData

@dataclass
class StrategySignal:
    """Sinal gerado pela estratégia"""
    symbol: str
    direction: str  # "LONG" ou "SHORT"
    strength: float  # 0-10
    confidence: float  # 0-1
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    leverage: int = 1
    reasoning: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class StrategyParameters:
    """Parâmetros da estratégia"""
    rsi_oversold: float = 30
    rsi_overbought: float = 70
    macd_threshold: float = 0.001
    volume_threshold: float = 1000000
    funding_threshold: float = 0.01
    min_score: float = 7.0
    max_leverage: int = 10
    stop_loss_pct: float = 2.0
    take_profit_pct: float = 4.0

class BaseStrategy(IStrategy, ABC):
    """
    Classe base para todas as estratégias de trading
    """
    
    def __init__(self, parameters: Optional[StrategyParameters] = None):
        self.parameters = parameters or StrategyParameters()
        self.name = self.get_name()
        self.version = self.get_version()
        self.is_active = True
        self.created_at = datetime.now()
        self.last_run = None
        self.run_count = 0
        self.success_count = 0
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> StrategySignal:
        """
        Analisa dados e retorna sinal de trading
        
        Args:
            data: Dados de mercado e indicadores técnicos
            
        Returns:
            StrategySignal: Sinal gerado pela estratégia
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna nome da estratégia"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Retorna versão da estratégia"""
        pass
    
    def get_parameters(self) -> Dict[str, Any]:
        """Retorna parâmetros da estratégia"""
        return self.parameters.__dict__
    
    def update_parameters(self, new_parameters: Dict[str, Any]) -> None:
        """Atualiza parâmetros da estratégia"""
        for key, value in new_parameters.items():
            if hasattr(self.parameters, key):
                setattr(self.parameters, key, value)
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Obtém parâmetro específico"""
        return getattr(self.parameters, key, default)
    
    def activate(self) -> None:
        """Ativa estratégia"""
        self.is_active = True
    
    def deactivate(self) -> None:
        """Desativa estratégia"""
        self.is_active = False
    
    def get_success_rate(self) -> float:
        """Calcula taxa de sucesso"""
        if self.run_count == 0:
            return 0.0
        return self.success_count / self.run_count
    
    def record_run(self, success: bool = True) -> None:
        """Registra execução da estratégia"""
        self.run_count += 1
        if success:
            self.success_count += 1
        self.last_run = datetime.now()
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida dados de entrada"""
        required_fields = ['symbol', 'price', 'rsi', 'macd_line', 'macd_signal', 'volume']
        
        for field in required_fields:
            if field not in data:
                return False
        
        # Validações específicas
        if not 0 <= data.get('rsi', 0) <= 100:
            return False
        
        if data.get('price', 0) <= 0:
            return False
        
        if data.get('volume', 0) < 0:
            return False
        
        return True
    
    def calculate_rsi_signal(self, rsi: float) -> Dict[str, Any]:
        """Calcula sinal baseado no RSI"""
        if rsi < self.parameters.rsi_oversold:
            return {
                'direction': 'LONG',
                'strength': (self.parameters.rsi_oversold - rsi) / self.parameters.rsi_oversold * 5,
                'reasoning': f'RSI oversold: {rsi:.1f}'
            }
        elif rsi > self.parameters.rsi_overbought:
            return {
                'direction': 'SHORT',
                'strength': (rsi - self.parameters.rsi_overbought) / (100 - self.parameters.rsi_overbought) * 5,
                'reasoning': f'RSI overbought: {rsi:.1f}'
            }
        else:
            return {
                'direction': 'NEUTRAL',
                'strength': 0,
                'reasoning': f'RSI neutral: {rsi:.1f}'
            }
    
    def calculate_macd_signal(self, macd_line: float, macd_signal: float) -> Dict[str, Any]:
        """Calcula sinal baseado no MACD"""
        macd_diff = macd_line - macd_signal
        
        if abs(macd_diff) < self.parameters.macd_threshold:
            return {
                'direction': 'NEUTRAL',
                'strength': 0,
                'reasoning': f'MACD neutral: {macd_diff:.6f}'
            }
        
        if macd_diff > 0:
            return {
                'direction': 'LONG',
                'strength': min(abs(macd_diff) / self.parameters.macd_threshold * 3, 5),
                'reasoning': f'MACD bullish: {macd_diff:.6f}'
            }
        else:
            return {
                'direction': 'SHORT',
                'strength': min(abs(macd_diff) / self.parameters.macd_threshold * 3, 5),
                'reasoning': f'MACD bearish: {macd_diff:.6f}'
            }
    
    def calculate_volume_signal(self, volume: float, avg_volume: float = None) -> Dict[str, Any]:
        """Calcula sinal baseado no volume"""
        if avg_volume is None:
            avg_volume = self.parameters.volume_threshold
        
        volume_ratio = volume / avg_volume if avg_volume > 0 else 1
        
        if volume_ratio > 1.5:
            return {
                'direction': 'VOLUME_HIGH',
                'strength': min((volume_ratio - 1) * 2, 3),
                'reasoning': f'High volume: {volume_ratio:.2f}x'
            }
        elif volume_ratio < 0.5:
            return {
                'direction': 'VOLUME_LOW',
                'strength': 0,
                'reasoning': f'Low volume: {volume_ratio:.2f}x'
            }
        else:
            return {
                'direction': 'VOLUME_NORMAL',
                'strength': 0,
                'reasoning': f'Normal volume: {volume_ratio:.2f}x'
            }
    
    def calculate_funding_signal(self, funding_rate: float) -> Dict[str, Any]:
        """Calcula sinal baseado na taxa de funding"""
        if abs(funding_rate) > self.parameters.funding_threshold:
            if funding_rate < 0:
                return {
                    'direction': 'LONG',
                    'strength': min(abs(funding_rate) / self.parameters.funding_threshold * 2, 3),
                    'reasoning': f'Negative funding: {funding_rate:.4f}'
                }
            else:
                return {
                    'direction': 'SHORT',
                    'strength': min(abs(funding_rate) / self.parameters.funding_threshold * 2, 3),
                    'reasoning': f'Positive funding: {funding_rate:.4f}'
                }
        else:
            return {
                'direction': 'NEUTRAL',
                'strength': 0,
                'reasoning': f'Neutral funding: {funding_rate:.4f}'
            }
    
    def combine_signals(self, signals: List[Dict[str, Any]]) -> StrategySignal:
        """Combina múltiplos sinais em um sinal final"""
        long_strength = 0
        short_strength = 0
        reasoning_parts = []
        
        for signal in signals:
            direction = signal.get('direction', 'NEUTRAL')
            strength = signal.get('strength', 0)
            reasoning = signal.get('reasoning', '')
            
            if direction == 'LONG':
                long_strength += strength
            elif direction == 'SHORT':
                short_strength += strength
            
            if reasoning:
                reasoning_parts.append(reasoning)
        
        # Determina direção final
        if long_strength > short_strength:
            final_direction = 'LONG'
            final_strength = long_strength
        elif short_strength > long_strength:
            final_direction = 'SHORT'
            final_strength = short_strength
        else:
            final_direction = 'NEUTRAL'
            final_strength = 0
        
        # Calcula confiança baseada na força e número de sinais
        confidence = min(final_strength / 10, 1.0) if final_strength > 0 else 0
        
        return StrategySignal(
            symbol=signals[0].get('symbol', '') if signals else '',
            direction=final_direction,
            strength=min(final_strength, 10),
            confidence=confidence,
            reasoning='; '.join(reasoning_parts)
        )
    
    def calculate_stop_loss(self, entry_price: float, direction: str) -> float:
        """Calcula stop loss"""
        if direction == 'LONG':
            return entry_price * (1 - self.parameters.stop_loss_pct / 100)
        else:
            return entry_price * (1 + self.parameters.stop_loss_pct / 100)
    
    def calculate_take_profit(self, entry_price: float, direction: str) -> float:
        """Calcula take profit"""
        if direction == 'LONG':
            return entry_price * (1 + self.parameters.take_profit_pct / 100)
        else:
            return entry_price * (1 - self.parameters.take_profit_pct / 100)
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Retorna informações da estratégia"""
        return {
            'name': self.name,
            'version': self.version,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'success_rate': self.get_success_rate(),
            'parameters': self.get_parameters()
        }
