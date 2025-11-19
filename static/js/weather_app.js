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
async function fetchForecast(lat, lon) {
  let url = "http://127.0.0.1:5001/weather/api/forecast";
  if (lat != null && lon != null) {
    url += `?lat=${encodeURIComponent(lat)}&lon=${encodeURIComponent(lon)}`;
  }

  console.log("Fetching forecast from:", url);
  const res = await fetch(url);
  console.log("Response status:", res.status, res.statusText);
  
  if (!res.ok) {
    const msg = await res.text();
    console.error("Forecast error response:", msg);
    throw new Error(`Błąd pobierania prognozy: ${res.status} ${msg}`);
  }
  const data = await res.json();
  console.log("Forecast data:", data);
  return data; // oczekujemy: { city, lat, lon, days: [...] }
}

// Zamiana nazwy miasta na współrzędne (geokodowanie)
async function geocodeCity(query) {
  const res = await fetch(`http://127.0.0.1:5001/weather/api/geocode?q=${encodeURIComponent(query)}`);
  if (!res.ok) {
    throw new Error("Błąd geokodowania");
  }
  const data = await res.json();
  if (!Array.isArray(data) || data.length === 0) {
    throw new Error("Nie znaleziono lokalizacji");
  }
  return data[0]; // pierwszy wynik, np. { name, lat, lon }
}

// =================== STAN APLIKACJI ===================

// aktualne koordynaty do /api/forecast i /plot.png
const currentCoords = {
  lat: 50.0647,   // Kraków – domyślnie (spójne z backendem)
  lon: 19.9450,
};

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
    today.t_max != null ? `${Math.round(today.t_max)}°C` : "--°C";

  $("#currentDesc").textContent = today.description || "";

  $("#currentPressure").textContent =
    today.pressure != null
      ? `Ciśnienie: ${Math.round(today.pressure)} hPa`
      : "Ciśnienie: -- hPa";

  $("#currentPrecip").textContent =
    today.precip_mm != null
      ? `Opady: ${today.precip_mm.toFixed(1)} mm`
      : "Opady: -- mm";

  // Ikona aktualnej pogody (iconUrl pochodzi z icons.js)
  if (today.icon) {
    $("#currentIcon").src = iconUrl(today.icon);
    $("#currentIcon").alt = today.description || "Ikona pogody";
  } else {
    $("#currentIcon").removeAttribute("src");
    $("#currentIcon").alt = "";
  }

  // Pasek 7-dniowej prognozy
  renderForecastStrip(data.days);

  // Po zmianie prognozy resetujemy wykres na "Dziś"
  chartDayOffset = 0;
  updateChart();
  updateCurrentDayPanel(0);  // Zaktualizuj lewy panel dla dnia 0
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
    day.t_max != null ? `${Math.round(day.t_max)}°C` : "--°C";

  $("#currentDesc").textContent = day.description || "";

  $("#currentPressure").textContent =
    day.pressure != null
      ? `Ciśnienie: ${Math.round(day.pressure)} hPa`
      : "Ciśnienie: -- hPa";

  $("#currentPrecip").textContent =
    day.precip_mm != null
      ? `Opady: ${day.precip_mm.toFixed(1)} mm`
      : "Opady: -- mm";

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
  const data = await fetchForecast();
  renderForecast(data);
}

// Ładowanie na podstawie wpisanej nazwy miasta
async function loadByCityName(name) {
  const place = await geocodeCity(name);
  const data = await fetchForecast(place.lat, place.lon);
  renderForecast(data);
}

// =================== OBSŁUGA WYSZUKIWANIA ===================

function setupSearch() {
  const input = $("#cityInput");
  const btn = $("#searchBtn");

  if (!input || !btn) return;

  const runSearch = () => {
    const q = input.value.trim();
    if (!q) return;
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

  btn.addEventListener("click", () => {
    const loggedIn = btn.dataset.loggedIn === "1";

    if (!loggedIn) {
      // użytkownik niezalogowany -> przenosimy do logowania
      window.location.href = "/login"; // jeśli masz inną ścieżkę, zmień tutaj
      return;
    }

    // TODO: tu w przyszłości zrobisz fetch() do backendu,
    // który zapisze ulubioną lokalizację w bazie.
    btn.classList.toggle("active");
  });
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
  const img = $("#chartImg");
  if (!img) return;

  const { lat, lon } = currentCoords;

  // day=chartDayOffset możesz później obsłużyć w /plot.png po stronie Flask
  img.src = `/plot.png?lat=${lat}&lon=${lon}&day=${chartDayOffset}&_=${Date.now()}`;

  updateChartTitle(chartDayOffset);
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

  // Załaduj prognozę dla domyślnej lokalizacji i wykres
  loadDefault()
    .catch((err) => {
      console.error(err);
      alert("Nie udało się załadować prognozy dla domyślnej lokalizacji.");
    });
});
