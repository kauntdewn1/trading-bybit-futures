#!/usr/bin/env python3
"""
Funções para o Assistente OpenAI - Bybit Trading Node
Implementa as funções chamadas pelo Node NΞØ
"""
import json
import pandas as pd
from bybit_api import connect_bybit, get_futures_price, get_klines, get_futures_balance
from futures_strategy import validate_trade_signal, get_futures_recommendations
from ta.momentum import RSIIndicator
from ta.trend import MACD
# Volume analysis será calculado manualmente

def analyze_market_data(symbol, timeframe, indicators):
    """
    Analisa dados de mercado da Bybit e retorna insights de trading
    """
    try:
        # Conecta com a API
        session = connect_bybit()
        
        # Obtém dados de mercado
        futures_data = get_futures_price(session, symbol)
        balance_data = get_futures_balance(session)
        
        # Obtém klines baseado no timeframe
        interval_map = {
            "1m": "1",
            "5m": "5", 
            "15m": "15",
            "30m": "30",
            "1h": "60",
            "4h": "240",
            "1d": "D"
        }
        
        interval = interval_map.get(timeframe, "15")
        df = get_klines(session, symbol, interval, 100)
        
        # Calcula indicadores
        analysis = {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamp": pd.Timestamp.now().isoformat(),
            "price": futures_data["price"],
            "funding_rate": futures_data["funding_rate"],
            "open_interest": futures_data["open_interest"],
            "volume_24h": futures_data["volume_24h"]
        }
        
        # RSI
        if "RSI" in indicators:
            rsi = RSIIndicator(close=df["close"], window=14).rsi()
            analysis["rsi"] = {
                "current": float(rsi.iloc[-1]),
                "signal": "OVERSOLD" if rsi.iloc[-1] < 30 else "OVERBOUGHT" if rsi.iloc[-1] > 70 else "NEUTRAL"
            }
        
        # MACD
        if "MACD" in indicators:
            macd = MACD(close=df["close"])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            histogram = macd_line - signal_line
            analysis["macd"] = {
                "macd": float(macd_line),
                "signal": float(signal_line),
                "histogram": float(histogram),
                "trend": "BULLISH" if macd_line > signal_line else "BEARISH"
            }
        
        # Volume
        if "VOLUME" in indicators:
            volume_sma = df["volume"].rolling(window=20).mean()
            analysis["volume"] = {
                "current": float(df["volume"].iloc[-1]),
                "sma_20": float(volume_sma.iloc[-1]),
                "signal": "HIGH" if df["volume"].iloc[-1] > volume_sma.iloc[-1] else "LOW"
            }
        
        # Validação de sinal
        if "RSI" in indicators and "MACD" in indicators:
            signals = validate_trade_signal(
                analysis["rsi"]["current"],
                analysis["macd"]["macd"],
                analysis["macd"]["signal"],
                futures_data["funding_rate"],
                futures_data["volume_24h"]
            )
            analysis["signals"] = signals
        
        # Recomendações
        recommendations = get_futures_recommendations(df, balance_data, futures_data)
        analysis["recommendations"] = recommendations
        
        # Status geral
        analysis["status"] = "SUCCESS"
        analysis["message"] = "Análise de mercado concluída com sucesso"
        
        return {
            "success": True,
            "data": analysis
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Erro na análise de mercado"
        }

def validate_trading_signal(symbol, timeframe, indicators):
    """
    Valida sinal de trading baseado em indicadores
    """
    try:
        # Conecta com a API
        session = connect_bybit()
        
        # Obtém dados
        futures_data = get_futures_price(session, symbol)
        df = get_klines(session, symbol, timeframe, 50)
        
        # Calcula indicadores
        rsi = RSIIndicator(close=df["close"], window=14).rsi()
        macd = MACD(close=df["close"])
        
        # Validação
        signals = validate_trade_signal(
            rsi.iloc[-1],
            macd.macd().iloc[-1],
            macd.macd_signal().iloc[-1],
            futures_data["funding_rate"],
            futures_data["volume_24h"]
        )
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "timeframe": timeframe,
                "signals": signals,
                "confidence": len([s for s in signals if "WARNING" not in s]) / len(signals) if signals else 0
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def calculate_risk_metrics(symbol, position_size, leverage, side):
    """
    Calcula métricas de risco para posição
    """
    try:
        from futures_strategy import calculate_liquidation_price, calculate_position_size
        
        session = connect_bybit()
        futures_data = get_futures_price(session, symbol)
        balance_data = get_futures_balance(session)
        
        # Cálculos de risco
        liquidation_price = calculate_liquidation_price(futures_data["price"], side, leverage)
        
        position_info = calculate_position_size(
            balance_data["available"], 
            2.0,  # 2% de risco
            futures_data["price"], 
            liquidation_price, 
            leverage
        )
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "position_size": position_size,
                "leverage": leverage,
                "side": side,
                "liquidation_price": liquidation_price,
                "max_risk": position_info["max_risk"],
                "margin_required": position_info["position_value"]
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# Exemplo de uso para teste
if __name__ == "__main__":
    result = analyze_market_data("BTCUSDT", "15m", ["RSI", "MACD", "VOLUME"])
    print(json.dumps(result, indent=2))
