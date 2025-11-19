document.addEventListener('DOMContentLoaded', function() {
    const tagButtons = document.querySelectorAll('.tag-btn');
    const selectedTagsData = document.getElementById('selected-tags-data');
    let selectedTags = new Set(JSON.parse(selectedTagsData.dataset.tags || '[]'));
    
    tagButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tag = this.dataset.tag;
            
            if (tag === '') {
                // "Wszystko" - wyczyść wszystkie filtry
                selectedTags.clear();
            } else {
                // Tag konkretny
                if (selectedTags.has(tag)) {
                    selectedTags.delete(tag);
                } else {
                    selectedTags.add(tag);
                }
            }
            
            // Zbuduj URL z parametrami
            const tagsParam = Array.from(selectedTags).join(',');
            const baseUrl = window.location.pathname;
            const url = tagsParam ? `${baseUrl}?tags=${tagsParam}` : baseUrl;
            window.location.href = url;
        });
    });
});
