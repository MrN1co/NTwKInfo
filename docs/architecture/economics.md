# Architektura modułu: Moduł Ekonomiczny

> **Cel dokumentu:**  
> Ten dokument odpowiada na pytanie: **„Jak ten konkretny moduł działa i na jakich danych operuje?”**


## 1. Cel modułu

Moduł ekonomii zajmuje się wszystkim, co związane z kursami walut i cenami złota. Pobiera aktualne dane ze strony NBP (Narodowy Bank Polski), przechowuje je w plikach JSON i wyświetla użytkownikowi w postaci tabel oraz wykresów. Dodatkowo oferuje kalkulator walutowy, żeby każdy mógł szybko przeliczyć kwotę z jednej waluty na drugą. Zalogowani użytkownicy mogą jeszcze zapisać sobie ulubione waluty, żeby szybciej znaleźli je na stronie.

---

## 2. Zakres funkcjonalny (powiązanie z User Stories)

Moduł realizuje poniższe User Stories:

-   **SCRUM-42** - Jako zalogowany użytkownik, chce mieć dostęp do dziennego kursu walut, aby być na bieżąco z aktualnymi cenami.
-   **SCRUM-41** - Jako zalogowany użytkownik, chce zobaczyć wykresy zmian kursu danej waluty, aby ocenić trendy.
-   **SCRUM-40** - Jako zalogowany użytkownik, chce zobaczyć po jakim kursie dokonano przeliczenia, aby mieć świadomość obliczeń.
-   **SCRUM-39** - Jako zalogowany użytkownik, chce, aby przeliczanie odbywało się natychmiast po wpisaniu kwoty, aby nie tracić czasu.
-   **SCRUM-38** - Jako zalogowany użytkownik, chce wybrać waluty z listy, które mogę przeliczyć, aby robić przeliczenia między dowolnymi walutami.
-   **SCRUM-37** - Jako zalogowany użytkownik, chce przeliczyć dowolną kwotę z jednej waluty na inną, aby poznać wartość w innej walucie.
-   **SCRUM-36** - Jako zalogowany użytkownik, chce zapisać najczęściej używane przeze mnie waluty, aby je szybko sprawdzać.
-   **SCRUM-34** - Jako niezalogowany użytkownik, chce zobaczyć aktualną cenę złota (w PLN), aby znać jej wartość w czasie rzeczywistym.
-   **SCRUM-33** - Jako zalogowany użytkownik, chcę ustawić domyślną walutę źródłową i docelową, aby przy kolejnych wizytach nie musieć ich wybierać ponownie.
-   **SCRUM-32** - Jako niezalogowany użytkownik, chce zobaczyć aktualne dzienne kursy USD, EUR oraz GBP, aby szybko sprawdzić najważniejsze waluty bez logowania.

**Nie zrealizowane (zaplanowane na przyszłość):**

-   SCRUM-35 - Historia ostatnich przeliczeń.
-   SCRUM-31 - Powiadomienia o zmianach kursu powyżej określonego progu.

---

## 3. Granice modułu (co wchodzi / co nie wchodzi)

### 3.1 Moduł odpowiada za

-   Pobieranie i buforowanie historycznych kursów walut (zapis JSON w `data/economics/*`).
-   Pobieranie i buforowanie historycznych cen złota (plik `data/economics/gold.json`).
-   Udostępnianie endpointów i widoków: strona `/ekonomia`, API `/ekonomia/api/exchange-rates` oraz API do zarządzania ulubionymi walutami (`/ekonomia/api/favorite-currencies`).
-   Generowanie wykresów (serwerowo, obrazy base64) dla walut i złota oraz przygotowanie danych do kalkulatora walutowego.
-   Logika biznesowa dostępu do aktualnych kursów poprzez warstwę serwisową (`Manager`, `CurrencyRates`, `GoldPrices`, `HistoricalData`).

### 3.2 Moduł nie odpowiada za

-   Zarządzanie kontami użytkowników i autoryzacją (realizowane przez `modules/auth` i model `User`).
-   Globalne zadania harmonogramu aplikacji (np. centralny scheduler) — moduł ma lokalne wywołanie aktualizacji (`fetch_nbp.run_update`) ale nie zarządza systemowym cronem.
-   Przechowywanie trwałych historycznych danych w bazie danych (moduł używa plików JSON jako cache/historyczne snapshoty).
-   Inne domeny aplikacji (news, weather itp.).

---

## 4. Struktura kodu modułu

**Struktura katalogów i plików (najważniejsze):**

-   `modules/ekonomia/ekonomia.py` — Flask Blueprint `ekonomia`; widoki, endpointy API, generowanie wykresów, ładowanie JSON-ów i integracja z `Manager`.
-   `modules/ekonomia/fetch_nbp.py` — skrypty pobierające dane z publicznego API NBP, łączące i zapisujące pliki JSON w `data/economics/` (obsługa limitu 93 dni per request, agregacja roczna).
-   `modules/ekonomia/fix_favorites_table.py` — narzędzie/migracja do odtworzenia tabeli `favorite_currencies` z kolumną `order` (skrypt jednorazowy).
-   `modules/ekonomia/klasy_api_obsluga/` — warstwa serwisowa:
    -   `APIClient.py` — prosty klient HTTP do pobierania JSON z NBP.
    -   `CurrencyRates.py` — logika pobierania listy walut i aktualnych kursów (tabele A/B/C).
    -   `GoldPrices.py` — pobieranie aktualnej ceny złota.
    -   `Manager.py` — koordynuje serwisy, udostępnia helpery (lista walut, tworzenie wykresów, pobranie aktualnych kursów/złota).
-   `modules/ekonomia/tests/` — testy jednostkowe i integracyjne modułu (`pytest`).

Ponadto:

-   `data/economics/` — snapshoty JSON z kursami i cenami złota (tworzone przez `fetch_nbp.py`).
-   `templates/ekonomia/exchange.html` — widok frontendowy modułu.
-   powiązane pliki JS/CSS w `static/js` i `static/css` (interakcje wykresów, kalkulator walutowy).

---

## 5. Interfejs modułu

> **Instrukcja:**
> Nie powielaj szczegółów request/response – pełna specyfikacja znajduje się w api_reference.md.

Poniżej przedstawiono endpointy udostępniane przez ten moduł.
Szczegółowa specyfikacja każdego endpointu (parametry, odpowiedzi, błędy)
znajduje się w pliku [`doc/api_reference.md`](../api_reference.md).

| Metoda | Ścieżka                                             | Typ  | Rola w module                                                         | Powiązane User Stories                                                         | Szczegóły                                                   |
| -----: | --------------------------------------------------- | ---- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------- |
|    GET | `/ekonomia`                                         | HTML | Widok główny modułu z kursami, wykresami, kalkulatorem i tabelą walut | SCRUM-32, SCRUM-34, SCRUM-37, SCRUM-38, SCRUM-39, SCRUM-40, SCRUM-41, SCRUM-42 | [Szczegóły](../api_reference.md#ekonomia-html)              |
|    GET | `/ekonomia/chart/<currency_code>`                   | JSON | Generowanie wykresu kursu wybranej waluty                             | SCRUM-41                                                                       | [Szczegóły](../api_reference.md#ekonomia-chart)             |
|    GET | `/ekonomia/api/exchange-rates`                      | JSON | Lista dostępnych walut z aktualnymi kursami                           | SCRUM-32, SCRUM-42                                                             | [Szczegóły](../api_reference.md#exchange-rates)             |
|    GET | `/ekonomia/api/favorite-currencies`                 | JSON | Pobranie listy ulubionych walut zalogowanego użytkownika (auth)       | SCRUM-36                                                                       | [Szczegóły](../api_reference.md#favorite-currencies-get)    |
|   POST | `/ekonomia/api/favorite-currencies`                 | JSON | Dodanie nowej ulubionej waluty (auth, max 3)                          | SCRUM-36                                                                       | [Szczegóły](../api_reference.md#favorite-currencies-post)   |
| DELETE | `/ekonomia/api/favorite-currencies/<currency_code>` | JSON | Usunięcie ulubionej waluty (auth)                                     | SCRUM-36                                                                       | [Szczegóły](../api_reference.md#favorite-currencies-delete) |

---

## 6. Zewnętrzne API wykorzystywane przez moduł

Moduł korzysta z publicznego API Narodowego Banku Polskiego (NBP). Poniżej opisano wykorzystywane zasoby, sposób mapowania odpowiedzi oraz informacje o autoryzacji i ograniczeniach.

Uwzględniono:

-   nazwę API i dostawcę
-   endpointy / zasoby wykorzystywane
-   autoryzację (klucz, token, brak)
-   limity i uwagi implementacyjne
-   mapowanie odpowiedzi API → struktura danych w projekcie

### 6.1 Konfiguracja (zmienne `.env`)

Wpisz zmienne używane do konfiguracji API:

| Zmienna | Przykład | Opis                                                                                                      | Wymagana |
| ------- | -------- | --------------------------------------------------------------------------------------------------------- | -------- |
| (brak)  | -        | Moduł korzysta z publicznego API NBP; w kodzie nie ma zmiennych środowiskowych wymaganych do autoryzacji. | NIE      |

> Szczegóły: [`doc/setup.md`](../setup.md)

### 6.2 Przykład zapytania do API (opcjonalnie)

```bash

# Pobranie tabeli A (lista walut)
curl "https://api.nbp.pl/api/exchangerates/tables/a/?format=json"

# Pobranie historycznych kursów (przykład: EUR za wybrany zakres)
curl "https://api.nbp.pl/api/exchangerates/rates/a/EUR/2024-01-01/2024-04-03/?format=json"

# Pobranie cen złota za zakres dat
curl "https://api.nbp.pl/api/cenyzlota/2024-01-01/2024-12-31/?format=json"
```

### 6.3 Obsługa błędów i fallback

**TU UZUPEŁNIĆ:** co się dzieje, gdy API nie działa / zwraca błąd / brak danych.

Obsługa błędów i fallback:

-   Funkcje w `fetch_nbp.py` i w klasach serwisowych (`APIClient`, `CurrencyRates`, `GoldPrices`, `HistoricalData`) obserwują status odpowiedzi i w przypadku błędu zwracają `None` lub pustą listę oraz logują błąd (print). Kod nie przerywa działania aplikacji.
-   Mechanizm fallback:
    -   Na stronach i endpointach modułu pierwszeństwo mają lokalne snapshoty z `data/economics/*.json` (funkcje `load_currency_json`, `load_gold_json`). Jeśli dane lokalne są dostępne, są używane bez żądań do API.
    -   Jeśli snapshot braknie lub jest niekompletny, warstwa `Manager` próbuje pobrać aktualne dane z NBP (`CurrencyRates.get_current_rates`, `GoldPrices.get_current_price`).
    -   API wykresu (`/ekonomia/chart/<currency_code>`) zwraca komunikat `{'success': False, 'message': 'Brak danych dla waluty ...'}` gdy nie ma danych.
    -   Operacje zapisu i odczytu JSON są odporne na częściowe błędy — `fetch_nbp.update_json` łączy nowe rekordy z istniejącymi i obcina dane starsze niż rok.
    -   Endpointy API zwracają odpowiednie statusy HTTP (401 dla braku autoryzacji, 400/409 dla błędnych danych, 500 dla wyjątków wewnętrznych).

---

## 7. Model danych modułu

> **Cel tej sekcji:**  
> Opisać **wszystkie dane**, na których operuje moduł.  
> Obejmuje to zarówno **encje bazodanowe**, jak i **obiekty domenowe bez własnych tabel**.

> **Ważne:**  
> Nie powtarzaj tutaj pełnego opisu encji wspólnych całej aplikacji  
> (np. `User`). Możesz się do nich odwołać.

---

### 7.1 Encje bazodanowe (tabele)

Dla każdej encji:

-   nazwa encji,
-   rola w module,
-   kluczowe pola,
-   relacje z innymi encjami.

**Encje specyficzne dla modułu:**

-   `FavoriteCurrency` (`favorite_currencies`)
    -   Rola: przechowuje maks. 3 ulubione waluty dla zalogowanego użytkownika, używane do personalizacji widoku ekonomicznego.
    -   Kluczowe pola: `id`, `user_id` (FK -> `users.id`), `currency_code` (string), `order` (integer — pozycja wyświetlania), `created_at`.
    -   Relacje: `user` (relacja do modelu `User` z `modules.database`).

Moduł nie tworzy innych tabel w bazie; historyczne dane kursowe i cen złota przechowywane są jako pliki JSON w `data/economics/`.

---

### 7.2 Obiekty domenowe (bez tabel w bazie)

Opisz obiekty:

-   pochodzące z API,
-   tworzone w logice modułu.

**Obiekty domenowe:**

-   `CurrencyRate` (słownik/rekord z API)
    -   Pola: `effectiveDate`, `mid`, `no` etc.; używane bezpośrednio lub konwertowane do pandas.DataFrame w celu tworzenia wykresów i agregacji.
-   `GoldPriceEntry`
    -   Pola: `data` / `date`, `cena` / `price`; mapowane do formatu `{"date": "YYYY-MM-DD", "price": <value>}` przy zapisie w `gold.json`.
-   `HistoricalDataFrame` (pandas.DataFrame)
    -   Wykorzystywany w `HistoricalData` i `Manager.create_plot_image` do generowania wykresów i agregacji czasowych.
-   `CurrencyRatesMap`
    -   Słownik mapujący kod waluty -> aktualny kurs (np. `{'EUR': 4.24, 'USD': 3.64, ...}`) używany przez frontend/kalkulator.

---

### 7.3 Relacje i przepływ danych

Opisz relacje i przepływ danych.

**TU UZUPEŁNIĆ**

**Relacje i przepływ danych (skrót):**

1. `fetch_nbp.run_update()` → pobiera dane z NBP (currency tables, rates, gold) i zapisuje snapshoty w `data/economics/*.json`.
2. `ekonomia.py` (widok `/ekonomia`) ładuje snapshoty przez `load_currency_json` / `load_gold_json` i uzupełnia je danymi z `Manager` jeśli brakuje aktualnych kursów.
3. `Manager` korzysta z `APIClient`, `CurrencyRates`, `GoldPrices`, `HistoricalData` do pobierania live danych lub agregowania historycznych DataFrame'ów.
4. Wyniki (maps, DataFrame, obrazy base64) przekazywane są do szablonu `templates/ekonomia/exchange.html` i do endpointów API (JSON, wykresy).
5. Użytkownik może zapisać ulubione waluty — zapisywane w tabeli `favorite_currencies` i odczytywane przy renderowaniu strony.

W skrócie: External API (NBP) → `fetch_nbp`/`Manager` → pliki JSON / pamięć → `ekonomia` blueprint → szablony/JSON → przeglądarka. Dodatkowo: zapisy użytkownika trafiają do DB (`FavoriteCurrency`).

---

## 8. Przepływ danych w module

Opisz 1 kluczowy scenariusz krok po kroku.

> **Instrukcja:** Scenariusz powinien odpowiadać jednej z User Stories wymienionych w sekcji 2.

Przykładowy scenariusz: „Jako użytkownik chcę zobaczyć stronę ekonomiczną z aktualnymi kursami i wykresami”

1. Użytkownik (browser) wysyła GET `/ekonomia`.
2. Handler `ekonomia()` w `modules/ekonomia/ekonomia.py` sprawdza plik `.last_update` w `data/economics/`. Jeśli brak lub upłynęło >24h, wywołuje `fetch_nbp.run_update()` w celu odświeżenia snapshotów JSON.
3. `ekonomia()` ładuje snapshoty (`load_currency_json`, `load_gold_json`), tworzy wykresy (funkcja `generate_currency_plot` i `Manager.create_plot_image`) oraz pobiera aktualne kursy przez `Manager().currencies.get_current_rates()` jako fallback/uzupełnienie.
4. Jeśli użytkownik jest zalogowany, pobierane są `FavoriteCurrency.get_for_user(user_id)` i uwzględniane przy renderowaniu (personalizacja, max 3).
5. Widok renderuje `exchange.html` z danymi: tabela kursów, obrazy wykresów (base64), kalkulator walutowy i interakcje JS. Klient może asynchronicznie wywołać `/ekonomia/chart/<code>` lub API do ulubionych walut.

---

## 9. Diagramy modułu (wymagane)

### 9.1 Diagram sekwencji (dla 1 user story)

**Opcja: Mermaid**

sequenceDiagram
participant U as User / Browser
participant F as Flask (ekonomia blueprint)
participant FN as fetch_nbp (cache updater)
participant API as NBP API
participant M as Service / Manager
participant DB as Database

U->>F: GET /ekonomia
F->>FN: check last_update
alt data outdated
FN->>API: fetch historical rates & gold (93d chunks)
API-->>FN: JSON data
FN-->>F: save economics/\*.json
end

F->>M: load data & prepare plots
opt current data needed
M->>API: fetch current rates / gold
API-->>M: JSON
end

F->>DB: FavoriteCurrency.get_for_user(user_id)
DB-->>F: favorites

F-->>U: render exchange.html<br/>(HTML + base64 charts + initial JSON)

### 9.2 Diagram komponentów modułu (opcjonalnie)

**Komponenty:**

-   `ekonomia` (Blueprint): kontrolery, renderowanie szablonów, punkty wejścia API.
-   `fetch_nbp.py`: proces pobierania i zapisu snapshotów JSON.
-   `klasy_api_obsluga` (serwisy): `APIClient`, `CurrencyRates`, `GoldPrices`, `HistoricalData`, `Manager` — logika komunikacji z NBP i przygotowania danych.
-   `data/economics/*`: lokalne snapshoty JSON (cache/history).
-   `database` (FavoriteCurrency): model DB do przechowywania ulubionych walut.
-   `templates/ekonomia/*` i `static/*`: warstwa prezentacji i skrypty klienckie.

---

## 10. Testowanie modułu

Szczegóły: [`doc/testing.md`](../testing.md)

### 10.1 Unit tests (pytest)

Testy jednostkowe znajdują się w `tests/unit/ekonomia/` i obejmują:

-   **`test_api_client.py`** — testy klasy `APIClient`:

    -   Inicjalizacja z domyślnym i niestandardowym base_url
    -   Pobieranie danych JSON (sukces, błąd HTTP, wyjątki)
    -   Obsługa błędów sieciowych i timeoutów

-   **`test_currency_rates.py`** — testy klasy `CurrencyRates`:

    -   Pobieranie listy walut z API NBP
    -   Pobieranie aktualnych kursów (tabele A, B, C)
    -   Mapowanie kursów do formatu słownikowego
    -   Obsługa błędów API (brak danych, nieprawidłowa odpowiedź)

-   **`test_gold_prices.py`** — testy klasy `GoldPrices`:

    -   Pobieranie aktualnej ceny złota
    -   Walidacja formatu odpowiedzi API
    -   Obsługa błędów i braków danych

-   **`test_manager.py`** — testy klasy `Manager`:

    -   Inicjalizacja komponentów (APIClient, CurrencyRates, GoldPrices)
    -   Metoda `update_all()` — koordynacja aktualizacji kursów i cen złota
    -   Generowanie wykresów (`create_plot_image`) z DataFrame'ów
    -   Pobieranie listy dostępnych walut

-   **`test_fetch_nbp.py`** — testy modułu `fetch_nbp`:

    -   Funkcje pomocnicze do dzielenia zakresu dat na chunki 93-dniowe (limit API NBP)
    -   Ładowanie i łączenie danych JSON (aktualizacja istniejących plików)
    -   Obcinanie danych starszych niż rok
    -   Obsługa błędów zapisu i parsowania JSON

-   **`test_homepage_rates.py`** — testy integracji z widokami homepage:
    -   Funkcje pomocnicze do ładowania danych JSON (`load_currency_json`, `load_gold_json`)
    -   Przygotowanie danych do wyświetlenia na stronie głównej

Testy wykorzystują `unittest.mock` (Mock, patch, MagicMock) do izolacji komponentów i symulacji odpowiedzi API.

### 10.2 Integration tests (HTML/API)

Testy integracyjne znajdują się w `tests/integration/test_ekonomia_integration.py` i weryfikują:

-   **GET `/ekonomia`** — widok główny modułu:

    -   Zwraca HTML z odpowiednim content-type
    -   Zawiera kluczowe elementy interfejsu (nagłówki, tabele walut)

-   **GET `/ekonomia/api/exchange-rates`** — lista dostępnych walut z kursami:

    -   Zwraca JSON z tablicą obiektów walut
    -   Każdy obiekt zawiera `code` i `rate`
    -   Zawiera główne waluty (EUR, USD, GBP, CHF)

-   **GET `/ekonomia/chart/<currency_code>`** — endpoint generowania wykresów:

    -   Zwraca JSON ze strukturą `{'success': bool, 'message': str, 'chart': str}`
    -   Wykres w formacie base64 PNG
    -   Obsługa błędów dla nieistniejących kodów walut

-   **GET `/ekonomia/api/favorite-currencies`** — ulubione waluty (wymaga autoryzacji):

    -   Zwraca 401 Unauthorized dla niezalogowanych użytkowników
    -   Zwraca JSON z listą ulubionych walut dla zalogowanych
    -   Maksymalnie 3 ulubione waluty

-   **POST `/ekonomia/api/favorite-currencies`** — dodawanie ulubionej waluty (wymaga autoryzacji):

    -   Zwraca 401 Unauthorized dla niezalogowanych
    -   Zwraca 201 Created po pomyślnym dodaniu
    -   Zwraca 409 Conflict przy próbie dodania 4. waluty (limit 3)
    -   Walidacja żądania (brak currency_code → 400 Bad Request)

-   **DELETE `/ekonomia/api/favorite-currencies/<currency_code>`** — usuwanie ulubionej waluty (wymaga autoryzacji):
    -   Zwraca 401 Unauthorized dla niezalogowanych
    -   Zwraca 200 OK po pomyślnym usunięciu
    -   Zwraca 404 Not Found dla nieistniejącej waluty

Testy integracyjne używają fixture `client` z aplikacji Flask i mockują warstwę serwisową (`Manager`), ale testują rzeczywiste routing, walidację, autoryzację i interakcję z bazą danych.

### 10.3 Acceptance tests (Playwright)

Wymaganie: **min. 1 test Playwright na każde User Story modułu**.

Testy akceptacyjne (E2E) znajdują się w `tests/e2e/` i realizują pełne scenariusze użytkownika:

| Test                                             | Plik                                       | User Stories       | Scenariusz                                                                                            |
| ------------------------------------------------ | ------------------------------------------ | ------------------ | ----------------------------------------------------------------------------------------------------- |
| `test_anonymous_user_views_daily_exchange_rates` | `test_anonymous_exchange_rates.py`         | SCRUM-32           | Niezalogowany użytkownik widzi kursy głównych walut (USD, EUR, CHF) bez logowania                     |
| `test_anonymous_user_views_gold_price`           | `test_anonymous_gold_price.py`             | SCRUM-34           | Niezalogowany użytkownik widzi aktualną cenę złota [oz] i wykres w skali roku                         |
| `test_user_converts_currencies_with_calculator`  | `test_currency_calculator.py`              | SCRUM-37, SCRUM-38 | Użytkownik wybiera waluty z listy dropdown, wpisuje kwotę i widzi przeliczenie                        |
| `test_user_gets_instant_currency_conversion`     | `test_currency_calculator.py`              | SCRUM-39           | Przeliczanie odbywa się natychmiast po wpisaniu kwoty (bez kliknięcia przycisku)                      |
| `test_user_converts_currencies_in_calculator`    | `test_logged_user_currency_preferences.py` | SCRUM-40           | Użytkownik widzi kurs użyty do przeliczenia w kalkulatorze                                            |
| `test_user_views_currency_trend_charts`          | `test_currency_charts.py`                  | SCRUM-41           | Użytkownik widzi wykresy zmian kursu walut (PNG base64), zmienia walutę i widzi zaktualizowany wykres |
| `test_daily_exchange_rates`                      | `test_daily_exchange_rates.py`             | SCRUM-42           | Zalogowany użytkownik ma dostęp do dziennych kursów wszystkich walut z tabeli                         |

**User Stories nie pokryte testami E2E:**

-   **SCRUM-36** — zapisywanie ulubionych walut (testowane w testach integracyjnych API)
-   **SCRUM-33** — ustawianie domyślnej waluty (funkcjonalność nie zrealizowana)
-   **SCRUM-35** — historia ostatnich przeliczeń (nie zrealizowane)
-   **SCRUM-31** — powiadomienia o zmianach kursu (nie zrealizowane)

Wszystkie testy E2E używają struktury **Given / When / Then**, wykorzystują `expect()` z Playwright oraz weryfikują rzeczywiste interakcje użytkownika z przeglądarką (Chrome headless).

---

## 11. Ograniczenia, ryzyka, dalszy rozwój

### 11.1 Obecne ograniczenia

**Zależność od NBP API:**
Cały moduł opiera się na publicznym API Narodowego Banku Polskiego. Jeśli NBP ma awarię albo zmieni format danych, aplikacja przestanie działać poprawnie. Co prawda mamy lokalny cache w postaci plików JSON, więc użytkownicy nadal będą widzieć ostatnio zapisane dane, ale przestaną się one aktualizować.

**Brak danych w czasie rzeczywistym:**
NBP publikuje kursy raz dziennie (zazwyczaj około godziny 12:00), więc nasze dane nie są real-time. Dla kogoś, kto chce śledzić szybkie zmiany kursów walut, to nie wystarczy. Pokazujemy kursy "dzienne", a nie te z ostatniej minuty.

**Przechowywanie w JSON zamiast w bazie:**
Wszystkie historyczne kursy trzymamy w plikach JSON w folderze `data/economics/`. To proste rozwiązanie, ale ma swoje problemy - trudniej zrobić backup, trudniej zapytać o konkretny zakres dat, i wszystko trzeba wczytywać do pamięci. Przy większej ilości danych (np. gdybyśmy chcieli trzymać historię za kilka lat) to może być problem.

**Brak historii przeliczeń:**
Użytkownik może sobie przeliczyć waluty w kalkulatorze, ale nigdzie nie zapisujemy tych operacji. Gdyby chciał wrócić do wcześniejszego przeliczenia albo zobaczyć, ile razy przeliczał EUR na PLN, to nie ma jak. To jest feature z backlogu (SCRUM-35), który nie został zrealizowany.

**Brak powiadomień o zmianach kursów:**
Nie ma możliwości ustawienia alertu typu "powiadom mnie, gdy EUR przekroczy 4.50 PLN". To również jest w backlogu (SCRUM-31), ale wymagałoby osobnego systemu powiadomień (email, push notifications), więc zostawiliśmy to na późniejsze usprawnienia strony.

**Limit 93 dni w jednym zapytaniu do NBP:**
API NBP ma ograniczenie - nie możemy pobrać więcej niż 93 dni danych w jednym zapytaniu. Nasz kod (`fetch_nbp.py`) radzi sobie z tym, dzieląc żądania na mniejsze kawałki, ale to oznacza więcej requestów i dłuższy czas aktualizacji przy pierwszym uruchomieniu.

### 11.2 Ryzyka

**Zmiana API NBP bez zapowiedzi:**
Jeśli NBP zdecyduje się zmienić strukturę odpowiedzi API (np. zmieni nazwy pól z `mid` na `rate`), nasz kod przestanie działać. Nie mamy kontroli nad tym API, więc musimy być gotowi na szybką reakcję. Teoretycznie moglibyśmy dodać testy monitorujące strukturę odpowiedzi i alerty, gdy coś się zmieni.

**Problem z wydajnością przy wielu użytkownikach:**
Jeśli nagle przybędzie dużo użytkowników i wszyscy będą generować wykresy jednocześnie, serwer może się przeciążyć (generowanie wykresów matplotlib jest CPU-intensive). Obecnie nie mamy cache'owania wykresów - każde wywołanie `/ekonomia/chart/<code>` generuje wykres od nowa.

### 11.3 Propozycje dalszego rozwoju

**Migracja z JSON do bazy danych:**
Przenieść historyczne kursy z plików JSON do tabeli PostgreSQL. To umożliwi łatwiejsze zapytania (np. "pokaż mi wszystkie dni, kiedy EUR był powyżej 4.50"), lepszą wydajność i prostsze backupy. Moduł nadal może działać z cache'em, ale jako główne źródło prawdy będzie baza.

**Implementacja brakujących User Stories:**

-   SCRUM-35 (historia przeliczeń) — dodać tabelę `conversion_history` w bazie, gdzie zapiszemy każde przeliczenie użytkownika wraz z datą, walutami i kwotami.
-   SCRUM-31 (powiadomienia o zmianach) — dodać tabelę `currency_alerts`, gdzie użytkownik może ustawić próg (np. "EUR > 4.50") i dostać email/powiadomienie push, gdy warunek zostanie spełniony.

**Cache wykresów:**
Dodać Redis lub prosty cache w pamięci, żeby wykresy generowane dla popularnych walut (EUR, USD) były zapisywane na np. 1 godzinę. To zmniejszy obciążenie serwera i przyspieszy ładowanie dla użytkowników.

**Więcej źródeł danych:**
Dodać kryptowaluty (Bitcoin, Ethereum) dla użytkowników zainteresowanych rynkiem crypto.git
