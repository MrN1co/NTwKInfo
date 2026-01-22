import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pytest
from modules.main.helpers import select_featured_article, summarize, format_published_date


class TestHelpers:
    """
    Klasa testowa testująca funkcje pomocnicze modułu strony głównej (main).
    
    Ta klasa weryfikuje prawidłowe działanie funkcji narzędziowych (helpers) 
    odpowiedzialnych za:
    - Wybór artykułu wyróżnionego (featured article) z listy wiadomości
    - Streszczanie tekstu artykułów z obcięciem do określonej długości
    - Formatowanie dat publikacji artykułów w czytelny format
    
    Testy obejmują zarówno przypadki poprawne (happy path), jak i przypadki 
    brzegowe (np. puste listy, nieprawidłowe formaty dat).
    """
    def test_select_featured_with_items(self):
        """
        Test jednostkowy: Wybór artykułu wyróżnionego z listy.
        
        Scenariusz:
        - Tworzy listę dwóch artykułów
        
        Oczekiwany wynik:
        - Funkcja zwraca pierwszy element listy (items[0])
        """
        items = [{'title': 'A'}, {'title': 'B'}]
        assert select_featured_article(items) == items[0]

    def test_select_featured_empty(self):
        """
        Test jednostkowy: Wybór artykułu wyróżnionego z pustej listy.
        
        Scenariusz:
        - Przekazuje pustą listę
        
        Oczekiwany wynik:
        - Funkcja zwraca None (brak artykułów do wybrania)
        """
        assert select_featured_article([]) is None

    def test_summarize_short(self):
        """
        Test jednostkowy: Streszczanie tekstu któryi jest już krótki.
        
        Scenariusz:
        - Tekst "short text" jest krótszy niż max_len=20
        
        Oczekiwany wynik:
        - Funkcja zwraca oryginalny tekst bez zmian
        """
        s = 'short text'
        assert summarize(s, max_len=20) == s

    def test_summarize_trim(self):
        """
        Test jednostkowy: Streszczanie długiego tekstu.
        
        Scenariusz:
        - Tekst 50 znaków 'x' ma być obcięty do 10 znaków
        
        Oczekiwany wynik:
        - Funkcja zwraca tekst obcięty do 10 znaków
        - Tekst kończy się z "..." (ellipsis)
        """
        s = 'x' * 50
        out = summarize(s, max_len=10)
        assert len(out) <= 10 and out.endswith('...')

    def test_format_published_iso(self):
        """
        Test jednostkowy: Formatowanie daty w formacie ISO 8601.
        
        Scenariusz:
        - Data w formacie ISO: '2024-12-05T14:30:00'
        
        Oczekiwany wynik:
        - Funkcja zwraca sformatowaną datę: '05 Dec 2024'
        """
        assert format_published_date('2024-12-05T14:30:00') == '05 Dec 2024'

    def test_format_published_simple(self):
        """
        Test jednostkowy: Formatowanie daty w formacie prostym (YYYY-MM-DD).
        
        Scenariusz:
        - Data w formacie prostym: '2023-01-02'
        
        Oczekiwany wynik:
        - Funkcja zwraca sformatowaną datę: '02 Jan 2023'
        """
        assert format_published_date('2023-01-02') == '02 Jan 2023'

    def test_format_published_invalid(self):
        """
        Test jednostkowy: Formatowanie nieprawidłowej daty.
        
        Scenariusz:
        - Tekst który nie jest datą: 'not a date'
        
        Oczekiwany wynik:
        - Funkcja zwraca pusty string '' (graceful error handling)
        """
        assert format_published_date('not a date') == ''
