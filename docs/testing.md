# Plan testowania (`testing.md`)

> Dokument opisuje **plan testów dla aplikacji webowej** realizowanej w ramach projektu.  
> Plan testowania jest **obowiązkowy** i stanowi część dokumentacji technicznej projektu.

---

## 1. Organizacja testów

- Projekt został podzielony na **moduły**, z których każdy realizowany jest przez osobny zespół.
- **Każdy zespół odpowiada za testy swojego modułu**.
- Każdy zespół przygotowuje **jeden spójny plan testów** dla swojego modułu.
- Plan testów **musi obejmować wszystkie trzy rodzaje testów**:
  - testy jednostkowe (**Unit**),
  - testy integracyjne (**Integration**),
  - testy akceptacyjne (**E2E**).

---

## 2. Wymagania minimalne – zakres testów

### 2.1 Testy jednostkowe (Unit)

Każdy zespół:
- przygotowuje **co najmniej 2–3 testy jednostkowe** dla modułu,
- testuje:
  - funkcje pomocnicze,
  - logikę biznesową,
  - przetwarzanie danych.

**Zakres testów jednostkowych (ważne):**
- ❌ bez uruchamiania Flask,
- ❌ bez warstwy HTTP,
- ❌ bez bazy danych.

**Narzędzia:**
- `pytest`
- mockowanie zależności (jeśli potrzebne)

---

### 2.2 Testy integracyjne (Integration)

Testy integracyjne sprawdzają **poprawność działania endpointów modułu**.

Każdy zespół:
- przygotowuje testy integracyjne dla **swoich endpointów**:
  - endpointów HTML (czy widok się renderuje),
  - endpointów API (czy JSON ma poprawną strukturę).

**Wymagania:**
- użycie `client` z `pytest` (Flask test client),
- mockowanie zewnętrznych API (jeśli występują),
- sprawdzanie:
  - kodów statusu HTTP,
  - struktury odpowiedzi (HTML / JSON).

---

### 2.3 Testy akceptacyjne (E2E)

Testy E2E odwzorowują **realną ścieżkę użytkownika** w aplikacji.

Każdy zespół:
- przygotowuje **co najmniej 1 test E2E dla każdej User Story** przypisanej do modułu,
- wykorzystuje **Playwright**.

Test E2E:
- odwzorowuje realne zachowanie użytkownika,
- testuje aplikację jako całość (frontend + backend),
- korzysta z `e2e_server`.

---

## 3. Uruchamianie testów

### 3.1 Testy jednostkowe
```bash
pytest tests/unit
```

### 3.2 Testy integracyjne
```bash
pytest tests/integration
```

### 3.3 Testy akceptacyjne (E2E)
```bash
pytest tests/e2e
```

---

## 4. Zbiorcze tabele planu testów (obowiązkowe)

> **Wymaganie:** dla **każdego modułu** powinna istnieć **oddzielna tabela**.  
> Format tabeli jest zgodny ze wzorcem ze slajdu (ID / Typ / Co testujemy / Scenariusz-funkcja / Status).

**Status (zalecane oznaczenia):** ⬜ – nie wykonano, ✅ – zaliczony, ❌ – błąd

---

### 4.1 Moduł: Strona główna (Home)

| ID    | Typ testu   | Co testujemy     | Scenariusz / funkcja                                      | Status |
|-------|-------------|------------------|-----------------------------------------------------------|--------|
| UT-01 | Unit        | **TU UZUPEŁNIĆ** | **TU UZUPEŁNIĆ** (np. `build_dashboard_context()`)        | ⬜     |
| IT-01 | Integration | Endpoint HTML    | **TU UZUPEŁNIĆ** (np. `/`)                                | ⬜     |
| IT-02 | Integration | Endpoint API     | **TU UZUPEŁNIĆ** (np. `/api/summary`)                     | ⬜     |
| E2E-01| E2E         | User Story       | **TU UZUPEŁNIĆ** (np. „Użytkownik widzi stronę główną”)    | ⬜     |

---

### 4.2 Moduł: Pogoda (Weather)

| ID    | Typ testu   | Co testujemy            | Scenariusz / funkcja                              | Status |
|-------|-------------|-------------------------|---------------------------------------------------|--------|
| UT-01 | Unit        | Normalizacja danych     | `normalize_forecast()` - przetwarzanie surowych danych pogodowych na znormalizowany format | ✅     |
| UT-02 | Unit        | Funkcje pomocnicze      | `_cache_set()`, `_cache_get()` - zarządzanie pamięcią podręczną | ✅     |
| UT-03 | Unit        | Wysyłka e-maili         | `send_favorite_cities_weather_alert()` - wysyłka alertów pogodowych | ✅     |
| IT-01 | Integration | Endpoint HTML           | `/weather/pogoda` - renderowanie strony HTML z pogodą | ✅     |
| IT-02 | Integration | Endpoint API            | `/weather/api/forecast` - zwracanie prognozy w formacie JSON | ✅     |
| IT-03 | Integration | Walidacja parametrów    | `/weather/api/forecast` - obsługa błędnych parametrów lat/lon | ✅     |
| IT-04 | Integration | Geokodowanie            | `/weather/api/geocode` - wyszukiwanie współrzędnych na podstawie nazwy miasta | ✅     |
| IT-05 | Integration | Prognoza godzinowa      | `/weather/api/hourly` - zwracanie danych godzinowych | ✅     |
| IT-06 | Integration | Generowanie wykresów    | `/weather/plot.png` - zwracanie wykresu pogodowego jako PNG | ✅     |
| IT-07 | Integration | Test e-maili            | `/weather/api/test-email` - test wysyłki alertów pogodowych | ✅     |
| E2E-01| E2E         | User Story 1              | „Niezalogowany użytkownik widzi pogodę dla Krakowa” | ✅    |
| E2E-02| E2E         | User Story 2              | „Niezalogowany użytkownik może wyszukać pogodę dla innego miasta” | ✅    |
| E2E-03| E2E         | User Story 3              | „Zalogowany użytkownik widzi sekcję ulubionych miast” | ✅    |
| E2E-04| E2E         | User Story 4             | „Zalogowany użytkownik może dodać miasto do ulubionych” | ✅    |
| E2E-05| E2E         | User Story 5             | „Użytkownik otrzymuje alerty pogodowe na e-mail” | ✅    |
| E2E-06| E2E         | User Story 6             | „Wyświetlanie ikon pogodowych” | ✅    |
| E2E-07| E2E         | User Story 7             | „Wyświetlanie prognozy 7-dniowej” | ✅    |
| E2E-08| E2E         | User Story 8             | „Wyświetlanie wykresów pogodowych” | ✅    |

---

### 4.3 Moduł: Ekonomia (Economy)

| ID    | Typ testu   | Co testujemy            | Scenariusz / funkcja                              | Status |
|-------|-------------|-------------------------|---------------------------------------------------|--------|
| UT-01 | Unit        | Inicjalizacja i atrybuty `Manager` | Walidacja pól, domyślne obiekty i klienta — [modules/ekonomia/tests/test_manager.py](../modules/ekonomia/tests/test_manager.py) | ✅ |
| UT-02 | Unit        | Aktualizacja danych (`Manager.update_all`) | Mockowanie źródeł → zwraca aktualne kursy i cenę złota — [modules/ekonomia/tests/test_manager.py](../modules/ekonomia/tests/test_manager.py) | ✅ |
| UT-03 | Unit        | Lista walut (`Manager.list_currencies`) | Filtracja, unikalność kodów, obsługa tabel — [modules/ekonomia/tests/test_manager.py](../modules/ekonomia/tests/test_manager.py) | ✅ |
| UT-04 | Unit        | Generowanie wykresów (`Manager.create_plot_image`) | Różne DataFrame (puste/None/kolumny niestandardowe) → base64 PNG — [modules/ekonomia/tests/test_manager.py](../modules/ekonomia/tests/test_manager.py) | ✅ |
| UT-05 | Unit        | Klient API (`APIClient.get_json`) | Obsługa poprawnej odpowiedzi, timeout, błędy HTTP — [modules/ekonomia/tests/test_api_client.py](../modules/ekonomia/tests/test_api_client.py) | ✅ |
| UT-06 | Unit        | Pobieranie kursów i listy (`CurrencyRates`) | Parsowanie odpowiedzi, filtrowanie tabel, puste odpowiedzi — [modules/ekonomia/tests/test_currency_rates.py](../modules/ekonomia/tests/test_currency_rates.py) | ✅ |
| UT-07 | Unit        | Fetch NBP (dane historyczne) | Parsowanie JSON, usuwanie duplikatów, filtrowanie starych dat — [modules/ekonomia/tests/test_fetch_nbp.py](../modules/ekonomia/tests/test_fetch_nbp.py) | ✅ |
| IT-01 | Integration | Widok główny `/ekonomia` (HTML) | `GET /ekonomia` → status 200, content-type HTML, zawiera elementy modułu — [modules/ekonomia/tests/test_ekonomia.py](../modules/ekonomia/tests/test_ekonomia.py) | ✅ |
| IT-02 | Integration | API kursów `/ekonomia/api/exchange-rates` | `GET` → status 200, `application/json`, struktura listy {code, rate} i obecność EUR/USD — [modules/ekonomia/tests/test_ekonomia.py](../modules/ekonomia/tests/test_ekonomia.py) | ✅ |
| IT-03 | Integration | Endpoint wykresu `/ekonomia/chart/<code>` | `GET /ekonomia/chart/EUR` → status 200, JSON z kluczem `chart` zawierającym base64 PNG — [modules/ekonomia/tests/test_ekonomia.py](../modules/ekonomia/tests/test_ekonomia.py) | ✅ |
| IT-04 | Integration | Ulubione waluty API (autoryzacja) | `GET/POST/DELETE /ekonomia/api/favorite-currencies` → statusy 401/200/201/409, struktura odpowiedzi; testy z sesją użytkownika i DB testową — [modules/ekonomia/tests/test_ekonomia.py](../modules/ekonomia/tests/test_ekonomia.py) | ✅ |
| IT-05 | Integration | Mockowanie zewnętrznych API | Przy integracyjnych endpointach mockować `Manager`/`APIClient` aby izolować logikę i sprawdzić format odpowiedzi — [modules/ekonomia/tests/test_ekonomia.py](../modules/ekonomia/tests/test_ekonomia.py) | ✅ |
| E2E-01 | E2E | User Story: widok dziennych kursów | Niezalogowany użytkownik otwiera `/ekonomia`, widzi USD/EUR/GBP w kaflach i w tabeli — [tests/e2e/test_daily_exchange_rates.py](../tests/e2e/test_daily_exchange_rates.py) | ✅ |
| E2E-02 | E2E | User Story: wykresy kursów walut | Użytkownik widzi wykres (base64 PNG/canvas), zmienia walutę w selektorze → wykres się aktualizuje — [tests/e2e/test_currency_charts.py](../tests/e2e/test_currency_charts.py) | ✅ |
| E2E-03 | E2E | User Story: zarządzanie ulubionymi walutami | Zalogowany użytkownik: dodaje/usuwa ulubione → interfejs i API odzwierciedlają zmiany (end-to-end) — [tests/e2e/test_logged_user_favorite_currencies.py](../tests/e2e/test_logged_user_favorite_currencies.py) | ✅ |

---

### 4.4 Moduł: Wiadomości (News)

| ID    | Typ testu   | Co testujemy            | Scenariusz / funkcja                              | Status |
|-------|-------------|-------------------------|---------------------------------------------------|--------|
| UT-01 | Unit        | Parsowanie danych       | **TU UZUPEŁNIĆ** (np. `parse_news_feed()`)        | ⬜     |
| UT-02 | Unit        | Filtrowanie/sortowanie  | **TU UZUPEŁNIĆ** (np. `filter_by_keyword()`)      | ⬜     |
| IT-01 | Integration | Endpoint HTML           | **TU UZUPEŁNIĆ** (np. `/news`)                    | ⬜     |
| IT-02 | Integration | Endpoint API            | **TU UZUPEŁNIĆ** (np. `/api/news/latest`)         | ⬜     |
| E2E-01| E2E         | User Story              | **TU UZUPEŁNIĆ** (np. „Użytkownik widzi listę wiadomości”) | ⬜ |

---

## 5. Powiązanie testów z User Stories

- Każda **User Story musi mieć co najmniej jeden test E2E**.
- Testy jednostkowe i integracyjne **wspierają** User Stories, ale nie zastępują testów akceptacyjnych.
- Numer User Story (np. `US-101`) powinien pojawiać się:
  - w nazwie testu,
  - w komentarzu w kodzie testu,
  - w tabeli planu testów (np. dopisz w kolumnie „Scenariusz / funkcja” lub w opisie testu).

---

## 6. Raport końcowy z testów (HTML)

Testy uruchamiane są przez **pytest**. Na koniec generowany jest **raport HTML**, który stanowi:

- ✅ **dowód wykonania testów**,
- ✅ część oddawanej dokumentacji projektu.

### Generowanie raportu HTML

```bash
pytest --html=report.html --self-contained-html
```

**Wymaganie:** raport HTML należy dołączyć do repozytorium w katalogu:

```
doc/assets/reports/
```

---

## 7. Statyczna analiza kodu (Linting)

Oprócz testów dynamicznych (Unit / Integration / E2E), w projekcie stosowana jest
**statyczna analiza kodu (linting)**, której celem jest poprawa jakości,
czytelności i spójności kodu źródłowego.

Statyczna analiza:
- **nie zastępuje testów**,
- nie weryfikuje logiki biznesowej,
- stanowi element kontroli jakości i **Definition of Done**.

W projekcie obowiązują dwa podstawowe narzędzia lintujące:
- **Python:** `flake8` (zgodność z PEP 8),
- **JavaScript:** `ESLint`.

---

### 7.1 Python – Flake8 (PEP 8)

W projekcie obowiązuje statyczna analiza kodu Python zgodnie z wytycznymi **PEP 8**,
realizowana z użyciem narzędzia **flake8**.

#### Wymagania
- Kod Python **nie powinien generować błędów flake8**,
- wyjątki są dopuszczalne wyłącznie w przypadkach **świadomych i uzasadnionych**.

#### Uruchamianie lokalnie
```bash
pip install flake8
flake8 .
```

Zaleca się uruchamianie flake8:
- przed wykonaniem commitów,
- przed utworzeniem Pull Requesta.

#### Wyjątki (`# noqa`)
Komentarz `# noqa` powoduje pominięcie danej linii kodu przez flake8.

Przykład:
```python
from module import *  # noqa: F403
```

Zasady:
- stosuj `# noqa` z **konkretnym kodem błędu**,
- użycie musi być **uzasadnione**,
- masowe wyciszanie błędów jest **niezalecane**.

#### Konfiguracja (`.flake8`)
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv
```

---

### 7.2 JavaScript – ESLint

Kod JavaScript w projekcie podlega statycznej analizie z użyciem **ESLint**.

#### Wymagania
- Kod JavaScript **nie powinien generować błędów ESLint**,
- wyjątki muszą być **świadome i uzasadnione**.

#### Uruchamianie lokalnie
```bash
npm install
npx eslint .
```

Zaleca się uruchamianie ESLint:
- przed wykonaniem commitów,
- przed utworzeniem Pull Requesta.

#### Wyjątki (`eslint-disable`)

Wyłączanie reguł dopuszczalne jest wyłącznie w uzasadnionych przypadkach.

Przykład (pojedyncza linia):
```js
// eslint-disable-next-line no-console
console.log("Debug info");
```

Przykład (cały plik):
```js
/* eslint-disable no-unused-vars */
```

Zasady:
- wyłączaj **konkretne reguły**, a nie całe narzędzie,
- unikaj wyłączania reguł globalnie bez uzasadnienia.

#### Konfiguracja (`.eslintrc`)
```json
{
  "env": {
    "browser": true,
    "es2021": true
  },
  "extends": ["eslint:recommended"],
  "parserOptions": {
    "ecmaVersion": "latest",
    "sourceType": "module"
  },
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "warn"
  }
}
```

---

### 7.3 Powiązanie z Definition of Done

Statyczna analiza kodu (flake8, ESLint) jest **elementem Definition of Done**.

Kod, który:
- spełnia wymagania funkcjonalne,
- posiada testy automatyczne,
- ale narusza podstawowe zasady jakości kodu,

**nie jest uznawany za ukończony**.

---

## 8. Uwagi końcowe

- Plan testów jest **częścią Definition of Done**.
- Brak testów E2E dla User Stories oznacza **niezrealizowaną funkcjonalność**.
