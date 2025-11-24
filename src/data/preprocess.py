import pandas as pd
import re
import os
from sklearn.model_selection import train_test_split

def clean_text(text):
    """Nettoie le texte des commentaires"""
    if pd.isna(text):
        return ""
    
    # Convertir en minuscules
    text = str(text).lower()
    
    # Supprimer les URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Supprimer les mentions (@username)
    text = re.sub(r'@\w+', '', text)
    
    # Supprimer les caractères spéciaux mais garder la ponctuation de base
    text = re.sub(r'[^a-zA-Z0-9\s,.!?]', '', text)
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def preprocess_data():
    """Prétraite les données et crée le split train/test"""
    print("Chargement des données...")
    df = pd.read_csv('raw/reddit.csv')
    
    # Renommer les colonnes pour plus de clarté
    df = df.rename(columns={'clean_comment': 'text', 'category': 'label'})
    
    # Nettoyer le texte
    print("Nettoyage du texte...")
    df['text'] = df['text'].apply(clean_text)
    
    # Supprimer les lignes vides
    df = df[df['text'].str.len() > 0]
    
    # Analyse exploratoire
    print("\n=== ANALYSE EXPLORATOIRE ===")
    print(f"Distribution des classes :")
    print(df['label'].value_counts())
    
    print(f"\nLongueur moyenne des textes : {df['text'].str.len().mean():.2f} caractères")
    print(f"Longueur min : {df['text'].str.len().min()}")
    print(f"Longueur max : {df['text'].str.len().max()}")
    
    # Split train/test (80/20)
    print("\nCréation du split train/test...")
    train_df, test_df = train_test_split(
        df, 
        test_size=0.2, 
        random_state=42, 
        stratify=df['label']
    )
    
    # Créer le dossier `processed` si nécessaire et sauvegarder les données prétraitées
    os.makedirs('processed', exist_ok=True)
    train_df.to_csv('processed/train.csv', index=False)
    test_df.to_csv('processed/test.csv', index=False)

    print(f"\nTrain set : {len(train_df)} exemples")
    print(f"Test set : {len(test_df)} exemples")
    print("\nDonnées sauvegardées dans processed/")
    
    return train_df, test_df

if __name__ == "__main__":
    train_df, test_df = preprocess_data()