#!/usr/bin/env python3
"""
📡 EVENT BUS NEØ - BARRAMENTO DE EVENTOS
Sistema de barramento de eventos com padrão Observer
"""

import asyncio
import threading
from typing import Dict, List, Set, Optional, Any, Callable
from collections import defaultdict
from datetime import datetime
import logging

from ...core.interfaces import IEventBus, IEvent, IEventHandler

class EventBus(IEventBus):
    """
    Barramento de eventos com suporte a handlers assíncronos
    """
    
    def __init__(self):
        self._handlers: Dict[str, Set[IEventHandler]] = defaultdict(set)
        self._middleware: List[Callable] = []
        self._lock = threading.RLock()
        self._logger = logging.getLogger(__name__)
        self._stats = {
            'events_published': 0,
            'events_handled': 0,
            'handlers_registered': 0,
            'errors': 0
        }
    
    async def publish(self, event: IEvent) -> None:
        """
        Publica evento no barramento
        
        Args:
            event: Evento a ser publicado
        """
        event_type = event.get_event_type()
        
        with self._lock:
            self._stats['events_published'] += 1
        
        # Aplica middleware
        for middleware in self._middleware:
            try:
                event = await middleware(event)
                if event is None:
                    return  # Middleware cancelou o evento
            except Exception as e:
                self._logger.error(f"Error in middleware: {e}")
                self._stats['errors'] += 1
        
        # Obtém handlers para o tipo de evento
        with self._lock:
            handlers = self._handlers[event_type].copy()
        
        if not handlers:
            self._logger.debug(f"No handlers for event type: {event_type}")
            return
        
        # Executa handlers em paralelo
        tasks = []
        for handler in handlers:
            task = self._execute_handler(handler, event)
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_handler(self, handler: IEventHandler, event: IEvent) -> None:
        """
        Executa handler de evento
        
        Args:
            handler: Handler a ser executado
            event: Evento a ser processado
        """
        try:
            await handler.handle(event)
            with self._lock:
                self._stats['events_handled'] += 1
        except Exception as e:
            self._logger.error(f"Error in handler {handler.__class__.__name__}: {e}")
            with self._lock:
                self._stats['errors'] += 1
    
    def subscribe(self, event_type: str, handler: IEventHandler) -> None:
        """
        Inscreve handler para tipo de evento
        
        Args:
            event_type: Tipo do evento
            handler: Handler a ser inscrito
        """
        with self._lock:
            self._handlers[event_type].add(handler)
            self._stats['handlers_registered'] += 1
        
        self._logger.debug(f"Handler {handler.__class__.__name__} subscribed to {event_type}")
    
    def unsubscribe(self, event_type: str, handler: IEventHandler) -> None:
        """
        Remove inscrição de handler
        
        Args:
            event_type: Tipo do evento
            handler: Handler a ser removido
        """
        with self._lock:
            if handler in self._handlers[event_type]:
                self._handlers[event_type].remove(handler)
                self._stats['handlers_registered'] -= 1
        
        self._logger.debug(f"Handler {handler.__class__.__name__} unsubscribed from {event_type}")
    
    def add_middleware(self, middleware: Callable) -> None:
        """
        Adiciona middleware ao barramento
        
        Args:
            middleware: Função middleware
        """
        self._middleware.append(middleware)
        self._logger.debug(f"Middleware {middleware.__name__} added")
    
    def remove_middleware(self, middleware: Callable) -> None:
        """
        Remove middleware do barramento
        
        Args:
            middleware: Função middleware a ser removida
        """
        if middleware in self._middleware:
            self._middleware.remove(middleware)
            self._logger.debug(f"Middleware {middleware.__name__} removed")
    
    def get_subscribers(self, event_type: str) -> List[IEventHandler]:
        """
        Obtém lista de subscribers para tipo de evento
        
        Args:
            event_type: Tipo do evento
            
        Returns:
            List[IEventHandler]: Lista de handlers
        """
        with self._lock:
            return list(self._handlers[event_type])
    
    def get_all_event_types(self) -> List[str]:
        """
        Obtém todos os tipos de eventos registrados
        
        Returns:
            List[str]: Lista de tipos de eventos
        """
        with self._lock:
            return list(self._handlers.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do barramento
        
        Returns:
            Dict[str, Any]: Estatísticas
        """
        with self._lock:
            return {
                'events_published': self._stats['events_published'],
                'events_handled': self._stats['events_handled'],
                'handlers_registered': self._stats['handlers_registered'],
                'errors': self._stats['errors'],
                'event_types': len(self._handlers),
                'middleware_count': len(self._middleware),
                'success_rate': (
                    self._stats['events_handled'] / self._stats['events_published']
                    if self._stats['events_published'] > 0 else 0
                )
            }
    
    def clear_stats(self) -> None:
        """Limpa estatísticas"""
        with self._lock:
            self._stats = {
                'events_published': 0,
                'events_handled': 0,
                'handlers_registered': 0,
                'errors': 0
            }
    
    def clear_handlers(self) -> None:
        """Limpa todos os handlers"""
        with self._lock:
            self._handlers.clear()
            self._stats['handlers_registered'] = 0
    
    def clear_middleware(self) -> None:
        """Limpa todos os middleware"""
        self._middleware.clear()

class EventHandler(IEventHandler):
    """
    Handler base para eventos
    """
    
    def __init__(self, event_types: List[str]):
        self.event_types = event_types
        self.handled_events = []
        self.error_count = 0
    
    async def handle(self, event: IEvent) -> None:
        """
        Processa evento
        
        Args:
            event: Evento a ser processado
        """
        try:
            await self._process_event(event)
            self.handled_events.append(event)
        except Exception as e:
            self.error_count += 1
            raise e
    
    async def _process_event(self, event: IEvent) -> None:
        """
        Processa evento específico (implementar nas subclasses)
        
        Args:
            event: Evento a ser processado
        """
        pass
    
    def can_handle(self, event_type: str) -> bool:
        """
        Verifica se pode processar o evento
        
        Args:
            event_type: Tipo do evento
            
        Returns:
            bool: True se pode processar
        """
        return event_type in self.event_types
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do handler
        
        Returns:
            Dict[str, Any]: Estatísticas
        """
        return {
            'event_types': self.event_types,
            'handled_events': len(self.handled_events),
            'error_count': self.error_count,
            'success_rate': (
                len(self.handled_events) / (len(self.handled_events) + self.error_count)
                if (len(self.handled_events) + self.error_count) > 0 else 0
            )
        }

# Instância global do event bus
_event_bus: Optional[EventBus] = None
_event_bus_lock = threading.RLock()

def get_event_bus() -> EventBus:
    """Obtém instância global do event bus"""
    global _event_bus
    with _event_bus_lock:
        if _event_bus is None:
            _event_bus = EventBus()
        return _event_bus

def set_event_bus(event_bus: EventBus) -> None:
    """Define instância global do event bus"""
    global _event_bus
    with _event_bus_lock:
        _event_bus = event_bus

def clear_event_bus() -> None:
    """Limpa instância global do event bus"""
    global _event_bus
    with _event_bus_lock:
        _event_bus = None
