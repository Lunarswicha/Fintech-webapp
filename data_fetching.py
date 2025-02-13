import yfinance as yf
import pandas as pd
from pathlib import Path

# 📌 Dossier de sortie
output_folder = Path("data")
output_folder.mkdir(exist_ok=True)

# 📌 Liste des actifs et leurs tickers
assets = {
    "Bitcoin": "BTC-USD",
    "S&P 500": "^GSPC",
    "Or": "GC=F"
}

# 📌 Fonction pour récupérer et sauvegarder les données
def fetch_asset_data(ticker, asset_name, output_folder):
    print(f"📥 Récupération des données pour {asset_name} ({ticker})...")
    data = yf.download(ticker, period="5y", interval="1d")
    
    # Vérifier et aplatir les colonnes multi-indexées
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]  # Garder uniquement les premiers noms

    print(f"Colonnes disponibles pour {asset_name} :", data.columns.tolist())  # Vérification des colonnes

    # Nettoyage des données
    data.reset_index(inplace=True)  # Convertir l'index en colonne (Date)
    data["Date"] = pd.to_datetime(data["Date"]).dt.date  # Forcer le format propre de la Date

    # Remplacement de 'Close' par 'Adj Close' si nécessaire
    if "Adj Close" not in data.columns and "Close" in data.columns:
        data.rename(columns={"Close": "Adj Close"}, inplace=True)

    # Garder uniquement les colonnes nécessaires
    required_columns = ["Date", "Adj Close", "High", "Low", "Open", "Volume"]
    data = data[[col for col in required_columns if col in data.columns]]  # Ne garder que les colonnes existantes
    data.dropna(subset=["Adj Close"], inplace=True)  # Supprimer les lignes sans prix

    # Sauvegarde dans un fichier CSV
    output_path = output_folder / f"{asset_name.lower().replace(' ', '_')}_data.csv"
    data.to_csv(output_path, index=False)
    print(f"✅ Données sauvegardées dans {output_path}")

# 📌 Récupération des données pour chaque actif
def get_assets_data():
    for asset_name, ticker in assets.items():
        fetch_asset_data(ticker, asset_name, output_folder)

if __name__ == "__main__":
    get_assets_data()
