"""
Testy jednostkowe dla klasy GoldPrices
"""

import pytest
import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.ekonomia.klasy_api_obsluga.GoldPrices import GoldPrices
from modules.ekonomia.klasy_api_obsluga.APIClient import APIClient


class TestGoldPrices:
    """Testy dla klasy GoldPrices"""

    def setup_method(self):
        """Przygotowanie przed każdym testem"""
        self.mock_client = Mock(spec=APIClient)
        self.mock_client.base_url = "https://api.nbp.pl/api"

    def test_init(self):
        """Test inicjalizacji klasy GoldPrices"""
        gold = GoldPrices(self.mock_client)
        assert gold.client == self.mock_client

    def test_get_current_price_success(self):
        """Test pomyślnego pobrania aktualnej ceny złota"""
        mock_data = [
            {
                "data": "2025-01-01",
                "cena": 250.50
            }
        ]
        self.mock_client.get_json.return_value = mock_data

        gold = GoldPrices(self.mock_client)
        result = gold.get_current_price()

        assert result == 250.50
        self.mock_client.get_json.assert_called_once_with(
            "https://api.nbp.pl/api/cenyzlota/",
            {"format": "json"}
        )

    def test_get_current_price_multiple_entries(self):
        """Test pobrania ceny gdy API zwraca wiele wpisów (bierze pierwszy)"""
        mock_data = [
            {"data": "2025-01-01", "cena": 250.50},
            {"data": "2024-12-31", "cena": 249.00}
        ]
        self.mock_client.get_json.return_value = mock_data

        gold = GoldPrices(self.mock_client)
        result = gold.get_current_price()

        assert result == 250.50

    def test_get_current_price_empty_response(self):
        """Test obsługi pustej odpowiedzi z API"""
        self.mock_client.get_json.return_value = []

        gold = GoldPrices(self.mock_client)
        result = gold.get_current_price()

        assert result is None

    def test_get_current_price_none_response(self):
        """Test obsługi None z API (błąd połączenia)"""
        self.mock_client.get_json.return_value = None

        gold = GoldPrices(self.mock_client)
        result = gold.get_current_price()

        assert result is None

    def test_update_success(self):
        """Test metody update - pomyślna aktualizacja"""
        mock_data = [
            {"data": "2025-01-01", "cena": 250.50}
        ]
        self.mock_client.get_json.return_value = mock_data

        gold = GoldPrices(self.mock_client)
        result = gold.update()

        assert result == 250.50
        assert hasattr(gold, 'gold_price')
        assert gold.gold_price == 250.50

    def test_update_empty_response(self):
        """Test metody update z pustą odpowiedzią"""
        self.mock_client.get_json.return_value = []

        gold = GoldPrices(self.mock_client)
        result = gold.update()

        assert result is None
        assert hasattr(gold, 'gold_price')
        assert gold.gold_price is None

    def test_update_none_response(self):
        """Test metody update z None"""
        self.mock_client.get_json.return_value = None

        gold = GoldPrices(self.mock_client)
        result = gold.update()

        assert result is None
        assert hasattr(gold, 'gold_price')
        assert gold.gold_price is None

    def test_update_called_twice(self):
        """Test wielokrotnego wywołania update"""
        mock_data_1 = [{"data": "2025-01-01", "cena": 250.50}]
        mock_data_2 = [{"data": "2025-01-02", "cena": 251.00}]
        
        self.mock_client.get_json.side_effect = [mock_data_1, mock_data_2]

        gold = GoldPrices(self.mock_client)
        
        result1 = gold.update()
        assert result1 == 250.50
        assert gold.gold_price == 250.50

        result2 = gold.update()
        assert result2 == 251.00
        assert gold.gold_price == 251.00
