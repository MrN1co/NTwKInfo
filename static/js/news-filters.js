document.addEventListener('DOMContentLoaded', function() {
    const tagButtons = document.querySelectorAll('.tag-btn[data-tag]');
    const selectedTagsData = document.getElementById('selected-tags-data');
    const newsItems = document.querySelectorAll('.news-item');
    const saveTagsBtn = document.getElementById('save-tags-btn');

    if (!selectedTagsData) return;

    let selectedTags = new Set();
    let savedTagsMode = false;
    let userSavedTags = new Set();
    
    try {
        const tagsJson = selectedTagsData.dataset.tags;
        if (tagsJson && tagsJson.trim() !== '') {
            selectedTags = new Set(JSON.parse(tagsJson));
        }
    } catch (e) {
        console.error('Błąd parsowania tagów:', e);
    }
    
    // Load user's saved tags if logged in
    async function loadUserSavedTags() {
        if (!saveTagsBtn) return;
        
        try {
            const response = await fetch('/auth/api/user/tags');
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.tags) {
                    userSavedTags = new Set(data.tags);
                }
            }
        } catch (e) {
            console.error('Błąd ładowania zapisanych tagów:', e);
        }
    }

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
    
    function updateSaveButton() {
        if (!saveTagsBtn) return;
        
        const heartIcon = saveTagsBtn.querySelector('svg');
        if (savedTagsMode) {
            // Filled heart
            heartIcon.innerHTML = '<path fill-rule="evenodd" d="M8 1.314C12.438-3.248 23.534 4.735 8 15-7.534 4.736 3.562-3.248 8 1.314"/>';
            heartIcon.classList.add('bi-heart-fill');
            heartIcon.classList.remove('bi-heart');
            saveTagsBtn.classList.add('active');
        } else {
            // Empty heart
            heartIcon.innerHTML = '<path d="m8 2.748-.717-.737C5.6.281 2.514.878 1.4 3.053c-.523 1.023-.641 2.5.314 4.385.92 1.815 2.834 3.989 6.286 6.357 3.452-2.368 5.365-4.542 6.286-6.357.955-1.886.838-3.362.314-4.385C13.486.878 10.4.28 8.717 2.01zM8 15C-7.333 4.868 3.279-3.04 7.824 1.143q.09.083.176.171a3 3 0 0 1 .176-.17C12.72-3.042 23.333 4.867 8 15"/>';
            heartIcon.classList.add('bi-heart');
            heartIcon.classList.remove('bi-heart-fill');
            saveTagsBtn.classList.remove('active');
        }
    }
    
    async function saveTagsToServer(tags) {
        const tagsArray = Array.from(tags);
        
        try {
            const response = await fetch('/auth/api/user/tags', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ tags: tagsArray })
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.success;
            }
            return false;
        } catch (e) {
            console.error('Błąd zapisywania tagów:', e);
            return false;
        }
    }

    function updateUrlParamWithoutReload() {
        const tagsParam = Array.from(selectedTags).join(',');
        const baseUrl = window.location.pathname;
        const url = tagsParam ? `${baseUrl}?tags=${encodeURIComponent(tagsParam)}` : baseUrl;
        window.history.replaceState({}, '', url);
    }

    function applyFilters() {
        // Pokaż wszystko, jeśli brak wybranych tagów
        if (selectedTags.size === 0) {
            newsItems.forEach(item => {
                item.style.display = '';
            });
            return;
        }

        newsItems.forEach(item => {
            const itemTagsRaw = item.dataset.tags || '';
            const itemTags = itemTagsRaw
                .split(',')
                .map(t => t.trim())
                .filter(Boolean);

            const hasAny = itemTags.some(t => selectedTags.has(t));
            item.style.display = hasAny ? '' : 'none';
        });
    }

    tagButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const tag = this.dataset.tag;

            if (tag === '') {
                selectedTags.clear();
            } else {
                if (selectedTags.has(tag)) {
                    selectedTags.delete(tag);
                } else {
                    selectedTags.add(tag);
                }
            }

            updateButtonStates();
            applyFilters();
            updateUrlParamWithoutReload();
            
            // If in saved tags mode, save changes to server
            if (savedTagsMode) {
                userSavedTags = new Set(selectedTags);
                saveTagsToServer(userSavedTags);
            }
        });
    });
    
    // Handle save tags button click
    if (saveTagsBtn) {
        saveTagsBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            if (!savedTagsMode) {
                // Activate saved tags mode
                savedTagsMode = true;
                
                // Load and apply saved tags
                if (userSavedTags.size > 0) {
                    selectedTags = new Set(userSavedTags);
                } else {
                    selectedTags.clear();
                }
                
                updateButtonStates();
                updateSaveButton();
                applyFilters();
                updateUrlParamWithoutReload();
            } else {
                // Deactivate saved tags mode
                savedTagsMode = false;
                
                // Show all news
                selectedTags.clear();
                
                updateButtonStates();
                updateSaveButton();
                applyFilters();
                updateUrlParamWithoutReload();
            }
        });
    }

    // Initialize
    loadUserSavedTags().then(() => {
        updateButtonStates();
        updateSaveButton();
        applyFilters();
        updateUrlParamWithoutReload();
    });
});
