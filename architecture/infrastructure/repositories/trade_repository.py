#!/usr/bin/env python3
"""
🗄️ TRADE REPOSITORY NEØ - REPOSITÓRIO DE TRADES
Implementação específica para repositório de trades
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ...core.interfaces import ITradeRepository
from ...core.entities import Trade, OrderSide, PositionSide
from .base_repository import BaseRepository

class TradeRepository(BaseRepository[Trade], ITradeRepository):
    """
    Repositório para entidades Trade
    """
    
    def __init__(self, data_file: str = "data/trades.json"):
        super().__init__(data_file, Trade)
    
    async def get_by_symbol(self, symbol: str) -> List[Trade]:
        """Obtém trades por símbolo"""
        trades = await self.get_all()
        return [trade for trade in trades if trade.symbol.upper() == symbol.upper()]
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Trade]:
        """Obtém trades por período"""
        trades = await self.get_all()
        return [
            trade for trade in trades 
            if start_date <= trade.executed_at <= end_date
        ]
    
    async def get_pending_trades(self) -> List[Trade]:
        """Obtém trades pendentes"""
        # Trades são sempre executados, então esta implementação retorna lista vazia
        # Em um sistema real, poderia haver trades pendentes de confirmação
        return []
    
    async def get_trades_by_side(self, side: OrderSide) -> List[Trade]:
        """Obtém trades por lado"""
        trades = await self.get_all()
        return [trade for trade in trades if trade.side == side]
    
    async def get_trades_by_position_side(self, position_side: PositionSide) -> List[Trade]:
        """Obtém trades por lado da posição"""
        trades = await self.get_all()
        return [trade for trade in trades if trade.position_side == position_side]
    
    async def get_trades_by_strategy(self, strategy_id: str) -> List[Trade]:
        """Obtém trades por estratégia"""
        trades = await self.get_all()
        return [trade for trade in trades if trade.strategy_id == strategy_id]
    
    async def get_recent_trades(self, hours: int = 24) -> List[Trade]:
        """Obtém trades recentes"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        trades = await self.get_all()
        return [trade for trade in trades if trade.executed_at >= cutoff_time]
    
    async def get_trades_by_leverage(self, min_leverage: int = 1, max_leverage: int = 100) -> List[Trade]:
        """Obtém trades por range de leverage"""
        trades = await self.get_all()
        return [
            trade for trade in trades 
            if min_leverage <= trade.leverage <= max_leverage
        ]
    
    async def get_trades_by_value_range(self, min_value: float = 0, max_value: float = float('inf')) -> List[Trade]:
        """Obtém trades por range de valor"""
        trades = await self.get_all()
        return [
            trade for trade in trades 
            if min_value <= trade.get_total_value().amount <= max_value
        ]
    
    async def get_long_trades(self) -> List[Trade]:
        """Obtém trades long"""
        return await self.get_trades_by_position_side(PositionSide.LONG)
    
    async def get_short_trades(self) -> List[Trade]:
        """Obtém trades short"""
        return await self.get_trades_by_position_side(PositionSide.SHORT)
    
    async def get_buy_trades(self) -> List[Trade]:
        """Obtém trades de compra"""
        return await self.get_trades_by_side(OrderSide.BUY)
    
    async def get_sell_trades(self) -> List[Trade]:
        """Obtém trades de venda"""
        return await self.get_trades_by_side(OrderSide.SELL)
    
    async def get_trades_by_symbol_and_date(self, symbol: str, date: datetime) -> List[Trade]:
        """Obtém trades por símbolo e data específica"""
        trades = await self.get_by_symbol(symbol)
        return [
            trade for trade in trades 
            if trade.executed_at.date() == date.date()
        ]
    
    async def get_top_trades_by_value(self, limit: int = 10) -> List[Trade]:
        """Obtém top trades por valor"""
        trades = await self.get_all()
        trades.sort(key=lambda t: t.get_total_value().amount, reverse=True)
        return trades[:limit]
    
    async def get_trades_by_order_id(self, order_id: str) -> List[Trade]:
        """Obtém trades por ID da ordem"""
        trades = await self.get_all()
        return [trade for trade in trades if trade.order_id == order_id]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas dos trades"""
        trades = await self.get_all()
        
        if not trades:
            return {
                'total_trades': 0,
                'total_value': 0,
                'long_trades': 0,
                'short_trades': 0,
                'buy_trades': 0,
                'sell_trades': 0,
                'avg_leverage': 0,
                'symbol_distribution': {},
                'strategy_distribution': {}
            }
        
        total_value = sum(trade.get_total_value().amount for trade in trades)
        long_count = len(await self.get_long_trades())
        short_count = len(await self.get_short_trades())
        buy_count = len(await self.get_buy_trades())
        sell_count = len(await self.get_sell_trades())
        avg_leverage = sum(trade.leverage for trade in trades) / len(trades)
        
        # Distribuição por símbolo
        symbol_dist = {}
        for trade in trades:
            symbol = trade.symbol
            symbol_dist[symbol] = symbol_dist.get(symbol, 0) + 1
        
        # Distribuição por estratégia
        strategy_dist = {}
        for trade in trades:
            if trade.strategy_id:
                strategy_dist[trade.strategy_id] = strategy_dist.get(trade.strategy_id, 0) + 1
        
        return {
            'total_trades': len(trades),
            'total_value': total_value,
            'long_trades': long_count,
            'short_trades': short_count,
            'buy_trades': buy_count,
            'sell_trades': sell_count,
            'avg_leverage': avg_leverage,
            'symbol_distribution': symbol_dist,
            'strategy_distribution': strategy_dist
        }
    
    async def get_daily_statistics(self, date: datetime) -> Dict[str, Any]:
        """Obtém estatísticas diárias"""
        trades = await self.get_trades_by_symbol_and_date("ALL", date)
        
        if not trades:
            return {
                'date': date.date().isoformat(),
                'total_trades': 0,
                'total_value': 0,
                'long_trades': 0,
                'short_trades': 0
            }
        
        total_value = sum(trade.get_total_value().amount for trade in trades)
        long_count = len([t for t in trades if t.is_long()])
        short_count = len([t for t in trades if t.is_short()])
        
        return {
            'date': date.date().isoformat(),
            'total_trades': len(trades),
            'total_value': total_value,
            'long_trades': long_count,
            'short_trades': short_count
        }
    
    async def get_monthly_statistics(self, year: int, month: int) -> Dict[str, Any]:
        """Obtém estatísticas mensais"""
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        trades = await self.get_by_date_range(start_date, end_date)
        
        if not trades:
            return {
                'year': year,
                'month': month,
                'total_trades': 0,
                'total_value': 0,
                'long_trades': 0,
                'short_trades': 0
            }
        
        total_value = sum(trade.get_total_value().amount for trade in trades)
        long_count = len([t for t in trades if t.is_long()])
        short_count = len([t for t in trades if t.is_short()])
        
        return {
            'year': year,
            'month': month,
            'total_trades': len(trades),
            'total_value': total_value,
            'long_trades': long_count,
            'short_trades': short_count
        }
