document.addEventListener('DOMContentLoaded', function () {
  const dateEl = document.getElementById('calendarDate');
  const factEl = document.getElementById('calendarFact');
  const dayEl = document.getElementById('calendarDay');
  const monthEl = document.getElementById('calendarMonth');

  if (!dateEl || !factEl) return;

  const polishMonths = ['stycznia','lutego','marca','kwietnia','maja','czerwca','lipca','sierpnia','września','października','listopada','grudnia'];

  const now = new Date();
  const day = now.getDate();
  const month = now.getMonth() + 1; // 1-based

  const polishMonthsShort = ['Sty','Lut','Mar','Kwi','Maj','Cze','Lip','Sie','Wrz','Paź','Lis','Gru'];

  // Fill icon (if present)
  if (dayEl) dayEl.textContent = day;
  if (monthEl) monthEl.textContent = polishMonthsShort[month - 1];

  // Show date (day + month name)
  dateEl.textContent = `${day} ${polishMonths[month - 1]}`;

  // Use the provided JSON feed of obscure holidays: /<month>/<day>.json
  const holidaysUrl = `https://pniedzwiedzinski.github.io/kalendarz-swiat-nietypowych/${month}/${day}.json`;

  fetch(holidaysUrl)
    .then(res => {
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    })
    .then(data => {
      if (Array.isArray(data) && data.length > 0) {
        // join holiday names into a short string
        const names = data.map(item => item.name).filter(Boolean);
        if (names.length === 0) {
          factEl.textContent = 'Brak nietypowych świąt dziś.';
        } else if (names.length === 1) {
          factEl.textContent = names[0];
        } else {
          // show up to first 3, indicate if more
          const shown = names.slice(0, 3).join(' · ');
          factEl.textContent = names.length > 3 ? `${shown} i więcej...` : shown;
        }
      } else {
        factEl.textContent = 'Brak nietypowych świąt dziś.';
      }
    })
    .catch(err => {
      console.warn('Holidays fetch failed', err);
      factEl.textContent = 'Nie można załadować świąt — spróbuj później.';
    });
});
