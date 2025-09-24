"""
📡 EVENTS NEØ - SISTEMA DE EVENTOS E OBSERVADORES
Sistema de eventos com padrão Observer para comunicação desacoplada
"""

from .event_bus import EventBus, EventHandler
from .event_handler import (
    TradeEventHandler, 
    StrategyEventHandler, 
    ErrorEventHandler, 
    SystemEventHandler, 
    NotificationEventHandler, 
    AuditEventHandler
)
from .events import *
from .event_dispatcher import EventDispatcher, LoggingMiddleware, TimingMiddleware, ValidationMiddleware

__all__ = [
    "EventBus",
    "EventHandler",
    "TradeEventHandler",
    "StrategyEventHandler", 
    "ErrorEventHandler",
    "SystemEventHandler",
    "NotificationEventHandler",
    "AuditEventHandler",
    "EventDispatcher",
    "LoggingMiddleware",
    "TimingMiddleware", 
    "ValidationMiddleware",
    "TradeExecutedEvent",
    "OrderCreatedEvent",
    "OrderFilledEvent",
    "OrderCancelledEvent",
    "PositionOpenedEvent",
    "PositionClosedEvent",
    "StrategySignalEvent",
    "ErrorEvent",
    "SystemEvent"
]
