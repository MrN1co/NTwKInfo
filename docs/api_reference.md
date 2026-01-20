# Referencja API (`api_reference.md`)

> **Cel dokumentu**  
> Ten plik stanowi **jedno źródło prawdy o wszystkich endpointach aplikacji**  
> (zarówno HTML, jak i API JSON).  
> Jest podstawą do **testów integracyjnych** oraz formalnym **kontraktem API** dla całego projektu.

> **Instrukcja:**
>
> -   Opisz **wszystkie endpointy aplikacji** (HTML i JSON).
> -   Każdy endpoint musi mieć **kompletny i jednoznaczny opis**.
> -   **Nie opisuj tutaj architektury modułów** – do tego służą pliki w `doc/architecture/<module>.md`.
> -   Dokument ten powinien umożliwić napisanie **testów integracyjnych bez zaglądania do kodu**.

---

## 1. Informacje ogólne

**TU UZUPEŁNIĆ (jeśli dotyczy):**

-   **Base URL (lokalnie):** `http://localhost:5000`
-   **Base URL (produkcyjnie):** `http://18.184.92.43`
-   **Format danych (API):** JSON
-   **Kodowanie:** UTF-8
-   **Framework:** Flask

---

## 2. Konwencje odpowiedzi (API JSON)

> **Instrukcja:**  
> Jeśli w projekcie stosujecie jednolity format odpowiedzi API, opiszcie go tutaj.

### 2.1 Sukces (przykład)

```json
{
    "status": "success",
    "data": {}
}
```

### 2.2 Błąd (przykład)

```json
{
    "status": "error",
    "message": "Opis błędu"
}
```

---

## 3. Lista endpointów (skrót / spis treści)

> **Instrukcja:**  
> Poniższa tabela jest **pełnym spisem endpointów aplikacji**.  
> Każdy endpoint wymieniony tutaj **musi** być opisany szczegółowo w dalszej części dokumentu.

|  Metoda | Endpoint                                   | Typ   | Krótki opis                          | Moduł    |
| ------: | ------------------------------------------ | ----- | ------------------------------------ | -------- |
|     GET | `/`                                        | HTML  | Strona główna aplikacji              | Home     |
|     GET | `/weather/pogoda`                          | HTML  | Widok bieżącej pogody                | Weather  |
|     GET | `/api/weather/forecast`                    | JSON  | Dane pogodowe                        | Weather  |
|    POST | `/api/weather/favorites`                   | JSON  | Zapis ulubionych miast               | Weather  |
|     GET | `/ekonomia`                                | HTML  | Kursy walut i ceny złota             | Ekonomia |
|     GET | `/ekonomia/chart/<code>`                   | JSON  | Wykres kursu waluty                  | Ekonomia |
|     GET | `/ekonomia/api/exchange-rates`             | JSON  | Lista dostępnych walut               | Ekonomia |
|     GET | `/ekonomia/api/favorite-currencies`        | JSON  | Moje ulubione waluty                 | Ekonomia |
|    POST | `/ekonomia/api/favorite-currencies`        | JSON  | Dodaj ulubioną walutę                | Ekonomia |
|  DELETE | `/ekonomia/api/favorite-currencies/<code>` | JSON  | Usuń ulubioną walutę                 | Ekonomia |
|     GET | `/news`                                    | HTML  | Lista wiadomości                     | News     |
|     GET | `/api/news/latest`                         | JSON  | Najnowsze wiadomości                 | News     |
|  Metoda | Endpoint                                   | Typ   | Krótki opis                          | Moduł    |
| ------: | ----------                                 | ----- | -------------                        | -------  |
|     GET | `/`                                        | HTML  | Strona główna aplikacji              | Home     |
|     GET | `/weather/pogoda`                          | HTML  | Widok bieżącej pogody                | Weather  |
|     GET | `/weather/api/forecast`                    | JSON  | 7-dniowa prognoza pogody             | Weather  |
|     GET | `/weather/api/favorites`                   | JSON  | Lista ulubionych miast               | Weather  |
|    POST | `/weather/api/favorites`                   | JSON  | Dodanie ulubionego miasta            | Weather  |
|  DELETE | `/weather/api/favorites`                   | JSON  | Usunięcie ulubionego miasta          | Weather  |
|     GET | `/weather/api/geocode`                     | JSON  | Wyszukiwanie miast                   | Weather  |
|     GET | `/weather/api/hourly`                      | JSON  | Godzinowa prognoza pogody            | Weather  |
|     GET | `/weather/plot.png`                        | PNG   | Wykres prognozy pogody               | Weather  |
|     GET | `/economy`                                 | HTML  | Widok danych ekonomicznych           | Economy  |
|     GET | `/api/economy/rates`                       | JSON  | Kursy walut                          | Economy  |
|     GET | `/news`                                    | HTML  | Lista wiadomości z filtrami          | News     |
|     GET | `/news_sport`                              | HTML  | Wiadomości sportowe                  | News     |
|     GET | `/tables`                                  | HTML  | Tabele ligowe i rankingi             | News     |
|     GET | `/history/view`                            | HTML  | Historia kliknięć (wymaga logowania) | News     |
|     GET | `/history/api`                             | JSON  | Historia kliknięć API                | News     |
|    POST | `/history/log`                             | JSON  | Logowanie kliknięcia w artykuł       | News     |
|    POST | `/history/clear`                           | JSON  | Czyszczenie historii                 | News     |
|    POST | `/history/delete/<int:entry_id>`           | JSON  | Usunięcie wpisu historii             | News     |
|     GET | `/image_proxy`                             | PROXY | Proxy dla obrazków z policji         | News     |

---

## 4. Endpointy HTML

> **Instrukcja:**  
> Opisz wszystkie endpointy renderujące widoki HTML.  
> Skup się na **trasach, parametrach i zachowaniu widoku**, a nie na wyglądzie UI.

---

### 4.1 GET `/`

**Moduł:** Home

**Opis:**  
**TU UZUPEŁNIĆ** – krótki opis celu widoku.

**Parametry:** brak

**Odpowiedź:**  
Renderowany widok HTML.

**Powiązana User Story:** **TU UZUPEŁNIĆ**

---

### 4.2 GET `/weather/pogoda`

**Moduł:** Weather

**Opis:**  
Widok pogodowy dostosowany do stanu autentykacji użytkownika. Dla zalogowanych użytkowników pokazuje dedykowany widok z sekcją ulubionych miast. Dla użytkowników anonimowych wyświetla standardowy widok pogodowy.

**Parametry (query):**

-   brak

**Odpowiedź:**

-   Dla zalogowanych użytkowników: HTML `weather-login.html` (zawiera sekcję ulubionych miast)
-   Dla użytkowników anonimowych: HTML `weather.html` (widok podstawowy)

**Powiązana User Story:** Wyświetlenie prognozy pogody, zarządzanie ulubionymi miastami dla zalogowanych użytkowników

---

### 4.3 GET `/ekonomia`

**Moduł:** Ekonomia

**Opis:**  
Główny widok modułu ekonomii. Wyświetla bieżące kursy walut (EUR, USD, CHF), ceny złota oraz interaktywny kalkulator walutowy. Dla zalogowanych użytkowników dodatkowo dostępna sekcja zarządzania ulubionymi walutami. Dla użytkowników anonimowych wyświetlane są domyślne kursy i pełna tabela dostępnych walut.

**Parametry (query):**

-   brak

**Odpowiedź:**  
HTML `ekonomia/exchange.html` zawierające:

-   Kafelki z aktualnymi kursami walut (EUR, USD, CHF z danych JSON)
-   Wykresy historyczne kursów walut
-   Cenę złota z wykresem historycznym
-   Kalkulator walutowy
-   Dla zalogowanych użytkowników: sekcja ulubionych walut (max 3)
-   Tabelę wszystkich dostępnych walut (z kursami z API)

**Dane renderowane:**

-   `kurs_walut` – słownik bieżących kursów walut: `{"EUR": 4.25, "USD": 4.10, "CHF": 4.80}`
-   `cena_zlota` – bieżąca cena złota (uncja w PLN)
-   `cena_zlota_formatted` – cena złota sformatowana polskim formatem (np. "2 345,67")
-   `wykres_waluty` – wykres EUR w formacie base64 PNG
-   `wykres_zlota` – wykres ceny złota w formacie base64 PNG
-   `currency_codes` – lista dostępnych kodów walut
-   `currency_rates` – słownik wszystkich kursów walut z API
-   `all_currencies_for_tiles` – wszystkie waluty do wyświetlenia w tabelach
-   `is_authenticated` – boolean, czy użytkownik jest zalogowany

**Powiązana User Story:** Wyświetlenie kursów walut, cen złota i zarządzanie ulubionymi walutami dla zalogowanych użytkowników

---

## 5. Endpointy API (JSON)

> **Instrukcja:**  
> Każdy endpoint API musi być opisany w sposób umożliwiający:
>
> -   przygotowanie testów integracyjnych,
> -   przygotowanie klienta API,
> -   weryfikację zgodności implementacji z dokumentacją.

---

### 5.1 GET `/weather/api/forecast`

**Moduł:** Weather

**Opis:**  
Zwraca 7-dniową prognozę pogody w postaci kafelków dziennych. Dane pobierane są z OpenWeather API. Domyślną lokalizacją jest Kraków (50.0647°N, 19.9450°E). Endpoint zawiera wbudowaną cache na 1 minutę.

**Parametry (query):**

-   `lat` (float, opcjonalny) – szerokość geograficzna; domyślnie 50.0647 (Kraków)
-   `lon` (float, opcjonalny) – długość geograficzna; domyślnie 19.9450 (Kraków)
-   `label` (string, opcjonalny) – nazwa miasta do wyświetlenia; jeśli nie podana, przy domyślnych współrzędnych używa się "Kraków"

**Przykład zapytania:**

```bash
curl "http://localhost:5000/weather/api/forecast?lat=52.2297&lon=21.0122&label=Warszawa"
```

**Przykład odpowiedzi:**

```json
{
    "city": "Warszawa",
    "days": [
        {
            "day_name": "Czwartek",
            "date": "2025-01-16",
            "temp_min": -2.5,
            "temp_max": 3.2,
            "condition": "Pochmurnie",
            "condition_code": "04d",
            "precip_mm": 0.5,
            "wind_kmh": 12.0
        }
    ]
}
```

**Kody odpowiedzi:**

-   `200` – OK, prognoza zwrócona
-   `400` – błędne parametry lat/lon
-   `502` – błąd OpenWeather API
-   `500` – błąd backendu

**Powiązana User Story:** Wyświetlenie 7-dniowej prognozy pogody

---

### 5.2 GET `/weather/api/favorites`

**Moduł:** Weather

**Opis:**  
Zwraca listę ulubionych miast dla zalogowanego użytkownika. Endpoint wymaga autentykacji sesji.

**Autentykacja:** Wymagana – sesja użytkownika

**Parametry (query):**

-   brak

**Przykład zapytania:**

```bash
curl "http://localhost:5000/weather/api/favorites" -H "Cookie: session=..."
```

**Przykład odpowiedzi:**

```json
{
    "favorites": [
        {
            "id": 1,
            "city": "Kraków",
            "lat": 50.0647,
            "lon": 19.945
        },
        {
            "id": 2,
            "city": "Warszawa",
            "lat": 52.2297,
            "lon": 21.0122
        }
    ]
}
```

**Kody odpowiedzi:**

-   `200` – OK, lista ulubionych zwrócona
-   `401` – użytkownik nie zalogowany

**Powiązana User Story:** Wyświetlenie listy ulubionych miast

---

### 5.3 POST `/weather/api/favorites`

**Moduł:** Weather

**Opis:**  
Dodaje nowe ulubione miasto dla zalogowanego użytkownika. Endpoint uniemożliwia dodanie duplikatów miasta dla tego samego użytkownika.

**Autentykacja:** Wymagana – sesja użytkownika (dekorator `@api_login_required`)

**Body (JSON):**

```json
{
    "city": "Gdańsk",
    "lat": 54.352,
    "lon": 18.6466
}
```

**Parametry Body:**

-   `city` (string, wymagany) – nazwa miasta
-   `lat` (float, opcjonalny) – szerokość geograficzna
-   `lon` (float, opcjonalny) – długość geograficzna

**Przykład odpowiedzi (sukces):**

```json
{
    "id": 3,
    "city": "Gdańsk",
    "lat": 54.352,
    "lon": 18.6466
}
```

**Kody odpowiedzi:**

-   `201` – Created, miasto dodane
-   `400` – brak pola `city` w body
-   `401` – użytkownik nie zalogowany
-   `409` – miasto już istnieje w ulubionych tego użytkownika

**Powiązana User Story:** Dodanie miasta do ulubionych

---

### 5.4 DELETE `/weather/api/favorites`

**Moduł:** Weather

**Opis:**  
Usuwa ulubione miasto dla zalogowanego użytkownika. Można usunąć po ID lub nazwie miasta.

**Autentykacja:** Wymagana – sesja użytkownika (dekorator `@api_login_required`)

**Body (JSON):**

```json
{
    "id": 3
}
```

Lub:

```json
{
    "city": "Gdańsk"
}
```

**Parametry Body:**

-   `id` (int, opcjonalny) – ID ulubionego miasta
-   `city` (string, opcjonalny) – nazwa miasta

(Wymagany co najmniej jeden z parametrów)

**Przykład odpowiedzi (sukces):**

```json
{
    "ok": true
}
```

**Kody odpowiedzi:**

-   `200` – OK, miasto usunięte
-   `400` – brak pola `id` i `city`
-   `401` – użytkownik nie zalogowany
-   `404` – miasto nie znalezione

**Powiązana User Story:** Usunięcie miasta z ulubionych

---

### 5.5 GET `/weather/api/geocode`

**Moduł:** Weather

**Opis:**  
Wyszukuje miasta po nazwie. Zwraca listę lokalizacji ze współrzędnymi geograficznymi. Dane pobierane z OpenWeather Geocoding API. Maksymalnie 5 wyników.

**Parametry (query):**

-   `q` (string, wymagany) – nazwa miasta do wyszukania

**Przykład zapytania:**

```bash
curl "http://localhost:5000/weather/api/geocode?q=Warszawa"
```

**Przykład odpowiedzi:**

```json
[
    {
        "name": "Warszawa",
        "lat": 52.2297,
        "lon": 21.0122,
        "country": "PL"
    }
]
```

**Kody odpowiedzi:**

-   `200` – OK
-   `500` – błąd serwera (np. brak dostępu do danych)

**Powiązane User Stories:** SCRUM-32, SCRUM-42

---

### 5.6 GET `/ekonomia/chart/<currency_code>`

**Moduł:** Ekonomia

**Opis:**  
Generuje wykres zmian kursu wybranej waluty za ostatni rok. Zwraca obraz w formacie PNG zakodowany w base64.

**Parametry (path):**

-   `currency_code` (string, wymagany) – kod waluty (np. EUR, USD, CHF)

**Przykład zapytania:**

```bash
curl "http://localhost:5000/ekonomia/chart/EUR"
```

**Przykład odpowiedzi:**

```json
{
    "success": true,
    "message": "Wykres dla EUR wygenerowany",
    "chart": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
}
```

**Kody odpowiedzi:**

-   `200` – OK
-   `400` – kod waluty nie znaleziony

**Powiązana User Story:** SCRUM-41

---

### 5.7 GET `/ekonomia/api/exchange-rates`

**Moduł:** Ekonomia

**Opis:**  
Zwraca listę dostępnych walut z ich bieżącymi kursami w stosunku do PLN. Dane pobierane z NBP API. Brak wymaganej autoryzacji – endpoint dostępny dla wszystkich użytkowników.

**Parametry (query):**

-   brak

**Autoryzacja:** Brak wymagań

**Przykład zapytania:**

```bash
curl "http://localhost:5000/ekonomia/api/exchange-rates"
```

**Przykład odpowiedzi:**

```json
[
    { "code": "EUR", "rate": 4.25 },
    { "code": "USD", "rate": 4.1 },
    { "code": "CHF", "rate": 4.8 },
    { "code": "GBP", "rate": 5.12 },
    { "code": "JPY", "rate": 0.028 },
    { "code": "AUD", "rate": 2.75 },
    { "code": "CAD", "rate": 2.95 },
    { "code": "NOK", "rate": 0.38 },
    { "code": "SEK", "rate": 0.39 },
    { "code": "DKK", "rate": 0.57 }
]
```

**Kody odpowiedzi:**

-   `200` – OK, lista walut zwrócona
-   `500` – błąd serwera (np. brak dostępu do NBP API)

**Powiązana User Story:** SCRUM-41

---

### 5.8 GET `/ekonomia/api/favorite-currencies`

**Moduł:** Ekonomia

**Opis:**  
Zwraca listę ulubionych walut zalogowanego użytkownika. Wymaga autoryzacji (sesji).

**Parametry:** brak

**Autoryzacja:** Wymagana sesja zalogowanego użytkownika

**Przykład zapytania:**

```bash
curl -b "session=xxx" "http://localhost:5000/ekonomia/api/favorite-currencies"
```

**Przykład odpowiedzi:**

```json
{
    "favorite_currencies": [
        { "currency_code": "EUR", "order": 1 },
        { "currency_code": "GBP", "order": 2 },
        { "currency_code": "JPY", "order": 3 }
    ]
}
```

**Kody odpowiedzi:**

-   `200` – OK
-   `401` – brak autoryzacji (użytkownik nie zalogowany)

**Powiązana User Story:** SCRUM-36

---

### 5.9 POST `/ekonomia/api/favorite-currencies`

**Moduł:** Ekonomia

**Opis:**  
Dodaje nową ulubioną walutę do listy zalogowanego użytkownika. Maksymalnie 3 waluty na użytkownika. Wymaga autoryzacji.

**Autoryzacja:** Wymagana sesja zalogowanego użytkownika

**Body (JSON):**

```json
{
    "currency_code": "CHF"
}
```

**Przykład zapytania:**

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"currency_code": "CHF"}' \
  -b "session=xxx" \
  "http://localhost:5000/ekonomia/api/favorite-currencies"
```

**Przykład odpowiedzi (sukces):**

```json
{
    "favorite_currencies": [
        { "currency_code": "EUR", "order": 1 },
        { "currency_code": "GBP", "order": 2 },
        { "currency_code": "CHF", "order": 3 }
    ]
}
```

**Kody odpowiedzi:**

-   `201` – Created (waluta dodana)
-   `400` – brak lub niepoprawny kod waluty
-   `401` – brak autoryzacji
-   `409` – osiągnięty limit 3 ulubionych walut

**Powiązana User Story:** SCRUM-36

---

### 5.10 DELETE `/ekonomia/api/favorite-currencies/<currency_code>`

**Moduł:** Ekonomia

**Opis:**  
Usuwa ulubioną walutę z listy zalogowanego użytkownika. Wymaga autoryzacji.

**Parametry (path):**

-   `currency_code` (string, wymagany) – kod waluty do usunięcia

**Autoryzacja:** Wymagana sesja zalogowanego użytkownika

**Przykład zapytania:**

```bash
curl -X DELETE -b "session=xxx" \
  "http://localhost:5000/ekonomia/api/favorite-currencies/EUR"
```

**Przykład odpowiedzi:**

```json
{
    "favorite_currencies": [
        { "currency_code": "GBP", "order": 1 },
        { "currency_code": "CHF", "order": 2 }
    ]
}
```

**Kody odpowiedzi:**

-   `200` – OK
-   `401` – brak autoryzacji
-   `404` – waluta nie znaleziona na liście ulubionych

**Powiązana User Story:** SCRUM-36

---

## 6. Uwierzytelnianie i autoryzacja

> **Instrukcja:**  
> Opisz, które endpointy wymagają uwierzytelnienia oraz w jaki sposób
> (np. sesja, token, nagłówki HTTP).

### 6.1 Moduł Ekonomii

**Mechanizm:** Sesja HTTP (cookie)

**Endpointy wymagające autoryzacji (Ekonomia):**

-   `GET /ekonomia/api/favorite-currencies` – zwraca ulubione waluty zalogowanego użytkownika
-   `POST /ekonomia/api/favorite-currencies` – dodawanie ulubionych walut
-   `DELETE /ekonomia/api/favorite-currencies/<currency_code>` – usuwanie ulubionych walut

**Endpointy dostępne dla wszystkich (bez autoryzacji):**

-   `GET /ekonomia` – główny widok (anonimowi użytkownicy widzą domyślne kursy i tabelę walut)
-   `GET /ekonomia/api/exchange-rates` – lista dostępnych walut
-   `GET /ekonomia/chart/<currency_code>` – wykresy walut

**Obsługa błędów autoryzacji:**

-   `401 Unauthorized` – brak ważnej sesji lub użytkownik nie zalogowany

### 6.2 Moduł Weather

**Typ autentykacji:** Sesja (session-based authentication)

**Endpointy wymagające uwierzytelnienia:**

| Endpoint                 | Metoda | Wymagane | Opis                                    |
| ------------------------ | ------ | -------- | --------------------------------------- |
| `/weather/api/favorites` | GET    | Tak      | Pobieranie ulubionych miast użytkownika |
| `/weather/api/favorites` | POST   | Tak      | Dodawanie ulubionego miasta             |
| `/weather/api/favorites` | DELETE | Tak      | Usuwanie ulubionego miasta              |

**Endpointy publiczne (brak wymaganej autentykacji):**

| Endpoint                | Metoda | Opis                                               |
| ----------------------- | ------ | -------------------------------------------------- |
| `/weather/pogoda`       | GET    | Widok pogodowy (dostosowany do stanu autentykacji) |
| `/weather/api/forecast` | GET    | Prognoza pogody                                    |
| `/weather/api/geocode`  | GET    | Wyszukiwanie miast                                 |
| `/weather/api/hourly`   | GET    | Prognoza godzinowa                                 |
| `/weather/plot.png`     | GET    | Wykres pogody                                      |

**Obsługa sesji:**

-   Sesja jest przechowywana w ciasteczku `session`
-   Identyfikator użytkownika dostępny w obiekcie `session['user_id']`
-   Dla endpointów wymagających autentykacji zwracany jest kod `401` jeśli `session['user_id']` nie istnieje
-   Uwierzytelnianie jest obsługiwane przez dekorator `@api_login_required`

---

## 7. Wymagania testowe (integracyjne)

> **Instrukcja:**  
> Każdy endpoint opisany w tym pliku:
>
> -   musi mieć **co najmniej jeden test integracyjny**,
> -   powinien być jednoznacznie testowalny na podstawie tej dokumentacji.

**TU UZUPEŁNIĆ (opcjonalnie):**

-   mapowanie endpoint → test integracyjny,
-   informacje o mockowaniu zewnętrznych API.

### 7.1 Moduł Ekonomia

Wszystkie endpointy modułu ekonomia są pokryte testami integracyjnymi w pliku `tests/integration/test_ekonomia_integration.py`.

**Mapowanie endpoint → test integracyjny:**

| Endpoint                                            | Metoda | Test integracyjny                                                                                                                                              | Zakres weryfikacji                                                                                    |
| --------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `/ekonomia`                                         | GET    | `test_ekonomia_main_page_returns_html`                                                                                                                         | Zwraca HTML z odpowiednim content-type, zawiera elementy modułu                                       |
| `/ekonomia/api/exchange-rates`                      | GET    | `test_ekonomia_api_exchange_rates_returns_json`                                                                                                                | Zwraca JSON z listą walut, weryfikacja struktury (`code`, `rate`), obecność głównych walut (EUR, USD) |
| `/ekonomia/chart/<currency_code>`                   | GET    | `test_ekonomia_chart_endpoint_returns_image`                                                                                                                   | Zwraca JSON ze strukturą `{'success': bool, 'message': str, 'chart': str}`, wykres w base64 PNG       |
| `/ekonomia/api/favorite-currencies`                 | GET    | `test_favorite_currencies_get_requires_authentication`                                                                                                         | Zwraca 401 dla niezalogowanych, zwraca JSON z listą dla zalogowanych                                  |
| `/ekonomia/api/favorite-currencies`                 | POST   | `test_favorite_currencies_post_requires_authentication`<br/>`test_favorite_currencies_post_validates_input`<br/>`test_favorite_currencies_post_enforces_limit` | Zwraca 401 dla niezalogowanych, 201 po dodaniu, 409 przy limicie (max 3), 400 dla błędnych danych     |
| `/ekonomia/api/favorite-currencies/<currency_code>` | DELETE | `test_favorite_currencies_delete_requires_authentication`<br/>`test_favorite_currencies_delete_removes_currency`                                               | Zwraca 401 dla niezalogowanych, 200 po usunięciu, 404 dla nieistniejącej waluty                       |

**Mockowanie zewnętrznych API:**

Wszystkie testy integracyjne modułu ekonomia **mockują** klasę `Manager` z `modules.ekonomia.ekonomia`, która jest odpowiedzialna za komunikację z NBP API. Dzięki temu:

-   Testy są szybkie i nie zależą od dostępności zewnętrznego API
-   Możemy symulować różne scenariusze (sukces, błędy, brak danych)
-   Testujemy logikę aplikacji bez testowania NBP API

Przykład mockowania:

```python
with patch('modules.ekonomia.ekonomia.Manager') as mock_manager:
    mock_manager.return_value.currencies.get_current_rates.return_value = {
        'eur': 4.32, 'usd': 4.05, 'gbp': 5.15
    }
    response = client.get('/ekonomia/api/exchange-rates')
```

**Obsługa bazy danych:**

Testy integracyjne używają fixture `client` z Flask, który automatycznie konfiguruje testową bazę danych (SQLite in-memory lub osobna instancja). Model `FavoriteCurrency` i jego relacje z `User` są testowane z rzeczywistą bazą danych, co pozwala weryfikować:

-   Autoryzację (sesje użytkowników)
-   Ograniczenia bazodanowe (limit 3 ulubionych walut)
-   Operacje CRUD na ulubionych walutach
    > -   musi mieć **co najmniej jeden test integracyjny**,
    > -   powinien być jednoznacznie testowalny na podstawie tej dokumentacji.

**TU UZUPEŁNIĆ (opcjonalnie):**

-   mapowanie endpoint → test integracyjny,
-   informacje o mockowaniu zewnętrznych API.

---

## 8. Moduł News - Endpointy HTML

### 8.1 GET `/news`

**Moduł:** News

**Opis:**  
Wyświetla wszystkie wiadomości z różnych źródeł (kryminalki, sport, policja) z możliwością filtrowania po tagach. Obsługuje zapisywanie ulubionych tagów dla zalogowanych użytkowników.

**Parametry (query):**

-   `tags` (string, opcjonalny) – lista tagów oddzielonych przecinkami do filtrowania wiadomości (np. `tags=piłka-nożna,tenis`)

**Przykład zapytania:**

```bash
curl "http://localhost:5000/news?tags=piłka-nożna,kryminalne"
```

**Odpowiedź:**  
Renderowany widok HTML `news/news.html` z wiadomościami spełniającymi kryteria filtrowania.

**Kontekst szablonu:**

-   `news_list` – lista wiadomości (posortowana po timestamp)
-   `selected_tags` – lista aktualnie wybranych tagów

**Powiązane User Stories:** SCRUM-10, SCRUM-11, SCRUM-12, SCRUM-13

---

### 8.2 GET `/news_sport`

**Moduł:** News

**Opis:**  
Wyświetla wiadomości sportowe z Przeglądu Sportowego. Jeśli brak danych w cache, pobiera świeże dane jako fallback.

**Parametry:** brak

**Odpowiedź:**  
Renderowany widok HTML `news/news_sport.html`

**Kontekst szablonu:**

-   `news_list` – lista wiadomości sportowych
-   `updated_at` – czas ostatniej aktualizacji

**Powiązane User Stories:** SCRUM-10, SCRUM-11

---

### 8.3 GET `/tables`

**Moduł:** News

**Opis:**  
Wyświetla tabele ligowe dla różnych sportów (piłka nożna, tenis ATP/WTA, koszykówka NBA, MLS). Obsługuje wybór ligi i sezonu.

**Parametry (query):**

-   `competition` (string, opcjonalny) – kod ligi/rozgrywek (np. 'PL', 'CL', 'EKS', 'ATP', 'WTA', 'NBA', 'MLS'); domyślnie 'EKS'
-   `season` (string, opcjonalny) – rok sezonu (np. '2025', '2024'); domyślnie '2025'

**Przykład zapytania:**

```bash
curl "http://localhost:5000/tables?competition=PL&season=2025"
```

**Odpowiedź:**  
Renderowany widok HTML `news/tables.html` z tabelą wybranej ligi.

**Kontekst szablonu (zmienia się w zależności od typu sportu):**

**Dla piłki nożnej:**

-   `is_football` = True
-   `standings` – lista drużyn z pozycjami
-   `competition_name` – nazwa rozgrywek (zlokalizowana)
-   `competition_emblem` – URL logo ligi
-   `season_info` – informacje o sezonie
-   `available_seasons` – dostępne sezony
-   `updated_at` – czas aktualizacji
-   `error` – komunikat błędu (jeśli wystąpił)

**Dla tenisa (ATP/WTA):**

-   `is_tennis` = True
-   `tennis_rankings` – słownik z kluczami 'atp' i/lub 'wta'
-   `competition_name` – 'Ranking ATP' lub 'Ranking WTA'

**Dla NBA:**

-   `is_nba` = True
-   `nba_conferences` – słownik konferencji z drużynami
-   `competition_name` – 'NBA'

**Dla MLS:**

-   `is_mls` = True
-   `mls_conferences` – słownik konferencji z drużynami
-   `competition_name` – 'MLS - Major League Soccer'

**Powiązane User Stories:** SCRUM-21

---

### 8.4 GET `/history/view`

**Moduł:** News

**Opis:**  
Wyświetla historię kliknięć w artykuły dla zalogowanego użytkownika wraz ze statystykami według źródeł.

**Autentykacja:** Wymagana – sesja użytkownika (dekorator `@login_required`)

**Parametry (query):**

-   `limit` (int, opcjonalny) – maksymalna liczba wpisów do wyświetlenia; domyślnie 200

**Przykład zapytania:**

```bash
curl "http://localhost:5000/history/view?limit=50" -H "Cookie: session=..."
```

**Odpowiedź:**  
Renderowany widok HTML `news/history.html`

**Kontekst szablonu:**

-   `history` – lista obiektów historii (id, url, title, clicked_at, source)
-   `stats` – statystyki kliknięć według źródeł
-   `total_clicks` – łączna liczba kliknięć

**Kody odpowiedzi:**

-   `200` – OK
-   `302` – redirect do logowania (użytkownik niezalogowany)

**Powiązana User Story:** SCRUM-44

---

## 9. Moduł News - Endpointy API (JSON)

### 9.1 GET `/history/api`

**Moduł:** News

**Opis:**  
Zwraca historię kliknięć w artykuły dla zalogowanego użytkownika w formacie JSON.

**Autentykacja:** Wymagana – sesja użytkownika (dekorator `@login_required`)

**Parametry (query):**

-   `limit` (int, opcjonalny) – maksymalna liczba wpisów; domyślnie 50

**Przykład zapytania:**

```bash
curl "http://localhost:5000/history/api?limit=10" -H "Cookie: session=..."
```

**Przykład odpowiedzi:**

```json
{
    "status": "ok",
    "total": 10,
    "history": [
        {
            "id": 123,
            "url": "https://kryminalki.pl/artykul/123",
            "title": "Wypadek na A4",
            "clicked_at": "2026-01-19T10:30:00",
            "source": "kryminalki"
        }
    ]
}
```

**Kody odpowiedzi:**

-   `200` – OK
-   `401` – użytkownik nie zalogowany

**Powiązana User Story:** SCRUM-44

---

### 9.2 POST `/history/log`

**Moduł:** News

**Opis:**  
Loguje kliknięcie w link wiadomości do bazy danych. Endpoint wywoływany automatycznie przez JavaScript (`news-history.js`) przy każdym kliknięciu w artykuł.

**Autentykacja:** Wymagana – sesja użytkownika

**Body (JSON):**

```json
{
    "url": "https://kryminalki.pl/artykul/123",
    "title": "Wypadek na A4",
    "source": "kryminalki"
}
```

**Parametry Body:**

-   `url` (string, wymagany) – URL artykułu
-   `title` (string, opcjonalny) – tytuł artykułu
-   `source` (string, opcjonalny) – źródło wiadomości (np. 'kryminalki', 'przegladsportowy', 'minut')

**Przykład zapytania:**

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"url": "https://kryminalki.pl/artykul/123", "title": "Wypadek na A4", "source": "kryminalki"}' \
  -b "session=xxx" \
  "http://localhost:5000/history/log"
```

**Przykład odpowiedzi:**

```json
{
    "status": "ok"
}
```

**Kody odpowiedzi:**

-   `200` – OK, kliknięcie zalogowane
-   `400` – brak wymaganego pola `url`
-   `401` – użytkownik nie zalogowany
-   `500` – błąd serwera

**Powiązana User Story:** SCRUM-44

---

### 9.3 POST `/history/clear`

**Moduł:** News

**Opis:**  
Usuwa całą historię kliknięć dla zalogowanego użytkownika.

**Autentykacja:** Wymagana – sesja użytkownika (dekorator `@login_required`)

**Parametry:** brak

**Przykład zapytania:**

```bash
curl -X POST -b "session=xxx" "http://localhost:5000/history/clear"
```

**Przykład odpowiedzi:**

```json
{
    "status": "ok"
}
```

**Kody odpowiedzi:**

-   `200` – OK, historia wyczyszczona
-   `401` – użytkownik nie zalogowany
-   `500` – błąd serwera

**Powiązana User Story:** SCRUM-44

---

### 9.4 POST `/history/delete/<int:entry_id>`

**Moduł:** News

**Opis:**  
Usuwa pojedynczy wpis z historii kliknięć. Użytkownik może usunąć tylko własne wpisy.

**Autentykacja:** Wymagana – sesja użytkownika (dekorator `@login_required`)

**Parametry (path):**

-   `entry_id` (int, wymagany) – ID wpisu do usunięcia

**Przykład zapytania:**

```bash
curl -X POST -b "session=xxx" "http://localhost:5000/history/delete/123"
```

**Przykład odpowiedzi (sukces):**

```json
{
    "status": "ok"
}
```

**Przykład odpowiedzi (błąd):**

```json
{
    "status": "error",
    "message": "not found or forbidden"
}
```

**Kody odpowiedzi:**

-   `200` – OK, wpis usunięty
-   `401` – użytkownik nie zalogowany
-   `404` – wpis nie znaleziony lub nie należy do użytkownika

**Powiązana User Story:** SCRUM-44

---

### 9.5 GET `/image_proxy`

**Moduł:** News

**Opis:**  
Proxy dla obrazków ze stron policji (krakow.policja.gov.pl, malopolska.policja.gov.pl). Omija blokadę CORS/Referer, która uniemożliwia bezpośrednie wyświetlanie obrazków na naszej stronie.

**Parametry (query):**

-   `url` (string, wymagany) – pełny URL obrazka do pobrania

**Przykład zapytania:**

```bash
curl "http://localhost:5000/image_proxy?url=https://krakow.policja.gov.pl/dokumenty/zalaczniki/1/1-123456.jpg"
```

**Odpowiedź:**  
Binarny content obrazka z odpowiednim Content-Type (np. `image/jpeg`)

**Kody odpowiedzi:**

-   `200` – OK, obrazek zwrócony
-   `400` – brak parametru `url`
-   `403` – domena nie jest na liście dozwolonych
-   `404` – obrazek nie znaleziony
-   `500` – błąd pobierania obrazka

**Bezpieczeństwo:**  
Endpoint akceptuje tylko URL-e z dozwolonych domen:

-   `krakow.policja.gov.pl`
-   `malopolska.policja.gov.pl`

**Powiązane User Stories:** SCRUM-10, SCRUM-12

---

## 10. Moduł News - Uwierzytelnianie

**Typ autentykacji:** Sesja (session-based authentication)

**Endpointy wymagające uwierzytelnienia:**

| Endpoint               | Metoda | Wymagane | Opis                     |
| ---------------------- | ------ | -------- | ------------------------ |
| `/history/view`        | GET    | Tak      | Widok historii kliknięć  |
| `/history/api`         | GET    | Tak      | Historia kliknięć (JSON) |
| `/history/log`         | POST   | Tak      | Logowanie kliknięcia     |
| `/history/clear`       | POST   | Tak      | Czyszczenie historii     |
| `/history/delete/<id>` | POST   | Tak      | Usunięcie wpisu historii |

**Endpointy publiczne (brak wymaganej autentykacji):**

| Endpoint       | Metoda | Opis                                              |
| -------------- | ------ | ------------------------------------------------- |
| `/news`        | GET    | Lista wiadomości (dostosowana do stanu logowania) |
| `/news_sport`  | GET    | Wiadomości sportowe                               |
| `/tables`      | GET    | Tabele ligowe                                     |
| `/image_proxy` | GET    | Proxy obrazków                                    |

**Obsługa sesji:**

-   Sesja przechowywana w ciasteczku `session`
-   Identyfikator użytkownika w `session['user_id']`
-   Dla endpointów wymagających autentykacji: kod `401` jeśli brak `session['user_id']`
-   Dla widoków HTML z `@login_required`: redirect do strony logowania

---

## 11. Uwagi końcowe

-   `api_reference.md` jest **jedynym miejscem**, gdzie opisuje się szczegóły requestów i response’ów.
-   Dokumentacja modułów (`doc/architecture/<module>.md`) zawiera wyłącznie:
    -   kontekst,
    -   rolę endpointów,
    -   powiązanie z User Stories.
-   Zmiana w API **wymaga aktualizacji tego pliku**.

---
