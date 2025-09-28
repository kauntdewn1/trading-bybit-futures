#!/usr/bin/env python3
"""
🏭 SERVICE FACTORY NEØ - FACTORY DE SERVIÇOS
Factory para criação de serviços usando padrão Factory
"""

from typing import Dict, List, Optional, Any, Type, TypeVar
from abc import ABC, abstractmethod
from datetime import datetime

from ...core.interfaces import IMarketDataService, IAnalysisService, ITradingService
from ...core.entities import Asset, Order, Trade, Position

T = TypeVar('T')

class ServiceFactory(ABC):
    """
    Factory base para criação de serviços
    """
    
    def __init__(self):
        self._services: Dict[str, Type] = {}
        self._instances: Dict[str, Any] = {}
        self._configurations: Dict[str, Dict[str, Any]] = {}
    
    @abstractmethod
    def create_service(self, service_type: str, config: Optional[Dict[str, Any]] = None) -> Any:
        """Cria serviço baseado no tipo"""
        pass
    
    def register_service(self, name: str, service_class: Type[T]) -> None:
        """Registra serviço na factory"""
        self._services[name] = service_class
    
    def unregister_service(self, name: str) -> bool:
        """Remove serviço da factory"""
        if name in self._services:
            del self._services[name]
            return True
        return False
    
    def get_available_services(self) -> List[str]:
        """Retorna serviços disponíveis"""
        return list(self._services.keys())
    
    def get_service_info(self, service_type: str) -> Dict[str, Any]:
        """Obtém informações do serviço"""
        if service_type not in self._services:
            raise ValueError(f"Unknown service type: {service_type}")
        
        service_class = self._services[service_type]
        return {
            'name': service_class.__name__,
            'module': service_class.__module__,
            'doc': service_class.__doc__,
            'bases': [base.__name__ for base in service_class.__bases__]
        }

class MarketDataServiceFactory(ServiceFactory):
    """
    Factory para serviços de dados de mercado
    """
    
    def __init__(self):
        super().__init__()
        self._register_default_services()
    
    def _register_default_services(self):
        """Registra serviços padrão"""
        # Em implementação real, registraria serviços como:
        # self.register_service('bybit', BybitMarketDataService)
        # self.register_service('binance', BinanceMarketDataService)
        pass
    
    def create_service(self, service_type: str, config: Optional[Dict[str, Any]] = None) -> IMarketDataService:
        """Cria serviço de dados de mercado"""
        if service_type not in self._services:
            raise ValueError(f"Unknown market data service type: {service_type}")
        
        service_class = self._services[service_type]
        config = config or {}
        
        # Cria instância do serviço
        instance = service_class(**config)
        
        # Armazena configuração
        self._configurations[service_type] = config
        
        return instance
    
    def create_bybit_service(self, api_key: str, api_secret: str, testnet: bool = True) -> IMarketDataService:
        """Cria serviço Bybit específico"""
        config = {
            'api_key': api_key,
            'api_secret': api_secret,
            'testnet': testnet
        }
        return self.create_service('bybit', config)
    
    def create_binance_service(self, api_key: str, api_secret: str, testnet: bool = True) -> IMarketDataService:
        """Cria serviço Binance específico"""
        config = {
            'api_key': api_key,
            'api_secret': api_secret,
            'testnet': testnet
        }
        return self.create_service('binance', config)

class AnalysisServiceFactory(ServiceFactory):
    """
    Factory para serviços de análise
    """
    
    def __init__(self):
        super().__init__()
        self._register_default_services()
    
    def _register_default_services(self):
        """Registra serviços padrão"""
        # Em implementação real, registraria serviços como:
        # self.register_service('technical', TechnicalAnalysisService)
        # self.register_service('fundamental', FundamentalAnalysisService)
        pass
    
    def create_service(self, service_type: str, config: Optional[Dict[str, Any]] = None) -> IAnalysisService:
        """Cria serviço de análise"""
        if service_type not in self._services:
            raise ValueError(f"Unknown analysis service type: {service_type}")
        
        service_class = self._services[service_type]
        config = config or {}
        
        # Cria instância do serviço
        instance = service_class(**config)
        
        # Armazena configuração
        self._configurations[service_type] = config
        
        return instance
    
    def create_technical_analysis_service(self, indicators: List[str] = None) -> IAnalysisService:
        """Cria serviço de análise técnica"""
        config = {
            'indicators': indicators or ['rsi', 'macd', 'ema', 'sma', 'bollinger']
        }
        return self.create_service('technical', config)
    
    def create_fundamental_analysis_service(self, data_sources: List[str] = None) -> IAnalysisService:
        """Cria serviço de análise fundamental"""
        config = {
            'data_sources': data_sources or ['funding_rate', 'open_interest', 'volume']
        }
        return self.create_service('fundamental', config)

class TradingServiceFactory(ServiceFactory):
    """
    Factory para serviços de trading
    """
    
    def __init__(self):
        super().__init__()
        self._register_default_services()
    
    def _register_default_services(self):
        """Registra serviços padrão"""
        # Em implementação real, registraria serviços como:
        # self.register_service('bybit', BybitTradingService)
        # self.register_service('binance', BinanceTradingService)
        pass
    
    def create_service(self, service_type: str, config: Optional[Dict[str, Any]] = None) -> ITradingService:
        """Cria serviço de trading"""
        if service_type not in self._services:
            raise ValueError(f"Unknown trading service type: {service_type}")
        
        service_class = self._services[service_type]
        config = config or {}
        
        # Cria instância do serviço
        instance = service_class(**config)
        
        # Armazena configuração
        self._configurations[service_type] = config
        
        return instance
    
    def create_bybit_trading_service(self, api_key: str, api_secret: str, testnet: bool = True) -> ITradingService:
        """Cria serviço de trading Bybit"""
        config = {
            'api_key': api_key,
            'api_secret': api_secret,
            'testnet': testnet
        }
        return self.create_service('bybit', config)
    
    def create_binance_trading_service(self, api_key: str, api_secret: str, testnet: bool = True) -> ITradingService:
        """Cria serviço de trading Binance"""
        config = {
            'api_key': api_key,
            'api_secret': api_secret,
            'testnet': testnet
        }
        return self.create_service('binance', config)

class CompositeServiceFactory:
    """
    Factory composta para criação de múltiplos serviços
    """
    
    def __init__(self):
        self.market_data_factory = MarketDataServiceFactory()
        self.analysis_factory = AnalysisServiceFactory()
        self.trading_factory = TradingServiceFactory()
    
    def create_trading_system(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cria sistema completo de trading
        
        Args:
            config: Configuração do sistema
                {
                    'market_data': {
                        'type': 'bybit',
                        'api_key': '...',
                        'api_secret': '...',
                        'testnet': True
                    },
                    'analysis': {
                        'type': 'technical',
                        'indicators': ['rsi', 'macd']
                    },
                    'trading': {
                        'type': 'bybit',
                        'api_key': '...',
                        'api_secret': '...',
                        'testnet': True
                    }
                }
        
        Returns:
            Dict[str, Any]: Serviços criados
        """
        services = {}
        
        # Cria serviço de dados de mercado
        if 'market_data' in config:
            market_config = config['market_data']
            services['market_data'] = self.market_data_factory.create_service(
                market_config['type'],
                market_config
            )
        
        # Cria serviço de análise
        if 'analysis' in config:
            analysis_config = config['analysis']
            services['analysis'] = self.analysis_factory.create_service(
                analysis_config['type'],
                analysis_config
            )
        
        # Cria serviço de trading
        if 'trading' in config:
            trading_config = config['trading']
            services['trading'] = self.trading_factory.create_service(
                trading_config['type'],
                trading_config
            )
        
        return services
    
    def create_minimal_system(self, api_key: str, api_secret: str, testnet: bool = True) -> Dict[str, Any]:
        """
        Cria sistema mínimo de trading
        
        Args:
            api_key: Chave da API
            api_secret: Segredo da API
            testnet: Se usar testnet
            
        Returns:
            Dict[str, Any]: Serviços criados
        """
        config = {
            'market_data': {
                'type': 'bybit',
                'api_key': api_key,
                'api_secret': api_secret,
                'testnet': testnet
            },
            'analysis': {
                'type': 'technical',
                'indicators': ['rsi', 'macd', 'ema']
            },
            'trading': {
                'type': 'bybit',
                'api_key': api_key,
                'api_secret': api_secret,
                'testnet': testnet
            }
        }
        
        return self.create_trading_system(config)
    
    def get_factory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das factories"""
        return {
            'market_data_services': len(self.market_data_factory.get_available_services()),
            'analysis_services': len(self.analysis_factory.get_available_services()),
            'trading_services': len(self.trading_factory.get_available_services()),
            'total_services': (
                len(self.market_data_factory.get_available_services()) +
                len(self.analysis_factory.get_available_services()) +
                len(self.trading_factory.get_available_services())
            )
        }
