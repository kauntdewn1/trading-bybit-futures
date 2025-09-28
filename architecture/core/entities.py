#!/usr/bin/env python3
"""
🏗️ ENTITIES NEØ - ENTIDADES DO DOMÍNIO
Entidades que representam conceitos de negócio
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid

# =============================================================================
# ENUMS
# =============================================================================

class OrderSide(Enum):
    """Lado da ordem"""
    BUY = "Buy"
    SELL = "Sell"

class OrderType(Enum):
    """Tipo da ordem"""
    MARKET = "Market"
    LIMIT = "Limit"
    STOP = "Stop"
    STOP_LIMIT = "StopLimit"

class OrderStatus(Enum):
    """Status da ordem"""
    PENDING = "Pending"
    FILLED = "Filled"
    PARTIALLY_FILLED = "PartiallyFilled"
    CANCELLED = "Cancelled"
    REJECTED = "Rejected"

class PositionSide(Enum):
    """Lado da posição"""
    LONG = "Long"
    SHORT = "Short"

class AssetStatus(Enum):
    """Status do ativo"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    DELISTED = "Delisted"

class StrategyType(Enum):
    """Tipo de estratégia"""
    SNIPER = "Sniper"
    SCALPING = "Scalping"
    SWING = "Swing"
    ARBITRAGE = "Arbitrage"
    GRID = "Grid"

# =============================================================================
# VALUE OBJECTS
# =============================================================================

@dataclass(frozen=True)
class Money:
    """Objeto de valor para representar dinheiro"""
    amount: float
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
    
    def __mul__(self, multiplier: float) -> 'Money':
        return Money(self.amount * multiplier, self.currency)
    
    def __str__(self) -> str:
        return f"{self.amount:.8f} {self.currency}"

@dataclass(frozen=True)
class Price:
    """Objeto de valor para representar preço"""
    value: float
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
    value: float
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
    value: float
    
    def __post_init__(self):
        if not -100 <= self.value <= 100:
            raise ValueError("Percentage must be between -100 and 100")
    
    def __str__(self) -> str:
        return f"{self.value:.2f}%"

# =============================================================================
# ENTITIES
# =============================================================================

@dataclass
class Asset:
    """Entidade que representa um ativo"""
    symbol: str
    name: str
    status: AssetStatus
    base_currency: str
    quote_currency: str
    min_qty: float
    max_qty: float
    step_size: float
    tick_size: float
    contract_type: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if not self.name:
            raise ValueError("Name cannot be empty")
        if self.min_qty <= 0:
            raise ValueError("Min quantity must be positive")
        if self.max_qty <= self.min_qty:
            raise ValueError("Max quantity must be greater than min quantity")
    
    def is_active(self) -> bool:
        """Verifica se ativo está ativo"""
        return self.status == AssetStatus.ACTIVE
    
    def can_trade(self) -> bool:
        """Verifica se pode fazer trading"""
        return self.is_active() and self.contract_type == "LinearPerpetual"
    
    def validate_quantity(self, quantity: float) -> bool:
        """Valida quantidade"""
        return self.min_qty <= quantity <= self.max_qty

@dataclass
class MarketData:
    """Entidade que representa dados de mercado"""
    symbol: str
    price: Price
    volume_24h: float
    funding_rate: float
    open_interest: float
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.volume_24h < 0:
            raise ValueError("Volume cannot be negative")
        if not -1 <= self.funding_rate <= 1:
            raise ValueError("Funding rate must be between -1 and 1")
    
    def is_high_volume(self, threshold: float = 1000000) -> bool:
        """Verifica se volume é alto"""
        return self.volume_24h > threshold
    
    def is_high_funding(self, threshold: float = 0.01) -> bool:
        """Verifica se funding rate é alto"""
        return abs(self.funding_rate) > threshold

@dataclass
class TechnicalIndicators:
    """Entidade que representa indicadores técnicos"""
    symbol: str
    rsi: float
    macd_line: float
    macd_signal: float
    macd_histogram: float
    ema_12: float
    ema_26: float
    sma_20: float
    sma_50: float
    bollinger_upper: float
    bollinger_middle: float
    bollinger_lower: float
    timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if not 0 <= self.rsi <= 100:
            raise ValueError("RSI must be between 0 and 100")
    
    def is_rsi_oversold(self, threshold: float = 30) -> bool:
        """Verifica se RSI está oversold"""
        return self.rsi < threshold
    
    def is_rsi_overbought(self, threshold: float = 70) -> bool:
        """Verifica se RSI está overbought"""
        return self.rsi > threshold
    
    def is_macd_bullish(self) -> bool:
        """Verifica se MACD é bullish"""
        return self.macd_line > self.macd_signal
    
    def is_macd_bearish(self) -> bool:
        """Verifica se MACD é bearish"""
        return self.macd_line < self.macd_signal

@dataclass
class AnalysisResult:
    """Entidade que representa resultado de análise"""
    symbol: str
    long_score: float
    short_score: float
    confidence: float
    indicators: TechnicalIndicators
    market_data: MarketData
    analysis_timestamp: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if not 0 <= self.long_score <= 10:
            raise ValueError("Long score must be between 0 and 10")
        if not 0 <= self.short_score <= 10:
            raise ValueError("Short score must be between 0 and 10")
        if not 0 <= self.confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1")
    
    def get_max_score(self) -> float:
        """Retorna score máximo"""
        return max(self.long_score, self.short_score)
    
    def get_direction(self) -> str:
        """Retorna direção recomendada"""
        return "LONG" if self.long_score > self.short_score else "SHORT"
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Verifica se confiança é alta"""
        return self.confidence > threshold
    
    def is_strong_signal(self, threshold: float = 8.0) -> bool:
        """Verifica se sinal é forte"""
        return self.get_max_score() > threshold

@dataclass
class Order:
    """Entidade que representa uma ordem"""
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Quantity
    price: Optional[Price]
    position_side: PositionSide
    leverage: int
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    external_id: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.leverage < 1 or self.leverage > 100:
            raise ValueError("Leverage must be between 1 and 100")
        if self.order_type == OrderType.LIMIT and not self.price:
            raise ValueError("Limit orders must have a price")
    
    def is_pending(self) -> bool:
        """Verifica se ordem está pendente"""
        return self.status == OrderStatus.PENDING
    
    def is_filled(self) -> bool:
        """Verifica se ordem foi executada"""
        return self.status == OrderStatus.FILLED
    
    def is_cancelled(self) -> bool:
        """Verifica se ordem foi cancelada"""
        return self.status == OrderStatus.CANCELLED
    
    def can_cancel(self) -> bool:
        """Verifica se ordem pode ser cancelada"""
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
    
    def get_total_value(self) -> Money:
        """Calcula valor total da ordem"""
        if self.price:
            total = self.quantity.value * self.price.value
            return Money(total, "USDT")
        return Money(0, "USDT")

@dataclass
class Position:
    """Entidade que representa uma posição"""
    symbol: str
    side: PositionSide
    size: Quantity
    entry_price: Price
    current_price: Price
    unrealized_pnl: Money
    realized_pnl: Money
    leverage: int
    margin: Money
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.leverage < 1 or self.leverage > 100:
            raise ValueError("Leverage must be between 1 and 100")
    
    def is_long(self) -> bool:
        """Verifica se posição é long"""
        return self.side == PositionSide.LONG
    
    def is_short(self) -> bool:
        """Verifica se posição é short"""
        return self.side == PositionSide.SHORT
    
    def is_profitable(self) -> bool:
        """Verifica se posição é lucrativa"""
        return self.unrealized_pnl.amount > 0
    
    def get_pnl_percentage(self) -> Percentage:
        """Calcula PnL em porcentagem"""
        if self.entry_price.value == 0:
            return Percentage(0)
        
        if self.is_long():
            pnl_pct = ((self.current_price.value - self.entry_price.value) / self.entry_price.value) * 100
        else:
            pnl_pct = ((self.entry_price.value - self.current_price.value) / self.entry_price.value) * 100
        
        return Percentage(pnl_pct)

@dataclass
class Strategy:
    """Entidade que representa uma estratégia"""
    name: str
    strategy_type: StrategyType
    version: str
    parameters: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Name cannot be empty")
        if not self.version:
            raise ValueError("Version cannot be empty")
    
    def activate(self) -> None:
        """Ativa estratégia"""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """Desativa estratégia"""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def update_parameters(self, new_parameters: Dict[str, Any]) -> None:
        """Atualiza parâmetros da estratégia"""
        self.parameters.update(new_parameters)
        self.updated_at = datetime.now()
    
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Obtém parâmetro da estratégia"""
        return self.parameters.get(key, default)

@dataclass
class Trade:
    """Entidade que representa um trade"""
    symbol: str
    side: OrderSide
    quantity: Quantity
    price: Price
    position_side: PositionSide
    leverage: int
    strategy_id: Optional[str] = None
    order_id: Optional[str] = None
    executed_at: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.symbol:
            raise ValueError("Symbol cannot be empty")
        if self.leverage < 1 or self.leverage > 100:
            raise ValueError("Leverage must be between 1 and 100")
    
    def get_total_value(self) -> Money:
        """Calcula valor total do trade"""
        total = self.quantity.value * self.price.value
        return Money(total, "USDT")
    
    def is_long(self) -> bool:
        """Verifica se trade é long"""
        return self.position_side == PositionSide.LONG
    
    def is_short(self) -> bool:
        """Verifica se trade é short"""
        return self.position_side == PositionSide.SHORT

# =============================================================================
# AGGREGATES
# =============================================================================

@dataclass
class TradingSession:
    """Agregado que representa uma sessão de trading"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_trades: int = 0
    successful_trades: int = 0
    failed_trades: int = 0
    total_pnl: Money = field(default_factory=lambda: Money(0, "USDT"))
    max_drawdown: Money = field(default_factory=lambda: Money(0, "USDT"))
    strategies_used: List[str] = field(default_factory=list)
    assets_traded: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.session_id:
            raise ValueError("Session ID cannot be empty")
    
    def is_active(self) -> bool:
        """Verifica se sessão está ativa"""
        return self.end_time is None
    
    def end_session(self) -> None:
        """Finaliza sessão"""
        self.end_time = datetime.now()
    
    def add_trade(self, trade: Trade, success: bool = True) -> None:
        """Adiciona trade à sessão"""
        self.total_trades += 1
        if success:
            self.successful_trades += 1
        else:
            self.failed_trades += 1
        
        if trade.symbol not in self.assets_traded:
            self.assets_traded.append(trade.symbol)
    
    def get_success_rate(self) -> Percentage:
        """Calcula taxa de sucesso"""
        if self.total_trades == 0:
            return Percentage(0)
        success_rate = (self.successful_trades / self.total_trades) * 100
        return Percentage(success_rate)
    
    def get_duration(self) -> Optional[float]:
        """Calcula duração da sessão em segundos"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
