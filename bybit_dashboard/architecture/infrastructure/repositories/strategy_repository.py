#!/usr/bin/env python3
"""
🗄️ STRATEGY REPOSITORY NEØ - REPOSITÓRIO DE ESTRATÉGIAS
Implementação específica para repositório de estratégias
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ...core.interfaces import IRepository
from ...core.entities import Strategy, StrategyType
from .base_repository import BaseRepository

class StrategyRepository(BaseRepository[Strategy], IRepository):
    """
    Repositório para entidades Strategy
    """
    
    def __init__(self, data_file: str = "data/strategies.json"):
        super().__init__(data_file, Strategy)
    
    async def get_by_name(self, name: str) -> Optional[Strategy]:
        """Obtém estratégia por nome"""
        strategies = await self.get_all()
        for strategy in strategies:
            if strategy.name.lower() == name.lower():
                return strategy
        return None
    
    async def get_by_type(self, strategy_type: StrategyType) -> List[Strategy]:
        """Obtém estratégias por tipo"""
        strategies = await self.get_all()
        return [strategy for strategy in strategies if strategy.strategy_type == strategy_type]
    
    async def get_active_strategies(self) -> List[Strategy]:
        """Obtém estratégias ativas"""
        strategies = await self.get_all()
        return [strategy for strategy in strategies if strategy.is_active]
    
    async def get_inactive_strategies(self) -> List[Strategy]:
        """Obtém estratégias inativas"""
        strategies = await self.get_all()
        return [strategy for strategy in strategies if not strategy.is_active]
    
    async def get_strategies_by_version(self, version: str) -> List[Strategy]:
        """Obtém estratégias por versão"""
        strategies = await self.get_all()
        return [strategy for strategy in strategies if strategy.version == version]
    
    async def get_recent_strategies(self, days: int = 7) -> List[Strategy]:
        """Obtém estratégias recentes"""
        cutoff_time = datetime.now() - timedelta(days=days)
        strategies = await self.get_all()
        return [strategy for strategy in strategies if strategy.created_at >= cutoff_time]
    
    async def get_strategies_by_parameter(self, param_name: str, param_value: Any) -> List[Strategy]:
        """Obtém estratégias por parâmetro específico"""
        strategies = await self.get_all()
        return [
            strategy for strategy in strategies 
            if strategy.get_parameter(param_name) == param_value
        ]
    
    async def get_strategies_by_min_score(self, min_score: float) -> List[Strategy]:
        """Obtém estratégias com score mínimo"""
        strategies = await self.get_all()
        return [
            strategy for strategy in strategies 
            if strategy.get_parameter('min_score', 0) >= min_score
        ]
    
    async def get_strategies_by_max_leverage(self, max_leverage: int) -> List[Strategy]:
        """Obtém estratégias com leverage máximo"""
        strategies = await self.get_all()
        return [
            strategy for strategy in strategies 
            if strategy.get_parameter('max_leverage', 1) <= max_leverage
        ]
    
    async def get_sniper_strategies(self) -> List[Strategy]:
        """Obtém estratégias Sniper"""
        return await self.get_by_type(StrategyType.SNIPER)
    
    async def get_scalping_strategies(self) -> List[Strategy]:
        """Obtém estratégias Scalping"""
        return await self.get_by_type(StrategyType.SCALPING)
    
    async def get_swing_strategies(self) -> List[Strategy]:
        """Obtém estratégias Swing"""
        return await self.get_by_type(StrategyType.SWING)
    
    async def get_arbitrage_strategies(self) -> List[Strategy]:
        """Obtém estratégias Arbitrage"""
        return await self.get_by_type(StrategyType.ARBITRAGE)
    
    async def get_grid_strategies(self) -> List[Strategy]:
        """Obtém estratégias Grid"""
        return await self.get_by_type(StrategyType.GRID)
    
    async def activate_strategy(self, strategy_id: str) -> bool:
        """Ativa estratégia"""
        strategy = await self.get_by_id(strategy_id)
        if strategy:
            strategy.activate()
            await self.save(strategy)
            return True
        return False
    
    async def deactivate_strategy(self, strategy_id: str) -> bool:
        """Desativa estratégia"""
        strategy = await self.get_by_id(strategy_id)
        if strategy:
            strategy.deactivate()
            await self.save(strategy)
            return True
        return False
    
    async def update_strategy_parameters(self, strategy_id: str, new_parameters: Dict[str, Any]) -> bool:
        """Atualiza parâmetros da estratégia"""
        strategy = await self.get_by_id(strategy_id)
        if strategy:
            strategy.update_parameters(new_parameters)
            await self.save(strategy)
            return True
        return False
    
    async def get_strategy_performance(self, strategy_id: str) -> Dict[str, Any]:
        """Obtém performance da estratégia"""
        strategy = await self.get_by_id(strategy_id)
        if not strategy:
            return {}
        
        return {
            'strategy_id': strategy_id,
            'name': strategy.name,
            'version': strategy.version,
            'is_active': strategy.is_active,
            'created_at': strategy.created_at.isoformat(),
            'last_run': strategy.last_run.isoformat() if strategy.last_run else None,
            'run_count': strategy.run_count,
            'success_count': strategy.success_count,
            'success_rate': strategy.get_success_rate(),
            'parameters': strategy.get_parameters()
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas das estratégias"""
        strategies = await self.get_all()
        
        if not strategies:
            return {
                'total_strategies': 0,
                'active_strategies': 0,
                'inactive_strategies': 0,
                'type_distribution': {},
                'version_distribution': {},
                'avg_success_rate': 0
            }
        
        active_count = len(await self.get_active_strategies())
        inactive_count = len(await self.get_inactive_strategies())
        
        # Distribuição por tipo
        type_dist = {}
        for strategy in strategies:
            strategy_type = strategy.strategy_type.value
            type_dist[strategy_type] = type_dist.get(strategy_type, 0) + 1
        
        # Distribuição por versão
        version_dist = {}
        for strategy in strategies:
            version = strategy.version
            version_dist[version] = version_dist.get(version, 0) + 1
        
        # Taxa de sucesso média
        success_rates = [strategy.get_success_rate() for strategy in strategies]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        
        return {
            'total_strategies': len(strategies),
            'active_strategies': active_count,
            'inactive_strategies': inactive_count,
            'type_distribution': type_dist,
            'version_distribution': version_dist,
            'avg_success_rate': avg_success_rate
        }
