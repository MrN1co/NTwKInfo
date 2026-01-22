import os
import time
import tempfile
import threading
from multiprocessing import Process
from flask import Flask, jsonify, request
import pytest

# Create a simple e2e_server fixture that runs the app on a test port.
# It registers a small test-only blueprint to check user existence and delete user.

from modules.database import db, User, init_db
from modules.auth import auth_bp
from modules.main import main_bp

TEST_PORT = 5001

def run_app(app):
    """
    Uruchamia aplikację Flask na wskazanym porcie.
    
    Funkcja:
    - Uruchamia serwer Flask na porcie TEST_PORT (5001)
    - use_reloader=False wyłącza auto-restart przy zmianach (nie potrzebny w testach)
    - Wykonywana w osobnym wątku za pośrednictwem fixture-y e2e_server
    
    Args:
        app (Flask): Instancja aplikacji Flask do uruchomienia
    """
    app.run(port=TEST_PORT, use_reloader=False)


@pytest.fixture(scope='session')
def e2e_server():
    """
    Fixture-a sesyjna uruchamiająca serwer Flask dla testów E2E.
    
    Funkcja:
    - Tworzy aplikację Flask z szablonami i plikami statycznymi
    - Konfiguruje testową bazę SQLite w pliku tymczasowym
    - Inicjalizuje bazę danych i rejestruje blueprinty (main, auth)
    - Rejestruje specjalny blueprint testowy (test_bp) z endpointami administracyjnymi:
        * GET /test/api/users/<username>/exists - sprawdzenie czy użytkownik istnieje
        * POST /test/api/users/<username>/delete - usunięcie użytkownika
    - Udostępnia kontekst aplikacji z context_processor do podania current_user 
      do szablonów (konieczne do renderowania szablonów)
    - Uruchamia serwer w wątku daemon'a w tle
    - Czeka 1 sekundę na start serwera
    - Zwraca URL serwera w postaci http://127.0.0.1:5001
    
    Scope='session' oznacza, że serwer uruchamia się raz na całą sesję testów 
    (szybsze, ale dane mogą się przechodzić między testami - ale baza jest 
    czyszczena w każdym teście).
    
    Yields:
        str: URL serwera (http://127.0.0.1:5001)
    """
    # Ensure templates and static are found when server runs in a different working dir
    templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'static'))

    app = Flask(__name__, template_folder=templates_dir, static_folder=static_dir)
    app.config['TESTING'] = True
    # Use a temporary file DB so background server and test process share state
    tmpfile = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    sqlite_uri = f"sqlite:///{tmpfile.name}"
    app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'e2e-secret'

    # Init DB and blueprints
    db.init_app(app)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Testing-only admin blueprint
    # Blueprint zawierający endpointy pomocnicze do testów E2E
    from flask import Blueprint
    test_bp = Blueprint('test', __name__)

    @test_bp.route('/test/api/users/<username>/exists')
    def user_exists(username):
        """
        Endpoint testowy sprawdzający czy użytkownik o danej nazwie istnieje.
        
        Args:
            username (str): Nazwa użytkownika do sprawdzenia
            
        Returns:
            JSON: {'exists': bool} - informacja czy użytkownik istnieje
        """
        u = User.get_by_username(username)
        return jsonify({'exists': bool(u)})

    @test_bp.route('/test/api/users/<username>/delete', methods=['POST'])
    def delete_user(username):
        """
        Endpoint testowy usuwający użytkownika z bazy danych.
        
        Funkcja:
        - Szuka użytkownika po nazwie
        - Jeśli znaleziony - usuwa go i zwraca {'deleted': True}
        - Jeśli nie znaleziony - zwraca {'deleted': False} ze statusem 404
        
        Args:
            username (str): Nazwa użytkownika do usunięcia
            
        Returns:
            JSON: {'deleted': bool} - informacja czy usunięcie powiodło się
            HTTP Status: 200 jeśli powiedzie się, 404 jeśli użytkownik nie istnieje
        """
        u = User.get_by_username(username)
        if not u:
            return jsonify({'deleted': False}), 404
        u.delete()
        return jsonify({'deleted': True})

    app.register_blueprint(test_bp)

    # Start server in background thread
    with app.app_context():
        init_db(app)

        # Provide `current_user` to templates to mimic real app context processors
        @app.context_processor
        def inject_current_user():
            """
            Context processor dostarczający current_user do wszystkich szablonów.
            
            Funkcja:
            - Pobiera user_id z sesji
            - Wyszukuje użytkownika po ID
            - Udostępnia zmienną 'current_user' w kontekście szablonów
            - Naśladuje działanie rzeczywistej aplikacji (ważne dla testów E2E)
            
            Returns:
                dict: Słownik z kluczem 'current_user' zawierającym obiektu użytkownika 
                      lub None jeśli użytkownik nie jest zalogowany
            """
            from flask import session
            user_id = session.get('user_id')
            user = User.get_by_id(user_id) if user_id else None
            return {'current_user': user}

    thread = threading.Thread(target=run_app, args=(app,), daemon=True)
    thread.start()

    # Give server time to start
    time.sleep(1.0)

    yield f'http://127.0.0.1:{TEST_PORT}'

    # Teardown
    try:
        tmpfile.close()
        os.unlink(tmpfile.name)
    except Exception:
        pass
