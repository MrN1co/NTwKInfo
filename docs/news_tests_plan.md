# Plan testów modułu wiadomości (news)

Poniższa tabela zawiera plan testów dla modułu `news` podzielony na sekcje: Unit, Integration, E2E.

| ID | Typ | Co testujemy | Scenariusz / plik testowy | Status |
|---|---:|---|---|---|
| UT-01 | Unit | Scraper Kryminalki | Parsowanie HTML mockup, ekstrakcja tytułów/linków/obrazków/dat/tagów; obsługa błędów HTTP/timeout; limit parametr — [tests/unit/news/test_kryminalki_scraper.py](tests/unit/news/test_kryminalki_scraper.py) | Wykonany (9 testów) |
| UT-02 | Unit | Scraper Policja | Parsowanie artykułów z policja.pl (Kraków/Małopolska); ekstrakcja dat/obrazków/linków; obsługa pustych stron; walidacja tagów — [tests/unit/news/test_policja_scraper.py](tests/unit/news/test_policja_scraper.py) | Wykonany (16 testów) |
| UT-03 | Unit | Scraper Ekstraklasa | Parsowanie tabel 90minut.pl; ekstrakcja pozycji/drużyn/punktów/emblematów; walidacja struktury danych; obsługa błędów — [tests/unit/news/test_ekstraklasa_scraper.py](tests/unit/news/test_ekstraklasa_scraper.py) | Wykonany (17 testów) |
| UT-04 | Unit | Model SavedTag | CRUD operacje na tagach użytkownika; get_user_tags(), add_tag(), remove_tag(), clear_tags(); cascade delete — [tests/unit/news/test_saved_tags.py](tests/unit/news/test_saved_tags.py) | Wykonany (7 testów) |
| UT-05 | Unit | API SavedTag | GET/POST/DELETE tagów; autoryzacja (401 dla niezalogowanych); walidacja JSON; obsługa błędnych danych — [tests/unit/news/test_saved_tags.py](tests/unit/news/test_saved_tags.py) | Wykonany (7 testów) |
| UT-06 | Unit | Test aggregator | Import wszystkich scraperów przez [tests/unit/news/test_news.py](tests/unit/news/test_news.py) — weryfikacja dostępności klas testowych | Wykonany (wszystkie testy scraperów x2) | 
| IT-01 | Integration | Widok główny `/news` (HTML) | `GET /news` → status 200, content-type HTML, renderuje listę wiadomości; obsługa filtrów `?tags=...` — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-02 | Integration | Widok `/news_sport` (HTML) | `GET /news_sport` → status 200, HTML; fallback do scrapera gdy JSON pusty — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-03 | Integration | Widok `/tables` z konkurencjami (HTML) | `GET /tables?competition=EKS/ATP/WTA/NBA` → status 200, HTML; parametr `season` — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-04 | Integration | Historia klików — widok `/history/view` (HTML) | `@login_required`: niezalogowany → redirect 302; zalogowany → status 200, HTML z tabelą historii — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-05 | Integration | Historia klików — API `/history/api` (JSON) | `@login_required`: zwraca JSON {status, total, history: [{id, url, title, clicked_at, source}]} — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-06 | Integration | Logowanie kliknięcia — `/history/log` (POST, JSON) | `POST` z {url, title, source} → tworzy wpis `NewsLinkHistory` w bazie; walidacja URL — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-07 | Integration | Czyszczenie historii — `/history/clear` (POST) | `@login_required`: usuwa całą historię użytkownika z bazy — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-08 | Integration | Usuwanie wpisu — `/history/delete/<id>` (POST) | `@login_required`: usuwa konkretny wpis; sprawdzenie właściciela (nie można usunąć wpisu innego użytkownika) — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-09 | Integration | Proxy obrazków — `/image_proxy` (GET) | Walidacja parametru `url`; blokada untrusted domen (403); proxy zaufanych domen (requests.get mockowany) — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| IT-10 | Integration | Mockowanie kolektorów | Przy integracyjnych endpointach mockować `get_przegladsportowy_news()` i inne scrapery — [tests/integration/test_news_integration.py](tests/integration/test_news_integration.py) | Wykonany |
| E2E-01 | E2E | User Story: przeglądanie wiadomości | Niezalogowany użytkownik otwiera `/news`, widzi listę wiadomości z tagami — [tests/e2e/test_news_browse.py](tests/e2e/test_news_browse.py) | Wykonany |
| E2E-02 | E2E | User Story: filtrowanie wiadomości | Użytkownik wybiera tagi (sport, kryminalne) → lista się filtruje dynamicznie — [tests/e2e/test_news_filters.py](tests/e2e/test_news_filters.py) | Wykonany |
| E2E-03 | E2E | User Story: historia klików | Zalogowany użytkownik: klika linki → pojawiają się w `/history/view`; może je usunąć — [tests/e2e/test_news_history.py](tests/e2e/test_news_history.py) | Wykonany |
| E2E-04 | E2E | User Story: przeglądanie tabel sportowych | Użytkownik zmienia konkurencję (EKS/ATP/NBA) w `/tables` → tabela się aktualizuje — [tests/e2e/test_tables_competition.py](tests/e2e/test_tables_competition.py) | Wykonany |

---

