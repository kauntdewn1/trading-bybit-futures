import os
import pandas as pd
from pybit.unified_trading import HTTP
from dotenv import load_dotenv
from security_validator import SecurityValidator, SecurityError

# Carrega variáveis do .env
load_dotenv()

# Inicializa validador de segurança
security_validator = SecurityValidator()

def connect_bybit():
    """
    Conecta à API Bybit com validação de segurança crítica
    """
    try:
        # Validação crítica de ambiente ANTES da conexão
        security_validator.validate_environment()
        
        # Determina modo testnet baseado na configuração de segurança
        testnet_mode = os.getenv("TESTNET_MODE", "true").lower() == "true"
        
        session = HTTP(
            api_key=os.getenv("API_KEY"),
            api_secret=os.getenv("API_SECRET"),
            testnet=testnet_mode
        )
        
        # Valida permissões da API após conexão (método removido temporariamente)
        # security_validator.validate_api_permissions(session)
        
        return session
        
    except SecurityError as e:
        print(f"🔒 ERRO DE SEGURANÇA: {e}")
        raise
    except Exception as e:
        print(f"❌ Erro na conexão Bybit: {e}")
        raise

def get_balance(session):
    """Obtém saldo USDT para Futures (margem disponível)"""
    result = session.get_wallet_balance(accountType="UNIFIED")
    balances = result["result"]["list"][0]["coin"]
    for asset in balances:
        if asset["coin"] == "USDT":
            try:
                return float(asset["availableToWithdraw"])
            except (ValueError, TypeError):
                return 0.0
    return 0.0

def get_futures_balance(session):
    """Obtém saldo específico para Futures com margem"""
    result = session.get_wallet_balance(accountType="UNIFIED")
    balances = result["result"]["list"][0]["coin"]
    for asset in balances:
        if asset["coin"] == "USDT":
            try:
                return {
                    "available": float(asset["availableToWithdraw"]),
                    "total": float(asset["walletBalance"]),
                    "used": float(asset["walletBalance"]) - float(asset["availableToWithdraw"])
                }
            except (ValueError, TypeError):
                return {"available": 0.0, "total": 0.0, "used": 0.0}
    return {"available": 0.0, "total": 0.0, "used": 0.0}

def get_price(session, symbol="BTCUSDT"):
    """Obtém preço para Futures (Perpetual)"""
    ticker = session.get_tickers(category="linear", symbol=symbol)
    return float(ticker["result"]["list"][0]["lastPrice"])

def get_futures_price(session, symbol="BTCUSDT"):
    """Obtém preço e dados específicos de Futures"""
    try:
        ticker = session.get_tickers(category="linear", symbol=symbol)
        
        # Verifica se há dados válidos
        if not ticker.get("result") or not ticker["result"].get("list") or len(ticker["result"]["list"]) == 0:
            return None
            
        data = ticker["result"]["list"][0]
        return {
            "price": float(data["lastPrice"]),
            "funding_rate": float(data.get("fundingRate", 0)),
            "next_funding": data.get("nextFundingTime", ""),
            "open_interest": float(data.get("openInterest", 0)),
            "volume_24h": float(data.get("volume24h", 0))
        }
    except Exception:
        # Silencia erros de símbolos inválidos
        return None

def get_open_orders(session, symbol="BTCUSDT"):
    """Obtém ordens abertas para Futures"""
    orders = session.get_open_orders(category="linear", symbol=symbol)
    return orders["result"]["list"]

def get_futures_positions(session, symbol="BTCUSDT"):
    """Obtém posições abertas de Futures"""
    positions = session.get_positions(category="linear", symbol=symbol)
    return positions["result"]["list"]

def get_order_history(session, symbol="BTCUSDT"):
    """Obtém histórico de ordens para Futures"""
    history = session.get_order_history(category="linear", symbol=symbol)
    return history["result"]["list"]

def get_klines(session, symbol="BTCUSDT", interval="15", limit=100):
    """Obtém klines para Futures (Perpetual)"""
    data = session.get_kline(
        category="linear",
        symbol=symbol,
        interval=interval,
        limit=limit
    )
    candles = data["result"]["list"]
    df = pd.DataFrame(candles, columns=[
        "timestamp", "open", "high", "low", "close", "volume", "turnover"])
    df["timestamp"] = pd.to_datetime(pd.to_numeric(df["timestamp"], errors='coerce'), unit='ms')
    df.set_index("timestamp", inplace=True)
    df = df.astype(float)
    return df

def create_futures_order(session, symbol, side, qty, price=None, order_type="Market", position_side="Long", leverage=1):
    """
    Cria ordem de Futures com validação de segurança crítica
    """
    try:
        # VALIDAÇÃO CRÍTICA DE SEGURANÇA
        valid, message = security_validator.validate_trade_operation(symbol, side, qty, price)
        if not valid:
            raise SecurityError(f"Operação rejeitada: {message}")
        
        # Converte qty para float para validação
        qty_float = float(qty)
        
        # Validação adicional de leverage
        if leverage > 10:
            raise SecurityError(f"Leverage {leverage}x excede limite máximo de 10x")
        
        # Validação de preço para ordens limit
        if order_type == "Limit" and price:
            price_float = float(price)
            if price_float <= 0:
                raise SecurityError("Preço deve ser maior que zero")
        
        order_data = {
            "category": "linear",
            "symbol": symbol,
            "side": side,
            "orderType": order_type,
            "qty": str(qty),
            "positionSide": position_side,
            "leverage": str(leverage),
            "timeInForce": "GTC"
        }
        
        if price and order_type == "Limit":
            order_data["price"] = str(price)
        
        # Log da operação antes da execução
        security_validator.security_logger.info(
            f"Executando ordem: {symbol} {side} {qty} @ {price or 'Market'}"
        )
        
        result = session.place_order(**order_data)
        
        # Log do resultado
        if result.get("retCode") == 0:
            security_validator.security_logger.info(f"✅ Ordem executada com sucesso: {result.get('result', {}).get('orderId', 'N/A')}")
        else:
            security_validator.security_logger.error(f"❌ Falha na ordem: {result.get('retMsg', 'Erro desconhecido')}")
        
        return result
        
    except SecurityError:
        raise
    except Exception as e:
        security_validator.security_logger.error(f"Erro na criação de ordem: {e}")
        raise
