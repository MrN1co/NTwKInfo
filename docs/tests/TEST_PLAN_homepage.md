# Plan testów dla 'Strona główna' (Homepage) ✅

## Przegląd
Plan obejmuje testy jednostkowe, integracyjne i E2E modułu strony głównej zgodnie z polityką testowania projektu.

---

## Testy jednostkowe (2–3) ✅
| ID testu | Cel | Opis | Akceptacja |
|---|---|---|---|
| U1 | helpers.select_featured_article | Zwraca pierwszy artykuł lub None gdy lista jest pusta | Zwrócony prawidłowy element / None na pustą listę
| U2 | helpers.summarize | Skraca długie streszczenia i dodaje wielokropek | Długość wyniku <= maksymalna i kończy się "..."
| U3 | helpers.format_published_date | Parsuje datę ISO/`YYYY-MM-DD` i zwraca "DD Mon YYYY" | Znane formaty sparsowane, nieprawidłowe zwracają pusty ciąg

---
## Testy integracyjne (endpointy HTML) ✅
| ID testu | Endpoint | Opis | Akceptacja |
|---|---:|---|---|
| I1 | GET / | Renderuje stronę główną ze zmockowanymi wiadomościami i kursami | 200 OK + tytuły wiadomości i kursy w HTML
| I2 | GET / | Renderuje fallback dla pustej listy wiadomości | 200 OK + "Brak wiadomości" widoczne
| I3 | GET /news, /pogoda, /ekonomia | Trasowanie przekierowuje / wywołuje prawidłowy widok | Oczekiwane przekierowanie lub odpowiedź

Uwagi: zależności zewnętrzne są mockowane za pomocą monkeypatch, aby uniknąć HTTP/uszkodzonych API.

---
## Testy E2E (Playwright, 1 na Story użytkownika) ✅
Dla każdego User Story wymienionego przez właściciela produktu istnieje jeden test E2E.

| ID historii | Podsumowanie historii | Opis testu E2E |
|---|---|---|
| S1 | Admin: tworzenie/aktualizacja/usuwanie użytkowników | Rejestracja użytkownika przez interfejs, weryfikacja istnienia użytkownika przez test admin API; aktualizacja przez API zapisanych tagów; czyszczenie BD
| S2 | Personalizacja dla zalogowanych | Login, wywołanie `/auth/api/user/tags` do zapisania tagów i weryfikacja ich trwałości
| S3 | Rejestracja + Login | Rejestracja (modal), następnie login i osiągnięcie pulpitu
| S4 | Ujednolicony interfejs | Sprawdzenie obecności nagłówka/stopki i nazw klas CSS
| S5 | Informacje o dacie na stronie głównej | Upewnienie się, że kalendarz wyświetla datę/dzień oraz fakty dostarczane przez serwer (mock kanału świąt)
| S6 | Fakty z kalendarza | Przechwycenie pobierania świąt i weryfikacja wyświetlanego tekstu faktu
| S7 | Responsywność | Weryfikacja, czy kluczowe elementy renderują się na urządzeniach mobilnych i stacjonarnych
| S8 | Dostęp anonimowy do informacji | Jako użytkownik anonimowy otwórz stronę główną i sprawdź ogólne informacje i CTA do logowania

Uwagi implementacyjne:
- Testy Playwright uruchamiają się na krótkotrwałym serwerze testowym (fixture `e2e_server`) uruchamianym podczas wykonywania testu.
- Testy e2e używają małego blueprintu tylko do testów (`/test/api/users/...`) do sprawdzania istnienia i czyszczenia.

---
## Artefakty testów i lokalizacje
- Testy jednostkowe: `tests/unit/main/test_helpers.py`
- Testy integracyjne: `modules/main/tests/test_main_integration.py`
- Testy E2E: `tests/e2e/test_homepage_user_stories.py` (+ `tests/e2e/conftest.py`)
- Plan testów (ten plik): `docs/TEST_PLAN_homepage.md`

---
## Szczegółowy plan testów (tabela)

Poniższa tabela zawiera plan testów dla modułu `homepage` podzielony na sekcje: Unit, Integration, E2E.

| ID | Typ | Co testujemy | Scenariusz / plik testowy | Status |
|---|---:|---|---|---|
| UT-01 | Unit | helpers.select_featured_article | Zwracanie pierwszego artykułu; obsługa pustej listy → None; walidacja typu zwrotnego — [tests/unit/main/test_helpers.py](tests/unit/main/test_helpers.py) | Do wykonania |
| UT-02 | Unit | helpers.summarize | Skracanie tekstów > max_length; dodawanie "..."; obsługa None i pustych stringów; ustawienia domyślne — [tests/unit/main/test_helpers.py](tests/unit/main/test_helpers.py) | Do wykonania |
| UT-03 | Unit | helpers.format_published_date | Parsowanie formatu ISO (`YYYY-MM-DD`); konwersja do `DD Mon YYYY`; obsługa błędnych formatów; locale (polska) — [tests/unit/main/test_helpers.py](tests/unit/main/test_helpers.py) | Do wykonania |
| IT-01 | Integration | Widok główny GET / (HTML) | `GET /` → status 200, content-type HTML, renderuje wiadomości i kursy walut; obsługa zmockowanych danych — [tests/integration/test_main_integration.py](tests/integration/test_main_integration.py) | Do wykonania |
| IT-02 | Integration | Fallback dla pustej listy wiadomości | `GET /` z pustą listą newsów → status 200, HTML zawiera "Brak wiadomości"; kursy nadal widoczne — [tests/integration/test_main_integration.py](tests/integration/test_main_integration.py) | Do wykonania |
| IT-03 | Integration | Routing i przekierowania | `GET /news`, `GET /pogoda`, `GET /ekonomia` → właściwe redirecty lub widoki; walidacja status code (302/200) — [tests/integration/test_main_integration.py](tests/integration/test_main_integration.py) | Do wykonania |
| E2E-01 | E2E | User Story S1: rejestracja i zarządzanie użytkownikami | Zalogowany admin rejestruje użytkownika; weryfikuje istnienie; updateuje tagi; czyści BD — [tests/e2e/test_homepage_user_stories.py](tests/e2e/test_homepage_user_stories.py) | Do wykonania |
| E2E-02 | E2E | User Story S2: personalizacja dla zalogowanych | Login → zapis tagów do API `/auth/api/user/tags` → weryfikacja trwałości danych — [tests/e2e/test_homepage_user_stories.py](tests/e2e/test_homepage_user_stories.py) | Do wykonania |
| E2E-03 | E2E | User Story S3: rejestracja i logowanie | Rejestracja nowego konta (modal); login; walidacja dostępu do pulpitu — [tests/e2e/test_homepage_user_stories.py](tests/e2e/test_homepage_user_stories.py) | Do wykonania |
| E2E-04 | E2E | User Story S4: ujednolicony interfejs | Sprawdzenie nagłówka, stopki i klasy CSS; responsywność layout — [tests/e2e/test_homepage_user_stories.py](tests/e2e/test_homepage_user_stories.py) | Do wykonania |
| E2E-05 | E2E | User Story S5: informacje o dacie na stronie | Kalendarz wyświetla datę/dzień; fakty z serwera (mock holidays) — [tests/e2e/test_homepage_user_stories.py](tests/e2e/test_homepage_user_stories.py) | Do wykonania |
| E2E-06 | E2E | User Story S6: fakty z kalendarza | Przechwycenie HTTP requestu holidays; weryfikacja wyświetlanego tekstu faktu — [tests/e2e/test_homepage_user_stories.py](tests/e2e/test_homepage_user_stories.py) | Do wykonania |
| E2E-07 | E2E | User Story S7: responsywność (mobile/desktop) | Viewport mobile (375x667) i desktop (1920x1080); elementy renderują się prawidłowo — [tests/e2e/test_homepage_user_stories.py](tests/e2e/test_homepage_user_stories.py) | Do wykonania |
| E2E-08 | E2E | User Story S8: dostęp anonimowy | Niezalogowany użytkownik; widzi informacje i CTA do logowania; brak błędów 401/403 — [tests/e2e/test_homepage_user_stories.py](tests/e2e/test_homepage_user_stories.py) | Do wykonania |

---
## Jak uruchomić
- Testy jednostkowe i integracyjne: `pytest tests/unit tests/integration` (upewnij się, że pytest i pytest-flask są zainstalowane)
- E2E (wymaga Playwright): `pytest tests/e2e --headed` i upewnij się, że Playwright i przeglądarki są zainstalowane. Więcej informacji znajdziesz w README dotyczącym instalacji Playwright.