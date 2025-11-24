// Configuration de l'API
const API_URL = 'http://localhost:8000'; // Changer après déploiement

// Éléments DOM
const analyzeBtn = document.getElementById('analyzeBtn');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const status = document.getElementById('status');
const themeToggle = document.getElementById('themeToggle');
const commentsList = document.getElementById('commentsList');
const copyBtn = document.getElementById('copyBtn');
const totalComments = document.getElementById('totalComments');
const filterBtns = document.querySelectorAll('.filter-btn');

let allComments = [];
let currentFilter = 'all';

// Gestion du thème
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    themeToggle.textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('darkMode', isDark);
});

// Charger le thème sauvegardé
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
    themeToggle.textContent = '☀️';
}

// Analyse des commentaires
analyzeBtn.addEventListener('click', async () => {
    try {
        hideStatus();
        showLoading();
        hideResults();

        // Vérifier l'onglet actif
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Vérification 1 : Est-ce une page YouTube ?
        if (!tab.url || !tab.url.includes('youtube.com/watch')) {
            showStatus('❌ Veuillez ouvrir une vidéo YouTube (youtube.com/watch?v=...)', 'error');
            hideLoading();
            return;
        }

        // Vérification 2 : Injecter le content script si nécessaire
        try {
            await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['content.js']
            });
            console.log('Content script injecté');
        } catch (e) {
            console.log('Content script déjà présent ou erreur:', e);
        }

        // Attendre un peu pour que le script soit prêt
        await new Promise(resolve => setTimeout(resolve, 500));

        // Vérification 3 : Extraire les commentaires
        let response;
        try {
            response = await chrome.tabs.sendMessage(tab.id, { action: 'extractComments' });
        } catch (error) {
            console.error('Erreur lors de l\'envoi du message:', error);
            showStatus('❌ Erreur de communication. Veuillez recharger la page YouTube (F5) et réessayer.', 'error');
            hideLoading();
            return;
        }

        // Vérification 4 : Commentaires trouvés ?
        if (!response || !response.comments || response.comments.length === 0) {
            showStatus('⚠️ Aucun commentaire trouvé. Faites défiler la page pour charger plus de commentaires, puis réessayez.', 'error');
            hideLoading();
            return;
        }

        console.log(`${response.comments.length} commentaires extraits`);

        // Vérification 5 : API accessible ?
        try {
            const healthCheck = await fetch(`${API_URL}/health`);
            if (!healthCheck.ok) {
                throw new Error('API non accessible');
            }
        } catch (error) {
            showStatus('❌ API non accessible. Assurez-vous que l\'API est lancée (python src/api/app.py)', 'error');
            hideLoading();
            return;
        }

        // Envoyer à l'API
        showStatus('🔄 Envoi à l\'API...', 'success');

        const apiResponse = await fetch(`${API_URL}/predict_batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                comments: response.comments
            })
        });

        if (!apiResponse.ok) {
            throw new Error(`Erreur API: ${apiResponse.status}`);
        }

        const data = await apiResponse.json();

        allComments = data.results;
        displayResults(data);

    } catch (error) {
        console.error('Erreur:', error);
        showStatus(`❌ Erreur: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
});

function displayResults(data) {
    // Afficher les statistiques
    document.getElementById('positivePercent').textContent =
        `${data.statistics.positive_percent.toFixed(1)}%`;
    document.getElementById('neutralPercent').textContent =
        `${data.statistics.neutral_percent.toFixed(1)}%`;
    document.getElementById('negativePercent').textContent =
        `${data.statistics.negative_percent.toFixed(1)}%`;

    totalComments.textContent = `${data.total_comments} commentaires`;

    // Afficher les commentaires
    renderComments();

    showResults();
    showStatus('✅ Analyse terminée avec succès!', 'success');
}

function renderComments() {
    commentsList.innerHTML = '';

    const filteredComments = currentFilter === 'all'
        ? allComments
        : allComments.filter(c => c.sentiment === currentFilter);

    if (filteredComments.length === 0) {
        commentsList.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 20px;">Aucun commentaire dans cette catégorie</p>';
        return;
    }

    filteredComments.forEach(comment => {
        const div = document.createElement('div');
        div.className = 'comment-item';
        div.innerHTML = `
            <div class="comment-header">
                <span class="sentiment-badge ${comment.sentiment}">${comment.sentiment.toUpperCase()}</span>
                <span class="confidence">${(comment.confidence * 100).toFixed(1)}%</span>
            </div>
            <div class="comment-text">${escapeHtml(comment.text)}</div>
        `;
        commentsList.appendChild(div);
    });
}

// Fonction pour échapper le HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Filtres
filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        renderComments();
    });
});

// Copier les résultats
copyBtn.addEventListener('click', () => {
    const text = allComments.map(c =>
        `[${c.sentiment.toUpperCase()}] (${(c.confidence * 100).toFixed(1)}%) ${c.text}`
    ).join('\n\n');

    navigator.clipboard.writeText(text).then(() => {
        showStatus('✅ Résultats copiés!', 'success');
        setTimeout(hideStatus, 2000);
    }).catch(err => {
        showStatus('❌ Erreur lors de la copie', 'error');
    });
});

// Fonctions utilitaires
function showLoading() {
    loading.classList.remove('hidden');
    analyzeBtn.disabled = true;
}

function hideLoading() {
    loading.classList.add('hidden');
    analyzeBtn.disabled = false;
}

function showResults() {
    results.classList.remove('hidden');
}

function hideResults() {
    results.classList.add('hidden');
}

function showStatus(message, type) {
    status.textContent = message;
    status.className = `status ${type}`;
    status.classList.remove('hidden');
}

function hideStatus() {
    status.classList.add('hidden');
}