import pytest
import threading
from werkzeug.serving import make_server
from werkzeug.security import generate_password_hash
from app import create_app
from modules.database import db, init_db, User
import modules.weather_app as weather_app
from config import TestingConfig


# =========================
# FIXTURE APLIKACJI (WSPÓLNA)
# =========================
@pytest.fixture(scope="function")
def app():
    """
    Fixture-a tworząca aplikację Flask w trybie TESTING z testową bazą danych.
    
    Funkcja:
    - Inicjalizuje aplikację Flask z konfiguracją testową (TestingConfig)
    - Czyści i tworzy nową bazę danych dla każdego testu (scope="function")
    - Dodaje testowego użytkownika (testuser/testpass) do bazy
    - Zwraca kontekst aplikacji dla testu
    - Po teście czyści bazę danych
    
    Parametr scope="function" zapewnia izolację testów poprzez osobną bazę 
    danych dla każdego testu.
    
    Yields:
        Flask: Aplikacja Flask skonfigurowana dla testów
    """
    from app import create_app
    app = create_app(TestingConfig)

    with app.app_context():
        db.drop_all()
        init_db(app)
        # Dodaj użytkownika testowego
        test_user = User(username='testuser', email='test@example.com', password_hash=generate_password_hash('testpass'))
        db.session.add(test_user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


# =========================
# FIXTURE CLIENTA (UNIT / INTEGRATION)
# =========================
@pytest.fixture()
def client(app):
    """
    Fixture-a dostarczająca Flask test client do testów unit i integracyjnych.
    
    Funkcja:
    - Tworzy testowego klienta Flask bez uruchamiania rzeczywistego serwera HTTP
    - Umożliwia wykonywanie żądań HTTP (GET, POST, etc.) w testach
    - Jest szybsza niż uruchamianie pełnego serwera (używana w testach unit/integration)
    - Zależy od fixture-y app() dla kontekstu aplikacji
    
    Returns:
        FlaskClient: Test client do wykonywania żądań HTTP
    """
    return app.test_client()


# =========================
# FIXTURE SERWERA (E2E / Playwright)
# =========================
@pytest.fixture(scope="function")
def e2e_server(app):
    """
    Fixture-a uruchamiająca prawdziwy serwer HTTP dla testów E2E z Playwright.
    
    Funkcja:
    - Uruchamia pełny serwer Flask w wątku w tle na losowo wybranym wolnym porcie
    - Udostępnia URL serwera (np. http://127.0.0.1:52341) dla testów przeglądarki
    - Gwarantuje, że serwer jest gotów do obsługi żądań przez wybrany czas
    - Po teście czyści zasoby (wyłącza serwer, czeka na wątek)
    
    Parametr scope="function" zapewnia osobny serwer dla każdego testu E2E.
    
    Yields:
        str: URL serwera w postaci http://host:port
    """

    # 0 = wybierz losowy wolny port
    server = make_server("127.0.0.1", 0, app)

    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()

    host, port = server.server_address
    base_url = f"http://{host}:{port}"

    # ---- tu test dostaje URL ----
    yield base_url

    # ---- teardown (ZAWSZE się wykona) ----
    server.shutdown()
    thread.join()

# =========================
# FIXTURE czyszczenia CACHE pogody
# ========================= 
@pytest.fixture(autouse=True)
def clear_weather_cache():
    """
    Fixture-a automatycznie czyszcząca cache pogody przed i po każdym teście.
    
    Funkcja:
    - Czyszcza globalny cache pogody (_OW_CACHE) PRZED wykonaniem testu
    - Czyszcza globalny cache pogody PO wykonaniu testu
    - Parametr autouse=True powoduje automatyczne uruchamianie dla każdego testu
    - Zapobiega przeciekaniu danych między testami
    
    Jest to krityczne dla testów pogody, aby każdy test miał czysty stan cache.
    """
    weather_app._OW_CACHE.clear()
    yield
    weather_app._OW_CACHE.clear()

# =========================
# FIXTURE czyszczenia sent_emails
# =========================
@pytest.fixture(autouse=True)
def clear_sent_emails():
    """
    Fixture-a automatycznie czyszcząca listę wysłanych e-maili przed każdym testem.
    
    Funkcja:
    - Czyszcza listę sent_emails PRZED wykonaniem testu
    - Czyszcza listę sent_emails PO wykonaniu testu
    - Parametr autouse=True powoduje automatyczne uruchamianie dla każdego testu
    - Zapobiega falszywym pozytywnym wyników gdy e-mail z poprzedniego testu 
      wpłynie na wynik bieżącego testu
    
    Jest to krityczne dla testów powiadomień e-mail, aby każdy test miał 
    czystą listę wysłanych wiadomości.
    """
    weather_app.sent_emails.clear()
    yield
    weather_app.sent_emails.clear()

# =========================