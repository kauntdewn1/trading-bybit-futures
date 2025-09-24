#!/usr/bin/env python3
"""
🗄️ ASSET REPOSITORY NEØ - REPOSITÓRIO DE ATIVOS
Implementação específica para repositório de ativos
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from ...core.interfaces import IAssetRepository
from ...core.entities import Asset, AssetStatus
from .base_repository import BaseRepository

class AssetRepository(BaseRepository[Asset], IAssetRepository):
    """
    Repositório para entidades Asset
    """
    
    def __init__(self, data_file: str = "data/assets.json"):
        super().__init__(data_file, Asset)
    
    async def get_by_symbol(self, symbol: str) -> Optional[Asset]:
        """Obtém ativo por símbolo"""
        assets = await self.get_all()
        
        for asset in assets:
            if asset.symbol.upper() == symbol.upper():
                return asset
        
        return None
    
    async def get_active_assets(self) -> List[Asset]:
        """Obtém ativos ativos"""
        assets = await self.get_all()
        return [asset for asset in assets if asset.is_active()]
    
    async def get_tradeable_assets(self) -> List[Asset]:
        """Obtém ativos que podem ser negociados"""
        assets = await self.get_all()
        return [asset for asset in assets if asset.can_trade()]
    
    async def search_by_criteria(self, criteria: Dict[str, Any]) -> List[Asset]:
        """Busca ativos por critérios"""
        assets = await self.get_all()
        filtered_assets = []
        
        for asset in assets:
            match = True
            
            # Filtra por status
            if 'status' in criteria:
                if asset.status != criteria['status']:
                    match = False
            
            # Filtra por base currency
            if 'base_currency' in criteria:
                if asset.base_currency.upper() != criteria['base_currency'].upper():
                    match = False
            
            # Filtra por quote currency
            if 'quote_currency' in criteria:
                if asset.quote_currency.upper() != criteria['quote_currency'].upper():
                    match = False
            
            # Filtra por contract type
            if 'contract_type' in criteria:
                if asset.contract_type != criteria['contract_type']:
                    match = False
            
            # Filtra por min quantity
            if 'min_qty' in criteria:
                if asset.min_qty < criteria['min_qty']:
                    match = False
            
            # Filtra por max quantity
            if 'max_qty' in criteria:
                if asset.max_qty > criteria['max_qty']:
                    match = False
            
            # Filtra por símbolo (partial match)
            if 'symbol_pattern' in criteria:
                pattern = criteria['symbol_pattern'].upper()
                if pattern not in asset.symbol.upper():
                    match = False
            
            if match:
                filtered_assets.append(asset)
        
        return filtered_assets
    
    async def get_assets_by_volume(self, min_volume: float = 1000000) -> List[Asset]:
        """Obtém ativos com volume mínimo"""
        # Esta implementação seria melhorada com dados de volume em tempo real
        # Por enquanto, retorna todos os ativos ativos
        return await self.get_active_assets()
    
    async def get_popular_assets(self, limit: int = 20) -> List[Asset]:
        """Obtém ativos mais populares"""
        assets = await self.get_active_assets()
        
        # Ordena por símbolo (simulação de popularidade)
        # Em implementação real, seria baseado em volume, trades, etc.
        assets.sort(key=lambda x: x.symbol)
        
        return assets[:limit]
    
    async def update_asset_status(self, symbol: str, status: AssetStatus) -> bool:
        """Atualiza status do ativo"""
        asset = await self.get_by_symbol(symbol)
        if asset:
            asset.status = status
            asset.updated_at = datetime.now()
            await self.save(asset)
            return True
        return False
    
    async def bulk_update_assets(self, updates: List[Dict[str, Any]]) -> int:
        """Atualiza múltiplos ativos em lote"""
        updated_count = 0
        
        for update in updates:
            symbol = update.get('symbol')
            if symbol:
                asset = await self.get_by_symbol(symbol)
                if asset:
                    # Atualiza campos especificados
                    for key, value in update.items():
                        if key != 'symbol' and hasattr(asset, key):
                            setattr(asset, key, value)
                    
                    asset.updated_at = datetime.now()
                    await self.save(asset)
                    updated_count += 1
        
        return updated_count
    
    async def get_assets_by_leverage(self, min_leverage: int = 1, max_leverage: int = 100) -> List[Asset]:
        """Obtém ativos por range de leverage"""
        # Esta implementação seria melhorada com dados de leverage em tempo real
        # Por enquanto, retorna todos os ativos ativos
        return await self.get_active_assets()
    
    async def get_assets_by_funding_rate(self, min_funding: float = -0.01, max_funding: float = 0.01) -> List[Asset]:
        """Obtém ativos por range de funding rate"""
        # Esta implementação seria melhorada com dados de funding em tempo real
        # Por enquanto, retorna todos os ativos ativos
        return await self.get_active_assets()
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtém estatísticas dos ativos"""
        assets = await self.get_all()
        
        if not assets:
            return {
                'total_assets': 0,
                'active_assets': 0,
                'inactive_assets': 0,
                'tradeable_assets': 0,
                'status_distribution': {},
                'currency_distribution': {}
            }
        
        active_count = len([a for a in assets if a.is_active()])
        tradeable_count = len([a for a in assets if a.can_trade()])
        
        # Distribuição por status
        status_dist = {}
        for asset in assets:
            status = asset.status.value
            status_dist[status] = status_dist.get(status, 0) + 1
        
        # Distribuição por moeda base
        currency_dist = {}
        for asset in assets:
            currency = asset.base_currency
            currency_dist[currency] = currency_dist.get(currency, 0) + 1
        
        return {
            'total_assets': len(assets),
            'active_assets': active_count,
            'inactive_assets': len(assets) - active_count,
            'tradeable_assets': tradeable_count,
            'status_distribution': status_dist,
            'currency_distribution': currency_dist
        }
