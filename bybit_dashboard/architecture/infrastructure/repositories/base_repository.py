#!/usr/bin/env python3
"""
🗄️ BASE REPOSITORY NEØ - REPOSITÓRIO BASE
Implementação base para todos os repositórios
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, TypeVar, Generic
from datetime import datetime
from pathlib import Path
import aiofiles

from ...core.interfaces import IRepository
from ...core.entities import Asset, Order, Trade, Position, Strategy

T = TypeVar('T')

class BaseRepository(IRepository, Generic[T]):
    """
    Repositório base com implementação genérica
    """
    
    def __init__(self, data_file: str, entity_class: type):
        self.data_file = Path(data_file)
        self.entity_class = entity_class
        self._cache: Dict[str, T] = {}
        self._lock = asyncio.Lock()
    
    async def _load_data(self) -> Dict[str, Dict]:
        """Carrega dados do arquivo"""
        if not self.data_file.exists():
            return {}
        
        async with aiofiles.open(self.data_file, 'r') as f:
            content = await f.read()
            if content.strip():
                return json.loads(content)
            return {}
    
    async def _save_data(self, data: Dict[str, Dict]) -> None:
        """Salva dados no arquivo"""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(self.data_file, 'w') as f:
            await f.write(json.dumps(data, indent=2, default=str))
    
    def _entity_to_dict(self, entity: T) -> Dict[str, Any]:
        """Converte entidade para dicionário"""
        if hasattr(entity, '__dict__'):
            return entity.__dict__.copy()
        return {}
    
    def _dict_to_entity(self, data: Dict[str, Any]) -> T:
        """Converte dicionário para entidade"""
        try:
            return self.entity_class(**data)
        except Exception as e:
            raise ValueError(f"Error converting dict to {self.entity_class.__name__}: {e}")
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """Obtém entidade por ID"""
        async with self._lock:
            # Verifica cache primeiro
            if id in self._cache:
                return self._cache[id]
            
            # Carrega do arquivo
            data = await self._load_data()
            if id in data:
                entity = self._dict_to_entity(data[id])
                self._cache[id] = entity
                return entity
            
            return None
    
    async def get_all(self) -> List[T]:
        """Obtém todas as entidades"""
        async with self._lock:
            data = await self._load_data()
            entities = []
            
            for entity_data in data.values():
                try:
                    entity = self._dict_to_entity(entity_data)
                    entities.append(entity)
                except Exception as e:
                    print(f"Error loading entity: {e}")
                    continue
            
            return entities
    
    async def save(self, entity: T) -> T:
        """Salva entidade"""
        async with self._lock:
            # Converte para dicionário
            entity_dict = self._entity_to_dict(entity)
            
            # Carrega dados existentes
            data = await self._load_data()
            
            # Atualiza timestamp
            entity_dict['updated_at'] = datetime.now().isoformat()
            
            # Salva no dicionário
            data[entity.id] = entity_dict
            
            # Salva no arquivo
            await self._save_data(data)
            
            # Atualiza cache
            self._cache[entity.id] = entity
            
            return entity
    
    async def delete(self, id: str) -> bool:
        """Remove entidade por ID"""
        async with self._lock:
            # Carrega dados existentes
            data = await self._load_data()
            
            if id in data:
                # Remove do dicionário
                del data[id]
                
                # Salva no arquivo
                await self._save_data(data)
                
                # Remove do cache
                if id in self._cache:
                    del self._cache[id]
                
                return True
            
            return False
    
    async def exists(self, id: str) -> bool:
        """Verifica se entidade existe"""
        async with self._lock:
            # Verifica cache primeiro
            if id in self._cache:
                return True
            
            # Verifica arquivo
            data = await self._load_data()
            return id in data
    
    async def count(self) -> int:
        """Conta número de entidades"""
        async with self._lock:
            data = await self._load_data()
            return len(data)
    
    async def clear_cache(self) -> None:
        """Limpa cache"""
        async with self._lock:
            self._cache.clear()
    
    async def reload_cache(self) -> None:
        """Recarrega cache do arquivo"""
        async with self._lock:
            self._cache.clear()
            data = await self._load_data()
            
            for entity_data in data.values():
                try:
                    entity = self._dict_to_entity(entity_data)
                    self._cache[entity.id] = entity
                except Exception as e:
                    print(f"Error loading entity to cache: {e}")
                    continue
