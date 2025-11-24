// Content script pour extraire les commentaires YouTube

console.log('🎬 YouTube Sentiment Analyzer: Content script chargé');

function extractComments() {
    console.log('🔍 Extraction des commentaires...');

    const comments = [];

    // Attendre que les commentaires soient chargés
    const commentElements = document.querySelectorAll('ytd-comment-thread-renderer #content-text');

    console.log(`Éléments de commentaires trouvés: ${commentElements.length}`);

    commentElements.forEach((element, index) => {
        const text = element.textContent.trim();
        if (text && text.length > 0) {
            comments.push(text);
            if (index < 3) {
                console.log(`Commentaire ${index + 1}: ${text.substring(0, 50)}...`);
            }
        }
    });

    console.log(`✅ Total de commentaires extraits: ${comments.length}`);

    return comments;
}

// Écouter les messages du popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('📨 Message reçu:', request);

    if (request.action === 'extractComments') {
        try {
            const comments = extractComments();
            console.log(`📤 Envoi de ${comments.length} commentaires au popup`);
            sendResponse({
                comments: comments,
                count: comments.length,
                success: true
            });
        } catch (error) {
            console.error('❌ Erreur lors de l\'extraction:', error);
            sendResponse({
                comments: [],
                count: 0,
                success: false,
                error: error.message
            });
        }
    }

    return true; // Important pour les réponses asynchrones
});

console.log('✅ Content script prêt à recevoir des messages');