import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns

# 📌 Correction du nom du fichier S&P 500
assets = {
    "Bitcoin": "data/bitcoin_data.csv",
    "S&P 500": "data/s&p_500_data.csv",  # Nouveau nom du fichier sans "&"
    "Or": "data/or_data.csv"
}

# Définition des couleurs pour les graphiques
colors = {
    "Bitcoin": "orange",
    "S&P 500": "blue",
    "Or": "gold"
}

# Initialisation d'un DataFrame pour stocker les prix ajustés
prices = pd.DataFrame()

# Chargement des données des actifs
for asset, file_path in assets.items():
    data = pd.read_csv(file_path)

    # Vérification de la colonne 'Date'
    if "Date" not in data.columns:
        print(f"⚠️ Problème avec le fichier {file_path}, 'Date' non trouvé.")
        continue

    # Conversion de la date
    data["Date"] = pd.to_datetime(data["Date"])

    # Vérification et utilisation de "Adj Close" ou "Close"
    if "Adj Close" not in data.columns:
        print(f"⚠️ 'Adj Close' absent pour {asset}, utilisation de 'Close'.")
        data.rename(columns={"Close": "Adj Close"}, inplace=True)

    # 📌 Correction : Conversion explicite des prix en float
    data["Adj Close"] = pd.to_numeric(data["Adj Close"], errors="coerce")

    # Stockage des prix ajustés dans le DataFrame
    prices[asset] = data.set_index("Date")["Adj Close"]

# ✅ Vérification du chargement des données
print("\n📊 Aperçu des données chargées :")
print(prices.head())

# 📌 **1. Affichage des courbes de prix**
plt.figure(figsize=(12, 6))
for asset in assets.keys():
    plt.plot(prices.index, prices[asset].astype(float), label=asset, color=colors[asset])  # 🔥 Correction ici

plt.title("Évolution des prix sur 5 ans")
plt.xlabel("Année")
plt.ylabel("Prix ajusté (USD)")
plt.legend()
plt.grid(True)
plt.show()

# 📌 **2. Comparaison de la performance cumulée**
returns = prices.pct_change().dropna()
cumulative_returns = (1 + returns).cumprod()

plt.figure(figsize=(12, 6))
for asset in assets.keys():
    plt.plot(cumulative_returns.index, cumulative_returns[asset].astype(float), label=asset, color=colors[asset])

plt.title("Performance cumulée des actifs")
plt.xlabel("Année")
plt.ylabel("Performance cumulée")
plt.legend()
plt.grid(True)
plt.show()

# 📌 **3. Analyse de la volatilité**
volatility = returns.rolling(window=30).std() * (252 ** 0.5)  # Annualisée

plt.figure(figsize=(12, 6))
for asset in assets.keys():
    plt.plot(volatility.index, volatility[asset].astype(float), label=asset, color=colors[asset])

plt.title("Volatilité mobile (30 jours)")
plt.xlabel("Année")
plt.ylabel("Volatilité annualisée")
plt.legend()
plt.grid(True)
plt.show()

# 📌 **4. Heatmap des corrélations**
correlation_matrix = returns.corr()
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", linewidths=0.5)
plt.title("Corrélation entre les actifs")
plt.show()

# 📌 **5. Calcul des performances en pourcentage (%)**
performance_5y = ((prices.iloc[-1] / prices.iloc[0]) - 1) * 100  # Variation en %
performance_df = pd.DataFrame(performance_5y, columns=["Performance sur 5 ans (%)"])
performance_df = performance_df.sort_values(by="Performance sur 5 ans (%)", ascending=False)

print("\n📈 Performance des actifs sur 5 ans (%) :")
print(performance_df)

# 📌 **6. Affichage des performances en bar chart**
plt.figure(figsize=(8, 5))
plt.barh(performance_df.index, performance_df["Performance sur 5 ans (%)"], color=["orange", "blue", "gold"])
plt.xlabel("Performance (%)")
plt.ylabel("Actifs")
plt.title("Performance des actifs sur 5 ans")
plt.grid(axis="x")
plt.show()

# 📌 **7. Comparaison entre actifs : Ratio de surperformance**
best_asset = performance_df.index[0]
worst_asset = performance_df.index[-1]
ratio_surperformance = performance_df.loc[best_asset, "Performance sur 5 ans (%)"] / performance_df.loc[worst_asset, "Performance sur 5 ans (%)"]

print(f"\n🚀 {best_asset} a surperformé {worst_asset} d'un facteur de {round(ratio_surperformance, 2)}x.")
