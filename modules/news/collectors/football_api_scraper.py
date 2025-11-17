"""
Scraper dla danych piłki nożnej z football-data.org API
Pobiera tabele ligowe różnych rozgrywek europejskich
"""

import requests
import json
import os
from dotenv import load_dotenv

# Ładuj zmienne środowiskowe z pliku .env
load_dotenv()

# Klucz API do football-data.org
API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = 'https://api.football-data.org/v4'

# Katalog główny projektu (3 poziomy w górę od tego pliku)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def get_available_competitions():
    """
    Pobiera listę dostępnych rozgrywek z pliku COMPETITIONS.JSON
    
    Returns:
        list: Lista słowników z informacjami o rozgrywkach
    """
    competitions_path = os.path.join(BASE_DIR, 'data', 'news', 'football-data', 'COMPETITIONS.JSON')
    
    try:
        with open(competitions_path, 'r', encoding='utf-8') as f:
            competitions_data = json.load(f)
            return competitions_data.get('competitions', [])
    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku {competitions_path}")
        return []
    except json.JSONDecodeError:
        print(f"Błąd: Nieprawidłowy format JSON w pliku {competitions_path}")
        return []


def get_competition_info(competition_code):
    """
    Pobiera szczegółowe informacje o rozgrywkach z API
    
    Args:
        competition_code (str): Kod rozgrywek (np. 'PL', 'PD', 'SA')
    
    Returns:
        dict: Słownik z informacjami o rozgrywkach i dostępnych sezonach
    """
    url = f'{BASE_URL}/competitions/{competition_code}'
    headers = {'X-Auth-Token': API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Błąd API: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Błąd podczas pobierania informacji o rozgrywkach: {e}")
        return None


def get_football_standings(competition_code='PL', season='current', skip_competition_info=False):
    """
    Pobiera tabelę ligową dla wybranych rozgrywek i sezonu
    
    Args:
        competition_code (str): Kod rozgrywek (domyślnie 'PL' - Ekstraklasa)
        season (str): Rok rozpoczęcia sezonu lub 'current' dla aktualnego sezonu
        skip_competition_info (bool): Jeśli True, nie pobiera dodatkowych info o rozgrywkach (oszczędza API calls)
    
    Returns:
        dict: Słownik zawierający:
            - standings: lista drużyn z pozycjami
            - competition_name: nazwa rozgrywek
            - competition_emblem: URL do logo rozgrywek
            - season_info: informacje o sezonie
            - available_seasons: lista dostępnych sezonów
            - error: komunikat błędu (jeśli wystąpił)
    """
    # Pobieramy informacje o rozgrywkach
    available_competitions = get_available_competitions()
    
    # Szukamy max liczby sezonów i emblematu dla wybranych rozgrywek
    max_seasons = 3
    competition_emblem = ''
    
    for comp in available_competitions:
        if comp['code'] == competition_code:
            max_seasons = comp.get('seasons', 3)
            competition_emblem = comp.get('emblem', '')
            break
    
    # Pobieramy informacje o rozgrywkach (zawiera listę sezonów)
    # TYLKO jeśli nie chcemy oszczędzać API calls
    available_seasons = []
    
    if not skip_competition_info:
        comp_data = get_competition_info(competition_code)
        
        if comp_data and 'seasons' in comp_data:
            # Przygotowujemy listę dostępnych sezonów (ograniczoną do max_seasons)
            for season_data in comp_data['seasons'][:max_seasons]:
                start_year = season_data['startDate'][:4]
                end_year = season_data['endDate'][:4]
                season_label = f"{start_year}/{end_year}"
                
                available_seasons.append({
                    'year': start_year,
                    'label': season_label,
                    'winner': season_data.get('winner', {}).get('name', '') if season_data.get('winner') else ''
                })
    
    # Budujemy URL do pobrania tabeli
    if season == 'current':
        standings_url = f'{BASE_URL}/competitions/{competition_code}/standings'
    else:
        standings_url = f'{BASE_URL}/competitions/{competition_code}/standings?season={season}'
    
    headers = {'X-Auth-Token': API_KEY}
    
    try:
        response = requests.get(standings_url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            return {
                'standings': data['standings'][0]['table'],
                'competition_name': data['competition']['name'],
                'competition_emblem': competition_emblem,
                'season_info': data['season'],
                'available_seasons': available_seasons,
                'error': None
            }
        else:
            # Błąd podczas pobierania danych
            error_msg = f"Błąd API: {response.status_code}"
            if response.status_code == 429:
                error_msg += " - Limit zapytań API przekroczony. Daemon będzie próbował ponownie później."
            elif response.status_code == 403:
                error_msg += " - Brak dostępu (sprawdź klucz API lub dostępność ligi)"
            elif response.status_code == 404:
                error_msg += " - Liga/sezon nie znaleziony"
            else:
                error_msg += " - Brak dostępu do tej ligi/sezonu"
            
            print(f"[Football API] {error_msg} dla {competition_code}/{season}")
            
            return {
                'standings': [],
                'competition_name': competition_code,
                'competition_emblem': competition_emblem,
                'season_info': None,
                'available_seasons': available_seasons,
                'error': error_msg
            }
            
    except Exception as e:
        # Wyjątek podczas pobierania danych
        return {
            'standings': [],
            'competition_name': competition_code,
            'competition_emblem': competition_emblem,
            'season_info': None,
            'available_seasons': available_seasons,
            'error': f"Błąd: {str(e)}"
        }
