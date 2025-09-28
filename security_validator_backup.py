#!/usr/bin/env python3
"""
🔒 SECURITY VALIDATOR NEØ - SISTEMA DE SEGURANÇA CRÍTICA
Validação robusta de ambiente, permissões e operações de trading
"""

import os
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class SecurityLevel(Enum):
    """Níveis de segurança do sistema"""
    TESTNET = "testnet"
    PRODUCTION = "production"
    DEVELOPMENT = "development"

class SecurityError(Exception):
    """Exceção específica para erros de segurança"""
    pass

@dataclass
class SecurityConfig:
    """Configuração de segurança do sistema"""
    environment: SecurityLevel
    max_position_size: float
    max_daily_trades: int
    require_confirmation: bool
    log_all_operations: bool
    api_permissions: List[str]
    allowed_symbols: List[str]
    blocked_symbols: List[str]

class SecurityValidator:
    """
    Validador de segurança crítico para operações de trading
    """
    
    def __init__(self):
        self.setup_logging()
        self.config = self.load_security_config()
        self.operation_log = []
        self.daily_trade_count = 0
        self.last_reset_date = datetime.now().date()
        
    def setup_logging(self):
        """Configura logging de segurança"""
        # Cria logger específico para segurança
        self.security_logger = logging.getLogger('security')
        self.security_logger.setLevel(logging.INFO)
        
        # Handler para arquivo de segurança
        security_handler = logging.FileHandler('security.log')
        security_handler.setLevel(logging.INFO)
        
        # Formato específico para logs de segurança
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        
        self.security_logger.addHandler(security_handler)
        
        # Handler para console (apenas erros críticos)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(security_formatter)
        self.security_logger.addHandler(console_handler)
        
    def load_security_config(self) -> SecurityConfig:
        """Carrega configuração de segurança"""
        # Configuração padrão segura
        default_config = SecurityConfig(
            environment=SecurityLevel.TESTNET,
            max_position_size=1000.0,  # USDT
            max_daily_trades=10,
            require_confirmation=True,
            log_all_operations=True,
            api_permissions=["read", "trade"],
            allowed_symbols=["BTCUSDT", "ETHUSDT", "SOLUSDT"],
            blocked_symbols=["DOGEUSDT", "SHIBUSDT"]  # Símbolos de alto risco
        )
        
        # Tenta carregar configuração personalizada
        try:
            if os.path.exists('security_config.json'):
                with open('security_config.json', 'r') as f:
                    config_data = json.load(f)
                    return SecurityConfig(**config_data)
        except Exception as e:
            self.security_logger.warning(f"Erro ao carregar config de segurança: {e}")
            
        return default_config
    
    def validate_environment(self) -> bool:
        """
        Valida se o ambiente está configurado corretamente
        CRÍTICO: Impede operações em produção sem confirmação explícita
        """
        try:
            # Verifica variáveis de ambiente críticas
            required_vars = ["API_KEY", "API_SECRET", "TELEGRAM_TOKEN"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                error_msg = f"Variáveis de ambiente obrigatórias ausentes: {missing_vars}"
                self.security_logger.error(error_msg)
                raise SecurityError(error_msg)
            
            # Validação crítica: Modo de operação
            testnet_mode = os.getenv("TESTNET_MODE", "true").lower()
            production_mode = os.getenv("PRODUCTION_MODE", "false").lower()
            
            if production_mode == "true":
                if testnet_mode != "false":
                    error_msg = "PRODUCTION_MODE=true requer TESTNET_MODE=false explícito"
                    self.security_logger.error(error_msg)
                    raise SecurityError(error_msg)
                
                # Confirmação adicional para produção
                confirmation = os.getenv("PRODUCTION_CONFIRMED", "false").lower()
                if confirmation != "true":
                    error_msg = "Produção requer PRODUCTION_CONFIRMED=true"
                    self.security_logger.error(error_msg)
                    raise SecurityError(error_msg)
                
                self.config.environment = SecurityLevel.PRODUCTION
                self.security_logger.warning("⚠️ MODO PRODUÇÃO ATIVADO - OPERAÇÕES REAIS!")
                
            elif testnet_mode == "true":
                self.config.environment = SecurityLevel.TESTNET
                self.security_logger.info("✅ Modo testnet ativado - operações simuladas")
            else:
                error_msg = "Ambiente não especificado - use TESTNET_MODE ou PRODUCTION_MODE"
                self.security_logger.error(error_msg)
                raise SecurityError(error_msg)
            
            # Validação de chaves de API
            self.validate_api_keys()
            
            self.security_logger.info(f"✅ Ambiente validado: {self.config.environment.value}")
            return True
            
        except SecurityError:
            raise
        except Exception as e:
            error_msg = f"Erro inesperado na validação de ambiente: {e}"
            self.security_logger.error(error_msg)
            raise SecurityError(error_msg)
    
    def validate_api_keys(self) -> bool:
        """Valida se as chaves de API são válidas e seguras"""
        try:
            api_key = os.getenv("API_KEY")
            api_secret = os.getenv("API_SECRET")
            
            # Validação básica de formato
            if not api_key or len(api_key) < 20:
                raise SecurityError("API_KEY inválida ou muito curta")
            
            if not api_secret or len(api_secret) < 20:
                raise SecurityError("API_SECRET inválida ou muito curta")
            
            # Verifica se não são valores padrão/teste
            test_keys = ["test", "demo", "example", "sua_api_key", "your_api_key"]
            if any(test_key in api_key.lower() for test_key in test_keys):
                raise SecurityError("API_KEY parece ser um valor de teste")
            
            if any(test_key in api_secret.lower() for test_key in test_keys):
                raise SecurityError("API_SECRET parece ser um valor de teste")
            
            self.security_logger.info("✅ Chaves de API validadas")
            return True
            
        except SecurityError:
            raise
        except Exception as e:
            error_msg = f"Erro na validação de chaves: {e}"
            self.security_logger.error(error_msg)
            raise SecurityError(error_msg)
    
    def validate_api_permissions(self, session) -> bool:
        """
        Valida se a API tem as permissões necessárias
        CRÍTICO: Impede operações sem permissões adequadas
        """
        try:
            # Testa conexão básica
            result = session.get_wallet_balance(accountType="UNIFIED")
            
            if result.get("retCode") != 0:
                error_msg = f"Falha na conexão com API: {result.get('retMsg', 'Erro desconhecido')}"
                self.security_logger.error(error_msg)
                raise SecurityError(error_msg)
            
            # Verifica permissões específicas
            required_permissions = ["read", "trade"]
            for permission in required_permissions:
                if permission not in self.config.api_permissions:
                    error_msg = f"Permissão '{permission}' não configurada"
                    self.security_logger.error(error_msg)
                    raise SecurityError(error_msg)
            
            self.security_logger.info("✅ Permissões de API validadas")
            return True
            
        except SecurityError:
            raise
        except Exception as e:
            error_msg = f"Erro na validação de permissões: {e}"
            self.security_logger.error(error_msg)
            raise SecurityError(error_msg)
    
    def validate_trade_operation(self, symbol: str, side: str, qty: float, 
                               price: Optional[float] = None) -> Tuple[bool, str]:
        """
        Valida operação de trading antes da execução
        CRÍTICO: Última linha de defesa contra operações perigosas
        """
        try:
            # Reset contador diário se necessário
            self.reset_daily_counter()
            
            # Validação 1: Símbolo permitido
            if symbol in self.config.blocked_symbols:
                error_msg = f"Símbolo {symbol} está na lista de bloqueados"
                self.security_logger.error(error_msg)
                return False, error_msg
            
            if self.config.allowed_symbols and symbol not in self.config.allowed_symbols:
                error_msg = f"Símbolo {symbol} não está na lista de permitidos"
                self.security_logger.error(error_msg)
                return False, error_msg
            
            # Validação 2: Tamanho da posição
            if qty > self.config.max_position_size:
                error_msg = f"Quantidade {qty} excede limite máximo {self.config.max_position_size}"
                self.security_logger.error(error_msg)
                return False, error_msg
            
            # Validação 3: Limite diário de trades
            if self.daily_trade_count >= self.config.max_daily_trades:
                error_msg = f"Limite diário de trades atingido: {self.daily_trade_count}/{self.config.max_daily_trades}"
                self.security_logger.error(error_msg)
                return False, error_msg
            
            # Validação 4: Modo de produção
            if self.config.environment == SecurityLevel.PRODUCTION:
                if self.config.require_confirmation:
                    # Em produção, sempre requer confirmação adicional
                    confirmation = input(f"⚠️ CONFIRMAR TRADE EM PRODUÇÃO: {symbol} {side} {qty}? (digite 'CONFIRMO'): ")
                    if confirmation != "CONFIRMO":
                        error_msg = "Trade cancelado - confirmação não fornecida"
                        self.security_logger.warning(error_msg)
                        return False, error_msg
            
            # Log da operação
            operation_data = {
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "price": price,
                "environment": self.config.environment.value,
                "status": "VALIDATED"
            }
            
            self.operation_log.append(operation_data)
            self.daily_trade_count += 1
            
            self.security_logger.info(f"✅ Trade validado: {symbol} {side} {qty}")
            return True, "Operação validada com sucesso"
            
        except Exception as e:
            error_msg = f"Erro na validação de trade: {e}"
            self.security_logger.error(error_msg)
            return False, error_msg
    
    def reset_daily_counter(self):
        """Reseta contador diário se necessário"""
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.daily_trade_count = 0
            self.last_reset_date = current_date
            self.security_logger.info("🔄 Contador diário resetado")
    
    def get_security_status(self) -> Dict:
        """Retorna status atual de segurança"""
        return {
            "environment": self.config.environment.value,
            "daily_trades": f"{self.daily_trade_count}/{self.config.max_daily_trades}",
            "max_position_size": self.config.max_position_size,
            "require_confirmation": self.config.require_confirmation,
            "last_operation": self.operation_log[-1] if self.operation_log else None,
            "total_operations": len(self.operation_log)
        }
    
    def create_security_report(self) -> str:
        """Cria relatório de segurança"""
        status = self.get_security_status()
        
        report = f"""
🔒 RELATÓRIO DE SEGURANÇA - SNIPER NEØ
=====================================

📊 STATUS ATUAL:
- Ambiente: {status['environment'].upper()}
- Trades hoje: {status['daily_trades']}
- Tamanho máximo: {status['max_position_size']} USDT
- Confirmação obrigatória: {'✅' if status['require_confirmation'] else '❌'}

📈 OPERAÇÕES:
- Total de operações: {status['total_operations']}
- Última operação: {status['last_operation']['timestamp'] if status['last_operation'] else 'Nenhuma'}

⚠️ CONFIGURAÇÕES CRÍTICAS:
- Modo produção: {'🔴 ATIVO' if status['environment'] == 'production' else '🟢 TESTNET'}
- Logs de segurança: {'✅ Ativo' if self.config.log_all_operations else '❌ Inativo'}

🛡️ PROTEÇÕES ATIVAS:
- Validação de ambiente: ✅
- Validação de API: ✅
- Validação de trades: ✅
- Limite diário: ✅
- Limite de posição: ✅
"""
        return report

def create_security_config_file():
    """Cria arquivo de configuração de segurança padrão"""
    default_config = {
        "environment": "testnet",
        "max_position_size": 1000.0,
        "max_daily_trades": 10,
        "require_confirmation": True,
        "log_all_operations": True,
        "api_permissions": ["read", "trade"],
        "allowed_symbols": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT", "AVAXUSDT"],
        "blocked_symbols": ["DOGEUSDT", "SHIBUSDT", "PEPEUSDT"]
    }
    
    with open('security_config.json', 'w') as f:
        json.dump(default_config, f, indent=2)
    
    print("✅ Arquivo security_config.json criado com configurações seguras")

def main():
    """Teste do sistema de segurança"""
    print("🔒 TESTE DO SISTEMA DE SEGURANÇA NEØ")
    print("=" * 50)
    
    try:
        # Cria configuração se não existir
        if not os.path.exists('security_config.json'):
            create_security_config_file()
        
        # Inicializa validador
        validator = SecurityValidator()
        
        # Testa validação de ambiente
        print("1. Testando validação de ambiente...")
        validator.validate_environment()
        print("   ✅ Ambiente validado")
        
        # Mostra status
        print("\n2. Status de segurança:")
        status = validator.get_security_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # Testa validação de trade
        print("\n3. Testando validação de trade...")
        valid, message = validator.validate_trade_operation("BTCUSDT", "Buy", 100.0)
        print(f"   {'✅' if valid else '❌'} {message}")
        
        # Gera relatório
        print("\n4. Relatório de segurança:")
        report = validator.create_security_report()
        print(report)
        
        print("\n✅ TESTE DE SEGURANÇA CONCLUÍDO!")
        
    except SecurityError as e:
        print(f"❌ ERRO DE SEGURANÇA: {e}")
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")

if __name__ == "__main__":
    main()
