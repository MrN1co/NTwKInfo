"""
Testy integracyjne dla modułu ekonomia
Testują współpracę endpointów Flask z logiką biznesową i bazą danych
"""

import pytest
import json
from unittest.mock import patch
from modules.database import db, User, FavoriteCurrency


class TestEkonomiaIntegration:
    """Testy integracyjne dla endpointów modułu ekonomia"""

    def test_ekonomia_main_page_returns_html(self, client):
        """Test głównej strony modułu ekonomia - zwraca HTML"""
        with patch('modules.ekonomia.ekonomia.Manager') as mock_manager:
            # Mock Manager response
            mock_manager.return_value.run_update.return_value = None
            
            response = client.get('/ekonomia')
            
            assert response.status_code == 200
            assert response.content_type.startswith('text/html')
            # Sprawdź, czy strona zawiera podstawowe elementy modułu ekonomia
            assert b'ekonomia' in response.data.lower() or b'waluty' in response.data.lower()

    def test_ekonomia_api_exchange_rates_returns_json(self, client):
        """Test API kursów walut - zwraca JSON z listą walut"""
        with patch('modules.ekonomia.ekonomia.Manager') as mock_manager:
            # Mock Manager response with sample currency data
            mock_manager.return_value.currencies.get_current_rates.return_value = {
                'eur': 4.32,
                'usd': 4.05,
                'gbp': 5.15,
                'chf': 4.58
            }
            
            response = client.get('/ekonomia/api/exchange-rates')
            
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) > 0
            
            # Sprawdź strukturę odpowiedzi
            for currency in data:
                assert 'code' in currency
                assert 'rate' in currency
                assert isinstance(currency['code'], str)
                assert isinstance(currency['rate'], (int, float))
            
            # Sprawdź obecność głównych walut
            codes = [c['code'] for c in data]
            assert 'EUR' in codes
            assert 'USD' in codes

    def test_ekonomia_chart_endpoint_returns_image(self, client):
        """Test endpointu wykresu waluty - zwraca obraz PNG"""
        with patch('modules.ekonomia.ekonomia.generate_currency_plot') as mock_plot:
            # Mock chart generation
            mock_plot.return_value = 'base64_encoded_image_data'
            
            response = client.get('/ekonomia/chart/EUR')
            
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            
            data = response.get_json()
            assert 'success' in data
            assert 'message' in data
            assert 'chart' in data
            
            if data['success']:
                assert isinstance(data['chart'], str)  # Base64 encoded image
                assert data['chart'] == 'base64_encoded_image_data'

    def test_favorite_currencies_get_requires_authentication(self, client):
        """Test GET ulubionych walut - wymaga autentyfikacji"""
        response = client.get('/ekonomia/api/favorite-currencies', 
                            headers={'Accept': 'application/json'})
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'not_authenticated'

    def test_favorite_currencies_full_workflow_with_auth(self, client, app):
        """Test pełnego workflow ulubionych walut z autentyfikacją"""
        with app.app_context():
            # Stwórz testowego użytkownika
            test_user = User(
                username='test_user',
                email='test@example.com',
                password_hash='hashed_password'
            )
            db.session.add(test_user)
            db.session.commit()
            user_id = test_user.id
            
            # Symuluj sesję zalogowanego użytkownika
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
                sess['username'] = 'test_user'
            
            # 1. GET - początkowo brak ulubionych walut
            response = client.get('/ekonomia/api/favorite-currencies',
                                headers={'Accept': 'application/json'})
            assert response.status_code == 200
            data = response.get_json()
            assert data['favorite_currencies'] == []
            
            # 2. POST - dodaj ulubioną walutę EUR
            response = client.post('/ekonomia/api/favorite-currencies', 
                                 json={'currency_code': 'EUR'},
                                 headers={'Content-Type': 'application/json'})
            assert response.status_code == 201
            data = response.get_json()
            assert 'favorite_currencies' in data
            assert len(data['favorite_currencies']) == 1
            assert data['favorite_currencies'][0]['currency_code'] == 'EUR'
            
            # 3. GET - sprawdź, czy EUR jest na liście
            response = client.get('/ekonomia/api/favorite-currencies',
                                headers={'Accept': 'application/json'})
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['favorite_currencies']) == 1
            assert data['favorite_currencies'][0]['currency_code'] == 'EUR'
            
            # 4. POST - dodaj drugą ulubioną walutę USD
            response = client.post('/ekonomia/api/favorite-currencies', 
                                 json={'currency_code': 'USD'},
                                 headers={'Content-Type': 'application/json'})
            assert response.status_code == 201
            data = response.get_json()
            assert len(data['favorite_currencies']) == 2
            
            # 5. DELETE - usuń EUR
            response = client.delete('/ekonomia/api/favorite-currencies/EUR',
                                   headers={'Accept': 'application/json'})
            assert response.status_code == 200
            data = response.get_json()
            assert 'favorite_currencies' in data
            assert len(data['favorite_currencies']) == 1
            assert data['favorite_currencies'][0]['currency_code'] == 'USD'
