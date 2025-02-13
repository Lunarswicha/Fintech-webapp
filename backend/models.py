import os
import pandas as pd
import numpy as np
from fastapi import FastAPI
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

app = FastAPI()

# 📂 Chargement des fichiers CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILES = {
    "bitcoin": os.path.join(BASE_DIR, "../data/bitcoin_data.csv"),
    "or": os.path.join(BASE_DIR, "../data/or_data.csv"),
    "s&p_500": os.path.join(BASE_DIR, "../data/s&p_500_data.csv"),
}

# 📈 Fonction pour charger et préparer les données
def prepare_data(asset: str):
    file_path = CSV_FILES.get(asset)
    if file_path and os.path.exists(file_path):
        df = pd.read_csv(file_path)
        
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.sort_values("Date")
        
        features = ["Open", "High", "Low", "Close"]
        df = df[features]
        
        # Normalisation des données
        scaler = MinMaxScaler()
        df_scaled = scaler.fit_transform(df)
        
        # Séparation Train/Test
        X = df_scaled[:-1]
        y = df_scaled[1:, 3]  # Prédiction sur le "Close"
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        return X_train, X_test, y_train, y_test, scaler
    return None

# 🎯 Prédiction avec Random Forest
@app.get("/predict/{asset}")
def predict_price(asset: str):
    data = prepare_data(asset)
    if data:
        X_train, X_test, y_train, y_test, scaler = data
        model = RandomForestRegressor(n_estimators=100)
        model.fit(X_train, y_train)
        
        # Prédiction sur les 30 prochains jours
        future_X = X_test[-30:]
        predicted_prices = model.predict(future_X)
        predicted_prices = scaler.inverse_transform(
            np.column_stack([np.zeros((30, 3)), predicted_prices])
        )[:, 3]
        
        return {"predictions": predicted_prices.tolist()}
    return {"error": "Données indisponibles pour cet actif"}
