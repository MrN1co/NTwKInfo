from pathlib import Path
import os

# Katalog główny projektu (root)
BASE_DIR = Path(__file__).resolve().parent


class BaseConfig:
    """
    Konfiguracja bazowa – wspólna dla wszystkich trybów.
    """
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """
    Konfiguracja developerska:
    - lokalna baza app.db
    - tryb DEBUG
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{BASE_DIR / 'app.db'}"
    )


class TestingConfig(BaseConfig):
    """
    Konfiguracja testowa:
    - osobna baza test.db
    - brak schedulerów
    - TESTING=True
    """
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'test.db'}"


class ProductionConfig(BaseConfig):
    """
    Konfiguracja produkcyjna:
    - baza tylko z DATABASE_URL
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
