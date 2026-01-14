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
-   **Base URL (produkcyjnie):** **TU UZUPEŁNIĆ**
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

| Metoda | Endpoint                                   | Typ  | Krótki opis              | Moduł    |
| -----: | ------------------------------------------ | ---- | ------------------------ | -------- |
|    GET | `/`                                        | HTML | Strona główna aplikacji  | Home     |
|    GET | `/weather`                                 | HTML | Widok bieżącej pogody    | Weather  |
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

### 4.2 GET `/weather`

**Moduł:** Weather

**Opis:**  
**TU UZUPEŁNIĆ** – co dokładnie pokazuje widok pogodowy.

**Parametry (query):**

-   `city` (string, opcjonalny) – **TU UZUPEŁNIĆ**

**Odpowiedź:**  
Renderowany widok HTML.

**Powiązana User Story:** **TU UZUPEŁNIĆ**

---

### 4.3 GET `/ekonomia`

**Moduł:** Ekonomia

**Opis:**  
Widok modułu ekonomii z aktualnymi kursami walut (EUR, USD, CHF), ceną złota, wykresami zmian kursów oraz kalkulatorem walutowym. Dla zalogowanych użytkowników wyświetla także ich ulubione waluty (maksymalnie 3).

**Parametry:** brak

**Odpowiedź:**  
Renderowany widok HTML z tabelą walut, wykresami (w formacie base64), kursami i kalkulatorem.

**Powiązane User Stories:** SCRUM-32, SCRUM-34, SCRUM-37, SCRUM-38, SCRUM-39, SCRUM-40, SCRUM-41, SCRUM-42

---

### 4.2 GET `/weather`

**Moduł:** Weather

**Opis:**  
**TU UZUPEŁNIĆ** – co dokładnie pokazuje widok pogodowy.

**Parametry (query):**

-   `city` (string, opcjonalny) – **TU UZUPEŁNIĆ**

**Odpowiedź:**  
Renderowany widok HTML.

**Powiązana User Story:** **TU UZUPEŁNIĆ**

---

## 5. Endpointy API (JSON)

> **Instrukcja:**  
> Każdy endpoint API musi być opisany w sposób umożliwiający:
>
> -   przygotowanie testów integracyjnych,
> -   przygotowanie klienta API,
> -   weryfikację zgodności implementacji z dokumentacją.

---

### 5.1 GET `/api/weather/forecast`

**Moduł:** Weather

**Opis:**  
**TU UZUPEŁNIĆ** – jakie dane zwraca endpoint i w jakim celu.

**Parametry (query):**

-   `city` (string, wymagany) – nazwa miasta

**Przykład zapytania:**

```bash
curl "http://localhost:5000/api/weather/forecast?city=Krakow"
```

**Przykład odpowiedzi:**

```json
{
    "status": "success",
    "data": {
        "city": "Krakow",
        "temperature": 12.5,
        "condition": "Cloudy"
    }
}
```

**Kody odpowiedzi:**

-   `200` – OK
-   `400` – niepoprawne dane wejściowe
-   `500` – błąd serwera

**Powiązana User Story:** **TU UZUPEŁNIĆ**

---

### 5.2 POST `/api/weather/favorites`

**Moduł:** Weather

**Opis:**  
**TU UZUPEŁNIĆ** – zapis ulubionego miasta użytkownika.

**Body (JSON):**

```json
{
    "city": "Krakow"
}
```

**Odpowiedź:**

```json
{
    "status": "success",
    "message": "City added to favorites"
}
```

**Kody odpowiedzi:**  
**TU UZUPEŁNIĆ**

**Powiązana User Story:** **TU UZUPEŁNIĆ**

---

### 5.3 GET `/ekonomia/api/exchange-rates`

**Moduł:** Ekonomia

**Opis:**  
Zwraca listę dostępnych walut z aktualnymi kursami (z publicznego API NBP). Endpoint dostępny dla wszystkich użytkowników (zalogowanych i anonimowych).

**Parametry:** brak

**Przykład zapytania:**

```bash
curl "http://localhost:5000/ekonomia/api/exchange-rates"
```

**Przykład odpowiedzi:**

```json
[
    { "code": "EUR", "rate": 4.24 },
    { "code": "USD", "rate": 3.64 },
    { "code": "CHF", "rate": 4.57 },
    { "code": "GBP", "rate": 4.87 },
    { "code": "JPY", "rate": 0.025 }
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

---

## 8. Uwagi końcowe

-   `api_reference.md` jest **jedynym miejscem**, gdzie opisuje się szczegóły requestów i response’ów.
-   Dokumentacja modułów (`doc/architecture/<module>.md`) zawiera wyłącznie:
    -   kontekst,
    -   rolę endpointów,
    -   powiązanie z User Stories.
-   Zmiana w API **wymaga aktualizacji tego pliku**.

---
