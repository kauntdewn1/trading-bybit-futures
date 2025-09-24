#!/usr/bin/env python3
"""
Estratégia de Trading para Futures Bybit
Inclui cálculos de risco, liquidação e funding
"""
import math

def get_futures_entry_levels(base_price, levels=3, leverage=10):
    """
    Calcula níveis de entrada para Futures com alavancagem
    """
    # Descontos progressivos mais conservadores para Futures
    steps = [0, -1.0, -2.5]  # Menos agressivo que Spot
    entry_prices = [round(base_price * (1 + s / 100), 2) for s in steps]
    
    return entry_prices

def calculate_position_size(account_balance, risk_percent, entry_price, stop_loss_price, leverage=10):
    """
    Calcula tamanho da posição baseado no risco
    """
    # Risco máximo por trade
    max_risk = account_balance * (risk_percent / 100)
    
    # Distância do stop loss
    stop_distance = abs(entry_price - stop_loss_price)
    
    # Tamanho da posição em USDT
    position_value = max_risk / (stop_distance / entry_price)
    
    # Quantidade considerando alavancagem
    quantity = (position_value * leverage) / entry_price
    
    return {
        "quantity": round(quantity, 6),
        "position_value": round(position_value, 2),
        "max_risk": round(max_risk, 2),
        "stop_distance": round(stop_distance, 2)
    }

def calculate_liquidation_price(entry_price, side, leverage, margin_ratio=0.1):
    """
    Calcula preço de liquidação
    """
    if side.upper() == "LONG":
        # Para LONG: Liquidação abaixo do preço de entrada
        liquidation = entry_price * (1 - (1 - margin_ratio) / leverage)
    else:
        # Para SHORT: Liquidação acima do preço de entrada
        liquidation = entry_price * (1 + (1 - margin_ratio) / leverage)
    
    return round(liquidation, 2)

def calculate_funding_cost(position_value, funding_rate):
    """
    Calcula custo de funding
    """
    return position_value * funding_rate

def get_risk_metrics(entry_price, current_price, quantity, leverage, side):
    """
    Calcula métricas de risco em tempo real
    """
    # P&L atual
    if side.upper() == "LONG":
        pnl = (current_price - entry_price) * quantity
    else:
        pnl = (entry_price - current_price) * quantity
    
    # Margem usada
    margin_used = (entry_price * quantity) / leverage
    
    # ROI
    roi = (pnl / margin_used) * 100 if margin_used > 0 else 0
    
    return {
        "pnl": round(pnl, 2),
        "margin_used": round(margin_used, 2),
        "roi": round(roi, 2),
        "side": side
    }

def validate_trade_signal(rsi, macd, macd_signal, funding_rate, volume_24h):
    """
    Valida sinal de trading considerando condições de Futures
    """
    signals = []
    
    # RSI
    if rsi < 30:
        signals.append("RSI_OVERSOLD")
    elif rsi > 70:
        signals.append("RSI_OVERBOUGHT")
    
    # MACD
    if macd > macd_signal:
        signals.append("MACD_BULLISH")
    else:
        signals.append("MACD_BEARISH")
    
    # Funding rate (evitar funding alto)
    if funding_rate > 0.01:  # 1%
        signals.append("HIGH_FUNDING_WARNING")
    elif funding_rate < -0.01:  # -1%
        signals.append("NEGATIVE_FUNDING")
    
    # Volume (liquidez)
    if volume_24h < 1000000:  # 1M USDT
        signals.append("LOW_VOLUME_WARNING")
    
    return signals

def get_futures_recommendations(price_data, balance_data, funding_data):
    """
    Gera recomendações específicas para Futures
    """
    recommendations = []
    
    # Análise de funding
    if funding_data["funding_rate"] > 0.005:  # 0.5%
        recommendations.append("⚠️ Funding alto - considere SHORT")
    elif funding_data["funding_rate"] < -0.005:  # -0.5%
        recommendations.append("✅ Funding negativo - considere LONG")
    
    # Análise de liquidez
    if funding_data["open_interest"] > 100000000:  # 100M
        recommendations.append("✅ Alta liquidez - boa para entrada")
    else:
        recommendations.append("⚠️ Baixa liquidez - cuidado com slippage")
    
    # Análise de margem
    margin_ratio = balance_data["used"] / balance_data["total"] if balance_data["total"] > 0 else 0
    if margin_ratio > 0.8:  # 80%
        recommendations.append("🚨 Margem alta - reduza posições")
    elif margin_ratio < 0.3:  # 30%
        recommendations.append("✅ Margem confortável - pode aumentar posição")
    
    return recommendations
