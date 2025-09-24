#!/usr/bin/env python3
"""
Dashboard Streamlit para Trading de Futures Bybit
Inclui métricas de risco, liquidação e funding
"""
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD
import pandas as pd
import streamlit as st
from bybit_api import (
    connect_bybit, get_futures_balance, get_futures_price, 
    get_klines, get_futures_positions, get_open_orders
)
from futures_strategy import (
    get_futures_entry_levels, calculate_position_size, 
    calculate_liquidation_price, get_risk_metrics,
    validate_trade_signal, get_futures_recommendations
)

st.set_page_config(layout="wide")
st.title("🥷 Bybit Futures Trading Dashboard - Protocolo NΞØ")

# Conecta com a API
session = connect_bybit()

# Obtém dados de mercado
futures_data = get_futures_price(session, "BTCUSDT")
balance_data = get_futures_balance(session)
price = futures_data["price"]

# Layout principal
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("💰 Preço BTC/USDT", f"{price:,.2f}")
    st.metric("📊 Funding Rate", f"{futures_data['funding_rate']*100:.4f}%")
    st.metric("🕐 Próximo Funding", futures_data['next_funding'][:19] if futures_data['next_funding'] else "N/A")

with col2:
    st.metric("💳 Margem Disponível", f"{balance_data['available']:.2f} USDT")
    st.metric("📈 Margem Total", f"{balance_data['total']:.2f} USDT")
    st.metric("🔒 Margem Usada", f"{balance_data['used']:.2f} USDT")

with col3:
    st.metric("📊 Open Interest", f"{futures_data['open_interest']:,.0f}")
    st.metric("📈 Volume 24h", f"{futures_data['volume_24h']:,.0f}")
    margin_ratio = (balance_data['used'] / balance_data['total'] * 100) if balance_data['total'] > 0 else 0
    st.metric("⚡ Uso de Margem", f"{margin_ratio:.1f}%")

# Seção de posições
st.subheader("🎯 Posições Abertas")
positions = get_futures_positions(session, "BTCUSDT")

if positions:
    for pos in positions:
        if float(pos['size']) > 0:  # Posição ativa
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.write(f"**{pos['side']}** {pos['size']} BTC")
            
            with col2:
                entry_price = float(pos['avgPrice'])
                current_price = price
                pnl = (current_price - entry_price) * float(pos['size']) if pos['side'] == 'Buy' else (entry_price - current_price) * float(pos['size'])
                st.write(f"P&L: {pnl:.2f} USDT")
            
            with col3:
                leverage = float(pos['leverage'])
                liquidation = calculate_liquidation_price(entry_price, pos['side'], leverage)
                st.write(f"Liquidação: {liquidation:.2f}")
            
            with col4:
                roi = (pnl / (entry_price * float(pos['size']) / leverage)) * 100
                st.write(f"ROI: {roi:.2f}%")
else:
    st.info("Nenhuma posição aberta")

# Seção de estratégia
st.subheader("🧠 Estratégia de Entrada - Futures")
leverage = st.slider("Alavancagem", 1, 20, 10)
risk_percent = st.slider("Risco por Trade (%)", 0.5, 5.0, 2.0)

entry_levels = get_futures_entry_levels(price, leverage=leverage)

for i, level in enumerate(entry_levels, 1):
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.write(f"**Entrada {i}:** {level:,.2f}")
    
    with col2:
        stop_loss = level * 0.98 if i == 1 else level * 0.95  # Stop mais apertado
        st.write(f"Stop: {stop_loss:,.2f}")
    
    with col3:
        liquidation = calculate_liquidation_price(level, "Long", leverage)
        st.write(f"Liquidação: {liquidation:,.2f}")
    
    with col4:
        position_size = calculate_position_size(balance_data['available'], risk_percent, level, stop_loss, leverage)
        st.write(f"Qty: {position_size['quantity']:.6f}")

# Seção de indicadores técnicos
st.subheader("📊 Indicadores Técnicos")
df = get_klines(session, "BTCUSDT", interval="15", limit=100)

if len(df) >= 14:
    rsi = RSIIndicator(close=df["close"], window=14).rsi()
    macd = MACD(close=df["close"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("RSI (14)", f"{rsi.iloc[-1]:.2f}")
    
    with col2:
        st.metric("MACD", f"{macd.macd().iloc[-1]:.2f}")
    
    with col3:
        st.metric("Signal", f"{macd.macd_signal().iloc[-1]:.2f}")
    
    # Validação de sinal
    signals = validate_trade_signal(
        rsi.iloc[-1], 
        macd.macd().iloc[-1], 
        macd.macd_signal().iloc[-1],
        futures_data['funding_rate'],
        futures_data['volume_24h']
    )
    
    st.write("**Sinais de Trading:**")
    for signal in signals:
        if "WARNING" in signal:
            st.warning(f"⚠️ {signal}")
        elif "HIGH" in signal or "LOW" in signal:
            st.error(f"🚨 {signal}")
        else:
            st.success(f"✅ {signal}")

# Seção de recomendações
st.subheader("🎯 Recomendações do Protocolo NΞØ")
recommendations = get_futures_recommendations(df, balance_data, futures_data)

for rec in recommendations:
    if "🚨" in rec:
        st.error(rec)
    elif "⚠️" in rec:
        st.warning(rec)
    else:
        st.success(rec)

# Gráfico candlestick
st.subheader("📈 Gráfico BTC/USDT - Futures")
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df.index,
    open=df["open"], high=df["high"],
    low=df["low"], close=df["close"],
    name="BTC/USDT"
))

# Adiciona linhas de liquidação se houver posições
if positions:
    for pos in positions:
        if float(pos['size']) > 0:
            liquidation = calculate_liquidation_price(float(pos['avgPrice']), pos['side'], float(pos['leverage']))
            fig.add_hline(
                y=liquidation,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Liquidação {pos['side']}",
                annotation_position="top right"
            )

fig.update_layout(
    title="BTC/USDT Futures - 15min",
    xaxis_title="Data",
    yaxis_title="Preço",
    height=600
)
st.plotly_chart(fig, use_container_width=True)

# Aviso de risco
st.error("""
⚠️ **AVISO DE RISCO - FUTURES TRADING**

- Trading de Futures envolve alto risco de liquidação
- Use stop-loss e gestão de risco adequada
- Nunca arrisque mais do que pode perder
- Teste sempre em testnet antes de operar com dinheiro real
""")
