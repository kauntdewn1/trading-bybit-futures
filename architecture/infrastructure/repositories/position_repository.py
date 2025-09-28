#!/usr/bin/env python3
"""
🗄️ POSITION REPOSITORY NEØ - REPOSITÓRIO DE POSIÇÕES
Implementação específica para repositório de posições
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ...core.interfaces import IRepository
from ...core.entities import Position, PositionSide
from .base_repository import BaseRepository

class PositionRepository(BaseRepository[Position], IRepository):
    """
    Repositório para entidades Position
    """
    
    def __init__(self, data_file: str = "data/positions.json"):
        super().__init__(data_file, Position)
    
    async def get_by_symbol(self, symbol: str) -> List[Position]:
        """Obtém posições por símbolo"""
        positions = await self.get_all()
        return [pos for pos in positions if pos.symbol.upper() == symbol.upper()]
    
    async def get_by_side(self, side: PositionSide) -> List[Position]:
        """Obtém posições por lado"""
        positions = await self.get_all()
        return [pos for pos in positions if pos.side == side]
    
    async def get_long_positions(self) -> List[Position]:
        """Obtém posições long"""
        return await self.get_by_side(PositionSide.LONG)
    
    async def get_short_positions(self) -> List[Position]:
        """Obtém posições short"""
        return await self.get_by_side(PositionSide.SHORT)
    
    async def get_profitable_positions(self) -> List[Position]:
        """Obtém posições lucrativas"""
        positions = await self.get_all()
        return [pos for pos in positions if pos.is_profitable()]
    
    async def get_losing_positions(self) -> List[Position]:
        """Obtém posições com prejuízo"""
        positions = await self.get_all()
        return [pos for pos in positions if not pos.is_profitable()]
    
    async def get_positions_by_leverage(self, min_leverage: int = 1, max_leverage: int = 100) -> List[Position]:
        """Obtém posições por range de leverage"""
        positions = await self.get_all()
        return [
            pos for pos in positions 
            if min_leverage <= pos.leverage <= max_leverage
        ]
    
    async def get_positions_by_pnl_range(self, min_pnl: float = float('-inf'), max_pnl: float = float('inf')) -> List[Position]:
        """Obtém posições por range de PnL"""
        positions = await self.get_all()
        return [
            pos for pos in positions 
            if min_pnl <= pos.unrealized_pnl.amount <= max_pnl
        ]
    
    async def get_recent_positions(self, hours: int = 24) -> List[Position]:
        """Obtém posições recentes"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        positions = await self.get_all()
        return [pos for pos in positions if pos.created_at >= cutoff_time]
    
    async def get_positions_by_margin_range(self, min_margin: float = 0, max_margin: float = float('inf')) -> List[Position]:
        """Obtém posições por range de margem"""
        positions = await self.get_all()
        return [
            pos for pos in positions 
            if min_margin <= pos.margin.amount <= max_margin
        ]
    
    async def get_top_positions_by_pnl(self, limit: int = 10) -> List[Position]:
        """Obtém top posições por PnL"""
        positions = await self.get_all()
        positions.sort(key=lambda p: p.unrealized_pnl.amount, reverse=True)
        return positions[:limit]
    
    async def get_worst_positions_by_pnl(self, limit: int = 10) -> List[Position]:
        """Obtém piores posições por PnL"""
        positions = await self.get_all()
        positions.sort(key=lambda p: p.unrealized_pnl.amount)
        return positions[:limit]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das posições"""
        positions = await self.get_all()
        
        if not positions:
            return {
                'total_positions': 0,
                'long_positions': 0,
                'short_positions': 0,
                'profitable_positions': 0,
                'losing_positions': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'max_pnl': 0,
                'min_pnl': 0,
                'avg_leverage': 0,
                'total_margin': 0
            }
        
        long_count = len(await self.get_long_positions())
        short_count = len(await self.get_short_positions())
        profitable_count = len(await self.get_profitable_positions())
        losing_count = len(await self.get_losing_positions())
        
        total_pnl = sum(pos.unrealized_pnl.amount for pos in positions)
        avg_pnl = total_pnl / len(positions)
        max_pnl = max(pos.unrealized_pnl.amount for pos in positions)
        min_pnl = min(pos.unrealized_pnl.amount for pos in positions)
        
        avg_leverage = sum(pos.leverage for pos in positions) / len(positions)
        total_margin = sum(pos.margin.amount for pos in positions)
        
        return {
            'total_positions': len(positions),
            'long_positions': long_count,
            'short_positions': short_count,
            'profitable_positions': profitable_count,
            'losing_positions': losing_count,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'max_pnl': max_pnl,
            'min_pnl': min_pnl,
            'avg_leverage': avg_leverage,
            'total_margin': total_margin
        }
