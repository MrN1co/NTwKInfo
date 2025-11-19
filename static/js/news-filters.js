document.addEventListener('DOMContentLoaded', function() {
    const tagButtons = document.querySelectorAll('.tag-btn');
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
    
    tagButtons.forEach(button => {
        button.addEventListener('click', function() {
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
            
            const tagsParam = Array.from(selectedTags).join(',');
            const baseUrl = window.location.pathname;
            const url = tagsParam ? `${baseUrl}?tags=${tagsParam}` : baseUrl;
            window.location.href = url;
        });
    });
});
