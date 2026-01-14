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
- `200` – OK, wyniki wyszukiwania zwrócone  
- `400` – brak parametru `q`  
- `502` – błąd OpenWeather API  

**Powiązana User Story:** Wyszukiwanie miast

---

### 5.6 GET `/weather/api/hourly`

**Moduł:** Weather  

**Opis:**  
Zwraca godzinową prognozę pogody dla wykresu (temperatury, opady). Dane zwrócone są w strefie czasowej miasta. Domyślną lokalizacją jest Kraków.

**Parametry (query):**
- `lat` (float, opcjonalny) – szerokość geograficzna; domyślnie 50.0647 (Kraków)
- `lon` (float, opcjonalny) – długość geograficzna; domyślnie 19.9450 (Kraków)
- `day` (int, opcjonalny) – numer dnia (0 = dziś, 1 = jutro, maks. 4); domyślnie 0

**Przykład zapytania:**
```bash
curl "http://localhost:5000/weather/api/hourly?lat=50.0647&lon=19.9450&day=0"
```

**Przykład odpowiedzi:**
```json
{
  "points": [
    {
      "dt": "2025-01-16T08:00:00+01:00",
      "temp": 2.5,
      "precip_mm": 0.0
    },
    {
      "dt": "2025-01-16T09:00:00+01:00",
      "temp": 3.1,
      "precip_mm": 0.0
    }
  ],
  "tz_offset": 3600
}
```

**Kody odpowiedzi:**
- `200` – OK, dane zwrócone  
- `400` – błędne parametry lat/lon  
- `502` – błąd OpenWeather API  
- `500` – błąd backendu  

**Powiązana User Story:** Wyświetlenie wykresu godzinowej prognozy pogody

---

### 5.7 GET `/weather/plot.png`

**Moduł:** Weather  

**Opis:**  
Generuje i zwraca wykres PNG prognozy godzinowej (temperatury i opady) dla wybranego dnia. Domyślną lokalizacją jest Kraków.

**Parametry (query):**
- `lat` (float, opcjonalny) – szerokość geograficzna; domyślnie 50.0647 (Kraków)
- `lon` (float, opcjonalny) – długość geograficzna; domyślnie 19.9450 (Kraków)
- `day` (int, opcjonalny) – numer dnia (0-4); domyślnie 0

**Przykład zapytania:**
```bash
curl "http://localhost:5000/weather/plot.png?lat=50.0647&lon=19.9450&day=0" > chart.png
```

**Odpowiedź:** Plik PNG z wykresem

**Kody odpowiedzi:**
- `200` – OK, obraz zwrócony  
- `400` – błędne parametry  
- `404` – brak danych dla wybranego okresu  
- `500` – błąd generowania wykresu  

**Powiązana User Story:** Wyświetlenie wizualizacji prognozy pogody

---

## 6. Uwierzytelnianie i autoryzacja

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
