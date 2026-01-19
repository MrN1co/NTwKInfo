# Dokumentacja modułu News

## Spis treści
- [User stories](#user-stories)
- [Opis ogólny](#opis-ogólny)
- [Architektura modułu](#architektura-modułu)
- [Struktura katalogów](#struktura-katalogów)
- [Komponenty główne](#komponenty-główne)
- [Collectors (Scrapery)](#collectors-scrapery)
- [System daemonów](#system-daemonów)
- [Routing i widoki](#routing-i-widoki)
- [Model danych](#model-danych)
- [Frontend](#frontend)
- [Konfiguracja](#konfiguracja)
- [API Endpoints](#api-endpoints)
---

## User stories

- **SCRUM 10:** Jako użytkownik chcę widzieć nagłówki wiadomości z zachęcającym mnie obrazkiem.  
- **SCRUM 11:** Jako użytkownik chcę przeczytać artykuł w oryginalnym serwisie, ponieważ na nasze stronie znajduje się odnośnik.  
- **SCRUM 12:** Jako niezalogowany użytkownik chcę widzieć wiadomości ze wszystkich kategorii w równych proporcjach.  
- **SCRUM 13:** Jako użytkownik chcę wybrać swoje zainteresowania (np. siatkówkę), aby widzieć wiadomości z wybranych kategorii.  
- **SCRUM 21:** Jako użytkownik chcę przeglądać tabele wybranych lig sportowych.  
- **SCRUM 44:** Jako zalogowany użytkownik chcę przejrzeć historię przeczytanych artykułów, aby nie szukać ich ponownie.  


## Opis ogólny

Moduł `news` to kompleksowy system agregacji wiadomości i wyników sportowych.  Moduł składa się z: 
- **Scraperów** pobierających dane z różnych źródeł
- **Daemonów** działających w tle i odświeżających dane periodycznie
- **Systemu routingu** Flask Blueprint
- **Historii kliknięć** użytkownika
- **Interfejsu webowego** do przeglądania wiadomości i tabel

### Główne funkcje
- Agregacja wiadomości sportowych z wielu źródeł
- Wyświetlanie tabel ligowych (piłka nożna, tenis, koszykówka, etc.)
- System tagowania i filtrowania wiadomości
- Historia przeglądanych linków dla zalogowanych użytkowników
- Automatyczna aktualizacja danych w tle

---

## Architektura modułu

```
modules/news/
├── news. py                    # Punkt wejścia modułu
├── routes.py                  # Blueprint Flask z trasami
├── scrapers_daemon.py         # Daemony scrapujące w tle
├── link_history_model.py      # Model SQLite historii kliknięć
└── collectors/                # Scrapery dla różnych źródeł
    ├── __init__.py
    ├── football_api_scraper.py
    ├── tennis_api_scraper.py
    ├── ekstraklasa_scraper.py
    ├── espn_api_scraper.py
    ├── kryminalki_scraper.py
    ├── minut_scraper.py
    ├── przegladsportowy_scraper.py
    └── policja_scraper.py
```

### Przepływ danych

```
[Źródła danych] 
    ↓
[Collectors/Scrapery] 
    ↓
[Scrapers Daemon] (pobiera dane co X sekund)
    ↓
[Pliki JSON] (cache danych)
    ↓
[Routes Blueprint] (odczytuje JSON)
    ↓
[Szablony HTML] (wyświetla użytkownikowi)
```

**WAŻNE:** Moduł `routes.py` **TYLKO CZYTA** dane z JSON. **NIGDY** nie wywołuje scraperów bezpośrednio!

---

## Struktura katalogów

### Katalogi danych
```
data/news/
├── football-data/              # Dane piłkarskie z football-data.org
│   ├── COMPETITIONS_config.JSON
│   ├── football_config.json
│   └── [pliki z danymi lig]. json
├── tennis-API/                 # Rankingi ATP/WTA
│   ├── tennis_config.json
│   ├── atp_rankings.json
│   └── wta_rankings.json
├── 90minut/                    # Polskie ligi piłkarskie
│   ├── ekstraklasa_config.json
│   ├── ekstraklasa. json
│   ├── first_league.json
│   └── second_league.json
├── ESPN-API/                   # NBA i MLS
│   ├── espn_config.json
│   ├── nba_standings.json
│   └── mls_standings.json
└── news/                       # Wiadomości
    ├── kryminalki_news.json
    ├── minut_news.json
    ├── przegladsportowy_news.json
    ├── policja_krakow_news.json
    └── policja_malopolska_news. json
```

### Szablony HTML
```
templates/news/
├── news_base.html             # Bazowy szablon z przyciskami nawigacyjnymi
├── news_main.html             # Strona główna wiadomości
├── tables. html                # Tabele ligowe
├── news_all. html              # Wszystkie wiadomości z filtrami
└── history.html               # Historia kliknięć użytkownika
```

### Pliki statyczne
```
static/
├── css/
│   └── news.css               # Style dla modułu news
└── js/
    ├── news-filters.js        # Filtrowanie wiadomości po tagach
    └── news-history.js        # Logowanie kliknięć do historii
```

---

## Komponenty główne

### 1. `news.py` - Punkt wejścia

```python
def init_news_module():
    """
    Inicjalizuje moduł news - uruchamia daemony scrapujące. 
    Wywoływane przy starcie aplikacji.
    """
    print("🚀 MODUŁ SPORTOWY - Uruchamianie scraperów...")
    daemon_threads = start_all_daemons()
```

**Funkcja:**
- Uruchamia wszystkie daemony w tle
- Eksportuje `tables_bp` (Blueprint Flask)

---

### 2. `routes.py` - Routing Flask

Blueprint:  `tables_bp`

**Kluczowe funkcje:**

#### `load_from_json(filepath, default=None)`
Wczytuje dane z pliku JSON. Zwraca `default` jeśli plik nie istnieje.

#### `localize_competition_name(name, area)`
Tłumaczy nazwę ligi i region na polski.

**Mapowania:**
```python
LEAGUE_NAME_TRANSLATIONS = {
    'UEFA Champions League': 'Liga Mistrzów',
    'Premier League': 'Premier League',
    'Bundesliga': 'Bundesliga',
    ... 
}

AREA_TRANSLATIONS = {
    'Europe': 'Europa',
    'England': 'Anglia',
    'Germany': 'Niemcy',
    ...
}
```

---

## Collectors (Scrapery)

Każdy scraper pobiera dane z konkretnego źródła i zwraca ustandaryzowany format danych.

### 1. `football_api_scraper.py`

**API:** football-data.org (wymaga klucza API)

**Funkcje:**
- `get_available_competitions()` - lista dostępnych rozgrywek z pliku JSON
- `get_competition_info(competition_code)` - szczegóły rozgrywek z API
- `get_football_standings(competition_code, season, skip_competition_info)` - tabela ligowa

**Zwracany format:**
```python
{
    'standings': [... ],           # Lista drużyn
    'competition_name': str,      # Nazwa rozgrywek
    'competition_emblem': str,    # URL do logo
    'season_info': {... },         # Informacje o sezonie
    'available_seasons': [...],   # Dostępne sezony
    'error': str or None
}
```

**Rozgrywki:** Liga Mistrzów, Premier League, Bundesliga, Serie A, La Liga, Ligue 1, Eredivisie, Primeira Liga, Championship

---

### 2. `tennis_api_scraper.py`

**API:** Tennis API (RapidAPI - wymaga klucza)

**Funkcje:**
- `get_atp_rankings(limit=20)` - ranking ATP (mężczyźni)
- `get_wta_rankings(limit=20)` - ranking WTA (kobiety)

**Zwracany format:**
```python
[
    {
        'ranking':  int,
        'team': {
            'name': str,
            'country': str
        },
        'points': int
    },
    ...
]
```

---

### 3. `ekstraklasa_scraper.py`

**Źródło:** 90minut.pl (scraping)

**Funkcje:**
- `get_emblems_map(id_rozgrywki)` - mapa logo drużyn
- `get_90minut_table(url, id_rozgrywki)` - tabela ligowa
- `get_ekstraklasa_table()` - Ekstraklasa (ID: 14072)
- `get_first_league_table()` - I Liga (ID: 14073)
- `get_second_league_table()` - II Liga (ID: 14074)

**Zwracany format:**
```python
{
    'standings': [
        {
            'position': int,
            'team_name': str,
            'crest': str,           # URL do logo
            'playedGames': int,
            'won': int,
            'draw':  int,
            'lost': int,
            'points': int
        },
        ...
    ],
    'error': str or None
}
```

---

### 4. `espn_api_scraper.py`

**API:** ESPN (publiczne, bez klucza)

**Funkcje:**
- `get_nba_standings()` - tabela NBA
- `get_mls_standings()` - tabela MLS

**Zwracany format:**
```python
{
    'data': {
        'children': [           # Konferencje
            {
                'name': str,
                'standings': {... }
            },
            ...
        ]
    },
    'error':  str or None
}
```

---

### 5. `kryminalki_scraper.py`

**Źródło:** kryminalki.pl (scraping)

**Funkcja:**
- `get_kryminalki_news(limit=10)` - wiadomości kryminalne

**Zwracany format:**
```python
[
    {
        'title': str,
        'link': str,
        'image': str or None,
        'date': str,            # Format: DD.MM.RRRR HH:MM
        'timestamp': int,       # Unix timestamp
        'tags': [str, ...]      # np. ['kryminalne', 'Kraków']
    },
    ... 
]
```

**Mapowanie tagów:**
```python
TAG_MAPPING = {
    'Kraków': ['kryminalne', 'Kraków'],
    'Małopolska': ['kryminalne', 'Małopolska'],
    ... 
}
```

---

### 6. `minut_scraper.py`

**Źródło:** 90minut.pl (scraping)

**Funkcja:**
- `get_minut_news(limit=10)` - wiadomości piłkarskie

**Zwracany format:**
```python
[
    {
        'title':  str,
        'link': str,
        'image': str or None,
        'date': str,
        'timestamp': int,
        'tags': ['piłka-nożna']
    },
    ...
]
```

**Uwaga:** Scraper wchodzi na każdą stronę artykułu aby pobrać datę z `<blockquote>` → drugi `<p>`.

---

### 7. `przegladsportowy_scraper.py`

**Źródło:** przegladsportowy.onet.pl (scraping)

**Funkcje:**
- `_parse_polish_date(date_raw)` - parsuje polską datę
- `_fetch_news_from_category(category_slug, limit)` - pobiera z kategorii
- `get_przegladsportowy_news(limit=30)` - wiadomości z wielu kategorii

**Kategorie:**
```python
CATEGORY_TAG_MAP = {
    'pilka-nozna': 'piłka-nożna',
    'tenis': 'tenis',
    'siatkowka': 'siatkówka',
    'zuzel': 'żużel',
    'lekkoatletyka': 'lekkoatletyka'
}
```

**Zwracany format:**
```python
[
    {
        'title': str,
        'link': str,
        'image': str or None,
        'date': str,
        'timestamp': int,
        'tags':  [str, ...]
    },
    ... 
]
```

---

### 8. `policja_scraper.py`

**Źródło:** Strony policji (Kraków, Małopolska)

**Funkcje:**
- `scrape_policja_news(url, tags, limit)` - uniwersalny scraper
- `get_policja_krakow_news(limit=10)`
- `get_policja_malopolska_news(limit=10)`

**Zwracany format:**
```python
[
    {
        'title': str,
        'link': str,
        'image': str or None,
        'date': str,           # Tylko data, bez godziny
        'timestamp': None,
        'tags': ['kryminalne', 'Kraków']  # lub 'Małopolska'
    },
    ...
]
```

**Struktura HTML:** `div#content` → `ul` → `li.news` → `strong`, `img`, `span. data`

---

## System daemonów

### `scrapers_daemon.py`

Daemony działają w osobnych wątkach i pobierają dane w regularnych odstępach czasu. 

**Główna funkcja:**
```python
def start_all_daemons():
    """
    Uruchamia wszystkie daemony w osobnych wątkach.
    Każdy daemon działa w nieskończonej pętli i zapisuje dane do JSON.
    """
```

**Kluczowe funkcje pomocnicze:**

#### `get_warsaw_time()`
```python
return datetime.now(WARSAW_TZ).strftime('%d.%m.%Y   %H:%M:%S')
```
Zwraca aktualny czas w strefie warszawskiej.

#### `save_to_json(filepath, data)`
**Bezpieczny zapis:**
- Sprawdza czy są dane do zapisania
- **NIE nadpisuje** pliku jeśli dane są puste (zapobiega utracie danych przy błędzie)
- Tworzy katalogi jeśli nie istnieją
- Zapisuje z `ensure_ascii=False` i `indent=2`

#### `load_*_config()`
Funkcje wczytujące konfigurację z plików JSON: 
- `load_football_config()`
- `load_football_competitions()`
- `load_tennis_config()`
- `load_ekstraklasa_config()`
- `load_espn_config()`

**Struktura daemona:**
```python
def football_daemon():
    while True:
        try:
            competitions = load_football_competitions()
            for comp in competitions:
                data = get_football_standings(comp['code'], skip_competition_info=True)
                save_to_json(f'data/news/football-data/{comp["code"]}.json', {
                    'data': data,
                    'updated_at': get_warsaw_time()
                })
            time.sleep(config['refresh_interval'])  # np. 3600s (1h)
        except Exception as e:
            print(f"Błąd w football_daemon: {e}")
            time.sleep(60)
```

**Uruchamianie:**
```python
thread = threading.Thread(target=football_daemon, daemon=True, name="FootballDaemon")
thread.start()
```

**Lista daemonów:**
1. `football_daemon` - tabele piłkarskie (football-data.org API)
2. `tennis_daemon` - rankingi ATP/WTA (Tennis API)
3. `ekstraklasa_daemon` - polskie ligi (90minut. pl)
4. `nba_mls_daemon` - NBA i MLS (ESPN API)
5. `news_daemon` - wiadomości z wszystkich źródeł

**Interwały odświeżania** (konfigurowalne w plikach `*_config.json`):
- Tabele piłkarskie: 3600s (1h)
- Rankingi tenisowe: 86400s (24h)
- Wiadomości: 300s (5 min)

---

## Routing i widoki

### Trasy Blueprint `tables_bp`

#### 1. Strona główna wiadomości
**Trasa:** `/news` (lub cokolwiek skonfigurowane w głównej aplikacji)  
**Nazwa:** `tables. news`  
**Metoda:** GET

**Funkcjonalność:**
- Wyświetla jedną wiadomość z kryminalek i jedną sportową
- Dane pobierane z JSON

**Szablon:** `news/news_main.html`

**Kontekst:**
```python
{
    'crime_item': {... },        # Wiadomość kryminalna
    'sport_item': {...},        # Wiadomość sportowa
    'crime_updated': str,       # Czas aktualizacji
    'sport_updated': str
}
```

---

#### 2. Wszystkie wiadomości
**Trasa:** `/news/all`  
**Nazwa:** `tables.news_all`  
**Metoda:** GET

**Parametry query:**
- `tags` (opcjonalnie) - JSON array tagów do filtrowania

**Funkcjonalność:**
- Wyświetla wszystkie wiadomości z wielu źródeł
- System filtrowania po tagach
- Zapisywanie ulubionych tagów dla zalogowanych użytkowników
- Sortowanie po dacie (timestamp)

**Źródła:**
- Kryminalki. pl
- Przegląd Sportowy
- 90minut.pl
- Policja Kraków
- Policja Małopolska

**Szablon:** `news/news_all.html`

**Kontekst:**
```python
{
    'news': [... ],              # Posortowane wiadomości
    'all_tags': [...],          # Wszystkie dostępne tagi
    'selected_tags': [...],     # Wybrane tagi (z query lub zapisane)
    'crime_updated': str,
    'sport_updated': str
}
```

---

#### 3. Tabele ligowe
**Trasa:** `/news/tables`  
**Nazwa:** `tables.tables`  
**Metoda:** GET

**Parametry query:**
- `competition` - kod rozgrywek (np. 'PL', 'CL', 'PD')
- `season` - rok sezonu (np. '2025')

**Funkcjonalność:**
- Wyświetla tabele ligowe dla różnych sportów
- Wybór ligi i sezonu z dropdown
- Obsługa:  piłka nożna, tenis (ATP/WTA), koszykówka (NBA), MLS

**Szablon:** `news/tables.html`

**Kontekst:**
```python
{
    'is_football': bool,
    'is_tennis': bool,
    'standings': [...],                 # Tabela ligowa
    'tennis_rankings': {... },           # Rankingi tenisowe
    'competition_name': str,
    'competition_emblem': str,
    'season_info': {...},
    'available_seasons': [...],
    'all_competitions': [...],
    'selected_code': str,
    'selected_season': str,
    'updated_at': str,
    'error': str or None
}
```

---

#### 4. Historia kliknięć
**Trasa:** `/news/history`  
**Nazwa:** `tables.history_view`  
**Metoda:** GET  
**Wymaga:** `@login_required`

**Funkcjonalność:**
- Wyświetla historię kliknięć użytkownika (ostatnie 200)
- Statystyki według źródeł

**Szablon:** `news/history.html`

**Kontekst:**
```python
{
    'history': [...],           # Lista NewsLinkHistory
    'stats': [...]              # Statystyki po źródłach
}
```

---

#### 5. API - Logowanie kliknięcia
**Trasa:** `/news/history/log`  
**Nazwa:** `tables.log_link_click`  
**Metoda:** POST  
**Content-Type:** application/json

**Body:**
```json
{
    "url": "https://...",
    "title": "Tytuł artykułu",
    "source": "kryminalki"
}
```

**Odpowiedź:**
```json
{
    "success": true
}
```

**Funkcjonalność:**
- Loguje kliknięcie linku do bazy danych
- Działa tylko dla zalogowanych użytkowników
- Wywoływane automatycznie przez `news-history. js`

---

#### 6. API - Usuwanie wpisu historii
**Trasa:** `/news/history/delete/<int:entry_id>`  
**Nazwa:** `tables.delete_history_entry`  
**Metoda:** POST  
**Wymaga:** `@login_required`

**Odpowiedź:**
```json
{
    "success": true
}
```

---

#### 7. API - Czyszczenie historii
**Trasa:** `/news/history/clear`  
**Nazwa:** `tables.clear_history`  
**Metoda:** POST  
**Wymaga:** `@login_required`

**Odpowiedź:**
```json
{
    "success": true
}
```

---

## Model danych

### `NewsLinkHistory` (SQLite)

**Tabela:** `news_link_history`

**Schemat:**
```python
class NewsLinkHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, index=True)
    link_url = db.Column(db.String(500), nullable=False)
    link_title = db.Column(db.String(300), nullable=True)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = db.Column(db.String(50), nullable=True)
```

**Metody statyczne:**

#### `log_click(user_id, link_url, link_title=None, source=None)`
Zapisuje kliknięcie do bazy. 

#### `get_user_history(user_id, limit=200)`
Pobiera historię użytkownika (sortowane po dacie malejąco).

#### `get_stats_by_source(user_id)`
Zwraca statystyki kliknięć pogrupowane po źródłach.

```python
[
    {'source': 'kryminalki', 'count': 15},
    {'source': 'przegladsportowy', 'count': 8},
    ... 
]
```

#### `clear_user_history(user_id)`
Usuwa całą historię użytkownika.

#### `delete_entry(entry_id, user_id)`
Usuwa konkretny wpis (tylko własny).

---

## Frontend

### Szablony HTML

#### `news_base.html`
Bazowy szablon dla całego modułu news.

**Elementy:**
- Extends `base.html`
- Linkuje `news. css`
- Górne przyciski nawigacyjne: 
  - "Wiadomości" → `/news`
  - "Tabele" → `/news/tables`
  - Ikona zegara (historia) → `/news/history` (tylko dla zalogowanych)
- Block `news_content` dla podszablonów
- Automatycznie ładuje `news-history.js`

---

#### `news_main.html`
Strona główna z 2 wiadomościami (crime + sport).

**Struktura:**
```html
<div class="news-container">
    <div class="news-item">
        <img src="..." class="news-image">
        <div class="news-content">
            <h3 class="news-title"><a href="...">... </a></h3>
            <p class="update-time">Źródło • Czas aktualizacji</p>
        </div>
    </div>
</div>
```

---

#### `news_all.html`
Wszystkie wiadomości z filtrami po tagach.

**Elementy:**
- Przyciski tagów (z data-tag)
- Przycisk "Zapisz tagi" (serce) dla zalogowanych
- Lista wiadomości `.news-item` z data-tags
- Filtrowanie po stronie klienta (JavaScript)

**Data attributes:**
```html
<div id="selected-tags-data" data-tags='["piłka-nożna","kryminalne"]'></div>
<div class="news-item" data-tags='["piłka-nożna"]'>... </div>
```

---

#### `tables.html`
Tabele ligowe z dropdownami wyboru. 

**Elementy:**
- Nagłówek z logo rozgrywek
- Formularz wyboru ligi i sezonu (onchange submit)
- Tabela HTML z wynikami
- Wsparcie dla różnych sportów (piłka, tenis, NBA, MLS)

**Struktura tabeli:**
```html
<table>
    <thead>
        <tr>
            <th>Pozycja</th>
            <th>Drużyna</th>
            <th>Mecze</th>
            <th>Wygrane</th>
            <th>Remisy</th>
            <th>Przegrane</th>
            <th>Punkty</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>1</td>
            <td><img src="..." width="30">Nazwa drużyny</td>
            <td>10</td>
            <td>7</td>
            <td>2</td>
            <td>1</td>
            <td>23</td>
        </tr>
    </tbody>
</table>
```

---

#### `history.html`
Historia kliknięć użytkownika. 

**Elementy:**
- Przycisk "Wyczyść historię"
- Tabela z historią (tytuł, źródło, data, akcja usuń)
- Statystyki po źródłach

---

### JavaScript

#### `news-filters.js`
Filtrowanie wiadomości po tagach.

**Funkcjonalność:**
- Obsługa kliknięcia przycisków tagów
- Pokazywanie/ukrywanie wiadomości według wybranych tagów
- Zapisywanie ulubionych tagów na serwerze (dla zalogowanych)
- Synchronizacja z query string URL

**API calls:**
```javascript
// Pobierz zapisane tagi użytkownika
fetch('/auth/api/user/tags')

// Zapisz tagi
fetch('/auth/api/user/tags', {
    method: 'POST',
    body: JSON.stringify({ tags: [... ] })
})
```

**Logika filtrowania:**
- Jeśli brak wybranych tagów → pokaż wszystkie
- Jeśli wybrane tagi → pokaż tylko wiadomości zawierające KTÓRYKOLWIEK z wybranych tagów

---

#### `news-history.js`
Automatyczne logowanie kliknięć linków.

**Event delegation:**
```javascript
document.addEventListener('click', function (e) {
    var el = e.target. closest('.news-link');
    if (!el) return;
    
    var url = el.getAttribute('href') || el.dataset.url;
    var title = el.getAttribute('data-title') || el.textContent. trim();
    var source = el.getAttribute('data-source') || ... ;
    
    fetch('/news/history/log', {
        method: 'POST',
        body: JSON.stringify({ url, title, source })
    });
}, true);  // Capture phase
```

**Funkcje na stronie historii:**
- Czyszczenie całej historii
- Usuwanie pojedynczych wpisów

---

### CSS

#### `news.css`

**Główne klasy:**

**Komunikaty:**
```css
.error         /* Czerwone tło, obramowanie */
.info          /* Szare, italic */
.update-time   /* Mniejsza czcionka, szary kolor */
```

**Przyciski górne:**
```css
.top-buttons    /* Flex container */
.top-btn        /* Główny przycisk */
.top-btn:hover  /* Zmiana koloru na secondary */
. top-btn. small  /* Mały przycisk (np. ikona) */
.top-btn.icon-btn /* Kwadratowy przycisk z ikoną */
```

**Tabele:**
```css
table           /* Border-collapse, shadow */
table thead     /* Kolor primary, białe napisy */
table tbody tr: hover /* Jasne tło przy hover */
table tbody tr:nth-child(even) /* Zebrowane rzędy */
```

**Wiadomości:**
```css
.news-container   /* Grid/Flex layout */
.news-item        /* Kontener artykułu */
.news-image       /* Obrazek wiadomości */
.news-title       /* Tytuł artykułu */
.news-content     /* Tekstowa część */
```

**Tagi:**
```css
.tag-btn          /* Przycisk tagu */
.tag-btn. active   /* Wybrany tag */
```

---

## Konfiguracja

### Pliki konfiguracyjne

#### `football_config.json`
```json
{
    "api_key": "YOUR_API_KEY",
    "refresh_interval": 3600,
    "competitions": ["PL", "CL", "PD", "SA", "BL1", "FL1", "PPL", "ELC", "EL", "BSA"]
}
```

#### `COMPETITIONS_config.JSON`
```json
{
    "competitions": [
        {
            "code": "CL",
            "name": "UEFA Champions League",
            "area": "Europa",
            "type": "INTERNATIONAL"
        },
        ... 
    ]
}
```

#### `tennis_config.json`
```json
{
    "rapidapi_key": "YOUR_RAPIDAPI_KEY",
    "rapidapi_host": "tennisapi1.p.rapidapi.com",
    "refresh_interval": 86400,
    "atp_limit": 20,
    "wta_limit":  20
}
```

#### `ekstraklasa_config.json`
```json
{
    "refresh_interval": 3600,
    "leagues": [
        {
            "name": "Ekstraklasa",
            "url": "http://www.90minut.pl/liga/liga. php? id_liga=1",
            "id_rozgrywki": "14072"
        },
        {
            "name": "I Liga",
            "url": "http://www.90minut.pl/liga/liga.php?id_liga=2",
            "id_rozgrywki": "14073"
        },
        {
            "name": "II Liga",
            "url": "http://www.90minut.pl/liga/liga.php?id_liga=3",
            "id_rozgrywki": "14074"
        }
    ]
}
```

#### `espn_config.json`
```json
{
    "refresh_interval": 3600,
    "nba_url": "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings",
    "mls_url": "https://site.api.espn.com/apis/v2/sports/soccer/usa. 1/standings"
}
```

### Zmienne środowiskowe (`.env`)

```bash
# Football Data API
FOOTBALL_API_KEY=your_football_data_api_key

# Tennis API (RapidAPI)
RAPIDAPI_KEY=your_rapidapi_key
```

---

## API Endpoints

### Publiczne

#### GET `/news`
Strona główna wiadomości.

#### GET `/news/all? tags=["piłka-nożna"]`
Wszystkie wiadomości z opcjonalnym filtrem. 

#### GET `/news/tables?competition=PL&season=2025`
Tabele ligowe. 

---
**Koniec**