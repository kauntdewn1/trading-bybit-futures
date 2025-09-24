import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import MACD
import pandas as pd
import streamlit as st
from bybit_api import connect_bybit, get_balance, get_price, get_klines, get_open_orders
from strategy import get_entry_levels

st.set_page_config(layout="wide")
st.title("\U0001F4C8 Painel de Trading - Bybit Spot")

session = connect_bybit()
price = get_price(session, "BTCUSDT")
usdt = get_balance(session)
ticker = session.get_tickers(category="spot", symbol="BTCUSDT")["result"]["list"][0]
st.write("\U0001F9E3 Dados brutos do ticker:", ticker)

high = ticker.get("highPrice", "N/D")
low = ticker.get("lowPrice", "N/D")

col1, col2 = st.columns(2)

with col1:
    st.metric("\U0001F4B0 Saldo USDT disponível", f"{usdt:.2f} USDT" if usdt else "N/A")
    st.metric("\U0001F4C8 Preço atual BTC/USDT", f"{price:.2f}")
    st.subheader("\U0001F4C5 Entradas fracionadas (Spot)")
    entry_levels = get_entry_levels(price)
    for i, level in enumerate(entry_levels, 1):
        st.markdown(f"- \U0001F4CC **Entrada {i}: {level:.2f} USDT**")

with col2:
    st.metric("\U0001F4CA Variação 24h", f"{float(ticker['price24hPcnt'])*100:.2f} %")
    st.metric("\U0001F53C Máxima 24h", high)
    st.metric("\U0001F53D Mínima 24h", low)

    st.subheader("\U0001F4C2 Ordens em Aberto")
    open_orders = get_open_orders(session, symbol="BTCUSDT")
    if open_orders:
        for order in open_orders:
            st.write(f"\U0001F7E1 {order['side']} {order['qty']} BTC @ {order['price']}")
    else:
        st.success("\u2705 Nenhuma ordem aberta no momento.")

col3, col4 = st.columns(2)

with col3:
    st.subheader("\U0001F4DC Histórico de Ordens")
    history = session.get_order_history(category="spot", symbol="BTCUSDT")["result"]["list"]
    if history:
        for order in history[:5]:
            st.write(f"\U0001F4CC {order['side']} {order['qty']} BTC @ {order['price']} - Status: {order['orderStatus']}")
    else:
        st.info("Sem histórico recente.")

with col4:
    st.subheader("\U0001F4CA Indicadores Técnicos (RSI / MACD)")
    # Usar dados reais das klines em vez de dados simulados
    df_indicators = get_klines(session, "BTCUSDT", interval="15", limit=50)
    if len(df_indicators) >= 14:
        rsi = RSIIndicator(close=df_indicators["close"], window=14).rsi().iloc[-1]
        macd = MACD(close=df_indicators["close"])
        st.metric("RSI (14)", f"{rsi:.2f}" if not pd.isna(rsi) else "N/A")
        st.write("MACD:", f"{macd.macd().iloc[-1]:.2f}" if not pd.isna(macd.macd().iloc[-1]) else "N/A")
        st.write("Signal:", f"{macd.macd_signal().iloc[-1]:.2f}" if not pd.isna(macd.macd_signal().iloc[-1]) else "N/A")
    else:
        st.warning("Dados insuficientes para calcular indicadores")

st.markdown("---")
st.subheader("\U0001F4C8 Gráfico Candlestick + RSI/MACD + Ordens Abertas")

df = get_klines(session, "BTCUSDT", interval="15", limit=100)
df["rsi"] = RSIIndicator(close=df["close"], window=14).rsi()
macd = MACD(close=df["close"])
df["macd"] = macd.macd()
df["macd_signal"] = macd.macd_signal()

# Gráfico de candles com linhas de ordens
fig_candle = go.Figure()
fig_candle.add_trace(go.Candlestick(
    x=df.index,
    open=df["open"], high=df["high"],
    low=df["low"], close=df["close"],
    name="Candles"
))

# Marcar ordens abertas
for order in open_orders:
    fig_candle.add_hline(
        y=float(order["price"]),
        line_dash="dot",
        line_color="green" if order["side"] == "Buy" else "red",
        annotation_text=f"{order['side']} @ {order['price']}",
        annotation_position="top left"
    )

fig_candle.update_layout(
    title="BTC/USDT - 15min",
    xaxis_title="Data",
    yaxis_title="Preço",
    height=700
)
st.plotly_chart(fig_candle, use_container_width=True)

# Gráfico RSI
fig_rsi = go.Figure()
fig_rsi.add_trace(go.Scatter(x=df.index, y=df["rsi"], mode="lines", name="RSI"))
fig_rsi.update_layout(title="RSI (14)", xaxis_title="Data", yaxis_title="RSI", height=300)

# Gráfico MACD
fig_macd = go.Figure()
fig_macd.add_trace(go.Scatter(x=df.index, y=df["macd"], mode="lines", name="MACD"))
fig_macd.add_trace(go.Scatter(x=df.index, y=df["macd_signal"], mode="lines", name="Signal"))
fig_macd.update_layout(title="MACD", xaxis_title="Data", yaxis_title="Valor", height=300)

st.plotly_chart(fig_rsi, use_container_width=True)
st.plotly_chart(fig_macd, use_container_width=True)
