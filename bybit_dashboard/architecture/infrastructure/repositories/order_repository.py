#!/usr/bin/env python3
"""
🗄️ ORDER REPOSITORY NEØ - REPOSITÓRIO DE ORDENS
Implementação específica para repositório de ordens
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from ...core.interfaces import IRepository
from ...core.entities import Order, OrderStatus, OrderSide, PositionSide
from .base_repository import BaseRepository

class OrderRepository(BaseRepository[Order], IRepository):
    """
    Repositório para entidades Order
    """
    
    def __init__(self, data_file: str = "data/orders.json"):
        super().__init__(data_file, Order)
    
    async def get_by_symbol(self, symbol: str) -> List[Order]:
        """Obtém ordens por símbolo"""
        orders = await self.get_all()
        return [order for order in orders if order.symbol.upper() == symbol.upper()]
    
    async def get_by_status(self, status: OrderStatus) -> List[Order]:
        """Obtém ordens por status"""
        orders = await self.get_all()
        return [order for order in orders if order.status == status]
    
    async def get_pending_orders(self) -> List[Order]:
        """Obtém ordens pendentes"""
        return await self.get_by_status(OrderStatus.PENDING)
    
    async def get_filled_orders(self) -> List[Order]:
        """Obtém ordens executadas"""
        return await self.get_by_status(OrderStatus.FILLED)
    
    async def get_cancelled_orders(self) -> List[Order]:
        """Obtém ordens canceladas"""
        return await self.get_by_status(OrderStatus.CANCELLED)
    
    async def get_by_side(self, side: OrderSide) -> List[Order]:
        """Obtém ordens por lado"""
        orders = await self.get_all()
        return [order for order in orders if order.side == side]
    
    async def get_by_position_side(self, position_side: PositionSide) -> List[Order]:
        """Obtém ordens por lado da posição"""
        orders = await self.get_all()
        return [order for order in orders if order.position_side == position_side]
    
    async def get_by_external_id(self, external_id: str) -> Optional[Order]:
        """Obtém ordem por ID externo"""
        orders = await self.get_all()
        for order in orders:
            if order.external_id == external_id:
                return order
        return None
    
    async def get_recent_orders(self, hours: int = 24) -> List[Order]:
        """Obtém ordens recentes"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        orders = await self.get_all()
        return [order for order in orders if order.created_at >= cutoff_time]
    
    async def get_orders_by_value_range(self, min_value: float = 0, max_value: float = float('inf')) -> List[Order]:
        """Obtém ordens por range de valor"""
        orders = await self.get_all()
        return [
            order for order in orders 
            if min_value <= order.get_total_value().amount <= max_value
        ]
    
    async def get_buy_orders(self) -> List[Order]:
        """Obtém ordens de compra"""
        return await self.get_by_side(OrderSide.BUY)
    
    async def get_sell_orders(self) -> List[Order]:
        """Obtém ordens de venda"""
        return await self.get_by_side(OrderSide.SELL)
    
    async def get_long_orders(self) -> List[Order]:
        """Obtém ordens long"""
        return await self.get_by_position_side(PositionSide.LONG)
    
    async def get_short_orders(self) -> List[Order]:
        """Obtém ordens short"""
        return await self.get_by_position_side(PositionSide.SHORT)
    
    async def get_orders_by_leverage(self, min_leverage: int = 1, max_leverage: int = 100) -> List[Order]:
        """Obtém ordens por range de leverage"""
        orders = await self.get_all()
        return [
            order for order in orders 
            if min_leverage <= order.leverage <= max_leverage
        ]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das ordens"""
        orders = await self.get_all()
        
        if not orders:
            return {
                'total_orders': 0,
                'pending_orders': 0,
                'filled_orders': 0,
                'cancelled_orders': 0,
                'buy_orders': 0,
                'sell_orders': 0,
                'long_orders': 0,
                'short_orders': 0,
                'avg_leverage': 0,
                'total_value': 0
            }
        
        pending_count = len(await self.get_pending_orders())
        filled_count = len(await self.get_filled_orders())
        cancelled_count = len(await self.get_cancelled_orders())
        buy_count = len(await self.get_buy_orders())
        sell_count = len(await self.get_sell_orders())
        long_count = len(await self.get_long_orders())
        short_count = len(await self.get_short_orders())
        
        total_value = sum(order.get_total_value().amount for order in orders)
        avg_leverage = sum(order.leverage for order in orders) / len(orders)
        
        return {
            'total_orders': len(orders),
            'pending_orders': pending_count,
            'filled_orders': filled_count,
            'cancelled_orders': cancelled_count,
            'buy_orders': buy_count,
            'sell_orders': sell_count,
            'long_orders': long_count,
            'short_orders': short_count,
            'avg_leverage': avg_leverage,
            'total_value': total_value
        }
