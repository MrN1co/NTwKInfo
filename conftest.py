import pytest
import threading
from werkzeug.serving import make_server
from modules.database import db, init_db
import modules.weather_app as weather_app
from config import TestingConfig


# =========================
# FIXTURE APLIKACJI (WSPÓLNA)
# =========================
@pytest.fixture(scope="function")
def app():
    """
    Tworzy aplikację Flask w trybie TESTING
    z testową bazą danych.
    scope="function" oznacza, że fixture będzie tworzona
    osobno dla każdego testu (zalecane przy bazie danych).
    """
    from app import create_app
    app = create_app(TestingConfig)

    with app.app_context():
        db.drop_all()
        init_db(app)
        yield app
        db.session.remove()
        db.drop_all()


# =========================
# FIXTURE CLIENTA (UNIT / INTEGRATION)
# =========================
@pytest.fixture()
def client(app):
    """
    Flask test client – do testów unit/integration.
    test_client() tworzy testowego klienta, który działa bez uruchamiania serwera HTTP.
    """
    return app.test_client()


# =========================
# FIXTURE SERWERA (E2E / Playwright)
# =========================
@pytest.fixture(scope="function")
def e2e_server(app):
    """
    Uruchamia prawdziwy serwer HTTP dla testów E2E (Playwright).
    Zwraca URL serwera, np. http://127.0.0.1:52341
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
    '''
    Czyści cache pogody przed i po każdym teście.
    '''
    weather_app._OW_CACHE.clear()
    yield
    weather_app._OW_CACHE.clear()

# =========================