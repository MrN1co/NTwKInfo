document.addEventListener('click', function (e) {
    // Delegated listener: any element with .news-link
    var el = e.target.closest && e.target.closest('.news-link');
    if (!el) return;

    // Zapobiega wielokrotnemu wysyłaniu (np. gdy link jest zagnieżdżony)
    if (e.news_history_logged) return;
    e.news_history_logged = true;

    var url = el.getAttribute('href') || el.dataset.url;
    if (!url) return;

    var title = el.getAttribute('data-title') || el.textContent.trim();
    var source = el.getAttribute('data-source') || (el.closest('[data-source]') && el.closest('[data-source]').getAttribute('data-source')) || '';

    fetch('/news/history/log', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url, title: title, source: source })
    }).catch(function () {
        // swallow errors silently
    });
}, true); // Capture phase, aby złapać event wcześniej

// Historia - obsługa przycisków na stronie history.html
document.addEventListener('DOMContentLoaded', function() {
  var clearBtn = document.getElementById('clear-history');
  if (clearBtn) {
    clearBtn.addEventListener('click', function() {
      if (!confirm('Na pewno wyczyścić historię?')) return;
      fetch('/news/history/clear', { method: 'POST' })
        .then(function(r){ if (r.ok) location.reload(); });
    });
  }

  document.querySelectorAll('.delete-entry').forEach(function(btn){
    btn.addEventListener('click', function(){
      var tr = this.closest('tr');
      var id = tr && tr.dataset.entryId;
      if (!id) return;
      fetch('/news/history/delete/' + id, { method: 'POST' })
        .then(function(r){ if (r.ok) location.reload(); });
    });
  });
});