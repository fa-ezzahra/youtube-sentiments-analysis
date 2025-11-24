import pandas as pd
import joblib
import numpy as np
import os
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt
import seaborn as sns
import time

def train_model():
    """Entraîne le modèle de sentiment"""
    print("Chargement des données...")
    # Résoudre les chemins relatifs au dossier du script (`src/data`)
    base_dir = Path(__file__).resolve().parent
    processed_dir = base_dir / 'processed'
    project_root = base_dir.parent.parent
    models_dir = project_root / 'models'

    train_path = processed_dir / 'train.csv'
    test_path = processed_dir / 'test.csv'

    # Lire les jeux de données
    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    
    X_train = train_df['text'].values
    y_train = train_df['label'].values
    X_test = test_df['text'].values
    y_test = test_df['label'].values
    
    # Vectorisation TF-IDF
    print("\nVectorisation TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Entraînement avec optimisation des hyperparamètres
    print("\nEntraînement du modèle...")
    
    param_grid = {
        'C': [0.1, 1, 10],
        'max_iter': [100, 200],
        'solver': ['lbfgs', 'liblinear']
    }
    
    lr = LogisticRegression(random_state=42)
    
    grid_search = GridSearchCV(
        lr, 
        param_grid, 
        cv=3, 
        scoring='f1_weighted',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(X_train_vec, y_train)
    
    best_model = grid_search.best_estimator_
    print(f"\nMeilleurs paramètres : {grid_search.best_params_}")
    
    # Prédictions
    print("\nÉvaluation du modèle...")
    y_pred = best_model.predict(X_test_vec)
    
    # Métriques
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average='weighted')
    
    print(f"\n=== RÉSULTATS ===")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print(f"\nRapport de classification :")
    print(classification_report(y_test, y_pred, 
                                target_names=['Négatif', 'Neutre', 'Positif']))
    
    # Matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['Négatif', 'Neutre', 'Positif'],
                yticklabels=['Négatif', 'Neutre', 'Positif'])
    plt.title('Matrice de Confusion')
    plt.ylabel('Vraie classe')
    plt.xlabel('Classe prédite')
    plt.tight_layout()
    # S'assurer que le dossier models existe (au niveau du projet)
    os.makedirs(models_dir, exist_ok=True)
    cm_path = models_dir / 'confusion_matrix.png'
    plt.savefig(cm_path)
    print(f"\nMatrice de confusion sauvegardée : {cm_path}")
    
    # Test du temps d'inférence
    print("\nTest du temps d'inférence...")
    sample_texts = X_test[:50]
    sample_vec = vectorizer.transform(sample_texts)
    
    start_time = time.time()
    _ = best_model.predict(sample_vec)
    inference_time = (time.time() - start_time) * 1000
    
    print(f"Temps d'inférence pour 50 commentaires : {inference_time:.2f}ms")
    
    # Sauvegarder le modèle et le vectoriseur
    print("\nSauvegarde du modèle...")
    model_path = models_dir / 'sentiment_model.joblib'
    vec_path = models_dir / 'vectorizer.joblib'
    joblib.dump(best_model, model_path)
    joblib.dump(vectorizer, vec_path)
    print(f"Modèle sauvegardé : {model_path}")
    print(f"Vectorizer sauvegardé : {vec_path}")
    
    print("\n✓ Modèle entraîné et sauvegardé avec succès !")
    
    return best_model, vectorizer

if __name__ == "__main__":
    model, vectorizer = train_model()