import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

# 📌 Configuration de la page Streamlit
st.set_page_config(page_title="🔮 Prédictions des Marchés", layout="wide")

# 📌 Définition des actifs et fichiers associés
assets = {
    "Bitcoin": "data/bitcoin_data.csv",
    "S&P 500": "data/s&p_500_data.csv",
    "Or": "data/or_data.csv"
}

# 📌 Sélection de l'actif
st.sidebar.title("Paramètres de Prédiction")
selected_asset = st.sidebar.selectbox("Sélectionnez un actif :", list(assets.keys()))
future_days = st.sidebar.slider("Jours à prédire :", 30, 365, 180)

# 📌 Chargement des données
file_path = assets[selected_asset]
data = pd.read_csv(file_path)

# Vérification des colonnes
if "Date" not in data.columns or "Adj Close" not in data.columns:
    st.error(f"❌ Les colonnes nécessaires sont absentes dans {file_path}")
    st.stop()

# Conversion des dates
data["Date"] = pd.to_datetime(data["Date"])

# 📊 Affichage des données récentes
st.subheader(f"📊 Données récentes pour {selected_asset}")
st.dataframe(data.tail())

# 📌 Préparation des données pour Prophet
df_prophet = data.rename(columns={"Date": "ds", "Adj Close": "y"})

# 📌 Création et entraînement du modèle Prophet
model = Prophet()
model.fit(df_prophet)

# 📌 Génération des futures dates
future = model.make_future_dataframe(periods=future_days)
forecast = model.predict(future)

# 📈 Graphique des prédictions
st.subheader(f"📈 Prédiction des prix pour {selected_asset}")
fig = px.line(forecast, x="ds", y="yhat", title=f"Projection des prix de {selected_asset}")
fig.add_scatter(x=data["Date"], y=data["Adj Close"], mode="lines", name="Historique", line=dict(color="blue"))
st.plotly_chart(fig, use_container_width=True)

# 📊 Affichage des valeurs prédites
st.subheader("📅 Prochaines valeurs prédites")
st.dataframe(forecast[["ds", "yhat"]].tail(10))
