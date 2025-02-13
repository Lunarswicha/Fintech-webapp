import pandas as pd
import numpy as np

# Fonction pour calculer le rendement journalier
def calculate_daily_returns(data):
    """
    Calcule les rendements quotidiens d'un DataFrame de données.
    Args:
        data (pd.DataFrame): Données avec une colonne 'Adj Close'.
    Returns:
        pd.Series: Rendements quotidiens.
    """
    return data['Adj Close'].pct_change()

# Fonction pour analyser un actif
def analyze_asset(file_path, asset_name):
    """
    Analyse un fichier CSV d'un actif et calcule des métriques financières clés.
    Args:
        file_path (str): Chemin vers le fichier CSV.
        asset_name (str): Nom de l'actif.
    Returns:
        dict: Résumé des métriques calculées.
    """
    # Charger les données
    data = pd.read_csv(file_path)

    # Vérification de la colonne "Date"
    if "Date" in data.columns:
        data["Date"] = pd.to_datetime(data["Date"])
        data.set_index("Date", inplace=True)
    else:
        print(f"⚠️ Attention : Colonne 'Date' absente dans {file_path}. Vérifie la structure du CSV.")
        print(f"Colonnes trouvées : {data.columns.tolist()}")
        return None  # ✅ Correction : return maintenant à l'intérieur de la fonction

    # Vérification et conversion des colonnes numériques
    num_cols = ["Adj Close", "Close", "High", "Low", "Open", "Volume"]
    for col in num_cols:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")  # Convertit en float et remplace les erreurs par NaN

    # Vérification de la colonne 'Adj Close'
    if "Adj Close" not in data.columns:
        print(f"⚠️ Attention : Colonne 'Adj Close' absente dans {file_path}. Vérifie la structure du CSV.")
        return None

    # Calculer les rendements quotidiens
    daily_returns = calculate_daily_returns(data)

    # Calcul des métriques
    annualized_return = daily_returns.mean() * 252  # Rendement annuel moyen
    annualized_volatility = daily_returns.std() * np.sqrt(252)  # Volatilité annualisée
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility != 0 else np.nan  # Sharpe ratio

    # Résumé
    summary = {
        "Asset": asset_name,
        "Annualized Return (%)": round(annualized_return * 100, 2),
        "Annualized Volatility (%)": round(annualized_volatility * 100, 2),
        "Sharpe Ratio": round(sharpe_ratio, 2)
    }

    return summary

# Fonction principale pour analyser tous les actifs
def analyze_all_assets():
    """
    Analyse les actifs Bitcoin, S&P 500 et Or.
    Affiche les résultats sous forme de tableau.
    """
    # Chemins des fichiers
    assets = {
        "Bitcoin": "data/bitcoin_data.csv",
        "S&P 500": "data/s&p_500_data.csv",
        "Or": "data/or_data.csv"
    }

    # Analyser chaque actif
    results = []
    for asset_name, file_path in assets.items():
        print(f"Analyse de {asset_name}...")
        summary = analyze_asset(file_path, asset_name)
        if summary:  # Vérifier si l’analyse a bien retourné des données
            results.append(summary)

    # Créer un DataFrame pour les résultats
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv("data/asset_analysis_summary.csv", index=False)
        print("\nRésumé de l'analyse sauvegardé dans 'data/asset_analysis_summary.csv'")
        print(results_df)
    else:
        print("\n⚠️ Aucune analyse n'a été réalisée. Vérifie les fichiers CSV.")

if __name__ == "__main__":
    analyze_all_assets()
