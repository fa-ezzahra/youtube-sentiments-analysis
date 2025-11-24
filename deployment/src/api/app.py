from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import joblib
import numpy as np
from pathlib import Path

# Créer l'application FastAPI
app = FastAPI(
    title="YouTube Sentiment Analysis API",
    description="API pour l'analyse de sentiment des commentaires YouTube",
    version="1.0.0"
)

# Configuration CORS pour l'extension Chrome
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle et le vectoriseur au démarrage
MODEL_PATH = Path("models/sentiment_model.joblib")
VECTORIZER_PATH = Path("models/vectorizer.joblib")

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("✓ Modèle et vectoriseur chargés avec succès")
except Exception as e:
    print(f"✗ Erreur lors du chargement du modèle : {e}")
    model = None
    vectorizer = None

# Modèles Pydantic pour la validation
class Comment(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class BatchRequest(BaseModel):
    comments: List[str] = Field(..., min_items=1, max_items=100)

class SentimentResult(BaseModel):
    text: str
    sentiment: str
    label: int
    confidence: float

class BatchResponse(BaseModel):
    results: List[SentimentResult]
    statistics: Dict[str, float]
    total_comments: int

# Mapping des labels
SENTIMENT_MAP = {
    -1: "négatif",
    0: "neutre",
    1: "positif"
}

@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "YouTube Sentiment Analysis API",
        "status": "running",
        "endpoints": {
            "/health": "Vérifier l'état de l'API",
            "/predict_batch": "Analyser un batch de commentaires"
        }
    }

@app.get("/health")
async def health_check():
    """Vérifie l'état de l'API et du modèle"""
    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé"
        )
    
    return {
        "status": "healthy",
        "model_loaded": True,
        "api_version": "1.0.0"
    }

@app.post("/predict_batch", response_model=BatchResponse)
async def predict_batch(request: BatchRequest):
    """Analyse un batch de commentaires"""
    
    if model is None or vectorizer is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non disponible"
        )
    
    try:
        # Vectoriser les commentaires
        comments_vec = vectorizer.transform(request.comments)
        
        # Prédictions
        predictions = model.predict(comments_vec)
        probabilities = model.predict_proba(comments_vec)
        
        # Créer les résultats
        results = []
        for text, pred, proba in zip(request.comments, predictions, probabilities):
            confidence = float(np.max(proba))
            results.append(SentimentResult(
                text=text[:100] + "..." if len(text) > 100 else text,
                sentiment=SENTIMENT_MAP[pred],
                label=int(pred),
                confidence=confidence
            ))
        
        # Calculer les statistiques
        unique, counts = np.unique(predictions, return_counts=True)
        total = len(predictions)
        
        statistics = {
            "positive_percent": float(counts[unique == 1][0] / total * 100) if 1 in unique else 0.0,
            "neutral_percent": float(counts[unique == 0][0] / total * 100) if 0 in unique else 0.0,
            "negative_percent": float(counts[unique == -1][0] / total * 100) if -1 in unique else 0.0,
        }
        
        return BatchResponse(
            results=results,
            statistics=statistics,
            total_comments=total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la prédiction : {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)