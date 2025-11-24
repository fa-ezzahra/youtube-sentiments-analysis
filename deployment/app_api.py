from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import joblib
import numpy as np

app = FastAPI(title="YouTube Sentiment Analysis API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle
model = joblib.load("models/sentiment_model.joblib")
vectorizer = joblib.load("models/vectorizer.joblib")

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

SENTIMENT_MAP = {-1: "négatif", 0: "neutre", 1: "positif"}

@app.get("/")
async def root():
    return {"message": "YouTube Sentiment Analysis API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": True}

@app.post("/predict_batch", response_model=BatchResponse)
async def predict_batch(request: BatchRequest):
    try:
        comments_vec = vectorizer.transform(request.comments)
        predictions = model.predict(comments_vec)
        probabilities = model.predict_proba(comments_vec)
        
        results = []
        for text, pred, proba in zip(request.comments, predictions, probabilities):
            confidence = float(np.max(proba))
            results.append(SentimentResult(
                text=text[:100] + "..." if len(text) > 100 else text,
                sentiment=SENTIMENT_MAP[pred],
                label=int(pred),
                confidence=confidence
            ))
        
        unique, counts = np.unique(predictions, return_counts=True)
        total = len(predictions)
        
        statistics = {
            "positive_percent": float(counts[unique == 1][0] / total * 100) if 1 in unique else 0.0,
            "neutral_percent": float(counts[unique == 0][0] / total * 100) if 0 in unique else 0.0,
            "negative_percent": float(counts[unique == -1][0] / total * 100) if -1 in unique else 0.0,
        }
        
        return BatchResponse(results=results, statistics=statistics, total_comments=total)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))