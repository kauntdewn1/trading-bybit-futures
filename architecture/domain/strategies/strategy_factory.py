#!/usr/bin/env python3
"""
🏭 STRATEGY FACTORY NEØ - FACTORY DE ESTRATÉGIAS
Factory para criação de estratégias usando padrão Factory
"""

from typing import Dict, List, Optional, Any, Type
from datetime import datetime

from ...core.interfaces import IStrategyFactory, IStrategy
from .base_strategy import BaseStrategy, StrategyParameters
from .sniper_strategy import SniperStrategy
from .scalping_strategy import ScalpingStrategy
from .swing_strategy import SwingStrategy

class StrategyFactory(IStrategyFactory):
    """
    Factory para criação de estratégias de trading
    """
    
    def __init__(self):
        self._strategies: Dict[str, Type[BaseStrategy]] = {
            'sniper': SniperStrategy,
            'scalping': ScalpingStrategy,
            'swing': SwingStrategy
        }
        self._instances: Dict[str, BaseStrategy] = {}
    
    def create_strategy(self, strategy_type: str, parameters: Optional[Dict[str, Any]] = None) -> IStrategy:
        """
        Cria estratégia baseada no tipo
        
        Args:
            strategy_type: Tipo da estratégia ('sniper', 'scalping', 'swing')
            parameters: Parâmetros da estratégia
            
        Returns:
            IStrategy: Instância da estratégia
        """
        if strategy_type not in self._strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        # Converte parâmetros para StrategyParameters se necessário
        strategy_params = None
        if parameters:
            strategy_params = StrategyParameters(**parameters)
        
        # Cria instância da estratégia
        strategy_class = self._strategies[strategy_type]
        instance = strategy_class(strategy_params)
        
        # Armazena instância para reutilização
        instance_key = f"{strategy_type}_{id(instance)}"
        self._instances[instance_key] = instance
        
        return instance
    
    def get_available_strategies(self) -> List[str]:
        """Retorna estratégias disponíveis"""
        return list(self._strategies.keys())
    
    def register_strategy(self, name: str, strategy_class: Type[BaseStrategy]) -> None:
        """
        Registra nova estratégia
        
        Args:
            name: Nome da estratégia
            strategy_class: Classe da estratégia
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError("Strategy class must inherit from BaseStrategy")
        
        self._strategies[name] = strategy_class
    
    def unregister_strategy(self, name: str) -> bool:
        """
        Remove estratégia registrada
        
        Args:
            name: Nome da estratégia
            
        Returns:
            bool: True se removida com sucesso
        """
        if name in self._strategies:
            del self._strategies[name]
            return True
        return False
    
    def get_strategy_info(self, strategy_type: str) -> Dict[str, Any]:
        """
        Obtém informações da estratégia
        
        Args:
            strategy_type: Tipo da estratégia
            
        Returns:
            Dict: Informações da estratégia
        """
        if strategy_type not in self._strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        strategy_class = self._strategies[strategy_type]
        
        # Cria instância temporária para obter informações
        temp_instance = strategy_class()
        
        return {
            'name': temp_instance.get_name(),
            'version': temp_instance.get_version(),
            'description': getattr(temp_instance, 'get_strategy_description', lambda: '')(),
            'parameters': temp_instance.get_parameters(),
            'class_name': strategy_class.__name__
        }
    
    def create_strategy_with_config(self, config: Dict[str, Any]) -> IStrategy:
        """
        Cria estratégia com configuração completa
        
        Args:
            config: Configuração da estratégia
                {
                    'type': 'sniper',
                    'parameters': {...},
                    'name': 'My Sniper',
                    'version': '1.0.0'
                }
        
        Returns:
            IStrategy: Instância da estratégia
        """
        strategy_type = config.get('type')
        if not strategy_type:
            raise ValueError("Strategy type is required")
        
        parameters = config.get('parameters', {})
        strategy = self.create_strategy(strategy_type, parameters)
        
        # Aplica configurações adicionais se disponíveis
        if 'name' in config:
            strategy.name = config['name']
        
        if 'version' in config:
            strategy.version = config['version']
        
        return strategy
    
    def create_multiple_strategies(self, configs: List[Dict[str, Any]]) -> List[IStrategy]:
        """
        Cria múltiplas estratégias
        
        Args:
            configs: Lista de configurações
            
        Returns:
            List[IStrategy]: Lista de estratégias
        """
        strategies = []
        
        for config in configs:
            try:
                strategy = self.create_strategy_with_config(config)
                strategies.append(strategy)
            except Exception as e:
                print(f"Error creating strategy with config {config}: {e}")
                continue
        
        return strategies
    
    def get_strategy_comparison(self) -> Dict[str, Any]:
        """
        Retorna comparação entre estratégias disponíveis
        
        Returns:
            Dict: Comparação das estratégias
        """
        comparison = {}
        
        for strategy_type in self._strategies:
            try:
                info = self.get_strategy_info(strategy_type)
                comparison[strategy_type] = {
                    'name': info['name'],
                    'version': info['version'],
                    'description': info['description'],
                    'parameters': info['parameters']
                }
            except Exception as e:
                comparison[strategy_type] = {'error': str(e)}
        
        return comparison
    
    def validate_strategy_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Valida configuração da estratégia
        
        Args:
            config: Configuração a ser validada
            
        Returns:
            List[str]: Lista de erros encontrados
        """
        errors = []
        
        # Valida tipo
        if 'type' not in config:
            errors.append("Strategy type is required")
        elif config['type'] not in self._strategies:
            errors.append(f"Unknown strategy type: {config['type']}")
        
        # Valida parâmetros
        if 'parameters' in config:
            parameters = config['parameters']
            
            # Valida parâmetros específicos
            if 'rsi_oversold' in parameters:
                if not 0 <= parameters['rsi_oversold'] <= 50:
                    errors.append("RSI oversold must be between 0 and 50")
            
            if 'rsi_overbought' in parameters:
                if not 50 <= parameters['rsi_overbought'] <= 100:
                    errors.append("RSI overbought must be between 50 and 100")
            
            if 'min_score' in parameters:
                if not 0 <= parameters['min_score'] <= 10:
                    errors.append("Min score must be between 0 and 10")
            
            if 'max_leverage' in parameters:
                if not 1 <= parameters['max_leverage'] <= 100:
                    errors.append("Max leverage must be between 1 and 100")
        
        return errors
    
    def get_recommended_config(self, strategy_type: str, risk_level: str = 'medium') -> Dict[str, Any]:
        """
        Retorna configuração recomendada para estratégia
        
        Args:
            strategy_type: Tipo da estratégia
            risk_level: Nível de risco ('low', 'medium', 'high')
            
        Returns:
            Dict: Configuração recomendada
        """
        if strategy_type not in self._strategies:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        # Configurações baseadas no nível de risco
        risk_configs = {
            'low': {
                'rsi_oversold': 20,
                'rsi_overbought': 80,
                'min_score': 8.5,
                'max_leverage': 3,
                'stop_loss_pct': 1.0,
                'take_profit_pct': 2.0
            },
            'medium': {
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'min_score': 7.0,
                'max_leverage': 5,
                'stop_loss_pct': 2.0,
                'take_profit_pct': 4.0
            },
            'high': {
                'rsi_oversold': 35,
                'rsi_overbought': 65,
                'min_score': 6.0,
                'max_leverage': 10,
                'stop_loss_pct': 3.0,
                'take_profit_pct': 6.0
            }
        }
        
        if risk_level not in risk_configs:
            risk_level = 'medium'
        
        return {
            'type': strategy_type,
            'parameters': risk_configs[risk_level],
            'risk_level': risk_level,
            'created_at': datetime.now().isoformat()
        }
    
    def get_factory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da factory"""
        return {
            'registered_strategies': len(self._strategies),
            'available_strategies': list(self._strategies.keys()),
            'active_instances': len(self._instances),
            'factory_created_at': datetime.now().isoformat()
        }
