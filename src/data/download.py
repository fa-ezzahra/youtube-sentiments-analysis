import pandas as pd
import requests
import os

def download_dataset():
    """Télécharge le dataset Reddit depuis GitHub"""
    url = "https://raw.githubusercontent.com/Himanshu-1703/reddit-sentiment-analysis/refs/heads/main/data/reddit.csv"
    
    print("Téléchargement du dataset...")
    response = requests.get(url)
    
    # Créer le dossier si nécessaire (chemin relatif au dossier `data`)
    os.makedirs('raw', exist_ok=True)

    # Sauvegarder le fichier dans le dossier `raw` local
    with open('raw/reddit.csv', 'wb') as f:
        f.write(response.content)

    # Charger et afficher les statistiques
    df = pd.read_csv('raw/reddit.csv')
    
    print("\n=== STATISTIQUES DU DATASET ===")
    print(f"Nombre total de commentaires : {len(df)}")
    print(f"\nDistribution des labels :")
    print(df['category'].value_counts())
    print(f"\nNombre de lignes : {df.shape[0]}")
    print(f"Nombre de colonnes : {df.shape[1]}")
    
    return df

if __name__ == "__main__":
    df = download_dataset()
    print("\nTéléchargement terminé !")