# NTwKInfo

Modułowa aplikacja webowa zbudowana na frameworku Flask, oferująca wielofunkcyjny panel z autentykacją użytkownika, systemem zarządzania danymi i responsywnym interfejsem użytkownika.

## Szybki Start

### 1. Klonowanie i Setup

```bash
git clone <repository-url>
cd NTwKInfo
python -m venv venv
source venv/bin/activate 
```

### 2. Instalacja Zależności

```bash
pip install -r requirements.txt
```

### 3. Konfiguracja Zmiennych Środowiskowych

```bash
cp .env.example .env
# Edytuj .env z własnymi ustawieniami
```

Główne zmienne:
- `SECRET_KEY` - klucz sekretu aplikacji Flask
- `DATABASE_URL` - adres bazy danych (opcjonalnie, domyślnie SQLite)
- Inne zmienne specyficzne dla poszczególnych modułów

### 4. Uruchomienie Aplikacji

```bash
python app.py
```

Aplikacja będzie dostępna pod adresem `http://localhost:5001`

### 5. Dostęp do Aplikacji

- Otwórz przeglądarkę: `http://localhost:5001`
- Każdy moduł ma własną dokumentację w katalogu `docs/`

## Struktura Projektu

```
NTwKInfo/
├── app.py                    # Punkt wejścia aplikacji Flask
├── config.py                 # Konfiguracja (Development, Testing, Production)
├── requirements.txt          # Zależności Python
├── modules/                  # Moduły aplikacji
│   ├── auth.py              # Autentykacja i zarządzanie użytkownikami
│   ├── database.py          # Definicje modeli bazy danych
│   ├── main.py              # Główne ścieżki aplikacji
│   ├── scheduler.py         # Scheduler zadań (APScheduler)
│   ├── weather_app.py       # Moduł pogody
│   ├── ekonomia/            # Moduł ekonomii i walut
│   ├── news/                # Moduł wiadomości i sportu
│   └── main/                # Moduł główny
├── templates/               # Szablony HTML (Jinja2)
├── static/                  # Zasoby statyczne (CSS, JS, obrazy)
├── tests/                   # Testy jednostkowe i integracyjne
├── docs/                    # Dokumentacja poszczególnych modułów
└── data/                    # Dane aplikacji
```

## Stack Technologiczny

### Backend

| Biblioteka | Wersja | Przeznaczenie |
|-----------|--------|--------------|
| **Flask** | >= 2.3.0 | Główny framework webowy |
| **SQLAlchemy** | >= 2.0.0 | ORM do obsługi bazy danych |
| **Flask-SQLAlchemy** | >= 3.0.0 | Integracja SQLAlchemy z Flask |
| **python-dotenv** | >= 1.0.0 | Zarządzanie zmiennymi środowiskowymi |
| **Werkzeug** | >= 2.3.0, < 3.0.0 | WSGI i narzędzia bezpieczeństwa |
| **Jinja2** | >= 3.1.0 | Silnik szablonów |
| **requests** | >= 2.30.0 | Biblioteka do żądań HTTP |
| **APScheduler** | >= 3.10.0 | Scheduler zadań cyklicznych |
| **Flask-CORS** | >= 4.0.0 | Obsługa Cross-Origin Resource Sharing |

### Frontend

| Biblioteka | Przeznaczenie |
|-----------|--------------|
| **Bootstrap 5** | Framework CSS dla responsywnego designu |
| **Jinja2** | Renderowanie szablonów HTML |
| **Vanilla JavaScript** | Funkcjonalność po stronie klienta |
| **CSS3** | Stylizacja i animacje |

### Analiza Danych i Wizualizacja (Moduły Specjalistyczne)

| Biblioteka | Wersja | Przeznaczenie |
|-----------|--------|--------------|
| **NumPy** | >= 1.21.0 | Obliczenia numeryczne |
| **Pandas** | >= 2.2.0 | Manipulacja strukturami danych |
| **Matplotlib** | >= 3.8.0 | Tworzenie wykresów i wizualizacji |

### Web Scraping (Moduły Specjalistyczne)

| Biblioteka | Przeznaczenie |
|-----------|--------------|
| **BeautifulSoup4** | Parser HTML do web scrapingu |
| **lxml** | Parser XML/HTML dla BeautifulSoup |
| **pytz** | Obsługa stref czasowych |

### Testing

| Biblioteka | Wersja | Przeznaczenie |
|-----------|--------|--------------|
| **pytest** | >= 7.0.0 | Framework do testów |
| **pytest-flask** | >= 1.2.0 | Plugin pytest dla Flask |
| **pytest-playwright** | >= 0.7.0 | Testy end-to-end (E2E) |
| **Playwright** | >= 1.0.0 | Automatyzacja przeglądarki |

### Production

| Biblioteka | Przeznaczenie |
|-----------|--------------|
| **gunicorn** | >= 21.0.0 | WSGI server dla produkcji |

## Konfiguracja Środowiska

Aplikacja obsługuje trzy konfiguracje:

### DevelopmentConfig
- DEBUG: `True`
- Database: SQLite (lokalna)
- Ścieżka: `sqlite:///app.db`

### TestingConfig
- DEBUG: `False`
- TESTING: `True`
- Database: SQLite (oddzielna baza testowa)
- Ścieżka: `sqlite:///test.db`

### ProductionConfig
- DEBUG: `False`
- Database: Ze zmiennej `DATABASE_URL` (wymagane)

## Architektura Modułów

Aplikacja zbudowana jest na modułowej architekturze:

### Moduły Główne
- **auth** - Autentykacja i sesje użytkowników
- **database** - Inicjalizacja ORM i modele bazowe
- **main** - Routing

### Moduły Funkcjonalne
- **weather** - Dane pogodowe i wykresy
- **ekonomia** - Kursy walut i ceny złota
- **news** - Wiadomości i artykuły sportowe

## Obsługa Błędów i Debugowanie

### Development
- Tryb DEBUG włączony automatycznie
- Szczegółowe komunikaty błędów w konsoli
- Zmienne środowiskowe ładowane z `.env`

### Testing
- Konfiguracja `TestingConfig` automatycznie wybierana
- Oddzielna baza testowa
- Bezpieczna izolacja testów od produkcji

### Production
- Wymagana zmienna `DATABASE_URL`
- SECRET_KEY powinny być silne
- Użyć gunicorn lub innego WSGI servera

## Uruchomienie Aplikacji

### Serwer Development
```bash
python app.py
```

## Testing

```bash
# Uruchomienie wszystkich testów
pytest

# Uruchomienie testów z raportami
pytest --html=report.html

# Testy E2E (Playwright)
pytest tests/e2e/

# Testy integracyjne
pytest tests/integration/

# Testy jednostkowe
pytest tests/unit/
```

## Wskaźniki Jakości

- Testy jednostkowe, integracyjne i E2E
- Raporty w formacie HTML i JUnit
- Automatyczne generowanie raportów w katalogu `reports/`

## Dokumentacja Modułów

Szczegółową dokumentację poszczególnych modułów można znaleźć w katalogu `docs/`:

- [Module Homepage](docs/module_homepage.md)
- [Economics Tests Plan](docs/economics_tests_plan.md)
- [Test Plan Homepage](docs/TEST_PLAN_homepage.md)
- [Setup Guide](docs/SETUP.md)

## Kontakt i Wsparcie

Dokumentacja: [docs/](docs/)
Raporty testów: [reports/](reports/)