#!/usr/bin/env python3
"""
📡 EVENTS NEØ - DEFINIÇÕES DE EVENTOS (CORRIGIDO)
Eventos do sistema de trading
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import uuid

from ...core.interfaces import IEvent

# =============================================================================
# EVENTOS BASE
# =============================================================================

@dataclass
class BaseEvent(IEvent):
    """Evento base do sistema"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_event_type(self) -> str:
        return self.__class__.__name__
    
    def get_timestamp(self) -> datetime:
        return self.timestamp
    
    def get_data(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'metadata': self.metadata
        }

# =============================================================================
# EVENTOS DE TRADING
# =============================================================================

@dataclass
class TradeExecutedEvent(BaseEvent):
    """Evento de trade executado"""
    symbol: str
    side: str  # "BUY" ou "SELL"
    quantity: float
    price: float
    position_side: str  # "LONG" ou "SHORT"
    leverage: int
    strategy_id: Optional[str] = field(default=None)
    order_id: Optional[str] = field(default=None)
    pnl: Optional[float] = field(default=None)
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'price': self.price,
            'position_side': self.position_side,
            'leverage': self.leverage,
            'strategy_id': self.strategy_id,
            'order_id': self.order_id,
            'pnl': self.pnl
        })
        return base_data

@dataclass
class OrderCreatedEvent(BaseEvent):
    """Evento de ordem criada"""
    order_id: str
    symbol: str
    side: str
    order_type: str
    quantity: float
    price: Optional[float] = field(default=None)
    position_side: str = field(default="LONG")
    leverage: int = field(default=1)
    strategy_id: Optional[str] = field(default=None)
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side,
            'order_type': self.order_type,
            'quantity': self.quantity,
            'price': self.price,
            'position_side': self.position_side,
            'leverage': self.leverage,
            'strategy_id': self.strategy_id
        })
        return base_data

@dataclass
class OrderFilledEvent(BaseEvent):
    """Evento de ordem executada"""
    order_id: str
    symbol: str
    filled_quantity: float
    filled_price: float
    remaining_quantity: float = field(default=0)
    commission: Optional[float] = field(default=None)
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'order_id': self.order_id,
            'symbol': self.symbol,
            'filled_quantity': self.filled_quantity,
            'filled_price': self.filled_price,
            'remaining_quantity': self.remaining_quantity,
            'commission': self.commission
        })
        return base_data

@dataclass
class OrderCancelledEvent(BaseEvent):
    """Evento de ordem cancelada"""
    order_id: str
    symbol: str
    reason: str
    cancelled_quantity: float
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'order_id': self.order_id,
            'symbol': self.symbol,
            'reason': self.reason,
            'cancelled_quantity': self.cancelled_quantity
        })
        return base_data

# =============================================================================
# EVENTOS DE POSIÇÃO
# =============================================================================

@dataclass
class PositionOpenedEvent(BaseEvent):
    """Evento de posição aberta"""
    position_id: str
    symbol: str
    side: str  # "LONG" ou "SHORT"
    size: float
    entry_price: float
    leverage: int
    margin: float
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'position_id': self.position_id,
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'entry_price': self.entry_price,
            'leverage': self.leverage,
            'margin': self.margin
        })
        return base_data

@dataclass
class PositionClosedEvent(BaseEvent):
    """Evento de posição fechada"""
    position_id: str
    symbol: str
    side: str
    size: float
    entry_price: float
    exit_price: float
    pnl: float
    pnl_percentage: float
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'position_id': self.position_id,
            'symbol': self.symbol,
            'side': self.side,
            'size': self.size,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'pnl': self.pnl,
            'pnl_percentage': self.pnl_percentage
        })
        return base_data

# =============================================================================
# EVENTOS DE ESTRATÉGIA
# =============================================================================

@dataclass
class StrategySignalEvent(BaseEvent):
    """Evento de sinal de estratégia"""
    strategy_id: str
    strategy_name: str
    symbol: str
    signal_type: str  # "LONG", "SHORT", "NEUTRAL"
    strength: float
    confidence: float
    reasoning: str
    entry_price: Optional[float] = field(default=None)
    stop_loss: Optional[float] = field(default=None)
    take_profit: Optional[float] = field(default=None)
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'strategy_id': self.strategy_id,
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'strength': self.strength,
            'confidence': self.confidence,
            'reasoning': self.reasoning,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit
        })
        return base_data

# =============================================================================
# EVENTOS DE SISTEMA
# =============================================================================

@dataclass
class ErrorEvent(BaseEvent):
    """Evento de erro"""
    error_type: str
    error_message: str
    error_code: Optional[str] = field(default=None)
    stack_trace: Optional[str] = field(default=None)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'error_type': self.error_type,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'stack_trace': self.stack_trace,
            'context': self.context
        })
        return base_data

@dataclass
class SystemEvent(BaseEvent):
    """Evento de sistema"""
    event_category: str  # "startup", "shutdown", "maintenance", "alert"
    message: str
    severity: str = field(default="info")  # "info", "warning", "error", "critical"
    details: Dict[str, Any] = field(default_factory=dict)
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'event_category': self.event_category,
            'message': self.message,
            'severity': self.severity,
            'details': self.details
        })
        return base_data

@dataclass
class PerformanceEvent(BaseEvent):
    """Evento de performance"""
    metric_name: str
    metric_value: float
    metric_unit: str
    threshold: Optional[float] = field(default=None)
    is_alert: bool = field(default=False)
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'threshold': self.threshold,
            'is_alert': self.is_alert
        })
        return base_data

@dataclass
class NotificationEvent(BaseEvent):
    """Evento de notificação"""
    notification_type: str  # "trade", "alert", "info", "warning", "error"
    title: str
    message: str
    channel: str = field(default="default")  # "telegram", "email", "webhook", "console"
    priority: str = field(default="normal")  # "low", "normal", "high", "urgent"
    data: Dict[str, Any] = field(default_factory=dict)
    
    def get_data(self) -> Dict[str, Any]:
        base_data = super().get_data()
        base_data.update({
            'notification_type': self.notification_type,
            'title': self.title,
            'message': self.message,
            'channel': self.channel,
            'priority': self.priority,
            'data': self.data
        })
        return base_data
