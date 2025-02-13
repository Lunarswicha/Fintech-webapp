import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 📌 Configuration de la page Streamlit
st.set_page_config(page_title="Analyse Technique des Marchés", layout="wide")

# 📌 Chargement des données
@st.cache_data
def load_data(asset_name):
    file_path = f"data/{asset_name.lower()}_data.csv"
    df = pd.read_csv(file_path)
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    return df

# 📌 Sélection de l'actif
assets = {"Bitcoin": "bitcoin", "S&P 500": "s&p_500", "Or": "or"}
selected_asset = st.sidebar.selectbox("Sélectionnez un actif :", list(assets.keys()))
data = load_data(assets[selected_asset])

# 📌 Filtres d'indicateurs techniques
st.sidebar.subheader("Indicateurs techniques")
show_bb = st.sidebar.checkbox("Bollinger Bands")
show_macd = st.sidebar.checkbox("MACD")
show_rsi = st.sidebar.checkbox("RSI")
show_ema = st.sidebar.checkbox("EMA 50 & 200")

# 📌 Fonctions pour calculer les indicateurs **(SANS `ta` ni `pandas_ta`)**
def calculate_bollinger_bands(prices, window=20, std_dev=2):
    rolling_mean = prices.rolling(window=window).mean()
    rolling_std = prices.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * std_dev)
    lower_band = rolling_mean - (rolling_std * std_dev)
    return upper_band, lower_band

def calculate_macd(prices, slow=26, fast=12, signal=9):
    exp1 = prices.ewm(span=fast, adjust=False).mean()
    exp2 = prices.ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    return macd, signal_line

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# 📌 Application des indicateurs sur les données
if show_bb:
    data["BB_High"], data["BB_Low"] = calculate_bollinger_bands(data["Adj Close"])

if show_macd:
    data["MACD"], data["MACD_Signal"] = calculate_macd(data["Adj Close"])

if show_rsi:
    data["RSI"] = calculate_rsi(data["Adj Close"])

if show_ema:
    data["EMA_50"] = data["Adj Close"].ewm(span=50, adjust=False).mean()
    data["EMA_200"] = data["Adj Close"].ewm(span=200, adjust=False).mean()

# 📊 **Graphique principal avec les indicateurs**
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Adj Close"],
    name="Prix"
))

if show_bb:
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_High"], name="BB High", line=dict(color='blue', dash='dot')))
    fig.add_trace(go.Scatter(x=data.index, y=data["BB_Low"], name="BB Low", line=dict(color='blue', dash='dot')))

if show_ema:
    fig.add_trace(go.Scatter(x=data.index, y=data["EMA_50"], name="EMA 50", line=dict(color='orange')))
    fig.add_trace(go.Scatter(x=data.index, y=data["EMA_200"], name="EMA 200", line=dict(color='red')))

fig.update_layout(title=f"📈 Evolution de {selected_asset}", xaxis_title="Date", yaxis_title="Prix", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# 📊 **Graphiques secondaires pour MACD et RSI**
if show_macd:
    st.subheader("📈 MACD")
    fig_macd = go.Figure()
    fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD"], name="MACD", line=dict(color='purple')))
    fig_macd.add_trace(go.Scatter(x=data.index, y=data["MACD_Signal"], name="Signal Line", line=dict(color='gray')))
    st.plotly_chart(fig_macd, use_container_width=True)

if show_rsi:
    st.subheader("📉 RSI")
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=data.index, y=data["RSI"], name="RSI", line=dict(color='blue')))
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    st.plotly_chart(fig_rsi, use_container_width=True)

# 📊 **Correction de la Heatmap de corrélation**
st.subheader("📊 Corrélation entre les actifs")

# 📌 Chargement des prix de tous les actifs pour la heatmap
prices = pd.DataFrame()
for asset, filename in assets.items():
    df = load_data(filename)
    prices[asset] = df["Adj Close"]

prices.dropna(inplace=True)  # Supprimer les valeurs NaN
returns = prices.pct_change().dropna()  # Calcul des rendements journaliers
correlation_matrix = returns.corr()  # Corrélation basée sur les variations

fig_corr, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5, ax=ax)
st.pyplot(fig_corr)

st.sidebar.success("✅ Sélectionnez des indicateurs pour les afficher 🎯")
