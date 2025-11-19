document.addEventListener('DOMContentLoaded', function () {
  const dayEl = document.getElementById('calendarDay');
  const monthEl = document.getElementById('calendarMonth');
  const dateEl = document.getElementById('calendarDate');
  const factEl = document.getElementById('calendarFact');

  if (!dayEl || !monthEl || !dateEl || !factEl) return;

  const polishMonths = ['stycznia','lutego','marca','kwietnia','maja','czerwca','lipca','sierpnia','września','października','listopada','grudnia'];
  const polishMonthsShort = ['Sty','Lut','Mar','Kwi','Maj','Cze','Lip','Sie','Wrz','Paź','Lis','Gru'];
  const polishWeekdays = ['niedziela','poniedziałek','wtorek','środa','czwartek','piątek','sobota'];

  const now = new Date();
  const day = now.getDate();
  const monthIndex = now.getMonth();
  const weekdayIndex = now.getDay();

  // Fill calendar elements
  dayEl.textContent = day;
  monthEl.textContent = polishMonthsShort[monthIndex];
  dateEl.textContent = `${day} ${polishMonths[monthIndex]}, ${polishWeekdays[weekdayIndex]}`;

  // Fetch a fun fact about the date from NumbersAPI
  // e.g. https://numbersapi.com/11/19/date?json
  const numbersUrl = `https://numbersapi.com/${monthIndex + 1}/${day}/date?json`;

  fetch(numbersUrl)
    .then(res => {
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    })
    .then(data => {
      if (data && data.text) {
        factEl.textContent = data.text;
      } else {
        factEl.textContent = 'Brak ciekawostki na dziś.';
      }
    })
    .catch(() => {
      // graceful fallback if API fails
      factEl.textContent = 'Nie można załadować ciekawostki — spróbuj później.';
    });
});
