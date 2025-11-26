"""
Testy jednostkowe dla scrapera kryminalek
Wykorzystuje mockup witryny do testowania funkcjonalności scrapowania
"""

import pytest
from unittest.mock import Mock, patch, mock_open
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.news.collectors.kryminalki_scraper import get_kryminalki_news


class TestKryminalekScraper:
    """Klasa testowa dla scrapera kryminalek"""
    
    @pytest.fixture
    def mockup_main_page(self):
        """Fixture zwracający zawartość mockup strony głównej"""
        mockup_path = os.path.join(os.path.dirname(__file__), 'mockup_kryminalki.html')
        with open(mockup_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def mockup_article_page(self):
        """Fixture zwracający zawartość mockup podstrony artykułu"""
        mockup_path = os.path.join(os.path.dirname(__file__), 'mockup_kryminalki_podstrona.html')
        with open(mockup_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_get_kryminalki_news_basic(self, mock_get, mockup_main_page, mockup_article_page):
        """
        Test podstawowego działania scrapera
        Sprawdza czy scraper poprawnie pobiera listę artykułów
        """
        mock_main_response = Mock()
        mock_main_response.status_code = 200
        mock_main_response.content = mockup_main_page.encode('utf-8')
        
        mock_article_response = Mock()
        mock_article_response.status_code = 200
        mock_article_response.content = mockup_article_page.encode('utf-8')
        
        def side_effect(url, **kwargs):
            if 'artykul' in url:
                return mock_article_response
            return mock_main_response
        
        mock_get.side_effect = side_effect
        
        news = get_kryminalki_news(limit=5)
        
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) > 0, "Lista nie powinna być pusta"
        assert len(news) <= 5, "Liczba artykułów nie powinna przekraczać limitu"
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_article_structure(self, mock_get, mockup_main_page, mockup_article_page):
        """
        Test struktury pojedynczego artykułu
        Sprawdza czy każdy artykuł ma wszystkie wymagane pola
        """
        mock_main_response = Mock()
        mock_main_response.status_code = 200
        mock_main_response.content = mockup_main_page.encode('utf-8')
        
        mock_article_response = Mock()
        mock_article_response.status_code = 200
        mock_article_response.content = mockup_article_page.encode('utf-8')
        
        def side_effect(url, **kwargs):
            if 'artykul' in url:
                return mock_article_response
            return mock_main_response
        
        mock_get.side_effect = side_effect
        
        news = get_kryminalki_news(limit=1)
        
        assert len(news) > 0, "Powinna być pobrana co najmniej jedna wiadomość"
        
        article = news[0]
        
        #Wymagane pola
        assert 'title' in article, "Artykuł powinien mieć pole 'title'"
        assert 'link' in article, "Artykuł powinien mieć pole 'link'"
        assert 'image' in article, "Artykuł powinien mieć pole 'image'"
        assert 'date' in article, "Artykuł powinien mieć pole 'date'"
        assert 'timestamp' in article, "Artykuł powinien mieć pole 'timestamp'"
        assert 'tags' in article, "Artykuł powinien mieć pole 'tags'"
        
        # Typy pól
        assert isinstance(article['title'], str), "Tytuł powinien być stringiem"
        assert isinstance(article['link'], str), "Link powinien być stringiem"
        assert isinstance(article['tags'], list), "Tagi powinny być listą"
        
        #assert len(article['title']) > 10, "Tytuł powinien mieć przynajmniej 10 znaków"
        
        assert article['link'].startswith('https://www.kryminalki.pl/artykul/'), \
            "Link powinien zaczynać się od 'https://www.kryminalki.pl/artykul/'"
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_tags_extraction(self, mock_get, mockup_main_page, mockup_article_page):
        """
        Test ekstrakcji tagów z artykułu
        Sprawdza czy tagi są poprawnie wyciągane ze strony artykułu
        """
        mock_main_response = Mock()
        mock_main_response.status_code = 200
        mock_main_response.content = mockup_main_page.encode('utf-8')
        
        mock_article_response = Mock()
        mock_article_response.status_code = 200
        mock_article_response.content = mockup_article_page.encode('utf-8')
        
        def side_effect(url, **kwargs):
            if 'artykul' in url:
                return mock_article_response
            return mock_main_response
        
        mock_get.side_effect = side_effect
        
        news = get_kryminalki_news(limit=1)
        
        assert len(news) > 0
        article = news[0]
        
        # Czy lista tagów zawiera bazowy tag 'kryminalne'
        assert 'kryminalne' in article['tags'], "Każdy artykuł powinien mieć tag 'kryminalne'"
        
        #Czy tagi są stringami
        for tag in article['tags']:
            assert isinstance(tag, str), "Każdy tag powinien być stringiem"
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_date_parsing(self, mock_get, mockup_main_page, mockup_article_page):
        """
        Test parsowania daty z artykułu
        Sprawdza czy data jest poprawnie konwertowana na timestamp
        """
        mock_main_response = Mock()
        mock_main_response.status_code = 200
        mock_main_response.content = mockup_main_page.encode('utf-8')
        
        mock_article_response = Mock()
        mock_article_response.status_code = 200
        mock_article_response.content = mockup_article_page.encode('utf-8')
        
        def side_effect(url, **kwargs):
            if 'artykul' in url:
                return mock_article_response
            return mock_main_response
        
        mock_get.side_effect = side_effect
        
        news = get_kryminalki_news(limit=1)
        
        assert len(news) > 0
        article = news[0]
        
        # Sprawdź czy data jest stringiem lub None
        assert article['date'] is None or isinstance(article['date'], str), \
            "Data powinna być stringiem lub None"
        
        if article['date']:
            if article['timestamp']:
                assert isinstance(article['timestamp'], int), \
                    "Timestamp powinien być liczbą całkowitą"
                assert article['timestamp'] > 0, "Timestamp powinien być dodatni"
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_no_duplicates(self, mock_get, mockup_main_page, mockup_article_page):
        """
        Test sprawdzający czy nie ma duplikatów w wynikach
        """
        mock_main_response = Mock()
        mock_main_response.status_code = 200
        mock_main_response.content = mockup_main_page.encode('utf-8')
        
        mock_article_response = Mock()
        mock_article_response.status_code = 200
        mock_article_response.content = mockup_article_page.encode('utf-8')
        
        def side_effect(url, **kwargs):
            if 'artykul' in url:
                return mock_article_response
            return mock_main_response
        
        mock_get.side_effect = side_effect
        
        news = get_kryminalki_news(limit=10)
        
        # Sprawdzanie duplikatów po linkach
        links = [article['link'] for article in news]
        unique_links = set(links)
        
        assert len(links) == len(unique_links), "Nie powinno być duplikatów artykułów"
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_http_error_handling(self, mock_get):
        """
        Test obsługi błędów HTTP
        Sprawdza czy scraper poprawnie radzi sobie z błędami serwera
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        news = get_kryminalki_news()
        
        # Przy błędzie powinna być zwrócona pusta lista
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) == 0, "Lista powinna być pusta przy błędzie HTTP"
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_timeout_handling(self, mock_get):
        """
        Test obsługi timeout'u
        Sprawdza czy scraper poprawnie radzi sobie z przekroczeniem czasu
        """
        import requests
        mock_get.side_effect = requests.Timeout("Timeout")
        
        news = get_kryminalki_news()
        
        # Przy timeout powinna być zwrócona pusta lista
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) == 0, "Lista powinna być pusta przy timeout"
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_limit_parameter(self, mock_get, mockup_main_page, mockup_article_page):
        """
        Test parametru limit
        Sprawdza czy scraper respektuje zadany limit artykułów
        """
        mock_main_response = Mock()
        mock_main_response.status_code = 200
        mock_main_response.content = mockup_main_page.encode('utf-8')
        
        mock_article_response = Mock()
        mock_article_response.status_code = 200
        mock_article_response.content = mockup_article_page.encode('utf-8')
        
        def side_effect(url, **kwargs):
            if 'artykul' in url:
                return mock_article_response
            return mock_main_response
        
        mock_get.side_effect = side_effect
        
        # Test różnych limitów
        for limit in [1, 3, 5]:
            news = get_kryminalki_news(limit=limit)
            assert len(news) <= limit, f"Liczba artykułów nie powinna przekraczać limitu {limit}"
    
    @patch('modules.news.collectors.kryminalki_scraper.requests.get')
    def test_image_extraction(self, mock_get, mockup_main_page, mockup_article_page):
        """
        Test ekstrakcji obrazków
        Sprawdza czy scraper poprawnie wyciąga URL obrazków
        """
        mock_main_response = Mock()
        mock_main_response.status_code = 200
        mock_main_response.content = mockup_main_page.encode('utf-8')
        
        mock_article_response = Mock()
        mock_article_response.status_code = 200
        mock_article_response.content = mockup_article_page.encode('utf-8')
        
        def side_effect(url, **kwargs):
            if 'artykul' in url:
                return mock_article_response
            return mock_main_response
        
        mock_get.side_effect = side_effect
        
        news = get_kryminalki_news(limit=5)
        
        # obrazki
        for article in news:
            # image może być None lub stringiem
            assert article['image'] is None or isinstance(article['image'], str), \
                "Obrazek powinien być stringiem lub None"
            
            # Jeśli obrazek istnieje, powinien zawierać URL
            if article['image']:
                assert article['image'].startswith('http'), \
                    "URL obrazka powinien zaczynać się od 'http'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
