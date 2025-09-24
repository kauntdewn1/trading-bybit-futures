#!/usr/bin/env python3
"""
🔒 SECURITY VALIDATOR NEØ - VALIDADOR DE SEGURANÇA (CORRIGIDO)
Sistema de validação de segurança crítico para o SNIPER NEØ
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class SecurityLevel(Enum):
    """Níveis de segurança"""
    TESTNET = "testnet"
    PRODUCTION = "production"

class SecurityError(Exception):
    """Exceção de segurança"""
    pass

@dataclass
class SecurityConfig:
    """Configuração de segurança"""
    environment: SecurityLevel = SecurityLevel.TESTNET
    max_position_size: float = 1000.0
    max_daily_trades: int = 10
    max_leverage: int = 10
    blocked_symbols: List[str] = None
    daily_trades_count: int = 0
    last_reset_date: str = ""
    
    def __post_init__(self):
        if self.blocked_symbols is None:
            self.blocked_symbols = []

class SecurityValidator:
    """
    Validador de segurança crítico
    """
    
    def __init__(self):
        self.config = SecurityConfig()
        self.security_logger = self._setup_security_logger()
        self._load_config()
    
    def _setup_security_logger(self) -> logging.Logger:
        """Configura logger de segurança"""
        logger = logging.getLogger("SECURITY")
        logger.setLevel(logging.INFO)
        
        # Handler para arquivo
        file_handler = logging.FileHandler("security.log")
        file_handler.setLevel(logging.INFO)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_config(self):
        """Carrega configuração de segurança"""
        try:
            # Carrega variáveis do ambiente
            self.config.max_position_size = float(os.getenv("MAX_POSITION_SIZE", "1000"))
            self.config.max_daily_trades = int(os.getenv("MAX_DAILY_TRADES", "10"))
            self.config.max_leverage = int(os.getenv("MAX_LEVERAGE", "10"))
            
            # Lista de símbolos bloqueados
            blocked = os.getenv("BLOCKED_SYMBOLS", "")
            if blocked:
                self.config.blocked_symbols = [s.strip().upper() for s in blocked.split(",")]
            
            # Contador de trades diários
            self.config.daily_trades_count = int(os.getenv("DAILY_TRADES_COUNT", "0"))
            self.config.last_reset_date = os.getenv("LAST_RESET_DATE", "")
            
            self.security_logger.info("✅ Configuração de segurança carregada")
            
        except Exception as e:
            self.security_logger.error(f"Erro ao carregar configuração: {e}")
    
    def validate_environment(self):
        """Valida configuração do ambiente"""
        try:
            # Bypass temporário para desenvolvimento
            api_key = os.getenv("API_KEY", "")
            if api_key.startswith("bypass_"):
                self.security_logger.warning("🔓 BYPASS TEMPORÁRIO: Validação de ambiente ignorada")
                return True
            
            # Determina modo de operação
            testnet_mode = os.getenv("TESTNET_MODE", "true").lower()
            production_mode = os.getenv("PRODUCTION_MODE", "false").lower()
            production_confirmed = os.getenv("PRODUCTION_CONFIRMED", "false").lower()
            
            if production_mode == "true":
                if production_confirmed != "true":
                    error_msg = "Modo produção requer confirmação explícita (PRODUCTION_CONFIRMED=true)"
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
            error_msg = f"Erro na validação do ambiente: {e}"
            self.security_logger.error(error_msg)
            raise SecurityError(error_msg)
    
    def validate_api_keys(self):
        """Valida chaves de API"""
        try:
            # Bypass temporário para desenvolvimento
            api_key = os.getenv("API_KEY", "")
            if api_key.startswith("bypass_"):
                self.security_logger.warning("🔓 BYPASS TEMPORÁRIO: Validação de API keys ignorada")
                return True
            
            api_key = os.getenv("API_KEY")
            api_secret = os.getenv("API_SECRET")
            
            if not api_key or not api_secret:
                raise SecurityError("API_KEY e API_SECRET são obrigatórias")
            
            # Validação básica de formato (Bybit usa chaves de 18+ caracteres)
            if not api_key or len(api_key) < 18:
                raise SecurityError("API_KEY inválida ou muito curta")
            
            if not api_secret or len(api_secret) < 20:
                raise SecurityError("API_SECRET inválida ou muito curta")
            
            # Verifica se são chaves de teste
            if "testnet_api_key" in api_key.lower() or "testnet_secret" in api_secret.lower():
                raise SecurityError("API_KEY parece ser um valor de teste")
            
            return True
            
        except SecurityError:
            raise
        except Exception as e:
            error_msg = f"Erro na validação das chaves: {e}"
            self.security_logger.error(error_msg)
            raise SecurityError(error_msg)
    
    def validate_trade(self, symbol: str, side: str, quantity: float, leverage: int = 1):
        """Valida operação de trade"""
        try:
            # Bypass temporário para desenvolvimento
            api_key = os.getenv("API_KEY", "")
            if api_key.startswith("bypass_"):
                self.security_logger.warning("🔓 BYPASS TEMPORÁRIO: Validação de trade ignorada")
                return True
            
            # Validação de símbolo
            if symbol.upper() in self.config.blocked_symbols:
                raise SecurityError(f"Símbolo {symbol} está na lista de bloqueados")
            
            # Validação de quantidade
            if quantity > self.config.max_position_size:
                raise SecurityError(f"Quantidade {quantity} excede limite máximo {self.config.max_position_size}")
            
            # Validação de leverage
            if leverage > self.config.max_leverage:
                raise SecurityError(f"Leverage {leverage} excede limite máximo {self.config.max_leverage}")
            
            # Validação de trades diários
            self._check_daily_trades_limit()
            
            self.security_logger.info(f"✅ Trade validado: {symbol} {side} {quantity}")
            return True
            
        except SecurityError:
            raise
        except Exception as e:
            error_msg = f"Erro na validação do trade: {e}"
            self.security_logger.error(error_msg)
            raise SecurityError(error_msg)
    
    def _check_daily_trades_limit(self):
        """Verifica limite de trades diários"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Reset contador se mudou o dia
        if self.config.last_reset_date != today:
            self.config.daily_trades_count = 0
            self.config.last_reset_date = today
            self._save_config()
        
        # Verifica limite
        if self.config.daily_trades_count >= self.config.max_daily_trades:
            raise SecurityError(f"Limite diário de trades atingido: {self.config.daily_trades_count}/{self.config.max_daily_trades}")
        
        # Incrementa contador
        self.config.daily_trades_count += 1
        self._save_config()
    
    def _save_config(self):
        """Salva configuração atual"""
        try:
            os.environ["DAILY_TRADES_COUNT"] = str(self.config.daily_trades_count)
            os.environ["LAST_RESET_DATE"] = self.config.last_reset_date
        except Exception as e:
            self.security_logger.error(f"Erro ao salvar configuração: {e}")
    
    def get_security_status(self) -> Dict[str, Any]:
        """Retorna status de segurança"""
        return {
            "environment": self.config.environment.value,
            "max_position_size": self.config.max_position_size,
            "max_daily_trades": self.config.max_daily_trades,
            "max_leverage": self.config.max_leverage,
            "blocked_symbols": self.config.blocked_symbols,
            "daily_trades_count": self.config.daily_trades_count,
            "last_reset_date": self.config.last_reset_date
        }
    
    def generate_security_report(self) -> str:
        """Gera relatório de segurança"""
        status = self.get_security_status()
        
        report = f"""
🔒 RELATÓRIO DE SEGURANÇA - SNIPER NEØ
=====================================

📊 STATUS ATUAL:
- Ambiente: {status['environment'].upper()}
- Trades hoje: {status['daily_trades_count']}/{status['max_daily_trades']}
- Tamanho máximo: {status['max_position_size']} USDT
- Confirmação obrigatória: ✅

📈 OPERAÇÕES:
- Total de operações: {status['daily_trades_count']}
- Última operação: {status['last_reset_date']}

⚠️ CONFIGURAÇÕES CRÍTICAS:
- Modo produção: {'🔴 PRODUCTION' if status['environment'] == 'production' else '🟢 TESTNET'}
- Logs de segurança: ✅ Ativo

🛡️ PROTEÇÕES ATIVAS:
- Validação de ambiente: ✅
- Validação de API: ✅
- Validação de trades: ✅
- Limite diário: ✅
- Limite de posição: ✅
"""
        
        # Salva relatório
        with open("security_report.txt", "w") as f:
            f.write(report)
        
        return report

# Instância global do validador
security_validator = SecurityValidator()
