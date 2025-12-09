"""
Testy jednostkowe dla funkcjonalności zapisywania tagów użytkownika
"""

import pytest
import json
from modules.database import db, User, SavedTag


class TestSavedTagModel:
    """Testy dla modelu SavedTag"""
    
    def test_create_saved_tag(self, app):
        """Test tworzenia zapisanego tagu"""
        with app.app_context():
            # Create test user
            user = User.create('testuser', 'test@example.com', 'password123')
            
            # Add tag
            SavedTag.add_tag(user.id, 'sport')
            
            # Verify tag was saved
            tags = SavedTag.get_user_tags(user.id)
            assert 'sport' in tags
            
            # Cleanup
            user.delete()
    
    def test_get_user_tags(self, app):
        """Test pobierania tagów użytkownika"""
        with app.app_context():
            user = User.create('testuser2', 'test2@example.com', 'password123')
            
            # Add multiple tags
            SavedTag.add_tag(user.id, 'sport')
            SavedTag.add_tag(user.id, 'kryminalne')
            SavedTag.add_tag(user.id, 'Kraków')
            
            # Get tags
            tags = SavedTag.get_user_tags(user.id)
            
            assert len(tags) == 3
            assert 'sport' in tags
            assert 'kryminalne' in tags
            assert 'Kraków' in tags
            
            # Cleanup
            user.delete()
    
    def test_save_tags_replaces_existing(self, app):
        """Test że save_tags zastępuje istniejące tagi"""
        with app.app_context():
            user = User.create('testuser3', 'test3@example.com', 'password123')
            
            # Add initial tags
            SavedTag.save_tags(user.id, ['sport', 'kryminalne'])
            tags = SavedTag.get_user_tags(user.id)
            assert len(tags) == 2
            
            # Replace with new tags
            SavedTag.save_tags(user.id, ['Kraków', 'Małopolska'])
            tags = SavedTag.get_user_tags(user.id)
            
            assert len(tags) == 2
            assert 'Kraków' in tags
            assert 'Małopolska' in tags
            assert 'sport' not in tags
            assert 'kryminalne' not in tags
            
            # Cleanup
            user.delete()
    
    def test_add_tag_no_duplicates(self, app):
        """Test że add_tag nie tworzy duplikatów"""
        with app.app_context():
            user = User.create('testuser4', 'test4@example.com', 'password123')
            
            # Add same tag twice
            SavedTag.add_tag(user.id, 'sport')
            SavedTag.add_tag(user.id, 'sport')
            
            tags = SavedTag.get_user_tags(user.id)
            assert len(tags) == 1
            assert tags[0] == 'sport'
            
            # Cleanup
            user.delete()
    
    def test_remove_tag(self, app):
        """Test usuwania pojedynczego tagu"""
        with app.app_context():
            user = User.create('testuser5', 'test5@example.com', 'password123')
            
            # Add tags
            SavedTag.add_tag(user.id, 'sport')
            SavedTag.add_tag(user.id, 'kryminalne')
            
            # Remove one tag
            SavedTag.remove_tag(user.id, 'sport')
            
            tags = SavedTag.get_user_tags(user.id)
            assert len(tags) == 1
            assert 'kryminalne' in tags
            assert 'sport' not in tags
            
            # Cleanup
            user.delete()
    
    def test_clear_tags(self, app):
        """Test czyszczenia wszystkich tagów"""
        with app.app_context():
            user = User.create('testuser6', 'test6@example.com', 'password123')
            
            # Add tags
            SavedTag.save_tags(user.id, ['sport', 'kryminalne', 'Kraków'])
            
            # Clear all tags
            SavedTag.clear_tags(user.id)
            
            tags = SavedTag.get_user_tags(user.id)
            assert len(tags) == 0
            
            # Cleanup
            user.delete()
    
    def test_cascade_delete(self, app):
        """Test że tagi są usuwane gdy użytkownik jest usuwany"""
        with app.app_context():
            user = User.create('testuser7', 'test7@example.com', 'password123')
            user_id = user.id
            
            # Add tags
            SavedTag.add_tag(user_id, 'sport')
            SavedTag.add_tag(user_id, 'kryminalne')
            
            # Delete user
            user.delete()
            
            # Verify tags are gone
            tags = SavedTag.get_user_tags(user_id)
            assert len(tags) == 0


class TestSavedTagsAPI:
    """Testy dla API endpointów tagów"""
    
    def test_get_tags_unauthorized(self, client):
        """Test że niezalogowany użytkownik nie może pobrać tagów"""
        response = client.get('/auth/api/user/tags')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_tags_authorized(self, client, app):
        """Test pobierania tagów dla zalogowanego użytkownika"""
        with app.app_context():
            # Create user and tags
            user = User.create('testuser8', 'test8@example.com', 'password123')
            SavedTag.save_tags(user.id, ['sport', 'kryminalne'])
            
            # Login
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Get tags
            response = client.get('/auth/api/user/tags')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['tags']) == 2
            assert 'sport' in data['tags']
            assert 'kryminalne' in data['tags']
            
            # Cleanup
            user.delete()
    
    def test_save_tags_unauthorized(self, client):
        """Test że niezalogowany użytkownik nie może zapisać tagów"""
        response = client.post('/auth/api/user/tags', 
                              json={'tags': ['sport', 'kryminalne']})
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_save_tags_authorized(self, client, app):
        """Test zapisywania tagów dla zalogowanego użytkownika"""
        with app.app_context():
            user = User.create('testuser9', 'test9@example.com', 'password123')
            
            # Login
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Save tags
            response = client.post('/auth/api/user/tags',
                                  json={'tags': ['sport', 'kryminalne', 'Kraków']})
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['tags']) == 3
            
            # Verify in database
            tags = SavedTag.get_user_tags(user.id)
            assert len(tags) == 3
            assert 'sport' in tags
            
            # Cleanup
            user.delete()
    
    def test_save_tags_invalid_data(self, client, app):
        """Test zapisywania tagów z nieprawidłowymi danymi"""
        with app.app_context():
            user = User.create('testuser10', 'test10@example.com', 'password123')
            
            # Login
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Try to save tags without 'tags' field
            response = client.post('/auth/api/user/tags', json={})
            assert response.status_code == 400
            
            # Try to save non-list tags
            response = client.post('/auth/api/user/tags', json={'tags': 'not-a-list'})
            assert response.status_code == 400
            
            # Cleanup
            user.delete()
    
    def test_clear_tags_unauthorized(self, client):
        """Test że niezalogowany użytkownik nie może wyczyścić tagów"""
        response = client.delete('/auth/api/user/tags')
        assert response.status_code == 401
    
    def test_clear_tags_authorized(self, client, app):
        """Test czyszczenia tagów dla zalogowanego użytkownika"""
        with app.app_context():
            user = User.create('testuser11', 'test11@example.com', 'password123')
            SavedTag.save_tags(user.id, ['sport', 'kryminalne'])
            
            # Login
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
            
            # Clear tags
            response = client.delete('/auth/api/user/tags')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # Verify in database
            tags = SavedTag.get_user_tags(user.id)
            assert len(tags) == 0
            
            # Cleanup
            user.delete()


@pytest.fixture
def app():
    from app import create_app
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
