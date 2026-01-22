"""
Testy dla funkcji get_homepage_rates (pomocy dla kursów walut na stronie głównej)
"""

import os
import sys
from unittest.mock import patch
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.ekonomia.ekonomia import get_homepage_rates


class TestHomepageRates:
    """
    Klasa testowa testująca funkcję get_homepage_rates() modułu ekonomia.
    
    Ta funkcja odpowiada za pobieranie aktualnych kursów walut wyświetlanych 
    na stronie głównej. Testy weryfikują:
    - Ładowanie danych z plików JSON
    - Fallback do API w przypadku braku plików JSON
    - Obsługę sytuacji, gdy dane są niedostępne
    
    Wykorzystuje mock'i dla bibliotek bazy danych i API, aby testy były 
    niezależne od rzeczywistych danych i serwisów zewnętrznych.
    """
    def test_json_only_all_present_no_api(self):
        """
        Test jednostkowy: Ładowanie kursów z plików JSON, brak potrzeby API.
        
        Scenariusz:
        - Mock'uje load_currency_json aby zwracała DataFrame z kursem 4.1234
        - Mock'uje Manager aby nie był wywoływany (API fallback nie jest potrzebny)
        - Testuje ładowanie USD i EUR
        
        Oczekiwany wynik:
        - Zwrócony tekst zawiera dwa kursy walut z kursem 4.1234
        - load_currency_json został wywołany
        - Manager nie został wywołany (nie potrzebujemy fallback do API)
        """
        df = pd.DataFrame({"rate": [4.1234]})

        with patch('modules.ekonomia.ekonomia.load_currency_json', return_value=df) as mock_json, \
             patch('modules.ekonomia.ekonomia.Manager') as mock_mgr:
            rates = get_homepage_rates(["USD", "EUR"])

        assert rates == [
            {"code": "USD", "rate": 4.1234},
            {"code": "EUR", "rate": 4.1234},
        ]
        mock_json.assert_called()
        mock_mgr.assert_not_called()

    def test_missing_json_uses_api_fallback(self):
        """
        Test jednostkowy: Fallback do API gdy brakuje danych JSON.
        
        Scenariusz:
        - Mock'uje load_currency_json aby zwracała dane dla USD ale None dla EUR
        - Mock'uje Manager aby zwracał kursy z API: USD=3.99, EUR=4.5
        - Testuje ładowanie USD i EUR
        
        Oczekiwany wynik:
        - USD: kurs z JSON (4.0)
        - EUR: kurs z API (4.5) - fallback dla brakujących danych
        - Manager.currencies.get_current_rates() został wywołany raz
        """
        df_usd = pd.DataFrame({"rate": [4.0]})

        def fake_load(code):
            return df_usd if code == "USD" else None

        api_rates = {"usd": 3.99, "eur": 4.5}

        with patch('modules.ekonomia.ekonomia.load_currency_json', side_effect=fake_load), \
             patch('modules.ekonomia.ekonomia.Manager') as mock_mgr:
            mock_mgr.return_value.currencies.get_current_rates.return_value = api_rates
            rates = get_homepage_rates(["USD", "EUR"])

        assert rates == [
            {"code": "USD", "rate": 4.0},
            {"code": "EUR", "rate": 4.5},
        ]
        mock_mgr.return_value.currencies.get_current_rates.assert_called_once()

    def test_no_data_returns_empty(self):
        """
        Test jednostkowy: Zwracanie pustej listy gdy brak jest danych.
        
        Scenariusz:
        - Mock'uje load_currency_json aby zwracała None (brak danych JSON)
        - Mock'uje Manager aby zwracał pusty słownik (brak danych API)
        - Testuje ładowanie USD i EUR
        
        Oczekiwany wynik:
        - Zwrócona pusta lista [] (nie ma dostępnych kursów)
        - Manager.currencies.get_current_rates() został wywołany raz
        - Funkcja obsługuje gracefully brak jakichkolwiek danych
        """
        with patch('modules.ekonomia.ekonomia.load_currency_json', return_value=None), \
             patch('modules.ekonomia.ekonomia.Manager') as mock_mgr:
            mock_mgr.return_value.currencies.get_current_rates.return_value = {}
            rates = get_homepage_rates(["USD", "EUR"])

        assert rates == []
        mock_mgr.return_value.currencies.get_current_rates.assert_called_once()
