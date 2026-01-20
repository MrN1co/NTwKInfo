# Plan testów modułu ekonomicznego

Poniższa tabela zawiera plan testów dla modułu `ekonomia` podzielony na sekcje: Unit, Integration, E2E.

| ID | Typ | Co testujemy | Scenariusz / plik testowy | Status |
|---|---:|---|---|---|
| UT-01 | Unit | Inicjalizacja i atrybuty `Manager` | Walidacja pól, domyślne obiekty i klienta — [tests/unit/ekonomia/test_manager.py](tests/unit/ekonomia/test_manager.py) | Nie wykonany |
| UT-02 | Unit | Aktualizacja danych (`Manager.update_all`) | Mockowanie źródeł → zwraca aktualne kursy i cenę złota — [tests/unit/ekonomia/test_manager.py](tests/unit/ekonomia/test_manager.py) | Nie wykonany |
| UT-03 | Unit | Lista walut (`Manager.list_currencies`) | Filtracja, unikalność kodów, obsługa tabel — [tests/unit/ekonomia/test_manager.py](tests/unit/ekonomia/test_manager.py) | Nie wykonany |
| UT-04 | Unit | Generowanie wykresów (`Manager.create_plot_image`) | Różne DataFrame (puste/None/kolumny niestandardowe) → base64 PNG — [tests/unit/ekonomia/test_manager.py](tests/unit/ekonomia/test_manager.py) | Nie wykonany |
| UT-05 | Unit | Klient API (`APIClient.get_json`) | Obsługa poprawnej odpowiedzi, timeout, błędy HTTP — [tests/unit/ekonomia/test_api_client.py](tests/unit/ekonomia/test_api_client.py) | Nie wykonany |
| UT-06 | Unit | Pobieranie kursów i listy (`CurrencyRates`) | Parsowanie odpowiedzi, filtrowanie tabel, puste odpowiedzi — [tests/unit/ekonomia/test_currency_rates.py](tests/unit/ekonomia/test_currency_rates.py) | Nie wykonany |
| UT-07 | Unit | Fetch NBP (dane historyczne) | Parsowanie JSON, usuwanie duplikatów, filtrowanie starych dat — [tests/unit/ekonomia/test_fetch_nbp.py](tests/unit/ekonomia/test_fetch_nbp.py) | Nie wykonany |
| IT-01 | Integration | Widok główny `/ekonomia` (HTML) | `GET /ekonomia` → status 200, content-type HTML, zawiera elementy modułu — [tests/integration/test_ekonomia_integration.py](tests/integration/test_ekonomia_integration.py) | Nie wykonany |
| IT-02 | Integration | API kursów `/ekonomia/api/exchange-rates` | `GET` → status 200, `application/json`, struktura listy {code, rate} i obecność EUR/USD — [tests/integration/test_ekonomia_integration.py](tests/integration/test_ekonomia_integration.py) | Nie wykonany |
| IT-03 | Integration | Endpoint wykresu `/ekonomia/chart/<code>` | `GET /ekonomia/chart/EUR` → status 200, JSON z kluczem `chart` zawierającym base64 PNG — [tests/integration/test_ekonomia_integration.py](tests/integration/test_ekonomia_integration.py) | Nie wykonany |
| IT-04 | Integration | Ulubione waluty API (autoryzacja) | `GET/POST/DELETE /ekonomia/api/favorite-currencies` → statusy 401/200/201/409, struktura odpowiedzi; testy z sesją użytkownika i DB testową — [tests/integration/test_ekonomia_integration.py](tests/integration/test_ekonomia_integration.py) | Nie wykonany |
| IT-05 | Integration | Mockowanie zewnętrznych API | Przy integracyjnych endpointach mockować `Manager`/APIClient aby izolować logikę i sprawdzić format odpowiedzi — (pliki integracyjne powyżej) | Nie wykonany |
| E2E-01 | E2E | User Story: widok dziennych kursów | Niezalogowany użytkownik otwiera `/ekonomia`, widzi USD/EUR/GBP w kaflach i w tabeli — [tests/e2e/test_daily_exchange_rates.py](tests/e2e/test_daily_exchange_rates.py) | Nie wykonany |
| E2E-02 | E2E | User Story: wykresy kursów walut | Użytkownik widzi wykres (base64 PNG/canvas), zmienia walutę w selektorze → wykres się aktualizuje — [tests/e2e/test_currency_charts.py](tests/e2e/test_currency_charts.py) | Nie wykonany |
| E2E-03 | E2E | User Story: zarządzanie ulubionymi walutami | Zalogowany użytkownik: dodaje/usuwa ulubione → interfejs i API odzwierciedlają zmiany (end-to-end) — [tests/e2e/test_logged_user_favorite_currencies.py](tests/e2e/test_logged_user_favorite_currencies.py) | Nie wykonany |

---

## Uwagi

- Można rozszerzyć tabelę o kolumny: właściciel testu, priorytet, data wykonania, link do wyników w `pytest-html`.
- Statusy są ustawione na `Nie wykonany`. Po uruchomieniu testów zaktualizuj kolumnę `Status` zgodnie z rezultatami.
- Pliki testowe wskazane w kolumnie `Scenariusz / plik testowy` służą jako punkt odniesienia — w razie potrzeby doprecyzuj przypadki testowe lub dodaj ID testów szczegółowych.
