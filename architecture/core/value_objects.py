#!/usr/bin/env python3
"""
💎 VALUE OBJECTS NEØ - OBJETOS DE VALOR
Objetos de valor imutáveis para representar conceitos de domínio
"""

from dataclasses import dataclass
from typing import Union
from decimal import Decimal

@dataclass(frozen=True)
class Money:
    """Objeto de valor para representar dinheiro"""
    amount: Decimal
    currency: str = "USDT"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency:
            raise ValueError("Currency cannot be empty")
    
    def __add__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
    
    def __sub__(self, other: 'Money') -> 'Money':
        if self.currency != other.currency:
            raise ValueError("Cannot subtract different currencies")
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, multiplier: Union[float, int, Decimal]) -> 'Money':
        return Money(self.amount * Decimal(str(multiplier)), self.currency)
    
    def __str__(self) -> str:
        return f"{self.amount:.8f} {self.currency}"

@dataclass(frozen=True)
class Price:
    """Objeto de valor para representar preço"""
    value: Decimal
    symbol: str
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Price must be positive")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
    
    def __str__(self) -> str:
        return f"{self.value:.8f} {self.symbol}"

@dataclass(frozen=True)
class Quantity:
    """Objeto de valor para representar quantidade"""
    value: Decimal
    symbol: str
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Quantity must be positive")
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
    
    def __str__(self) -> str:
        return f"{self.value:.8f} {self.symbol}"

@dataclass(frozen=True)
class Percentage:
    """Objeto de valor para representar porcentagem"""
    value: Decimal
    
    def __post_init__(self):
        if not -100 <= self.value <= 100:
            raise ValueError("Percentage must be between -100 and 100")
    
    def __str__(self) -> str:
        return f"{self.value:.2f}%"
