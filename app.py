import streamlit as st
import pandas as pd
import plotly.express as px

# 📌 Chargement des fichiers CSV
assets = {
    "Bitcoin": "data/bitcoin_data.csv",
    "S&P 500": "data/s&p_500_data.csv",
    "Or": "data/or_data.csv"
}

# 📌 Lecture des fichiers et pré-traitement
prices = pd.DataFrame()

for asset, file_path in assets.items():
    data = pd.read_csv(file_path)
    data["Date"] = pd.to_datetime(data["Date"])

    # ✅ Normaliser les prix pour une meilleure visibilité
    data["Adj Close"] = data["Adj Close"] / data["Adj Close"].iloc[0] * 100

    # ✅ Interpoler les valeurs manquantes pour éviter les discontinuités
    data = data.set_index("Date").asfreq("D").interpolate().reset_index()

    # ✅ Fusionner les données
    if prices.empty:
        prices = data[["Date", "Adj Close"]].rename(columns={"Adj Close": asset})
    else:
        prices = prices.merge(data[["Date", "Adj Close"]].rename(columns={"Adj Close": asset}), on="Date", how="outer")

# 📉 **Graphique de comparaison**
st.subheader("📊 Évolution des actifs avec normalisation")
prices_long = prices.melt(id_vars="Date", var_name="Actif", value_name="Prix")
fig_price = px.line(prices_long, x="Date", y="Prix", color="Actif",
                    title="Comparaison des actifs (normalisés à 100%)")
st.plotly_chart(fig_price, use_container_width=True)
