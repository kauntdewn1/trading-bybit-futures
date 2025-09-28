#!/usr/bin/env python3
"""
📡 EVENT DISPATCHER NEØ - DISPATCHER DE EVENTOS
Sistema de despacho de eventos com middleware e filtros
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from collections import defaultdict

from ...core.interfaces import IEvent, IEventHandler
from .event_bus import EventBus, get_event_bus

class EventDispatcher:
    """
    Dispatcher de eventos com middleware e filtros
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or get_event_bus()
        self.logger = logging.getLogger(__name__)
        self.middleware: List[Callable] = []
        self.filters: Dict[str, List[Callable]] = defaultdict(list)
        self.handlers: Dict[str, List[IEventHandler]] = defaultdict(list)
        self.stats = {
            'events_dispatched': 0,
            'events_filtered': 0,
            'events_processed': 0,
            'errors': 0
        }
    
    def add_middleware(self, middleware: Callable) -> None:
        """Adiciona middleware ao dispatcher"""
        self.middleware.append(middleware)
        self.logger.debug(f"Middleware adicionado: {middleware.__name__}")
    
    def remove_middleware(self, middleware: Callable) -> None:
        """Remove middleware do dispatcher"""
        if middleware in self.middleware:
            self.middleware.remove(middleware)
            self.logger.debug(f"Middleware removido: {middleware.__name__}")
    
    def add_filter(self, event_type: str, filter_func: Callable) -> None:
        """Adiciona filtro para tipo de evento"""
        self.filters[event_type].append(filter_func)
        self.logger.debug(f"Filtro adicionado para {event_type}: {filter_func.__name__}")
    
    def remove_filter(self, event_type: str, filter_func: Callable) -> None:
        """Remove filtro para tipo de evento"""
        if filter_func in self.filters[event_type]:
            self.filters[event_type].remove(filter_func)
            self.logger.debug(f"Filtro removido para {event_type}: {filter_func.__name__}")
    
    def add_handler(self, event_type: str, handler: IEventHandler) -> None:
        """Adiciona handler para tipo de evento"""
        self.handlers[event_type].append(handler)
        self.logger.debug(f"Handler adicionado para {event_type}: {handler.__class__.__name__}")
    
    def remove_handler(self, event_type: str, handler: IEventHandler) -> None:
        """Remove handler para tipo de evento"""
        if handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            self.logger.debug(f"Handler removido para {event_type}: {handler.__class__.__name__}")
    
    async def dispatch(self, event: IEvent) -> None:
        """
        Despacha evento através do sistema
        
        Args:
            event: Evento a ser despachado
        """
        event_type = event.get_event_type()
        
        try:
            # Aplica middleware
            for middleware in self.middleware:
                event = await middleware(event)
                if event is None:
                    self.logger.debug(f"Evento cancelado por middleware: {middleware.__name__}")
                    return
            
            # Aplica filtros
            if event_type in self.filters:
                for filter_func in self.filters[event_type]:
                    if not await filter_func(event):
                        self.stats['events_filtered'] += 1
                        self.logger.debug(f"Evento filtrado: {event_type}")
                        return
            
            # Despacha para event bus
            await self.event_bus.publish(event)
            
            # Despacha para handlers locais
            if event_type in self.handlers:
                for handler in self.handlers[event_type]:
                    try:
                        await handler.handle(event)
                    except Exception as e:
                        self.logger.error(f"Erro no handler {handler.__class__.__name__}: {e}")
                        self.stats['errors'] += 1
            
            self.stats['events_dispatched'] += 1
            self.stats['events_processed'] += 1
            
        except Exception as e:
            self.logger.error(f"Erro ao despachar evento {event_type}: {e}")
            self.stats['errors'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do dispatcher"""
        return {
            'events_dispatched': self.stats['events_dispatched'],
            'events_filtered': self.stats['events_filtered'],
            'events_processed': self.stats['events_processed'],
            'errors': self.stats['errors'],
            'middleware_count': len(self.middleware),
            'filters_count': sum(len(filters) for filters in self.filters.values()),
            'handlers_count': sum(len(handlers) for handlers in self.handlers.values()),
            'success_rate': (
                self.stats['events_processed'] / self.stats['events_dispatched']
                if self.stats['events_dispatched'] > 0 else 0
            )
        }
    
    def clear_stats(self) -> None:
        """Limpa estatísticas"""
        self.stats = {
            'events_dispatched': 0,
            'events_filtered': 0,
            'events_processed': 0,
            'errors': 0
        }

# Middleware de exemplo
class LoggingMiddleware:
    """Middleware para logging de eventos"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
    
    async def __call__(self, event: IEvent) -> IEvent:
        """Aplica logging ao evento"""
        self.logger.debug(f"Evento recebido: {event.get_event_type()}")
        return event

class TimingMiddleware:
    """Middleware para medição de tempo"""
    
    def __init__(self):
        self.times = {}
    
    async def __call__(self, event: IEvent) -> IEvent:
        """Aplica timing ao evento"""
        event_type = event.get_event_type()
        self.times[event_type] = datetime.now()
        return event
    
    def get_timing(self, event_type: str) -> Optional[datetime]:
        """Obtém tempo de processamento"""
        return self.times.get(event_type)

class ValidationMiddleware:
    """Middleware para validação de eventos"""
    
    def __init__(self):
        self.required_fields = {
            'TradeExecutedEvent': ['symbol', 'side', 'quantity', 'price'],
            'OrderCreatedEvent': ['order_id', 'symbol', 'side', 'quantity'],
            'ErrorEvent': ['error_type', 'error_message']
        }
    
    async def __call__(self, event: IEvent) -> Optional[IEvent]:
        """Valida evento"""
        event_type = event.get_event_type()
        
        if event_type in self.required_fields:
            data = event.get_data()
            required_fields = self.required_fields[event_type]
            
            for field in required_fields:
                if field not in data:
                    logging.error(f"Campo obrigatório ausente: {field} em {event_type}")
                    return None
        
        return event

# Filtros de exemplo
class RateLimitFilter:
    """Filtro para rate limiting"""
    
    def __init__(self, max_events_per_minute: int = 100):
        self.max_events = max_events_per_minute
        self.events = []
    
    async def __call__(self, event: IEvent) -> bool:
        """Aplica rate limiting"""
        now = datetime.now()
        
        # Remove eventos antigos
        self.events = [e for e in self.events if (now - e).total_seconds() < 60]
        
        # Verifica limite
        if len(self.events) >= self.max_events:
            logging.warning(f"Rate limit excedido: {len(self.events)} eventos no último minuto")
            return False
        
        self.events.append(now)
        return True

class PriorityFilter:
    """Filtro por prioridade"""
    
    def __init__(self, min_priority: str = 'normal'):
        self.priority_order = {'low': 1, 'normal': 2, 'high': 3, 'urgent': 4}
        self.min_priority = min_priority
    
    async def __call__(self, event: IEvent) -> bool:
        """Filtra por prioridade"""
        data = event.get_data()
        priority = data.get('priority', 'normal')
        
        return self.priority_order.get(priority, 2) >= self.priority_order.get(self.min_priority, 2)

# Instância global do dispatcher
_dispatcher: Optional[EventDispatcher] = None

def get_dispatcher() -> EventDispatcher:
    """Obtém instância global do dispatcher"""
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = EventDispatcher()
    return _dispatcher

def set_dispatcher(dispatcher: EventDispatcher) -> None:
    """Define instância global do dispatcher"""
    global _dispatcher
    _dispatcher = dispatcher

def clear_dispatcher() -> None:
    """Limpa instância global do dispatcher"""
    global _dispatcher
    _dispatcher = None
