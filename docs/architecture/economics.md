# Architektura modułu: Moduł `nazwa_modułu`

> **Cel dokumentu:**  
> Ten dokument odpowiada na pytanie: **„Jak ten konkretny moduł działa i na jakich danych operuje?”**

> **Instrukcja:**  
> Uzupełnij wszystkie miejsca oznaczone **TU UZUPEŁNIĆ**.  
> Ten plik opisuje architekturę **konkretnego modułu**, za który odpowiada dany zespół.  
> Architektura wspólna całej aplikacji: [`doc/architecture.md`](../architecture.md)

---

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

**TU UZUPEŁNIĆ:** co testujecie jednostkowo (np. funkcje services, walidacja).

### 10.2 Integration tests (HTML/API)

**TU UZUPEŁNIĆ:** które endpointy są testowane integracyjnie.

### 10.3 Acceptance tests (Playwright)

Wymaganie: **min. 1 test Playwright na każde User Story modułu**.

**TU UZUPEŁNIĆ:** lista testów akceptacyjnych + mapowanie do US.

---

## 11. Ograniczenia, ryzyka, dalszy rozwój

**TU UZUPEŁNIĆ:** lista ograniczeń i propozycje usprawnień.
