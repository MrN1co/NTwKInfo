document.addEventListener('DOMContentLoaded', function() {
    const tagButtons = document.querySelectorAll('.tag-btn[data-tag]');
    const selectedTagsData = document.getElementById('selected-tags-data');
    
    if (!selectedTagsData) return;
    
    let selectedTags = new Set();
    try {
        const tagsJson = selectedTagsData.dataset.tags;
        if (tagsJson) {
            selectedTags = new Set(JSON.parse(tagsJson));
        }
    } catch (e) {
        console.error('Błąd parsowania tagów:', e);
    }
    
    let redirectTimer = null;
    
    // Funkcja aktualizująca wizualny stan przycisków
    function updateButtonStates() {
        tagButtons.forEach(button => {
            const tag = button.dataset.tag;
            if (tag === '' && selectedTags.size === 0) {
                button.classList.add('active');
            } else if (tag !== '' && selectedTags.has(tag)) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });
    }
    
    // Funkcja przekierowująca
    function scheduleRedirect() {
        // Anuluj poprzedni timer
        if (redirectTimer) {
            clearTimeout(redirectTimer);
        }
        

        redirectTimer = setTimeout(() => {
            const tagsParam = Array.from(selectedTags).join(',');
            const baseUrl = window.location.pathname;
            const url = tagsParam ? `${baseUrl}?tags=${tagsParam}` : baseUrl;
            window.location.href = url;
        }, 1000);
    }
    
    // Kliknięcia na przyciski tagów
    tagButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const tag = this.dataset.tag;
            
            if (tag === '') {
                // "Wszystko" - wyczyść wszystkie filtry
                selectedTags.clear();
            } else {
                // Tag konkretny - przełącz
                if (selectedTags.has(tag)) {
                    selectedTags.delete(tag);
                } else {
                    selectedTags.add(tag);
                }
            }
            
            updateButtonStates();
            scheduleRedirect();
        });
    });
});
