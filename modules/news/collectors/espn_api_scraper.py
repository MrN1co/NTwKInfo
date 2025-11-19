"""
Scraper dla danych NBA i MLS z ESPN API
Pobiera tabele i wyniki z publicznego API ESPN
"""

import requests


def get_nba_standings():
    """
    Pobiera aktualną tabelę NBA z ESPN API
    
    Returns:
        dict: Słownik zawierający:
            - children: lista konferencji z danymi drużyn
            - error: komunikat błędu (jeśli wystąpił)
    """
    try:
        url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/standings"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'data': data,
            'error': None
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'data': {},
            'error': f'Błąd pobierania danych NBA: {str(e)}'
        }
    except Exception as e:
        return {
            'data': {},
            'error': f'Nieoczekiwany błąd: {str(e)}'
        }


def get_mls_standings():
    """
    Pobiera aktualną tabelę MLS z ESPN API
    
    Returns:
        dict: Słownik zawierający:
            - children: lista konferencji z danymi drużyn
            - error: komunikat błędu (jeśli wystąpił)
    """
    try:
        url = "https://site.api.espn.com/apis/v2/sports/soccer/usa.1/standings"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'data': data,
            'error': None
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'data': {},
            'error': f'Błąd pobierania danych MLS: {str(e)}'
        }
    except Exception as e:
        return {
            'data': {},
            'error': f'Nieoczekiwany błąd: {str(e)}'
        }
