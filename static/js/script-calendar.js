/**
 * OBSŁUGA KALENDARZA Z NIETYPOWYMI ŚWIĘTAMI
 * 
 * Funkcjonalność:
 * - Wyświetlenie dzisiejszej daty w formacie polskim
 * - Pobranie danych o nietypowych świętach z zewnętrznego API
 * - Wyświetlenie faktów dnia w nagłówku
 */

document.addEventListener('DOMContentLoaded', function () {
  // Pobranie elementów DOM do wyświetlania daty i faktów
  const dateEl = document.getElementById('calendarDate');       // Element na datę
  const factEl = document.getElementById('calendarFact');       // Element na fakt/święto
  const dayEl = document.getElementById('calendarDay');         // Element na dzień (w ikonce)
  const monthEl = document.getElementById('calendarMonth');     // Element na miesiąc (w ikonce)

  // Jeśli brakuje głównych elementów, zakończ skrypt
  if (!dateEl || !factEl) return;

  /**
   * Nazwy miesięcy w pełnej postaci po polsku
   * Indeks odpowiada miesiącowi (0 = styczeń, 11 = grudzień)
   */
  const polishMonths = [
    'stycznia','lutego','marca','kwietnia','maja','czerwca',
    'lipca','sierpnia','września','października','listopada','grudnia'
  ];

  /**
   * Nazwy miesięcy w skróconej postaci (3 znaki)
   * Do wyświetlenia w ikonce kalendarza
   */
  const polishMonthsShort = ['Sty','Lut','Mar','Kwi','Maj','Cze','Lip','Sie','Wrz','Paź','Lis','Gru'];

  // Pobranie dzisiejszej daty
  const now = new Date();
  const day = now.getDate();                  // Dzień miesiąca (1-31)
  const month = now.getMonth() + 1;           // Miesiąc (1-12, bo getMonth() zwraca 0-11)

  // Ustawienie elementów ikony kalendarza (jeśli istnieją)
  if (dayEl) dayEl.textContent = day;
  if (monthEl) monthEl.textContent = polishMonthsShort[month - 1];

  // Wyświetlenie daty w formacie: "22 stycznia"
  dateEl.textContent = `${day} ${polishMonths[month - 1]}`;

  /**
   * URL do API z nietypowymi świętami
   * Serwis: https://github.com/pniedzwiedzinski/kalendarz-swiat-nietypowych
   * Format: /<miesiąc>/<dzień>.json
   */
  const holidaysUrl = `https://pniedzwiedzinski.github.io/kalendarz-swiat-nietypowych/${month}/${day}.json`;

  /**
   * Pobranie danych o świętach dla dzisiejszego dnia
   */
  fetch(holidaysUrl)
    .then(res => {
      // Sprawdzenie, czy odpowiedź jest OK
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    })
    .then(data => {
      // Jeśli istnieją dane i to tablica
      if (Array.isArray(data) && data.length > 0) {
        // Wyodrębnienie nazw świąt z obiektu
        const names = data.map(item => item.name).filter(Boolean);
        
        if (names.length === 0) {
          // Brak świąt
          factEl.textContent = 'Brak nietypowych świąt dziś.';
        } else if (names.length === 1) {
          // Jedno święto - wyświetl je w całości
          factEl.textContent = names[0];
        } else {
          // Wiele świąt - wyświetl pierwsze 3, a jeśli więcej to dodaj "i więcej..."
          const shown = names.slice(0, 3).join(' · ');
          factEl.textContent = names.length > 3 ? `${shown} i więcej...` : shown;
        }
      } else {
        // Brak świąt w bazie na dzisiaj
        factEl.textContent = 'Brak nietypowych świąt dziś.';
      }
    })
    .catch(err => {
      // Obsługa błędu (brak internetu, problem z API, itp.)
      console.warn('Holidays fetch failed', err);
      factEl.textContent = 'Nie można załadować świąt — spróbuj później.';
    });
});
