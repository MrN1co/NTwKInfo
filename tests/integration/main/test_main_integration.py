import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pytest
from flask import Flask
import modules.main as main_module


@pytest.fixture
def app():
    flask_app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'templates')))
    flask_app.config['TESTING'] = True

    # Register blueprint under test
    flask_app.register_blueprint(main_module.main_bp)
    # Register auth blueprint so templates using auth endpoints render
    from modules.auth import auth_bp
    flask_app.register_blueprint(auth_bp, url_prefix='/auth')

    with flask_app.app_context():
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


def test_index_renders_with_news_and_rates(monkeypatch, client):
    # Prepare fake data
    def fake_news(limit=3):
        return [
            {'title': 'News 1', 'link': 'http://example.com/1', 'image': None, 'summary': 'S1', 'published': '2024-01-01'},
            {'title': 'News 2', 'link': 'http://example.com/2', 'image': None, 'summary': 'S2', 'published': '2024-01-02'},
        ]

    def fake_rates():
        return [{'code': 'USD', 'rate': 4.0}, {'code': 'EUR', 'rate': 4.5}]

    monkeypatch.setattr(main_module, 'get_kryminalki_news', fake_news)
    monkeypatch.setattr(main_module, 'get_homepage_rates', fake_rates)

    rv = client.get('/')
    assert rv.status_code == 200
    data = rv.get_data(as_text=True)
    assert 'News 1' in data
    assert 'USD' in data


def test_index_renders_empty_news(monkeypatch, client):
    monkeypatch.setattr(main_module, 'get_kryminalki_news', lambda limit=3: [])
    monkeypatch.setattr(main_module, 'get_homepage_rates', lambda: [])

    rv = client.get('/')
    assert rv.status_code == 200
    data = rv.get_data(as_text=True)
    assert 'Brak wiadomości' in data


def test_helper_redirects():
    # Simple check of other endpoints
    # create flask app for URL building
    app = Flask(__name__)
    app.register_blueprint(main_module.main_bp)

    with app.test_request_context():
        assert main_module.main_bp.url_prefix is None
        # confirm route endpoints exist
        assert 'main.index' in app.view_functions
        assert 'main.news' in app.view_functions
        assert 'main.weather' in app.view_functions
