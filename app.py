from flask import Flask
import os

from dotenv import load_dotenv

from modules.auth import auth_bp
from modules.main import main_bp
from modules.database import db, init_db
from modules.news.routes import tables_bp
from modules.weather_app import weather_bp
from modules.ekonomia.ekonomia import ekonomia_bp
from modules.scheduler import init_scheduler
from modules.news.news import init_news_module

from config import DevelopmentConfig, TestingConfig, ProductionConfig

# =========================
# ZMIANA 1:
# Ładujemy .env TYLKO dla uruchomienia ręcznego
# (pytest NIE powinien polegać na .env)
# =========================
load_dotenv()


def create_app(config_object=None):
    """
    Factory aplikacji Flask.
    Umożliwia wstrzyknięcie konfiguracji (np. testowej).
    """

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    # =========================
    # ZMIANA 2:
    # Jawny wybór konfiguracji
    # =========================
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(DevelopmentConfig)

    # =========================
    # Inicjalizacja bazy
    # =========================
    db.init_app(app)
    init_db(app)

    # =========================
    # Context processor – bez zmian
    # =========================
    @app.context_processor
    def inject_user():
        from flask import session
        from modules.database import User

        current_user = None
        if "user_id" in session:
            current_user = User.query.get(session["user_id"])
        return dict(current_user=current_user)

    # =========================
    # Rejestracja blueprintów
    # =========================
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tables_bp, url_prefix="/news")
    app.register_blueprint(weather_bp, url_prefix="/weather")
    app.register_blueprint(ekonomia_bp)

    # =========================
    # ZMIANA 3:
    # Tworzenie tabel w kontekście aplikacji
    # =========================
    with app.app_context():
        db.create_all()

    # =========================
    # ZMIANA 4 (BARDZO WAŻNA):
    # Scheduler i kolektory NIE uruchamiają się w testach
    # =========================
    if not app.config.get("TESTING"):
        print("Inicjalizacja schedulerów i modułów...")
        init_scheduler(app)
        # Przy poprawkach to zaginęło, ale dodaję z powrotem, bo się wyczerpuje limit API
        # i wyskakują błędy na stronie, brzydko wygląda.
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            init_news_module()
    return app


# =========================
# ZMIANA 5:
# Ten blok służy TYLKO do uruchomienia ręcznego
# pytest NIGDY tu nie wchodzi
# =========================
if __name__ == "__main__":
    app = create_app(DevelopmentConfig)

    port = int(os.environ.get("FLASK_RUN_PORT", 5001))
    host = os.environ.get("FLASK_RUN_HOST", "0.0.0.0")

    app.run(
        debug=app.config["DEBUG"],
        host=host,
        port=port
    )
