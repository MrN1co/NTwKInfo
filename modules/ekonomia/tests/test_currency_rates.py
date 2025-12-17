"""
Testy jednostkowe dla klasy CurrencyRates
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.ekonomia.klasy_api_obsluga.CurrencyRates import CurrencyRates
from modules.ekonomia.klasy_api_obsluga.APIClient import APIClient


class TestCurrencyRates:
    """Testy dla klasy CurrencyRates"""

    def setup_method(self):
        """Przygotowanie przed każdym testem"""
        self.mock_client = Mock(spec=APIClient)
        self.mock_client.base_url = "https://api.nbp.pl/api"

    def test_init_default_tables(self):
        """Test inicjalizacji z domyślnymi tabelami"""
        rates = CurrencyRates(self.mock_client)
        assert rates.client == self.mock_client
        assert set(rates.tables) == {"a", "b"}

    def test_init_custom_tables(self):
        """Test inicjalizacji z niestandardowymi tabelami"""
        rates = CurrencyRates(self.mock_client, tables=["a", "c"])
        assert set(rates.tables) == {"a", "c"}

    def test_set_tables_valid(self):
        """Test ustawiania poprawnych tabel"""
        rates = CurrencyRates(self.mock_client)
        rates.set_tables(["a", "b", "c"])
        assert set(rates.tables) == {"a", "b", "c"}

    def test_set_tables_invalid_filtered(self):
        """Test filtrowania niepoprawnych tabel"""
        rates = CurrencyRates(self.mock_client)
        rates.set_tables(["a", "d", "x", "b"])
        assert set(rates.tables) == {"a", "b"}

    def test_set_tables_empty(self):
        """Test ustawiania pustej listy tabel"""
        rates = CurrencyRates(self.mock_client)
        rates.set_tables([])
        assert rates.tables == []

    def test_get_current_rates_success(self):
        """Test pomyślnego pobrania aktualnych kursów"""
        # Mock response z API
        mock_data = [
            {
                "table": "A",
                "no": "001/A/NBP/2025",
                "effectiveDate": "2025-01-01",
                "rates": [
                    {"code": "EUR", "mid": 4.25},
                    {"code": "USD", "mid": 4.00}
                ]
            }
        ]
        self.mock_client.get_json.return_value = mock_data

        rates = CurrencyRates(self.mock_client, tables=["a"])
        result = rates.get_current_rates()

        assert result == {"eur": 4.25, "usd": 4.00}
        self.mock_client.get_json.assert_called_once()

    def test_get_current_rates_multiple_tables(self):
        """Test pobrania kursów z wielu tabel"""
        def mock_get_json(url, params=None):
            if "/a/" in url:
                return [{"rates": [{"code": "EUR", "mid": 4.25}]}]
            elif "/b/" in url:
                return [{"rates": [{"code": "USD", "mid": 4.00}]}]
            return None

        self.mock_client.get_json.side_effect = mock_get_json

        rates = CurrencyRates(self.mock_client, tables=["a", "b"])
        result = rates.get_current_rates()

        assert result == {"eur": 4.25, "usd": 4.00}
        assert self.mock_client.get_json.call_count == 2

    def test_get_current_rates_empty_response(self):
        """Test obsługi pustej odpowiedzi z API"""
        self.mock_client.get_json.return_value = []

        rates = CurrencyRates(self.mock_client, tables=["a"])
        result = rates.get_current_rates()

        assert result == {}

    def test_get_current_rates_none_response(self):
        """Test obsługi None z API (błąd połączenia)"""
        self.mock_client.get_json.return_value = None

        rates = CurrencyRates(self.mock_client, tables=["a"])
        result = rates.get_current_rates()

        assert result == {}

    def test_get_currency_list_success(self):
        """Test pomyślnego pobrania listy walut"""
        mock_data = [
            {
                "rates": [
                    {"code": "EUR", "currency": "euro"},
                    {"code": "USD", "currency": "dolar amerykański"}
                ]
            }
        ]
        self.mock_client.get_json.return_value = mock_data

        rates = CurrencyRates(self.mock_client, tables=["a"])
        result = rates.get_currency_list()

        expected = [
            {"code": "EUR", "table": "a"},
            {"code": "USD", "table": "a"}
        ]
        assert result == expected

    def test_get_currency_list_multiple_tables(self):
        """Test pobrania listy walut z wielu tabel"""
        def mock_get_json(url, params=None):
            if "/a/" in url:
                return [{"rates": [{"code": "EUR"}]}]
            elif "/b/" in url:
                return [{"rates": [{"code": "USD"}]}]
            return None

        self.mock_client.get_json.side_effect = mock_get_json

        rates = CurrencyRates(self.mock_client, tables=["a", "b"])
        result = rates.get_currency_list()

        expected = [
            {"code": "EUR", "table": "a"},
            {"code": "USD", "table": "b"}
        ]
        assert result == expected

    def test_get_currency_list_empty_response(self):
        """Test obsługi pustej odpowiedzi"""
        self.mock_client.get_json.return_value = []

        rates = CurrencyRates(self.mock_client, tables=["a"])
        result = rates.get_currency_list()

        assert result == []

    def test_update_success(self):
        """Test metody update"""
        mock_data = [
            {
                "rates": [
                    {"code": "EUR", "mid": 4.25},
                    {"code": "USD", "mid": 4.00}
                ]
            }
        ]
        self.mock_client.get_json.return_value = mock_data

        rates = CurrencyRates(self.mock_client, tables=["a"])
        result = rates.update()

        assert result == {"eur": 4.25, "usd": 4.00}
        assert hasattr(rates, 'rates')
        assert rates.rates == {"eur": 4.25, "usd": 4.00}
