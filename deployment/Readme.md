---
title: YouTube Sentiment Analysis API
emoji: 🎭
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# YouTube Sentiment Analysis API

API REST pour l'analyse automatique du sentiment des commentaires YouTube.

## Endpoints

### GET /
Informations sur l'API

### GET /health
Vérifier l'état de l'API

### POST /predict_batch
Analyser un batch de commentaires

**Request Body:**
```json
{
  "comments": [
    "This video is amazing!",
    "I don't like this content",
    "It's okay, nothing special"
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "text": "This video is amazing!",
      "sentiment": "positif",
      "label": 1,
      "confidence": 0.95
    }
  ],
  "statistics": {
    "positive_percent": 33.3,
    "neutral_percent": 33.3,
    "negative_percent": 33.3
  },
  "total_comments": 3
}
```

## Utilisation
```python
import requests

url = "https://YOUR-SPACE-NAME.hf.space/predict_batch"
data = {
    "comments": ["Great video!", "Not good"]
}

response = requests.post(url, json=data)
print(response.json())
```

## Modèle

- **Vectorisation**: TF-IDF
- **Classification**: Logistic Regression
- **Classes**: Négatif (-1), Neutre (0), Positif (1)
```

### 1.7 Créer `.dockerignore` dans deployment/
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
.git/
.gitignore
README.md
.env
*.log