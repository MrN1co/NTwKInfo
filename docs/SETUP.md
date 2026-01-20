# Konfiguracja projektu i środowiska (`setup.md`)

## 1. Wymagania systemowe

- Python: **3.9+**
- Node.js (dla Playwright): **14.0+** (do testów E2E)
- System operacyjny: **Linux/macOS/Windows**

---

## 2. Instalacja lokalna

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

---

## 3. Plik `.env`

Plik `.env` zawiera **sekrety i konfigurację środowiskową** i **nie może być commitowany**.

### 3.1 Wymagane zmienne środowiskowe

| Zmienna | Przykład | Opis | Wymagana |
|---|---|---|---|
| FLASK_ENV | development | Tryb uruchomienia | TAK |
| SECRET_KEY | ******** | Klucz sesji Flask | TAK |
| DATABASE_URL | sqlite:///app.db | URL bazy danych | NIE (domyślnie SQLite) |
| DEBUG | True | Tryb debugowania | NIE |
| FLASK_APP | app.py | Główny plik aplikacji | NIE |

---

## 4. `.env.example`

Projekt zawiera plik `.env.example` jako wzorzec konfiguracji.

**Sprawdzono:**
- plik nie zawiera sekretów (zawiera domyślne wartości)
- wszystkie wymagane zmienne są opisane
- przy klonowaniu repozytorium skopiuj `.env.example` do `.env` i uzupełnij sekretami lokalnie

---

## 5. Konfiguracja środowisk (dev / test / prod)

**Development:**
- `FLASK_ENV=development`
- `DEBUG=True`
- `DATABASE_URL=sqlite:///app.db` (lokalna SQLite)
- Scheduler uruchomiony

**Testing:**
- `FLASK_ENV=testing`
- `DEBUG=False`
- `DATABASE_URL=sqlite:///test.db` (testowa baza)
- Scheduler wyłączony (brak periodycznych aktualizacji)

**Production (AWS):**
- `FLASK_ENV=production`
- `DEBUG=False`
- `DATABASE_URL=postgresql://...` (PostgreSQL)
- HTTPS wymuszony
- Scheduler uruchomiony
- Monitoring/logging do CloudWatch

---

## 6. Typowe problemy

**Brak zmiennych `.env`:**
- Rozwiązanie: skopiuj `.env.example` do `.env` i uzupełnij wymagane zmienne

**Zajęty port 5001:**
- Rozwiązanie: zmień port w pliku `app.py` lub zabij proces na tym porcie
- Linux/macOS: `lsof -i :5001` i `kill -9 <PID>`

**Brak kluczy API:**
- Niektóre endpointy wymagają kluczy do zewnętrznych API (pogoda, ekonomia, wiadomości)
- Entwicking: można testować bez nich (zwracane są placeholder’y)
- Production: pobierz klucze ze stron dostawców API i dodaj do `.env`

**Problemy z bazą danych:**
- Upewnij się, że `DATABASE_URL` jest poprawny
- Uruchom `python app.py` – baza zostanie stworzenia automatycznie
- Jeśli błędy: usuń `app.db` i uruchom ponownie

