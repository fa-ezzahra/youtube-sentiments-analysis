# 🎭 YouTube Sentiment Analysis

Système complet MLOps pour l'analyse automatique du sentiment des commentaires YouTube.

## 🚀 Fonctionnalités

- ✅ Modèle ML entraîné (TF-IDF + Logistic Regression)
- ✅ API REST FastAPI déployée sur Hugging Face
- ✅ Extension Chrome avec interface moderne
- ✅ Pipeline de tests et validation
- ✅ Déploiement Docker

## 📁 Structure du projet
```
youtube-sentiment-analysis/
├── data/
│   ├── raw/          # Données brutes
│   └── processed/    # Données prétraitées
├── models/           # Modèles entraînés
├── src/
│   ├── data/         # Scripts de traitement
│   ├── models/       # Entraînement
│   └── api/          # API FastAPI
├── chrome-extension/ # Extension Chrome
├── deployment/       # Fichiers de déploiement
└── logs/            # Logs
```

## 🔧 Installation

### Prérequis
- Python 3.10+
- Docker
- Google Chrome

### Installation locale
```bash
# Cloner le repository
git clone https://github.com/VOTRE-USERNAME/youtube-sentiment-analysis.git
cd youtube-sentiment-analysis

# Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Télécharger les données
python src/data/download_data.py

# Prétraiter
python src/data/preprocess.py

# Entraîner le modèle
python src/models/train.py

# Lancer l'API
python src/api/app.py
```

## 🐳 Déploiement Docker
```bash
cd deployment
docker build -t youtube-sentiment-api .
docker run -p 7860:7860 youtube-sentiment-api
```

## 🌐 API en ligne

L'API est déployée sur Hugging Face Spaces :
- URL : `https://VOTRE-SPACE.hf.space`
- Documentation : `https://VOTRE-SPACE.hf.space/docs`

## 🔌 Extension Chrome

1. Ouvrez Chrome
2. Allez dans `chrome://extensions/`
3. Activez "Mode développeur"
4. Cliquez "Charger l'extension non empaquetée"
5. Sélectionnez le dossier `chrome-extension/`

## 📊 Performance du modèle

- Accuracy : 85%+
- F1-Score : 0.80+
- Temps d'inférence : <100ms pour 50 commentaires

## 👥 Auteur

Fezzahra - ENSAM Rabat

## 📄 License

MIT License