#!/usr/bin/env python3
"""
💉 DECORATORS NEØ - DECORATORS DE INJEÇÃO DE DEPENDÊNCIA
Decorators para facilitar injeção de dependências
"""

import inspect
import functools
from typing import Type, Callable, Any, Dict, List

from .container import get_container

def injectable(cls: Type) -> Type:
    """
    Decorator para marcar classe como injetável
    
    Usage:
        @injectable
        class MyService:
            def __init__(self, repository: IRepository):
                self.repository = repository
    """
    cls._injectable = True
    return cls

def inject(*dependencies: Type) -> Callable:
    """
    Decorator para injeção de dependências específicas
    
    Usage:
        @inject(IRepository, ILogger)
        def my_function(repository: IRepository, logger: ILogger):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            container = get_container()
            resolved_kwargs = kwargs.copy()
            
            # Resolve dependências especificadas
            for dep_type in dependencies:
                dep_name = dep_type.__name__.lower()
                if dep_name not in resolved_kwargs:
                    try:
                        resolved_kwargs[dep_name] = container.resolve(dep_type)
                    except ValueError:
                        # Se não conseguir resolver, continua sem a dependência
                        pass
            
            return func(*args, **resolved_kwargs)
        
        return wrapper
    return decorator

def auto_inject(func: Callable) -> Callable:
    """
    Decorator para injeção automática de dependências baseada em type hints
    
    Usage:
        @auto_inject
        def my_function(repository: IRepository, logger: ILogger):
            pass
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        container = get_container()
        signature = inspect.signature(func)
        parameters = signature.parameters
        
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

def singleton(cls: Type) -> Type:
    """
    Decorator para registrar classe como singleton
    
    Usage:
        @singleton
        class MyService:
            pass
    """
    container = get_container()
    container.register_singleton(cls, cls)
    return cls

def transient(cls: Type) -> Type:
    """
    Decorator para registrar classe como transient
    
    Usage:
        @transient
        class MyService:
            pass
    """
    container = get_container()
    container.register_transient(cls, cls)
    return cls

def factory(func: Callable) -> Callable:
    """
    Decorator para registrar função como factory
    
    Usage:
        @factory
        def create_service() -> IService:
            return MyService()
    """
    container = get_container()
    
    # Obtém tipo de retorno da função
    signature = inspect.signature(func)
    return_type = signature.return_annotation
    
    if return_type != inspect.Parameter.empty:
        container.register_factory(return_type, func)
    
    return func

def scoped(cls: Type) -> Type:
    """
    Decorator para registrar classe como scoped (uma instância por escopo)
    
    Usage:
        @scoped
        class MyService:
            pass
    """
    cls._scoped = True
    return cls

def inject_property(property_name: str, dependency_type: Type) -> Callable:
    """
    Decorator para injeção de propriedade
    
    Usage:
        class MyService:
            @inject_property('repository', IRepository)
            def repository(self):
                return self._repository
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, f'_{property_name}'):
                container = get_container()
                setattr(self, f'_{property_name}', container.resolve(dependency_type))
            return func(self, *args, **kwargs)
        
        return wrapper
    return decorator

def lazy_inject(dependency_type: Type) -> Callable:
    """
    Decorator para injeção lazy (criada apenas quando acessada)
    
    Usage:
        class MyService:
            @lazy_inject(IRepository)
            def repository(self):
                return self._repository
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            property_name = f'_{dependency_type.__name__.lower()}'
            if not hasattr(self, property_name):
                container = get_container()
                setattr(self, property_name, container.resolve(dependency_type))
            return getattr(self, property_name)
        
        return wrapper
    return decorator

def inject_config(config_key: str, default_value: Any = None) -> Callable:
    """
    Decorator para injeção de configuração
    
    Usage:
        @inject_config('api_key', 'default_key')
        def my_function(api_key: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            container = get_container()
            
            # Tenta resolver configuração
            try:
                config = container.resolve(type(default_value))
                value = config.get(config_key, default_value)
            except ValueError:
                value = default_value
            
            # Injeta valor como parâmetro
            param_name = config_key.lower()
            if param_name not in kwargs:
                kwargs[param_name] = value
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def inject_environment(env_var: str, default_value: Any = None) -> Callable:
    """
    Decorator para injeção de variável de ambiente
    
    Usage:
        @inject_environment('API_KEY', 'default_key')
        def my_function(api_key: str):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import os
            value = os.getenv(env_var, default_value)
            
            # Injeta valor como parâmetro
            param_name = env_var.lower()
            if param_name not in kwargs:
                kwargs[param_name] = value
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def validate_dependencies(*required_types: Type) -> Callable:
    """
    Decorator para validar dependências obrigatórias
    
    Usage:
        @validate_dependencies(IRepository, ILogger)
        def my_function(repository: IRepository, logger: ILogger):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            container = get_container()
            
            # Valida se todas as dependências estão registradas
            for dep_type in required_types:
                if not container.is_registered(dep_type):
                    raise ValueError(f"Required dependency {dep_type} is not registered")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

def conditional_inject(condition: Callable[[], bool], *dependencies: Type) -> Callable:
    """
    Decorator para injeção condicional de dependências
    
    Usage:
        @conditional_inject(lambda: os.getenv('ENV') == 'production', IProductionService)
        def my_function(service: IProductionService):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if condition():
                container = get_container()
                resolved_kwargs = kwargs.copy()
                
                for dep_type in dependencies:
                    dep_name = dep_type.__name__.lower()
                    if dep_name not in resolved_kwargs:
                        try:
                            resolved_kwargs[dep_name] = container.resolve(dep_type)
                        except ValueError:
                            pass
                
                return func(*args, **resolved_kwargs)
            else:
                return func(*args, **kwargs)
        
        return wrapper
    return decorator
