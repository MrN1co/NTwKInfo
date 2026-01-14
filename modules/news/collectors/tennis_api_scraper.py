"""
Scraper dla danych tenisowych z Tennis API (RapidAPI)
Pobiera rankingi ATP i WTA
"""

import requests
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv(os.path.join(BASE_DIR, '.env'))

# Klucz API z RapidAPI dla Tennis API
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
RAPIDAPI_HOST = "tennisapi1.p.rapidapi.com"
BASE_URL = f"https://{RAPIDAPI_HOST}/api/tennis"


def get_atp_rankings(limit=20):
    """
    Pobiera ranking ATP (mężczyźni)
    
    Args:
        limit (int): Liczba zawodników do pobrania (domyślnie 20)
    
    Returns:
        list: Lista słowników z danymi zawodników ATP
              Każdy słownik zawiera: ranking, team (nazwa, kraj), punkty
    """
    url = f"{BASE_URL}/rankings/atp"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # API zwraca ranking w formacie: {"rankings": [...]}
            rankings = data.get('rankings', [])
            
            # Zwracamy tylko określoną liczbę zawodników
            return rankings[:limit]
        else:
            print(f"Błąd ATP API: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Błąd podczas pobierania rankingu ATP: {e}")
        return []


def get_wta_rankings(limit=20):
    """
    Pobiera ranking WTA (kobiety)
    
    Args:
        limit (int): Liczba zawodniczek do pobrania (domyślnie 20)
    
    Returns:
        list: Lista słowników z danymi zawodniczek WTA
              Każdy słownik zawiera: ranking, team (nazwa, kraj), punkty
    """
    url = f"{BASE_URL}/rankings/wta"
    
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # API zwraca ranking w formacie: {"rankings": [...]}
            rankings = data.get('rankings', [])
            
            # Zwracamy tylko określoną liczbę zawodniczek
            return rankings[:limit]
        else:
            print(f"Błąd WTA API: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Błąd podczas pobierania rankingu WTA: {e}")
        return []
