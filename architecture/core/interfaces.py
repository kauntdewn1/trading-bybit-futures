#!/usr/bin/env python3
"""
🔌 INTERFACES NEØ - CONTRATOS DO SISTEMA
Interfaces que definem contratos entre camadas
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Protocol
from dataclasses import dataclass
from datetime import datetime

# =============================================================================
# INTERFACES DE REPOSITÓRIO
# =============================================================================

class IRepository(ABC):
    """Interface base para repositórios"""
    
    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[Any]:
        """Obtém entidade por ID"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Any]:
        """Obtém todas as entidades"""
        pass
    
    @abstractmethod
    async def save(self, entity: Any) -> Any:
        """Salva entidade"""
        pass
    
    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Remove entidade por ID"""
        pass

class IAssetRepository(IRepository):
    """Interface para repositório de ativos"""
    
    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> Optional[Any]:
        """Obtém ativo por símbolo"""
        pass
    
    @abstractmethod
    async def get_active_assets(self) -> List[Any]:
        """Obtém ativos ativos"""
        pass
    
    @abstractmethod
    async def search_by_criteria(self, criteria: Dict[str, Any]) -> List[Any]:
        """Busca ativos por critérios"""
        pass

class ITradeRepository(IRepository):
    """Interface para repositório de trades"""
    
    @abstractmethod
    async def get_by_symbol(self, symbol: str) -> List[Any]:
        """Obtém trades por símbolo"""
        pass
    
    @abstractmethod
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Any]:
        """Obtém trades por período"""
        pass
    
    @abstractmethod
    async def get_pending_trades(self) -> List[Any]:
        """Obtém trades pendentes"""
        pass

# =============================================================================
# INTERFACES DE SERVIÇO
# =============================================================================

class IMarketDataService(ABC):
    """Interface para serviço de dados de mercado"""
    
    @abstractmethod
    async def get_price(self, symbol: str) -> Optional[float]:
        """Obtém preço atual"""
        pass
    
    @abstractmethod
    async def get_klines(self, symbol: str, interval: str, limit: int) -> Optional[List[Dict]]:
        """Obtém dados de klines"""
        pass
    
    @abstractmethod
    async def get_funding_rate(self, symbol: str) -> Optional[float]:
        """Obtém taxa de funding"""
        pass
    
    @abstractmethod
    async def get_volume(self, symbol: str) -> Optional[float]:
        """Obtém volume 24h"""
        pass

class IAnalysisService(ABC):
    """Interface para serviço de análise"""
    
    @abstractmethod
    async def analyze_asset(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Analisa um ativo"""
        pass
    
    @abstractmethod
    async def analyze_multiple_assets(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Analisa múltiplos ativos"""
        pass
    
    @abstractmethod
    async def calculate_indicators(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula indicadores técnicos"""
        pass

class ITradingService(ABC):
    """Interface para serviço de trading"""
    
    @abstractmethod
    async def create_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Cria ordem de trading"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancela ordem"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status da ordem"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> List[Dict[str, Any]]:
        """Obtém posições abertas"""
        pass

# =============================================================================
# INTERFACES DE ESTRATÉGIA
# =============================================================================

class IStrategy(ABC):
    """Interface base para estratégias de trading"""
    
    @abstractmethod
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa dados e retorna sinal"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Retorna nome da estratégia"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Retorna versão da estratégia"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> Dict[str, Any]:
        """Retorna parâmetros da estratégia"""
        pass

class IStrategyFactory(ABC):
    """Interface para factory de estratégias"""
    
    @abstractmethod
    def create_strategy(self, strategy_type: str, parameters: Dict[str, Any]) -> IStrategy:
        """Cria estratégia baseada no tipo"""
        pass
    
    @abstractmethod
    def get_available_strategies(self) -> List[str]:
        """Retorna estratégias disponíveis"""
        pass

# =============================================================================
# INTERFACES DE CACHE
# =============================================================================

class ICache(ABC):
    """Interface para sistema de cache"""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Define valor no cache"""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Limpa todo o cache"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cache"""
        pass

# =============================================================================
# INTERFACES DE VALIDAÇÃO
# =============================================================================

class IValidator(ABC):
    """Interface para validadores"""
    
    @abstractmethod
    async def validate(self, data: Any) -> bool:
        """Valida dados"""
        pass
    
    @abstractmethod
    def get_errors(self) -> List[str]:
        """Retorna erros de validação"""
        pass

class IValidationRule(ABC):
    """Interface para regras de validação"""
    
    @abstractmethod
    def validate(self, value: Any) -> bool:
        """Valida um valor"""
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """Retorna mensagem de erro"""
        pass

# =============================================================================
# INTERFACES DE EVENTOS
# =============================================================================

class IEvent(ABC):
    """Interface para eventos"""
    
    @abstractmethod
    def get_event_type(self) -> str:
        """Retorna tipo do evento"""
        pass
    
    @abstractmethod
    def get_timestamp(self) -> datetime:
        """Retorna timestamp do evento"""
        pass
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """Retorna dados do evento"""
        pass

class IEventHandler(ABC):
    """Interface para handlers de eventos"""
    
    @abstractmethod
    async def handle(self, event: IEvent) -> None:
        """Processa evento"""
        pass
    
    @abstractmethod
    def can_handle(self, event_type: str) -> bool:
        """Verifica se pode processar o evento"""
        pass

class IEventBus(ABC):
    """Interface para barramento de eventos"""
    
    @abstractmethod
    async def publish(self, event: IEvent) -> None:
        """Publica evento"""
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: IEventHandler) -> None:
        """Inscreve handler para evento"""
        pass
    
    @abstractmethod
    def unsubscribe(self, event_type: str, handler: IEventHandler) -> None:
        """Remove inscrição de handler"""
        pass

# =============================================================================
# INTERFACES DE LOGGING
# =============================================================================

class ILogger(ABC):
    """Interface para sistema de logging"""
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log de debug"""
        pass
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log de informação"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log de aviso"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log de erro"""
        pass
    
    @abstractmethod
    def critical(self, message: str, **kwargs) -> None:
        """Log crítico"""
        pass

# =============================================================================
# INTERFACES DE CONFIGURAÇÃO
# =============================================================================

class IConfiguration(ABC):
    """Interface para sistema de configuração"""
    
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém valor de configuração"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Define valor de configuração"""
        pass
    
    @abstractmethod
    def has(self, key: str) -> bool:
        """Verifica se chave existe"""
        pass
    
    @abstractmethod
    def get_section(self, section: str) -> Dict[str, Any]:
        """Obtém seção de configuração"""
        pass

# =============================================================================
# INTERFACES DE MONITORAMENTO
# =============================================================================

class IMetricsCollector(ABC):
    """Interface para coletor de métricas"""
    
    @abstractmethod
    def increment_counter(self, name: str, value: float = 1.0, tags: Dict[str, str] = None) -> None:
        """Incrementa contador"""
        pass
    
    @abstractmethod
    def record_gauge(self, name: str, value: float, tags: Dict[str, str] = None) -> None:
        """Registra gauge"""
        pass
    
    @abstractmethod
    def record_timing(self, name: str, duration: float, tags: Dict[str, str] = None) -> None:
        """Registra timing"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Obtém métricas coletadas"""
        pass

# =============================================================================
# INTERFACES DE SEGURANÇA
# =============================================================================

class ISecurityValidator(ABC):
    """Interface para validador de segurança"""
    
    @abstractmethod
    async def validate_environment(self) -> None:
        """Valida ambiente de execução"""
        pass
    
    @abstractmethod
    async def validate_api_permissions(self) -> None:
        """Valida permissões da API"""
        pass
    
    @abstractmethod
    async def validate_trade(self, trade_data: Dict[str, Any]) -> bool:
        """Valida dados de trade"""
        pass
    
    @abstractmethod
    async def validate_position_size(self, symbol: str, size: float) -> bool:
        """Valida tamanho da posição"""
        pass

# =============================================================================
# INTERFACES DE NOTIFICAÇÃO
# =============================================================================

class INotificationService(ABC):
    """Interface para serviço de notificações"""
    
    @abstractmethod
    async def send_notification(self, message: str, channel: str = "default") -> bool:
        """Envia notificação"""
        pass
    
    @abstractmethod
    async def send_trade_alert(self, trade_data: Dict[str, Any]) -> bool:
        """Envia alerta de trade"""
        pass
    
    @abstractmethod
    async def send_error_alert(self, error: Exception, context: Dict[str, Any]) -> bool:
        """Envia alerta de erro"""
        pass

# =============================================================================
# INTERFACES DE PERSISTÊNCIA
# =============================================================================

class IUnitOfWork(ABC):
    """Interface para unidade de trabalho"""
    
    @abstractmethod
    async def begin(self) -> None:
        """Inicia transação"""
        pass
    
    @abstractmethod
    async def commit(self) -> None:
        """Confirma transação"""
        pass
    
    @abstractmethod
    async def rollback(self) -> None:
        """Desfaz transação"""
        pass
    
    @abstractmethod
    async def __aenter__(self):
        """Context manager entry"""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        pass

# =============================================================================
# INTERFACES DE DEPENDÊNCIA
# =============================================================================

class IDependencyContainer(ABC):
    """Interface para container de dependências"""
    
    @abstractmethod
    def register_singleton(self, interface: type, implementation: type) -> None:
        """Registra implementação como singleton"""
        pass
    
    @abstractmethod
    def register_transient(self, interface: type, implementation: type) -> None:
        """Registra implementação como transient"""
        pass
    
    @abstractmethod
    def register_instance(self, interface: type, instance: Any) -> None:
        """Registra instância específica"""
        pass
    
    @abstractmethod
    def resolve(self, interface: type) -> Any:
        """Resolve dependência"""
        pass
    
    @abstractmethod
    def is_registered(self, interface: type) -> bool:
        """Verifica se interface está registrada"""
        pass
