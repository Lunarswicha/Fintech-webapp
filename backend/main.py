import os
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chemin des fichiers CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILES = {
    "bitcoin": os.path.join(BASE_DIR, "../Data/bitcoin_data.csv"),
    "s&p_500": os.path.join(BASE_DIR, "../Data/s&p_500_data.csv"),
    "or": os.path.join(BASE_DIR, "../Data/or_data.csv"),
}

# Fonction de lecture des fichiers CSV
def read_csv_data(asset_name: str):
    file_path = CSV_FILES.get(asset_name)
    if file_path and os.path.exists(file_path):
        try:
            data = pd.read_csv(file_path)
            if "Date" in data.columns:
                return data.to_dict(orient="records")
            else:
                return {"error": f"Le fichier {file_path} ne contient pas de colonne 'Date'."}
        except Exception as e:
            return {"error": f"Erreur lors de la lecture du fichier CSV : {str(e)}"}
    return {"error": f"Aucun fichier CSV trouvé pour l'actif '{asset_name}'."}

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l'API backend de FastAPI !"}

@app.get("/data/{asset}")
async def get_asset_data(asset: str):
    if asset not in CSV_FILES:
        return {"error": f"L'actif '{asset}' n'est pas disponible."}
    
    data = read_csv_data(asset)
    return data if isinstance(data, list) else {"error": data["error"]}
