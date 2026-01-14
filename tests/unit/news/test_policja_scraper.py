"""
Testy jednostkowe dla scrapera policji (Kraków i Małopolska)
Wykorzystuje mockup witryny do testowania funkcjonalności scrapowania
"""

import pytest
from unittest.mock import Mock, patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.news.collectors.policja_scraper import (
    scrape_policja_news,
    get_policja_krakow_news,
    get_policja_malopolska_news
)


class TestPolicjaScraper:
    """Klasa testowa dla scrapera policji"""
    
    @pytest.fixture
    def mockup_policja_krakow(self):
        """Fixture zwracający zawartość mockup strony policji Kraków"""
        mockup_path = os.path.join(os.path.dirname(__file__), 'mockup_policja_krakow_.html')
        with open(mockup_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @pytest.fixture
    def mockup_policja_malopolska(self):
        """Fixture zwracający zawartość mockup strony policji Małopolska"""
        mockup_path = os.path.join(os.path.dirname(__file__), 'mockup_policja_malopolska.html')
        with open(mockup_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_scrape_policja_krakow_basic(self, mock_get, mockup_policja_krakow):
        """
        Test podstawowego działania scrapera dla Krakowa
        Sprawdza czy scraper poprawnie pobiera listę artykułów
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news(limit=5)
        
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) > 0, "Lista nie powinna być pusta"
        assert len(news) <= 5, "Liczba artykułów nie powinna przekraczać limitu"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_scrape_policja_malopolska_basic(self, mock_get, mockup_policja_malopolska):
        """
        Test podstawowego działania scrapera dla Małopolski
        Sprawdza czy scraper poprawnie pobiera listę artykułów
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_malopolska.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_malopolska_news(limit=5)
        
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) > 0, "Lista nie powinna być pusta"
        assert len(news) <= 5, "Liczba artykułów nie powinna przekraczać limitu"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_article_structure(self, mock_get, mockup_policja_krakow):
        """
        Test struktury pojedynczego artykułu
        Sprawdza czy każdy artykuł ma wszystkie wymagane pola
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news(limit=1)
        
        assert len(news) > 0, "Powinna być pobrana co najmniej jedna wiadomość"
        
        article = news[0]
        
        # Wymagane pola
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
        
        # Niepuste pola
        assert len(article['title']) > 0, "Tytuł nie powinien być pusty"
        assert len(article['link']) > 0, "Link nie powinien być pusty"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_tags_krakow(self, mock_get, mockup_policja_krakow):
        """
        Test tagów dla Krakowa
        Sprawdza czy artykuły mają odpowiednie tagi
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news(limit=1)
        
        assert len(news) > 0
        article = news[0]
        
        # Czy lista tagów zawiera oczekiwane tagi
        assert 'kryminalne' in article['tags'], "Artykuł powinien mieć tag 'kryminalne'"
        assert 'Kraków' in article['tags'], "Artykuł powinien mieć tag 'Kraków'"
        
        # Czy tagi są stringami
        for tag in article['tags']:
            assert isinstance(tag, str), "Każdy tag powinien być stringiem"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_tags_malopolska(self, mock_get, mockup_policja_malopolska):
        """
        Test tagów dla Małopolski
        Sprawdza czy artykuły mają odpowiednie tagi
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_malopolska.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_malopolska_news(limit=1)
        
        assert len(news) > 0
        article = news[0]
        
        # Czy lista tagów zawiera oczekiwane tagi
        assert 'kryminalne' in article['tags'], "Artykuł powinien mieć tag 'kryminalne'"
        assert 'Małopolska' in article['tags'], "Artykuł powinien mieć tag 'Małopolska'"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_date_extraction(self, mock_get, mockup_policja_krakow):
        """
        Test ekstrakcji daty z artykułu
        Sprawdza czy data jest poprawnie wyciągana
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news(limit=1)
        
        assert len(news) > 0
        article = news[0]
        
        # Sprawdź czy data jest stringiem lub None
        assert article['date'] is None or isinstance(article['date'], str), \
            "Data powinna być stringiem lub None"
        
        if article['date']:
            # Sprawdź czy data jest w oczekiwanym formacie (DD.MM.YYYY)
            assert len(article['date']) >= 8, "Data powinna mieć co najmniej 8 znaków"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_image_extraction(self, mock_get, mockup_policja_krakow):
        """
        Test ekstrakcji obrazków
        Sprawdza czy scraper poprawnie wyciąga URL obrazków
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news(limit=5)
        
        # Obrazki
        for article in news:
            # image może być None lub stringiem
            assert article['image'] is None or isinstance(article['image'], str), \
                "Obrazek powinien być stringiem lub None"
            
            # Jeśli obrazek istnieje, powinien zawierać URL
            if article['image']:
                assert article['image'].startswith('http') or article['image'].startswith('/'), \
                    "URL obrazka powinien zaczynać się od 'http' lub '/'"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_link_validation(self, mock_get, mockup_policja_krakow):
        """
        Test walidacji linków
        Sprawdza czy linki są poprawnie formatowane
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news(limit=3)
        
        for article in news:
            # Link powinien zaczynać się od http lub https
            assert article['link'].startswith('http'), \
                f"Link powinien zaczynać się od 'http': {article['link']}"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_no_duplicates(self, mock_get, mockup_policja_krakow):
        """
        Test sprawdzający czy nie ma duplikatów w wynikach
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news(limit=10)
        
        # Sprawdzanie duplikatów po linkach
        links = [article['link'] for article in news]
        unique_links = set(links)
        
        assert len(links) == len(unique_links), "Nie powinno być duplikatów artykułów"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_http_error_handling(self, mock_get):
        """
        Test obsługi błędów HTTP
        Sprawdza czy scraper poprawnie radzi sobie z błędami serwera
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news()
        
        # Przy błędzie powinna być zwrócona pusta lista
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) == 0, "Lista powinna być pusta przy błędzie HTTP"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_timeout_handling(self, mock_get):
        """
        Test obsługi timeout'u
        Sprawdza czy scraper poprawnie radzi sobie z przekroczeniem czasu
        """
        import requests
        mock_get.side_effect = requests.Timeout("Timeout")
        
        news = get_policja_krakow_news()
        
        # Przy timeout powinna być zwrócona pusta lista
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) == 0, "Lista powinna być pusta przy timeout"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_limit_parameter(self, mock_get, mockup_policja_krakow):
        """
        Test parametru limit
        Sprawdza czy scraper respektuje zadany limit artykułów
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        # Test różnych limitów
        for limit in [1, 3, 5, 10]:
            news = get_policja_krakow_news(limit=limit)
            assert len(news) <= limit, f"Liczba artykułów nie powinna przekraczać limitu {limit}"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_title_extraction(self, mock_get, mockup_policja_krakow):
        """
        Test ekstrakcji tytułu
        Sprawdza czy tytuły są poprawnie wyciągane z elementu strong
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news(limit=1)
        
        assert len(news) > 0
        article = news[0]
        
        # Tytuł powinien istnieć i być niepusty
        assert article['title'], "Tytuł nie powinien być pusty"
        assert len(article['title']) > 10, "Tytuł powinien mieć więcej niż 10 znaków"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_empty_page_handling(self, mock_get):
        """
        Test obsługi pustej strony
        Sprawdza czy scraper radzi sobie z pustą stroną HTML
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><div id='content'></div></body></html>"
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news()
        
        # Powinna być zwrócona pusta lista
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) == 0, "Lista powinna być pusta dla pustej strony"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_missing_content_div(self, mock_get):
        """
        Test obsługi braku div#content
        Sprawdza czy scraper radzi sobie z brakiem głównego kontenera
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"<html><body><div id='other'></div></body></html>"
        mock_get.return_value = mock_response
        
        news = get_policja_krakow_news()
        
        # Powinna być zwrócona pusta lista
        assert isinstance(news, list), "Wynik powinien być listą"
        assert len(news) == 0, "Lista powinna być pusta gdy brak div#content"
    
    @patch('modules.news.collectors.policja_scraper.requests.get')
    def test_universal_scraper_function(self, mock_get, mockup_policja_krakow):
        """
        Test uniwersalnej funkcji scrape_policja_news
        Sprawdza czy można używać funkcji z niestandardowymi parametrami
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = mockup_policja_krakow.encode('utf-8')
        mock_get.return_value = mock_response
        
        custom_tags = ['custom', 'test']
        custom_url = 'https://example.policja.gov.pl/test'
        
        news = scrape_policja_news(custom_url, custom_tags, limit=3)
        
        assert isinstance(news, list), "Wynik powinien być listą"
        
        if len(news) > 0:
            # Sprawdź czy tagi są prawidłowe
            for article in news:
                assert article['tags'] == custom_tags, "Artykuły powinny mieć niestandardowe tagi"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
