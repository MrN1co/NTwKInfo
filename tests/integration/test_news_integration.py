"""
Testy integracyjne dla modułu wiadomości (news).
Kluczowe testy sprawdzające:
- Renderowanie endpointów HTML (status 200, content-type)
- Strukturę odpowiedzi JSON API
- Autoryzację (login required)
- Podstawowe operacje na bazie danych
"""

import pytest
from unittest.mock import patch, MagicMock
from modules.database import db, User
from modules.news.link_history_model import NewsLinkHistory


class TestNewsHTMLEndpoints:
    """Kluczowe testy endpointów modułu news"""

    # =====================
    # ENDPOINTY HTML
    # =====================
    
    def test_news_page_renders(self, client):
        """Test: /news renderuje HTML"""
        response = client.get('/news/news')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')

    def test_news_sport_page_renders(self, client):
        """Test: /news_sport renderuje HTML"""
        response = client.get('/news/news_sport')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')

    def test_tables_page_renders(self, client):
        """Test: /tables renderuje HTML"""
        response = client.get('/news/tables')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')

    def test_tables_page_with_different_competition(self, client):
        """Test: /tables z różnymi konkurencjami"""
        for competition in ['EKS', 'ATP', 'WTA', 'NBA']:
            response = client.get(f'/news/tables?competition={competition}')
            assert response.status_code == 200
            assert response.content_type.startswith('text/html')

    def test_history_view_requires_login(self, client):
        """Test: /history/view wymaga autentyfikacji"""
        response = client.get('/news/history/view', follow_redirects=False)
        assert response.status_code == 302  # redirect do logowania

    def test_history_view_renders_for_logged_user(self, client, app):
        """Test: /history/view renderuje HTML dla zalogowanego użytkownika"""
        with app.app_context():
            user = User(username='test', email='test@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        with client.session_transaction() as sess:
            sess['user_id'] = user_id

        response = client.get('/news/history/view')
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')

    # =====================
    # API JSON ENDPOINTY
    # =====================

    def test_history_api_requires_login(self, client):
        """Test: /history/api wymaga autentyfikacji"""
        response = client.get('/news/history/api', follow_redirects=False)
        assert response.status_code == 302

    def test_history_api_returns_valid_json(self, client, app):
        """Test: /history/api zwraca JSON z poprawną strukturą"""
        with app.app_context():
            user = User(username='test', email='test@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        with client.session_transaction() as sess:
            sess['user_id'] = user_id

        response = client.get('/news/history/api')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = response.get_json()
        assert 'status' in data
        assert 'total' in data
        assert 'history' in data
        assert isinstance(data['history'], list)

    def test_history_log_without_auth_fails(self, client):
        """Test: /history/log bez autentyfikacji zwraca 401"""
        response = client.post('/news/history/log', json={'url': 'http://example.com'})
        assert response.status_code == 401
        assert response.get_json()['status'] == 'error'

    def test_history_log_creates_entry(self, client, app):
        """Test: /history/log tworzy wpis w bazie"""
        with app.app_context():
            user = User(username='test', email='test@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

        with client.session_transaction() as sess:
            sess['user_id'] = user_id

        response = client.post(
            '/news/history/log',
            json={'url': 'https://example.com', 'title': 'Test', 'source': 'test'}
        )
        assert response.status_code == 200
        assert response.get_json()['status'] == 'ok'

        with app.app_context():
            entry = NewsLinkHistory.query.filter_by(user_id=user_id).first()
            assert entry is not None
            assert entry.link_url == 'https://example.com'

    def test_history_clear_requires_login(self, client):
        """Test: /history/clear wymaga autentyfikacji"""
        response = client.post('/news/history/clear', follow_redirects=False)
        assert response.status_code == 302

    def test_history_clear_removes_entries(self, client, app):
        """Test: /history/clear usuwa historię użytkownika"""
        with app.app_context():
            user = User(username='test', email='test@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Dodaj historię
            for i in range(3):
                entry = NewsLinkHistory(
                    user_id=user_id,
                    link_url=f'https://example.com/{i}',
                    link_title=f'News {i}',
                    source='test'
                )
                db.session.add(entry)
            db.session.commit()

        with client.session_transaction() as sess:
            sess['user_id'] = user_id

        response = client.post('/news/history/clear')
        assert response.status_code == 200
        assert response.get_json()['status'] == 'ok'

        with app.app_context():
            count = NewsLinkHistory.query.filter_by(user_id=user_id).count()
            assert count == 0

    def test_history_delete_removes_entry(self, client, app):
        """Test: /history/delete/<id> usuwa wpis"""
        with app.app_context():
            user = User(username='test', email='test@example.com', password_hash='hash')
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            entry = NewsLinkHistory(
                user_id=user_id,
                link_url='https://example.com',
                link_title='Test',
                source='test'
            )
            db.session.add(entry)
            db.session.commit()
            entry_id = entry.id

        with client.session_transaction() as sess:
            sess['user_id'] = user_id

        response = client.post(f'/news/history/delete/{entry_id}')
        assert response.status_code == 200
        assert response.get_json()['status'] == 'ok'

        with app.app_context():
            deleted = NewsLinkHistory.query.get(entry_id)
            assert deleted is None

    # =====================
    # IMAGE PROXY
    # =====================

    def test_image_proxy_requires_url(self, client):
        """Test: /image_proxy bez URL zwraca 400"""
        response = client.get('/news/image_proxy')
        assert response.status_code == 400

    def test_image_proxy_blocks_untrusted_domain(self, client):
        """Test: /image_proxy blokuje niezaufane domeny"""
        response = client.get('/news/image_proxy?url=https://malicious.com/image.jpg')
        assert response.status_code == 403

    def test_image_proxy_allows_trusted_domain(self, client):
        """Test: /image_proxy zezwala na zaufane domeny"""
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b'image_data'
            mock_response.headers = {'Content-Type': 'image/jpeg'}
            mock_get.return_value = mock_response
            
            response = client.get(
                '/news/image_proxy?url=https://krakow.policja.gov.pl/dokumenty/image.jpg'
            )
            assert response.status_code == 200
