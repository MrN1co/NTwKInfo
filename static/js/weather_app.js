// static/app.js

// Mały skrót do wybierania elementów
const $ = (sel) => document.querySelector(sel);

// =================== DATA W TOPBARZE ===================

function formatToday() {
  const d = new Date();
  const opts = {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  };
  return d.toLocaleDateString("pl-PL", opts);
}

// =================== KOMUNIKACJA Z BACKENDEM ===================

// Pobranie prognozy z backendu.
// Bez parametrów -> domyślna lokalizacja (Kraków),
// z lat/lon -> prognoza dla wskazanych współrzędnych.
async function fetchForecast(lat, lon, label = null) {
  let url = "/weather/api/forecast";

  
  const params = new URLSearchParams();

  if (lat != null && lon != null) {
    params.append("lat", lat);
    params.append("lon", lon);
  }

  if (label) {
    params.append("label", label); // <<< NAZWA MIASTA
  }

  if (params.toString().length > 0) {
    url += "?" + params.toString();
  }

  const res = await fetch(url);

  if (!res.ok) {
    const msg = await res.text();
    console.error("Forecast error response:", msg);
    throw new Error(`Błąd pobierania prognozy: ${res.status} ${msg}`);
  }

  const data = await res.json();
  return data;
}
// Funkcja do pobrania współrzędnych miasta z backendu
async function geocodeCity(name) {
  const url = `/weather/api/geocode?q=${encodeURIComponent(name)}`;
  const res = await fetch(url);

  if (!res.ok) {
    const msg = await res.text();
    throw new Error(`Błąd geokodowania: ${res.status} ${msg}`);
  }

  const data = await res.json();
  if (!data || data.length === 0) {
    throw new Error("Nie znaleziono miasta.");
  }

  return data[0]; // pierwszy wynik
}

// =================== STAN APLIKACJI ===================

// aktualne koordynaty do /api/forecast i /plot.png
const currentCoords = {
  lat: 50.0647,   // Kraków – domyślnie (spójne z backendem)
  lon: 19.9450,
};

// CACHE: localStorage TTL (ms)
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minut

function cacheKeyFor(lat, lon, label){
  if (label) return `forecast_label_${label}`;
  return `forecast_${lat}_${lon}`;
}

function getCachedForecast(key){
  try{
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const obj = JSON.parse(raw);
    if (!obj || !obj.ts) return null;
    if (Date.now() - obj.ts > CACHE_TTL_MS) {
      localStorage.removeItem(key);
      return null;
    }
    return obj.data;
  }catch(e){
    return null;
  }
}

function setCachedForecast(key, data){
  try{
    const obj = { ts: Date.now(), data };
    localStorage.setItem(key, JSON.stringify(obj));
  }catch(e){ /* ignore */ }
}

// Cache for hourly JSON (short TTL)
const HOURLY_CACHE_TTL = 30 * 1000; // 30s
function hourlyCacheKey(lat, lon, day){
  return `hourly_${lat}_${lon}_${day}`;
}
function getCachedHourly(key){
  try{
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const obj = JSON.parse(raw);
    if (!obj || !obj.ts) return null;
    if (Date.now() - obj.ts > HOURLY_CACHE_TTL) { localStorage.removeItem(key); return null; }
    return obj.data;
  }catch(e){ return null; }
}
function setCachedHourly(key, data){
  try{ localStorage.setItem(key, JSON.stringify({ ts: Date.now(), data })); }catch(e){}
}

// nazwa miasta
let currentCity = "Kraków";

// który dzień pokazuje wykres (0 = dziś, 1 = jutro, …)
let chartDayOffset = 0;
// maksymalny offset (np. dla 7-dniowej prognozy: 0..6)
const MAX_CHART_OFFSET = 6;

// przechowaj wszystkie dni prognozy
let allForecastDays = [];

// =================== RENDEROWANIE UI – GŁÓWNA KARTA ===================

function renderForecast(data) {
  if (!data || !data.days || data.days.length === 0) {
    throw new Error("Brak danych prognozy");
  }

  // Przechowaj wszystkie dni dla później
  allForecastDays = data.days;

  const today = data.days[0];

  // Zaktualizuj globalne koordynaty (jeśli backend je zwrócił)
  if (typeof data.lat === "number" && typeof data.lon === "number") {
    currentCoords.lat = data.lat;
    currentCoords.lon = data.lon;
  }

  // Nazwa miasta - przechowaj i wyświetl
  currentCity = data.city || "Lokalizacja";
  $("#cityName").textContent = currentCity;
  
  // Wyświetl datę
  $("#currentDate").textContent = "Dziś";

  // Temperatura, opis, ciśnienie, opady
  $("#currentTemp").textContent =
    (today.t_day != null ? `${Math.round(today.t_day)}°C` : (today.t_max != null ? `${Math.round(today.t_max)}°C` : "--°C"));

  $("#currentDesc").textContent = today.description || "";

  $("#currentPressure").textContent =
    today.pressure != null
      ? `${Math.round(today.pressure)}`
      : "--";

  $("#currentPrecip").textContent =
    today.precip_mm != null
      ? `${today.precip_mm.toFixed(1)}`
      : "--";

  // Ikona aktualnej pogody (iconUrl pochodzi z icons.js)
  if (today.icon) {
    $("#currentIcon").src = iconUrl(today.icon);
    $("#currentIcon").alt = today.description || "Ikona pogody";
  } else {
    $("#currentIcon").removeAttribute("src");
    $("#currentIcon").alt = "";
  }

  // Preload ikon dla wszystkich dni, aby zmniejszyć opóźnienia przy ładowaniu obrazków
  data.days.forEach(d => {
    if (d.icon){
      const img = new Image();
      img.src = iconUrl(d.icon);
    }
  });

  // Pasek 7-dniowej prognozy
  renderForecastStrip(data.days);

  // Po zmianie prognozy resetujemy wykres na "Dziś"
  chartDayOffset = 0;
  updateChart();
  updateCurrentDayPanel(0);  // Zaktualizuj lewy panel dla dnia 0

  // Po wyrenderowaniu prognozy sprawdź, czy aktualne miasto jest w ulubionych
  try{
    refreshFavorites().then((favs) => {
      try{
        const btn = document.getElementById('favoriteBtn');
        if (!btn) return;
        const found = (favs || []).some(f => {
          if (!f || !f.city) return false;
          return String(f.city).toLowerCase() === String(currentCity).toLowerCase();
        });
        setFavoriteButtonActive(found);
      }catch(e){ console.warn('set favorite state failed', e); }
    }).catch(()=>{});
  }catch(e){}
}

// Pasek kart z prognozą na kolejne dni
function renderForecastStrip(days) {
  const strip = $("#forecastStrip");
  strip.innerHTML = "";

  days.slice(0, 7).forEach((d, idx) => {
    const card = document.createElement("div");
    card.className = "day-card";
    card.dataset.dayIndex = idx;  // Dodaj indeks dnia

    // Dzisiaj / Jutro / nazwa dnia tygodnia
    let label;
    if (idx === 0) label = "dzisiaj";
    else if (idx === 1) label = "jutro";
    else {
      const date = d.date ? new Date(d.date) : null;
      label = date
        ? date.toLocaleDateString("pl-PL", { weekday: "long" })
        : "";
    }

    const max = d.t_max != null ? Math.round(d.t_max) + "°" : "--";
    const min = d.t_min != null ? Math.round(d.t_min) + "°" : "--";

    card.innerHTML = `
      <div class="day-name">${label}</div>
      ${
        d.icon
          ? `<img class="day-icon" src="${iconUrl(d.icon)}" alt="">`
          : ""
      }
      <div class="temps"><strong>${max}</strong> / ${min}</div>
    `;

    // Jeśli to 6. lub 7. dzień (ostatnie dwa kafelki), oznacz jako disabled i nie dodawaj listenera
    if (idx >= 5) {
      card.classList.add("disabled");
      card.setAttribute("aria-disabled", "true");
      // Informacja tooltipowa dla użytkownika
      card.setAttribute(
        "title",
        "Godzinowa prognoza dla tego dnia nie jest dostępna"
      );
      // Nie dajemy tabIndex (nie fokusowalny)
      card.tabIndex = -1;
    } else {
      // Event listener - zmiana wykresu po kliknięciu
      card.addEventListener("click", () => {
        chartDayOffset = idx;
        updateChart();
        updateForecastStripActive();  // Zaznacz wybrany dzień
        updateCurrentDayPanel(idx);   // Zaktualizuj lewy panel z danymi wybranego dnia
      });
      // Umożliwienie focusu klawiaturą
      card.tabIndex = 0;
      card.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          card.click();
        }
      });
    }

    strip.appendChild(card);
  });

  updateForecastStripActive();  // Zaznacz "dziś" na start
}

// Funkcja do aktualizowania lewego panelu z danymi wybranego dnia
function updateCurrentDayPanel(dayIndex) {
  if (!allForecastDays || !allForecastDays[dayIndex]) return;

  const day = allForecastDays[dayIndex];

  // Temperatura, opis, ciśnienie, opady
  $("#currentTemp").textContent =
    (day.t_day != null ? `${Math.round(day.t_day)}°C` : (day.t_max != null ? `${Math.round(day.t_max)}°C` : "--°C"));

  $("#currentDesc").textContent = day.description || "";

  $("#currentPressure").textContent =
    day.pressure != null
      ? `${Math.round(day.pressure)}`
      : "--";

  $("#currentPrecip").textContent =
    day.precip_mm != null
      ? `${day.precip_mm.toFixed(1)}`
      : "--";

  // Ikona pogody na wybrany dzień
  if (day.icon) {
    $("#currentIcon").src = iconUrl(day.icon);
    $("#currentIcon").alt = day.description || "Ikona pogody";
  } else {
    $("#currentIcon").removeAttribute("src");
    $("#currentIcon").alt = "";
  }

  // Zaktualizuj datę w lewym panelu
  const now = new Date();
  const target = new Date(now.getTime() + dayIndex * 24 * 60 * 60 * 1000);

  const options = {
    weekday: "long",
    day: "numeric",
    month: "long",
  };

  let dateLabel;
  if (dayIndex === 0) dateLabel = "Dziś";
  else if (dayIndex === 1) dateLabel = "Jutro";
  else dateLabel = target.toLocaleDateString("pl-PL", options);

  // Wyświetl nazwę miasta i datę oddzielnie
  $("#cityName").textContent = currentCity;
  $("#currentDate").textContent = dateLabel;
}

// Funkcja do zaznaczania aktywnego dnia w panelu prognozy
function updateForecastStripActive() {
  const cards = document.querySelectorAll(".day-card");
  cards.forEach((card) => {
    const dayIndex = parseInt(card.dataset.dayIndex, 10);
    if (dayIndex === chartDayOffset) {
      card.classList.add("active");
    } else {
      card.classList.remove("active");
    }
  });
}

// =================== ŁADOWANIE DANYCH ===================

// Domyślna lokalizacja (bez parametrów -> Kraków po stronie backendu)
async function loadDefault() {
  const key = cacheKeyFor(currentCoords.lat, currentCoords.lon, null);
  const cached = getCachedForecast(key);
  if (cached){
    try{ renderForecast(cached); }catch(e){ console.warn('Cached render failed', e); }
    // fetch fresh in background
    fetchForecast().then((fresh)=>{ setCachedForecast(key, fresh); renderForecast(fresh); }).catch(()=>{});
    return;
  }

  const data = await fetchForecast();
  setCachedForecast(key, data);
  renderForecast(data);
}

// Ładowanie na podstawie wpisanej nazwy miasta
async function loadByCityName(name) {
  const place = await geocodeCity(name);
  const cityName = place.local_names?.pl || place.name;
  const key = cacheKeyFor(place.lat, place.lon, cityName);
  const cached = getCachedForecast(key);
  if (cached){
    try{ renderForecast(cached); }catch(e){ console.warn('Cached render failed', e); }
    // refresh in background
    fetchForecast(place.lat, place.lon, cityName).then((fresh)=>{ setCachedForecast(key, fresh); renderForecast(fresh); }).catch(()=>{});
    try{ const inp = document.getElementById('cityInput'); if (inp) { inp.value = ''; inp.blur(); } }catch(e){}
    return;
  }

  const data = await fetchForecast(place.lat, place.lon, cityName);
  setCachedForecast(key, data);
  renderForecast(data);
  try{ const inp = document.getElementById('cityInput'); if (inp) { inp.value = ''; inp.blur(); } }catch(e){}
}

// Ładowanie na podstawie współrzędnych (szybkie: używa cache jeśli dostępny,
// a potem odświeża w tle). Zwraca promise, resolves gdy pobrano świeże dane.
async function loadByCoords(lat, lon, label){
  // update basic UI immediately
  try{
    if (label) {
      currentCity = label;
      const cityEl = document.getElementById('cityName');
      if (cityEl) cityEl.textContent = label + ' (ładowanie...)';
    }
    currentCoords.lat = lat;
    currentCoords.lon = lon;
  }catch(e){}

  const key = cacheKeyFor(lat, lon, label || null);
  const cached = getCachedForecast(key);
  if (cached){
    try{ renderForecast(cached); }catch(e){ console.warn('Cached render failed', e); }
    // refresh in background and update when fresh
    try{
      const fresh = await fetchForecast(lat, lon, label);
      setCachedForecast(key, fresh);
      renderForecast(fresh);
      try{ const inp = document.getElementById('cityInput'); if (inp) { inp.value = ''; inp.blur(); } }catch(e){}
      return fresh;
    }catch(e){
      console.warn('Background refresh failed', e);
      return cached;
      try{ const inp = document.getElementById('cityInput'); if (inp) { inp.value = ''; inp.blur(); } }catch(e){}
    }
  } else {
    // no cache -> fetch and render
    const data = await fetchForecast(lat, lon, label);
    setCachedForecast(key, data);
    renderForecast(data);
    try{ const inp = document.getElementById('cityInput'); if (inp) { inp.value = ''; inp.blur(); } }catch(e){}
    return data;
  }
}

// =================== OBSŁUGA WYSZUKIWANIA ===================

function setupSearch() {
  const input = $("#cityInput");
  const btn = $("#searchBtn");

  if (!input || !btn) return;

  const runSearch = () => {
  const q = input.value.trim();
  if (!q) {
    alert("Podaj nazwę miasta.");
    return;
  }
  if (!/^[a-zA-ZąćęłńóśżźĄĆĘŁŃÓŚŻŹ\s-]+$/.test(q)) {
    alert("Nazwa miasta zawiera niedozwolone znaki.");
    return;
  }
  loadByCityName(q).catch((err) => {
    console.error(err);
    alert(err.message || "Nie udało się znaleźć miasta.");
  });
};
  btn.addEventListener("click", runSearch);

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      runSearch();
    }
  });
}

// =================== SERDUSZKO (ULUBIONE) ===================

// Na razie: jeśli niezalogowany -> przekierowanie do /login
// Jeśli zalogowany -> tylko wizualny toggle klasy .active
function setupFavoriteButton() {
  const btn = $("#favoriteBtn");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    const loggedIn = btn.dataset.loggedin === "1" || btn.dataset.loggedIn === "1";

    if (!loggedIn) {
      // show auth modal (existing UI)
      const overlay = document.getElementById("authOverlay");
      const modal = document.getElementById("authModal");
      const loginForm = document.getElementById("loginForm");

      if (overlay) overlay.classList.remove("hidden");
      if (modal) modal.classList.remove("hidden");
      if (loginForm) {
        loginForm.classList.remove("hidden");
        const reg = document.getElementById("registerForm");
        if (reg) reg.classList.add("hidden");
      }
      return;
    }

    // jeśli zalogowany -> wyślij request do API
    const isActive = btn.classList.contains("active");
    try {
      if (!isActive) {
        // add favorite
        const res = await fetch(`/weather/api/favorites`, {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ city: currentCity, lat: currentCoords.lat, lon: currentCoords.lon }),
        });
        if (res.ok) {
          btn.classList.add("active");
          // refresh favorites list UI
          refreshFavorites().catch(()=>{});
        } else {
          const txt = await res.text();
          console.error('Add favorite failed', res.status, txt);
          alert('Nie udało się dodać do ulubionych.');
        }
      } else {
        // remove favorite by city
        const res = await fetch(`/weather/api/favorites`, {
          method: "DELETE",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ city: currentCity }),
        });
        if (res.ok) {
          btn.classList.remove("active");
          // refresh favorites list UI
          refreshFavorites().catch(()=>{});
        } else {
          const txt = await res.text();
          console.error('Remove favorite failed', res.status, txt);
          alert('Nie udało się usunąć z ulubionych.');
        }
      }
    } catch (err) {
      console.error('Favorite request error', err);
      alert('Błąd sieci podczas operacji ulubionych.');
    }
  });
}

// Fetch and render favorites list into #favoritesList
async function refreshFavorites(){
  try{
    const res = await fetch('/weather/api/favorites', { credentials: 'same-origin' });
    if (!res.ok) {
      // not logged in or no favorites; show empty state
      renderFavorites([]);
      return [];
    }
    const data = await res.json();
    const favs = data.favorites || [];
    renderFavorites(favs);
    return favs;
  }catch(e){
    console.warn('refreshFavorites failed', e);
    renderFavorites([]);
    return [];
  }
}

function renderFavorites(favs){
  const container = document.getElementById('favoritesList');
  if (!container) return;
  container.innerHTML = '';
  if (!favs || favs.length === 0){
    const row = document.createElement('div');
    row.className = 'fav-row';
    row.innerHTML = `<span class="fav-name">Brak zapisanych ulubionych lokalizacji</span><span class="fav-temp"></span>`;
    container.appendChild(row);
    return;
  }

  favs.forEach(f => {
    const row = document.createElement('div');
    row.className = 'fav-row';
      row.style.cursor = 'pointer';
      row.tabIndex = 0;
      row.dataset.lat = f.lat;
      row.dataset.lon = f.lon;
    const name = document.createElement('span');
    name.className = 'fav-name';
    name.textContent = f.city;
    name.tabIndex = 0;
    name.style.cursor = 'pointer';
    name.dataset.lat = f.lat;
    name.dataset.lon = f.lon;
      name.addEventListener('click', (e) => {
        e.stopPropagation();
        // load forecast for this favorite (via coords if available)
        const lat = name.closest('.fav-row').dataset.lat ? parseFloat(name.closest('.fav-row').dataset.lat) : null;
        const lon = name.closest('.fav-row').dataset.lon ? parseFloat(name.closest('.fav-row').dataset.lon) : null;
        const label = f.city;
        if (lat != null && lon != null) {
          loadByCoords(lat, lon, label).catch(err=>{ console.error(err); alert('Nie udało się załadować miasta.'); });
        } else {
          loadByCityName(f.city).catch(err=>{ console.error(err); alert('Nie udało się załadować miasta.'); });
        }
      });
      name.addEventListener('keydown', (e)=>{ if (e.key==='Enter') name.click(); });

    const temp = document.createElement('span');
    temp.className = 'fav-temp';
    temp.textContent = '';

    row.appendChild(name);
    row.appendChild(temp);

    // make the whole row clickable and keyboard-accessible
    row.addEventListener('click', () => {
      const lat = row.dataset.lat ? parseFloat(row.dataset.lat) : null;
      const lon = row.dataset.lon ? parseFloat(row.dataset.lon) : null;
      const label = f.city;
      if (lat != null && lon != null) {
        loadByCoords(lat, lon, label).catch(err=>{ console.error(err); alert('Nie udało się załadować miasta.'); });
      } else {
        loadByCityName(f.city).catch(err=>{ console.error(err); alert('Nie udało się załadować miasta.'); });
      }
    });
    row.addEventListener('keydown', (e)=>{ if (e.key==='Enter') row.click(); });

    container.appendChild(row);
  });
}

function setFavoriteButtonActive(active){
  const btn = document.getElementById('favoriteBtn');
  if (!btn) return;
  if (active){
    btn.classList.add('active');
  } else {
    btn.classList.remove('active');
  }
}


// =================== WYKRES (IMG + NAWIGACJA) ===================

// Ustawia tekst nad wykresem, zależny od chartDayOffset
function updateChartTitle(dayOffset) {
  const chartTitle = $("#chartTitle");
  if (!chartTitle) return;

  const now = new Date();
  const target = new Date(now.getTime() + dayOffset * 24 * 60 * 60 * 1000);

  const options = {
    weekday: "long",
    day: "numeric",
    month: "long",
  };

  let label;
  if (dayOffset === 0) label = "dziś";
  else if (dayOffset === 1) label = "jutro";
  else label = target.toLocaleDateString("pl-PL", options);

  chartTitle.textContent = `Wykres temperatury i opadów – ${label}`;
}

// Wstawia poprawny src do <img id="chartImg">
function updateChart() {
  const canvas = document.getElementById('chartCanvas');
  const img = $("#chartImg");
  const { lat, lon } = currentCoords;

  // Prefer client-side chart using hourly JSON endpoint (faster perception)
  if (canvas && window.Chart) {
    canvas.style.display = 'block';
    if (img) img.style.display = 'none';
    const hourlyKey = hourlyCacheKey(lat, lon, chartDayOffset);
    const cached = getCachedHourly(hourlyKey);
    if (cached){
      try{
        const pts = (cached.points || []).map(p => ({ t: p.dt, temp: p.temp, precip: p.precip_mm }));
        renderChartFromPoints(pts);
      }catch(e){ console.warn('Render from hourly cache failed', e); }
      // refresh in background
      fetch(`/weather/api/hourly?lat=${lat}&lon=${lon}&day=${chartDayOffset}`)
        .then(async (res)=>{ if (!res.ok) throw new Error(await res.text()); return res.json(); })
        .then(json=>{ setCachedHourly(hourlyKey, json); const pts=(json.points||[]).map(p=>({ t:p.dt, temp:p.temp, precip:p.precip_mm })); renderChartFromPoints(pts); })
        .catch(err=>{ console.warn('Hourly refresh failed', err); });
    } else {
      fetch(`/weather/api/hourly?lat=${lat}&lon=${lon}&day=${chartDayOffset}`)
        .then(async (res) => {
          if (!res.ok) throw new Error(await res.text());
          return res.json();
        })
        .then((json) => {
          setCachedHourly(hourlyKey, json);
          const pts = (json.points || []).map(p => ({ t: p.dt, temp: p.temp, precip: p.precip_mm }));
          renderChartFromPoints(pts);
        })
        .catch((err) => {
          // fallback: load server-generated PNG without spinner
          console.warn('Hourly JSON failed, falling back to PNG:', err);
          if (canvas) canvas.style.display = 'none';
          if (img) {
            const src = `/weather/plot.png?lat=${lat}&lon=${lon}&day=${chartDayOffset}&_=${Date.now()}`;
            img.style.display = 'block';
            img.src = src;
          }
        });
    }
  } else {
    // no Chart.js available: use PNG fallback
    if (canvas) canvas.style.display = 'none';
    if (img) { img.style.display = 'block'; img.src = `/weather/plot.png?lat=${lat}&lon=${lon}&day=${chartDayOffset}&_=${Date.now()}`; }
  }

  updateChartTitle(chartDayOffset);
}

// Chart.js instance
let chartInstance = null;

function renderChartFromPoints(points){
  const ctx = document.getElementById('chartCanvas').getContext('2d');
  // helper: extract HH:MM from ISO-local string like 2025-11-26T06:00:00+08:00
  function timeFromISO(iso){
    try{
      const m = iso.match(/T(\d{2}:\d{2})/);
      if (m && m[1]) return m[1];
      // fallback: create Date and format (may show user's local tz)
      const d = new Date(iso);
      return d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
    }catch(e){ return iso; }
  }

  const labels = points.map(p => {
    if (typeof p.t === 'string') return timeFromISO(p.t);
    if (p.t instanceof Date) return p.t.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
    return String(p.t);
  });
  const temps = points.map(p => p.temp == null ? NaN : p.temp);
  const prec = points.map(p => p.precip == null ? 0 : p.precip);

  const data = {
    labels: labels,
    datasets: [
      {
        type: 'line',
        label: 'Temperatura (°C)',
        data: temps,
        borderColor: '#2B7A78',
        backgroundColor: 'rgba(43,122,120,0.08)',
        yAxisID: 'y1',
        tension: 0.3,
        pointRadius: 3,
      },
      {
        type: 'bar',
        label: 'Opady (mm)',
        data: prec,
        backgroundColor: 'rgba(138,162,74,0.7)',
        yAxisID: 'y2',
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false } },
      y1: { type: 'linear', position: 'left', title: { display: true, text: '°C' } },
      y2: { type: 'linear', position: 'right', title: { display: true, text: 'mm' }, grid: { drawOnChartArea: false } }
    },
    plugins: { legend: { display: true } }
  };

  if (chartInstance) {
    chartInstance.data = data;
    chartInstance.options = options;
    chartInstance.update();
  } else {
    chartInstance = new Chart(ctx, { data, options });
  }
}

// Obsługa przycisków ‹ i ›
function setupChartNavigation() {
  const prevBtn = $("#chartPrev");
  const nextBtn = $("#chartNext");

  if (!prevBtn || !nextBtn) return;

  prevBtn.addEventListener("click", () => {
    if (chartDayOffset > 0) {
      chartDayOffset -= 1;
      updateChart();
    }
  });

  nextBtn.addEventListener("click", () => {
    if (chartDayOffset < MAX_CHART_OFFSET) {
      chartDayOffset += 1;
      updateChart();
    }
  });
}

// =================== START APLIKACJI ===================

document.addEventListener("DOMContentLoaded", () => {
  // Data w topbarze
  const dateLabel = $("#todayLabel");
  if (dateLabel) {
    dateLabel.textContent = formatToday();
  }

  setupSearch();
  setupFavoriteButton();
  setupChartNavigation();

  // If page was rendered as logged-in, load favorites list
  try{
    const favBtn = document.getElementById('favoriteBtn');
    if (favBtn && (favBtn.dataset.loggedin === '1' || favBtn.dataset.loggedIn === '1')){
      refreshFavorites().catch(()=>{});
    }
  }catch(e){ }

  // Załaduj prognozę dla domyślnej lokalizacji i wykres
  loadDefault()
    .catch((err) => {
      console.error(err);
    
    });
});
