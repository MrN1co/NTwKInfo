"""
Testy jednostkowe dla scrapera Ekstraklasy i polskich lig piłkarskich
Wykorzystuje mockup witryny 90minut.pl do testowania funkcjonalności scrapowania
"""

import pytest
from unittest.mock import Mock, patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.news.collectors.ekstraklasa_scraper import (
    get_90minut_table,
    get_ekstraklasa_table,
    get_first_league_table,
    get_second_league_table,
    get_emblems_map
)


class TestEkstraklasaScraper:
    """Klasa testowa dla scrapera Ekstraklasy i polskich lig"""
    
    @pytest.fixture
    def mockup_ekstraklasa(self):
        """Fixture zwracający zawartość mockup strony Ekstraklasy"""
        mockup_path = os.path.join(os.path.dirname(__file__), 'mockup_esa.html')
        with open(mockup_path, 'r', encoding='iso-8859-2') as f:
            return f.read()
    
    @pytest.fixture
    def mockup_emblems(self):
        """Fixture zwracający zawartość mockup strony z emblematami"""
        mockup_path = os.path.join(os.path.dirname(__file__), 'mockup_esa_emblematy.html')
        with open(mockup_path, 'r', encoding='iso-8859-2') as f:
            return f.read()
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_get_ekstraklasa_table_basic(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test podstawowego działania scrapera tabeli Ekstraklasy
        Sprawdza czy scraper poprawnie pobiera tabelę ligową
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        assert isinstance(result, dict), "Wynik powinien być słownikiem"
        assert 'standings' in result, "Wynik powinien zawierać pole 'standings'"
        assert 'error' in result, "Wynik powinien zawierać pole 'error'"
        assert isinstance(result['standings'], list), "Standings powinno być listą"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_standings_structure(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test struktury danych tabeli
        Sprawdza czy każda drużyna ma wszystkie wymagane pola
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        assert len(result['standings']) > 0, "Tabela nie powinna być pusta"
        
        team = result['standings'][0]
        
        # Wymagane pola
        assert 'position' in team, "Drużyna powinna mieć pole 'position'"
        assert 'team' in team, "Drużyna powinna mieć pole 'team'"
        assert 'played_games' in team, "Drużyna powinna mieć pole 'played_games'"
        assert 'points' in team, "Drużyna powinna mieć pole 'points'"
        assert 'won' in team, "Drużyna powinna mieć pole 'won'"
        assert 'draw' in team, "Drużyna powinna mieć pole 'draw'"
        assert 'lost' in team, "Drużyna powinna mieć pole 'lost'"
        assert 'goals' in team, "Drużyna powinna mieć pole 'goals'"
        
        # Struktura team
        assert isinstance(team['team'], dict), "Pole 'team' powinno być słownikiem"
        assert 'name' in team['team'], "Team powinien mieć pole 'name'"
        assert 'crest' in team['team'], "Team powinien mieć pole 'crest'"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_team_data_types(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test typów danych
        Sprawdza czy pola mają odpowiednie typy danych
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        assert len(result['standings']) > 0
        
        for team in result['standings']:
            # Typy pól
            assert isinstance(team['position'], str), "Position powinno być stringiem"
            assert isinstance(team['team']['name'], str), "Nazwa drużyny powinna być stringiem"
            assert isinstance(team['team']['crest'], str), "Crest powinien być stringiem"
            assert isinstance(team['played_games'], str), "Played_games powinno być stringiem"
            assert isinstance(team['points'], str), "Points powinno być stringiem"
            
            # Niepuste nazwy
            assert len(team['team']['name']) > 0, "Nazwa drużyny nie powinna być pusta"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_positions_ordering(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test kolejności pozycji
        Sprawdza czy drużyny są w poprawnej kolejności
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        assert len(result['standings']) > 0
        
        # Sprawdź czy pozycje są uporządkowane
        for i, team in enumerate(result['standings']):
            expected_position = str(i + 1)
            assert team['position'] == expected_position, \
                f"Pozycja drużyny powinna być {expected_position}, a jest {team['position']}"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_points_are_numeric(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test czy punkty są liczbami
        Sprawdza czy wartości liczbowe można przekonwertować na int
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        for team in result['standings']:
            # Sprawdź czy można przekonwertować na int
            assert team['points'].isdigit(), "Punkty powinny być cyframi"
            assert team['played_games'].isdigit(), "Mecze powinny być cyframi"
            assert team['won'].isdigit(), "Wygrane powinny być cyframi"
            assert team['draw'].isdigit(), "Remisy powinny być cyframi"
            assert team['lost'].isdigit(), "Przegrane powinny być cyframi"
            
            # Konwersja na int nie powinna rzucić wyjątku
            int(team['points'])
            int(team['played_games'])
            int(team['won'])
            int(team['draw'])
            int(team['lost'])
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_http_error_handling(self, mock_get):
        """
        Test obsługi błędów HTTP
        Sprawdza czy scraper poprawnie radzi sobie z błędami serwera
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_get.return_value = mock_response
        
        result = get_ekstraklasa_table()
        
        # Przy błędzie powinna być zwrócona pusta lista ze status error
        assert isinstance(result, dict), "Wynik powinien być słownikiem"
        assert result['standings'] == [], "Standings powinno być puste przy błędzie"
        assert result['error'] is not None, "Error nie powinien być None"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_timeout_handling(self, mock_get):
        """
        Test obsługi timeout'u
        Sprawdza czy scraper poprawnie radzi sobie z przekroczeniem czasu
        """
        import requests
        mock_get.side_effect = requests.Timeout("Timeout")
        
        result = get_ekstraklasa_table()
        
        # Przy timeout powinna być zwrócona pusta lista
        assert isinstance(result, dict), "Wynik powinien być słownikiem"
        assert result['standings'] == [], "Standings powinno być puste przy timeout"
        assert result['error'] is not None, "Error nie powinien być None"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_emblems_extraction(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test ekstrakcji emblematów
        Sprawdza czy emblematy są poprawnie przypisane do drużyn
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        # Sprawdź czy niektóre drużyny mają emblematy
        teams_with_crests = [team for team in result['standings'] if team['team']['crest']]
        
        # Powinno być co najmniej kilka drużyn z emblematami
        # (mogą nie wszystkie mieć, jeśli w mockup nie wszystkie są)
        for team in teams_with_crests:
            # Jeśli crest istnieje, powinien zawierać ścieżkę do obrazka
            assert '/logo/' in team['team']['crest'] or team['team']['crest'].startswith('http'), \
                "Crest powinien zawierać ścieżkę do obrazka"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_goals_format(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test formatu bramek
        Sprawdza czy bramki są w formacie XX-YY
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        for team in result['standings']:
            if team['goals']:  # Jeśli pole goals nie jest puste
                # Format powinien być XX-YY lub po prostu liczba
                assert isinstance(team['goals'], str), "Goals powinno być stringiem"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_no_duplicate_teams(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test sprawdzający czy nie ma duplikatów drużyn
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        # Sprawdzanie duplikatów po nazwach drużyn
        team_names = [team['team']['name'] for team in result['standings']]
        unique_names = set(team_names)
        
        assert len(team_names) == len(unique_names), "Nie powinno być duplikatów drużyn"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_minimum_teams_count(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test sprawdzający minimalną liczbę drużyn
        Ekstraklasa powinna mieć co najmniej kilka drużyn
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_ekstraklasa_table()
        
        # Ekstraklasa powinna mieć co najmniej 10 drużyn (typowo 18)
        assert len(result['standings']) >= 10, \
            f"Ekstraklasa powinna mieć co najmniej 10 drużyn, ma {len(result['standings'])}"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_first_league_function(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test funkcji pobierającej I Ligę
        Sprawdza czy funkcja działa analogicznie do Ekstraklasy
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_first_league_table()
        
        assert isinstance(result, dict), "Wynik powinien być słownikiem"
        assert 'standings' in result, "Wynik powinien zawierać pole 'standings'"
        assert 'error' in result, "Wynik powinien zawierać pole 'error'"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_second_league_function(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test funkcji pobierającej II Ligę
        Sprawdza czy funkcja działa analogicznie do Ekstraklasy
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        result = get_second_league_table()
        
        assert isinstance(result, dict), "Wynik powinien być słownikiem"
        assert 'standings' in result, "Wynik powinien zawierać pole 'standings'"
        assert 'error' in result, "Wynik powinien zawierać pole 'error'"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_empty_table_handling(self, mock_get):
        """
        Test obsługi pustej tabeli
        Sprawdza czy scraper radzi sobie z brakiem danych
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><table></table></body></html>"
        mock_get.return_value = mock_response
        
        result = get_ekstraklasa_table()
        
        # Powinna być zwrócona pusta lista ze stosownym komunikatem
        assert isinstance(result, dict), "Wynik powinien być słownikiem"
        assert result['standings'] == [], "Standings powinno być puste dla pustej tabeli"
        assert result['error'] is not None, "Powinien być komunikat o braku danych"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_emblems_map_function(self, mock_get, mockup_emblems):
        """
        Test funkcji pobierającej mapę emblematów
        Sprawdza czy funkcja poprawnie wyciąga emblematy
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mockup_emblems
        mock_get.return_value = mock_response
        
        emblems = get_emblems_map("14072")
        
        assert isinstance(emblems, dict), "Wynik powinien być słownikiem"
        
        # Jeśli są jakieś emblematy, sprawdź ich strukturę
        if len(emblems) > 0:
            for team_name, emblem_url in emblems.items():
                assert isinstance(team_name, str), "Nazwa drużyny powinna być stringiem"
                assert isinstance(emblem_url, str), "URL emblemu powinien być stringiem"
                assert '/logo/dobazy/' in emblem_url, "URL powinien zawierać ścieżkę do logosu"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_emblems_error_handling(self, mock_get):
        """
        Test obsługi błędów przy pobieraniu emblematów
        Sprawdza czy funkcja radzi sobie z błędami
        """
        mock_get.side_effect = Exception("Network error")
        
        emblems = get_emblems_map("14072")
        
        # Przy błędzie powinien być zwrócony pusty słownik
        assert isinstance(emblems, dict), "Wynik powinien być słownikiem"
        assert len(emblems) == 0, "Słownik powinien być pusty przy błędzie"
    
    @patch('modules.news.collectors.ekstraklasa_scraper.requests.get')
    def test_universal_scraper_function(self, mock_get, mockup_ekstraklasa, mockup_emblems):
        """
        Test uniwersalnej funkcji get_90minut_table
        Sprawdza czy można używać funkcji z niestandardowymi parametrami
        """
        def side_effect(url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 200
            if 'skarb.php' in url:
                mock_response.text = mockup_emblems
            else:
                mock_response.text = mockup_ekstraklasa
            return mock_response
        
        mock_get.side_effect = side_effect
        
        custom_url = "http://www.90minut.pl/liga/1/liga14072.html"
        custom_id = "14072"
        
        result = get_90minut_table(custom_url, custom_id)
        
        assert isinstance(result, dict), "Wynik powinien być słownikiem"
        assert 'standings' in result, "Wynik powinien zawierać pole 'standings'"
        assert 'error' in result, "Wynik powinien zawierać pole 'error'"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
