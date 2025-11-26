document.addEventListener('DOMContentLoaded', function() {
    const tagButtons = document.querySelectorAll('.tag-btn[data-tag]');
    const selectedTagsData = document.getElementById('selected-tags-data');
    const newsItems = document.querySelectorAll('.news-item');

    if (!selectedTagsData) return;

    let selectedTags = new Set();
    try {
        const tagsJson = selectedTagsData.dataset.tags;
        if (tagsJson && tagsJson.trim() !== '') {
            selectedTags = new Set(JSON.parse(tagsJson));
        }
    } catch (e) {
        console.error('Błąd parsowania tagów:', e);
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
        });
    });

    updateButtonStates();
    applyFilters();
    updateUrlParamWithoutReload();
});
