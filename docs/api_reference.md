# Referencja API (`api_reference.md`)

> **Cel dokumentu**  
> Ten plik stanowi **jedno źródło prawdy o wszystkich endpointach aplikacji**  
> (zarówno HTML, jak i API JSON).  
> Jest podstawą do **testów integracyjnych** oraz formalnym **kontraktem API** dla całego projektu.

> **Instrukcja:**  
> - Opisz **wszystkie endpointy aplikacji** (HTML i JSON).  
> - Każdy endpoint musi mieć **kompletny i jednoznaczny opis**.  
> - **Nie opisuj tutaj architektury modułów** – do tego służą pliki w `doc/architecture/<module>.md`.  
> - Dokument ten powinien umożliwić napisanie **testów integracyjnych bez zaglądania do kodu**.

---

## 1. Informacje ogólne

**TU UZUPEŁNIĆ (jeśli dotyczy):**
- **Base URL (lokalnie):** `http://localhost:5000`
- **Base URL (produkcyjnie):** **TU UZUPEŁNIĆ**
- **Format danych (API):** JSON
- **Kodowanie:** UTF-8
- **Framework:** Flask

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

| Metoda | Endpoint                                   | Typ  | Krótki opis              | Moduł    |
| -----: | ------------------------------------------ | ---- | ------------------------ | -------- |
|    GET | `/`                                        | HTML | Strona główna aplikacji  | Home     |
|    GET | `/weather/pogoda`                    | HTML | Widok bieżącej pogody    | Weather  |
|    GET | `/api/weather/forecast`                    | JSON | Dane pogodowe            | Weather  |
|   POST | `/api/weather/favorites`                   | JSON | Zapis ulubionych miast   | Weather  |
|    GET | `/ekonomia`                                | HTML | Kursy walut i ceny złota | Ekonomia |
|    GET | `/ekonomia/chart/<code>`                   | JSON | Wykres kursu waluty      | Ekonomia |
|    GET | `/ekonomia/api/exchange-rates`             | JSON | Lista dostępnych walut   | Ekonomia |
|    GET | `/ekonomia/api/favorite-currencies`        | JSON | Moje ulubione waluty     | Ekonomia |
|   POST | `/ekonomia/api/favorite-currencies`        | JSON | Dodaj ulubioną walutę    | Ekonomia |
| DELETE | `/ekonomia/api/favorite-currencies/<code>` | JSON | Usuń ulubioną walutę     | Ekonomia |
|    GET | `/news`                                    | HTML | Lista wiadomości         | News     |
|    GET | `/api/news/latest`                         | JSON | Najnowsze wiadomości     | News     |
| Metoda | Endpoint | Typ | Krótki opis | Moduł |
|------:|----------|-----|-------------|-------|
| GET | `/` | HTML | Strona główna aplikacji | Home |
| GET | `/weather/pogoda` | HTML | Widok bieżącej pogody | Weather |
| GET | `/weather/api/forecast` | JSON | 7-dniowa prognoza pogody | Weather |
| GET | `/weather/api/favorites` | JSON | Lista ulubionych miast | Weather |
| POST | `/weather/api/favorites` | JSON | Dodanie ulubionego miasta | Weather |
| DELETE | `/weather/api/favorites` | JSON | Usunięcie ulubionego miasta | Weather |
| GET | `/weather/api/geocode` | JSON | Wyszukiwanie miast | Weather |
| GET | `/weather/api/hourly` | JSON | Godzinowa prognoza pogody | Weather |
| GET | `/weather/plot.png` | PNG | Wykres prognozy pogody | Weather |
| GET | `/economy` | HTML | Widok danych ekonomicznych | Economy |
| GET | `/api/economy/rates` | JSON | Kursy walut | Economy |
| GET | `/news` | HTML | Lista wiadomości | News |
| GET | `/api/news/latest` | JSON | Najnowsze wiadomości | News |

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
- brak

**Odpowiedź:**  
- Dla zalogowanych użytkowników: HTML `weather-login.html` (zawiera sekcję ulubionych miast)
- Dla użytkowników anonimowych: HTML `weather.html` (widok podstawowy)

**Powiązana User Story:** Wyświetlenie prognozy pogody, zarządzanie ulubionymi miastami dla zalogowanych użytkowników

---

## 5. Endpointy API (JSON)

> **Instrukcja:**  
> Każdy endpoint API musi być opisany w sposób umożliwiający:
> - przygotowanie testów integracyjnych,
> - przygotowanie klienta API,
> - weryfikację zgodności implementacji z dokumentacją.

---

### 5.1 GET `/weather/api/forecast`

**Moduł:** Weather  

**Opis:**  
Zwraca 7-dniową prognozę pogody w postaci kafelków dziennych. Dane pobierane są z OpenWeather API. Domyślną lokalizacją jest Kraków (50.0647°N, 19.9450°E). Endpoint zawiera wbudowaną cache na 1 minutę.

**Parametry (query):**
- `lat` (float, opcjonalny) – szerokość geograficzna; domyślnie 50.0647 (Kraków)
- `lon` (float, opcjonalny) – długość geograficzna; domyślnie 19.9450 (Kraków)
- `label` (string, opcjonalny) – nazwa miasta do wyświetlenia; jeśli nie podana, przy domyślnych współrzędnych używa się "Kraków"

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
- `200` – OK, prognoza zwrócona  
- `400` – błędne parametry lat/lon  
- `502` – błąd OpenWeather API  
- `500` – błąd backendu  

**Powiązana User Story:** Wyświetlenie 7-dniowej prognozy pogody

---

### 5.2 GET `/weather/api/favorites`

**Moduł:** Weather  

**Opis:**  
Zwraca listę ulubionych miast dla zalogowanego użytkownika. Endpoint wymaga autentykacji sesji.

**Autentykacja:** Wymagana – sesja użytkownika

**Parametry (query):**
- brak

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
      "lon": 19.9450
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
- `200` – OK, lista ulubionych zwrócona  
- `401` – użytkownik nie zalogowany  

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
  "lat": 54.3520,
  "lon": 18.6466
}
```

**Parametry Body:**
- `city` (string, wymagany) – nazwa miasta
- `lat` (float, opcjonalny) – szerokość geograficzna
- `lon` (float, opcjonalny) – długość geograficzna

**Przykład odpowiedzi (sukces):**
```json
{
  "id": 3,
  "city": "Gdańsk",
  "lat": 54.3520,
  "lon": 18.6466
}
```

**Kody odpowiedzi:**
- `201` – Created, miasto dodane
- `400` – brak pola `city` w body  
- `401` – użytkownik nie zalogowany  
- `409` – miasto już istnieje w ulubionych tego użytkownika

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
- `id` (int, opcjonalny) – ID ulubionego miasta
- `city` (string, opcjonalny) – nazwa miasta

(Wymagany co najmniej jeden z parametrów)

**Przykład odpowiedzi (sukces):**
```json
{
  "ok": true
}
```

**Kody odpowiedzi:**
- `200` – OK, miasto usunięte
- `400` – brak pola `id` i `city`  
- `401` – użytkownik nie zalogowany  
- `404` – miasto nie znalezione

**Powiązana User Story:** Usunięcie miasta z ulubionych

---

### 5.5 GET `/weather/api/geocode`

**Moduł:** Weather  

**Opis:**  
Wyszukuje miasta po nazwie. Zwraca listę lokalizacji ze współrzędnymi geograficznymi. Dane pobierane z OpenWeather Geocoding API. Maksymalnie 5 wyników.

**Parametry (query):**
- `q` (string, wymagany) – nazwa miasta do wyszukania

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

### 5.4 GET `/ekonomia/chart/<currency_code>`

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

### 5.5 GET `/ekonomia/api/favorite-currencies`

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

### 5.6 POST `/ekonomia/api/favorite-currencies`

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

### 5.7 DELETE `/ekonomia/api/favorite-currencies/<currency_code>`

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

**Ekonomia**
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
### 6.1 Moduł Weather

**Typ autentykacji:** Sesja (session-based authentication)

**Endpointy wymagające uwierzytelnienia:**

| Endpoint | Metoda | Wymagane | Opis |
|----------|--------|----------|-------|
| `/weather/api/favorites` | GET | Tak | Pobieranie ulubionych miast użytkownika |
| `/weather/api/favorites` | POST | Tak | Dodawanie ulubionego miasta |
| `/weather/api/favorites` | DELETE | Tak | Usuwanie ulubionego miasta |

**Endpointy publiczne (brak wymaganej autentykacji):**

| Endpoint | Metoda | Opis |
|----------|--------|-------|
| `/weather/pogoda` | GET | Widok pogodowy (dostosowany do stanu autentykacji) |
| `/weather/api/forecast` | GET | Prognoza pogody |
| `/weather/api/geocode` | GET | Wyszukiwanie miast |
| `/weather/api/hourly` | GET | Prognoza godzinowa |
| `/weather/plot.png` | GET | Wykres pogody |

**Obsługa sesji:**
- Sesja jest przechowywana w ciasteczku `session`
- Identyfikator użytkownika dostępny w obiekcie `session['user_id']`
- Dla endpointów wymagających autentykacji zwracany jest kod `401` jeśli `session['user_id']` nie istnieje
- Uwierzytelnianie jest obsługiwane przez dekorator `@api_login_required`

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
> - musi mieć **co najmniej jeden test integracyjny**,
> - powinien być jednoznacznie testowalny na podstawie tej dokumentacji.

**TU UZUPEŁNIĆ (opcjonalnie):**
- mapowanie endpoint → test integracyjny,
- informacje o mockowaniu zewnętrznych API.

---

## 8. Uwagi końcowe

- `api_reference.md` jest **jedynym miejscem**, gdzie opisuje się szczegóły requestów i response’ów.
- Dokumentacja modułów (`doc/architecture/<module>.md`) zawiera wyłącznie:
  - kontekst,
  - rolę endpointów,
  - powiązanie z User Stories.
- Zmiana w API **wymaga aktualizacji tego pliku**.

---
