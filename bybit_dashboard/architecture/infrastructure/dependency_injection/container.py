#!/usr/bin/env python3
"""
💉 DEPENDENCY CONTAINER NEØ - CONTAINER DE DEPENDÊNCIAS
Sistema de injeção de dependência com suporte a singleton e transient
"""

import inspect
import threading
from typing import Dict, Type, Any, Optional, Callable, Union
from functools import wraps

from ...core.interfaces import IDependencyContainer

class DependencyContainer(IDependencyContainer):
    """
    Container de dependências com suporte a singleton e transient
    """
    
    def __init__(self):
        self._singletons: Dict[Type, Any] = {}
        self._transients: Dict[Type, Type] = {}
        self._instances: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._lock = threading.RLock()
    
    def register_singleton(self, interface: Type, implementation: Type) -> None:
        """Registra implementação como singleton"""
        with self._lock:
            self._singletons[interface] = implementation
    
    def register_transient(self, interface: Type, implementation: Type) -> None:
        """Registra implementação como transient"""
        with self._lock:
            self._transients[interface] = implementation
    
    def register_instance(self, interface: Type, instance: Any) -> None:
        """Registra instância específica"""
        with self._lock:
            self._instances[interface] = instance
    
    def register_factory(self, interface: Type, factory: Callable) -> None:
        """Registra factory para criação de instâncias"""
        with self._lock:
            self._factories[interface] = factory
    
    def resolve(self, interface: Type) -> Any:
        """Resolve dependência"""
        with self._lock:
            # Verifica se é instância registrada
            if interface in self._instances:
                return self._instances[interface]
            
            # Verifica se é singleton já criado
            if interface in self._singletons:
                if interface not in self._singletons:
                    # Cria singleton
                    implementation = self._singletons[interface]
                    instance = self._create_instance(implementation)
                    self._singletons[interface] = instance
                return self._singletons[interface]
            
            # Verifica se é transient
            if interface in self._transients:
                implementation = self._transients[interface]
                return self._create_instance(implementation)
            
            # Verifica se tem factory
            if interface in self._factories:
                factory = self._factories[interface]
                return factory()
            
            # Tenta criar instância diretamente
            try:
                return self._create_instance(interface)
            except Exception as e:
                raise ValueError(f"Cannot resolve dependency for {interface}: {e}")
    
    def _create_instance(self, implementation: Type) -> Any:
        """Cria instância da implementação"""
        try:
            # Obtém assinatura do construtor
            signature = inspect.signature(implementation.__init__)
            parameters = signature.parameters
            
            # Remove 'self' dos parâmetros
            param_names = list(parameters.keys())[1:]  # Remove 'self'
            
            if not param_names:
                # Construtor sem parâmetros
                return implementation()
            
            # Resolve dependências
            resolved_args = {}
            for param_name in param_names:
                param = parameters[param_name]
                param_type = param.annotation
                
                if param_type != inspect.Parameter.empty:
                    try:
                        resolved_args[param_name] = self.resolve(param_type)
                    except ValueError:
                        if param.default != inspect.Parameter.empty:
                            # Usa valor padrão
                            resolved_args[param_name] = param.default
                        else:
                            raise ValueError(f"Cannot resolve parameter {param_name} of type {param_type}")
                else:
                    if param.default != inspect.Parameter.empty:
                        resolved_args[param_name] = param.default
                    else:
                        raise ValueError(f"Parameter {param_name} has no type annotation or default value")
            
            return implementation(**resolved_args)
            
        except Exception as e:
            raise ValueError(f"Error creating instance of {implementation}: {e}")
    
    def is_registered(self, interface: Type) -> bool:
        """Verifica se interface está registrada"""
        with self._lock:
            return (
                interface in self._singletons or
                interface in self._transients or
                interface in self._instances or
                interface in self._factories
            )
    
    def clear(self) -> None:
        """Limpa todas as dependências"""
        with self._lock:
            self._singletons.clear()
            self._transients.clear()
            self._instances.clear()
            self._factories.clear()
    
    def get_registered_types(self) -> Dict[str, list]:
        """Retorna tipos registrados"""
        with self._lock:
            return {
                'singletons': list(self._singletons.keys()),
                'transients': list(self._transients.keys()),
                'instances': list(self._instances.keys()),
                'factories': list(self._factories.keys())
            }
    
    def create_scope(self) -> 'DependencyScope':
        """Cria escopo de dependências"""
        return DependencyScope(self)

class DependencyScope:
    """
    Escopo de dependências para isolamento
    """
    
    def __init__(self, container: DependencyContainer):
        self.container = container
        self._scope_instances: Dict[Type, Any] = {}
        self._lock = threading.RLock()
    
    def resolve(self, interface: Type) -> Any:
        """Resolve dependência no escopo"""
        with self._lock:
            # Verifica se já existe no escopo
            if interface in self._scope_instances:
                return self._scope_instances[interface]
            
            # Resolve do container principal
            instance = self.container.resolve(interface)
            
            # Armazena no escopo se for transient
            if interface in self.container._transients:
                self._scope_instances[interface] = instance
            
            return instance
    
    def dispose(self) -> None:
        """Descarta escopo"""
        with self._lock:
            self._scope_instances.clear()

# Instância global do container
_container: Optional[DependencyContainer] = None
_container_lock = threading.RLock()

def get_container() -> DependencyContainer:
    """Obtém instância global do container"""
    global _container
    with _container_lock:
        if _container is None:
            _container = DependencyContainer()
        return _container

def set_container(container: DependencyContainer) -> None:
    """Define instância global do container"""
    global _container
    with _container_lock:
        _container = container

def clear_container() -> None:
    """Limpa instância global do container"""
    global _container
    with _container_lock:
        _container = None

# Decorator para injeção automática
def inject_dependencies(func: Callable) -> Callable:
    """Decorator para injeção automática de dependências"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Obtém assinatura da função
        signature = inspect.signature(func)
        parameters = signature.parameters
        
        # Resolve dependências
        container = get_container()
        resolved_kwargs = kwargs.copy()
        
        for param_name, param in parameters.items():
            if param_name not in resolved_kwargs and param_name not in args:
                param_type = param.annotation
                if param_type != inspect.Parameter.empty:
                    try:
                        resolved_kwargs[param_name] = container.resolve(param_type)
                    except ValueError:
                        if param.default != inspect.Parameter.empty:
                            resolved_kwargs[param_name] = param.default
        
        return func(*args, **resolved_kwargs)
    
    return wrapper

# Decorator para classes injetáveis
def injectable(cls: Type) -> Type:
    """Decorator para marcar classe como injetável"""
    cls._injectable = True
    return cls

# Decorator para métodos com injeção
def inject(*dependencies: Type) -> Callable:
    """Decorator para injeção de dependências específicas"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            container = get_container()
            resolved_kwargs = kwargs.copy()
            
            for dep_type in dependencies:
                dep_name = dep_type.__name__.lower()
                if dep_name not in resolved_kwargs:
                    resolved_kwargs[dep_name] = container.resolve(dep_type)
            
            return func(*args, **resolved_kwargs)
        
        return wrapper
    return decorator
