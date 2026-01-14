# Dokumentacja testów - Moduł News

## Struktura testów

Testy modułu news są zorganizowane w trzy kategorie zgodnie z piramidą testów:

```
tests/
├── unit/
│   └── news/
│       ├── test_ekstraklasa_scraper.py  # 17 testów - scraper tabel Ekstraklasy
│       ├── test_kryminalki_scraper.py   # 9 testów - scraper wiadomości kryminalnych
│       ├── test_policja_scraper.py      # 16 testów - scraper wiadomości policyjnych  
│       ├── test_saved_tags.py           # 14 testów - model i API zapisanych tagów
│       ├── test_news.py                 # 42 testy - duplikat testów scraperów
│       └── mockup_*.html                # Pliki mockup HTML do testowania
├── integration/
│   └── test_news_integration.py         # Testy endpointów i widoków
└── e2e/
    ├── test_news.py                     # Test przeglądania wiadomości
    ├── test_news_headlines.py           # Test nagłówków
    ├── test_news_link.py                # Test linków
    ├── test_news_category.py            # Test filtrowania
    ├── test_news_history.py             # Test historii klików
    └── test_news_tabels.py              # Test tabel sportowych
```

## Statystyki testów

### Testy jednostkowe (Unit)
- **Łącznie**: 98 testów
- **Status**: ✅ Wszystkie przechodzą (98 passed)
- **Czas wykonania**: ~9 sekund
- **Ostrzeżenia**: 11 (deprecation warning dla datetime.utcnow)

### Kategorie testów jednostkowych

#### 1. Scraper Ekstraklasy (17 testów)
- Podstawowe pobieranie tabel (tabela, struktura, typy danych)
- Walidacja danych (pozycje, punkty, brak duplikatów)
- Obsługa błędów (HTTP errors, timeouty)
- Ekstrakcja dodatkowych danych (emblematy, gole)
- Różne ligi (1. liga, 2. liga)

#### 2. Scraper kryminalek (9 testów)
- Pobieranie wiadomości z mockup HTML
- Struktura artykułów i ekstrakcja danych
- Parsowanie dat i tagów
- Usuwanie duplikatów
- Obsługa błędów i limitów

#### 3. Scraper policji (16 testów)
- Pobieranie z dwóch źródeł (Kraków, Małopolska)
- Walidacja struktury artykułów
- Ekstrakcja dat, linków, obrazów
- Tagi regionalne
- Obsługa błędów i edge cases

#### 4. Zapisane tagi (14 testów)
- Model SavedTag (7 testów)
  - Tworzenie i pobieranie tagów
  - Operacje CRUD
  - Kaskadowe usuwanie
- API SavedTags (7 testów)
  - Autoryzacja endpointów
  - GET, POST, DELETE operacje
  - Walidacja danych

## Uruchamianie testów

### Wszystkie testy jednostkowe
```powershell
python -m pytest tests/unit/news/ -v -o addopts=""
```

### Z raportem HTML
```powershell
python -m pytest tests/unit/news/ -v -o addopts="" --html=report_news.html --self-contained-html
```

### Konkretna kategoria
```powershell
# Tylko scraper ekstraklasy
python -m pytest tests/unit/news/test_ekstraklasa_scraper.py -v -o addopts=""

# Tylko zapisane tagi
python -m pytest tests/unit/news/test_saved_tags.py -v -o addopts=""
```

### Testy integracyjne
```powershell
python -m pytest tests/integration/test_news_integration.py -v -o addopts=""
```

### Testy E2E
```powershell
# Wymagają uruchomionego serwera i przeglądarki
python -m pytest tests/e2e/test_news*.py -v
```

## Pliki mockup

W folderze `tests/unit/news/` znajdują się pliki mockup HTML używane do testowania scraperów:

- `mockup_esa.html` - mockup strony Ekstraklasy
- `mockup_esa_emblematy.html` - mockup strony z emblematami
- `mockup_kryminalki.html` - mockup strony głównej kryminalek
- `mockup_kryminalki_podstrona.html` - mockup podstrony artykułu
- `mockup_policja_krakow_.html` - mockup strony policji Kraków
- `mockup_policja_malopolska.html` - mockup strony policji Małopolska
- `mockup_przeglad_sportowy.html` - mockup Przeglądu Sportowego

## Plan testów

Szczegółowy plan testów znajduje się w pliku [docs/news_tests_plan.md](../../docs/news_tests_plan.md).

## Raport z testów

Najnowszy raport HTML: [report_news.html](../../report_news.html)

## Uwagi

1. **Duplikaty testów**: Plik `test_news.py` zawiera duplikaty testów z innych plików. Rozważ jego usunięcie.
2. **Ostrzeżenia**: Ostrzeżenia dotyczące `datetime.utcnow()` - należy zaktualizować kod do użycia timezone-aware datetime.
3. **Struktura**: Testy zostały przeniesione z `modules/news/tests/` do `tests/unit/news/` dla lepszej organizacji.
4. **Mockowanie**: Wszystkie testy używają mocków dla requests.get() - nie wykonują rzeczywistych zapytań HTTP.
