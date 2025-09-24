#!/usr/bin/env python3
"""
⚠️ EXCEPTIONS NEØ - EXCEÇÕES DO SISTEMA
Exceções específicas do domínio
"""

class SniperException(Exception):
    """Exceção base do sistema Sniper"""
    pass

class SecurityError(SniperException):
    """Erro de segurança"""
    pass

class ValidationError(SniperException):
    """Erro de validação"""
    pass

class TradingError(SniperException):
    """Erro de trading"""
    pass

class StrategyError(SniperException):
    """Erro de estratégia"""
    pass

class RepositoryError(SniperException):
    """Erro de repositório"""
    pass

class ServiceError(SniperException):
    """Erro de serviço"""
    pass
