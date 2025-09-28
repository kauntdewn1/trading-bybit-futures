"""
💉 DEPENDENCY INJECTION NEØ - SISTEMA DE INJEÇÃO DE DEPENDÊNCIA
Container de dependências com suporte a singleton e transient
"""

from .container import DependencyContainer, get_container, set_container, clear_container
from .decorators import injectable, inject

__all__ = [
    "DependencyContainer",
    "get_container",
    "set_container", 
    "clear_container",
    "injectable", 
    "inject"
]
