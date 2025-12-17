"""
Testy jednostkowe dla klasy HistoricalData
"""

import pytest
import sys
import os
from unittest.mock import Mock
from datetime import datetime, timedelta
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.ekonomia.klasy_api_obsluga.HistoricalData import HistoricalData
from modules.ekonomia.klasy_api_obsluga.APIClient import APIClient


class TestHistoricalData:
    """Testy dla klasy HistoricalData"""

    def setup_method(self):
        """Przygotowanie przed każdym testem"""
        self.mock_client = Mock(spec=APIClient)
        self.mock_client.base_url = "https://api.nbp.pl/api"

    def test_init(self):
        """Test inicjalizacji klasy HistoricalData"""
        history = HistoricalData(self.mock_client)
        assert history.client == self.mock_client

    def test_get_historical_rates_df_success(self):
        """Test pomyślnego pobrania historycznych kursów walut"""
        # Mock dla listy walut
        table_data = [
            {
                "rates": [
                    {"code": "EUR"},
                    {"code": "USD"}
                ]
            }
        ]
        
        # Mock dla historycznych kursów
        rates_data = {
            "code": "EUR",
            "rates": [
                {"effectiveDate": "2025-01-01", "mid": 4.25},
                {"effectiveDate": "2025-01-02", "mid": 4.26}
            ]
        }

        def mock_get_json(url, params=None):
            if "/tables/" in url:
                return table_data
            elif "/rates/" in url:
                return rates_data
            return None

        self.mock_client.get_json.side_effect = mock_get_json

        history = HistoricalData(self.mock_client)
        df = history.get_historical_rates_df(tables=["a"], years=1)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "date" in df.columns
        assert "code" in df.columns
        assert "rate" in df.columns
        assert "table" in df.columns

    def test_get_historical_rates_df_empty_response(self):
        """Test obsługi pustej odpowiedzi z API"""
        self.mock_client.get_json.return_value = []

        history = HistoricalData(self.mock_client)
        df = history.get_historical_rates_df(tables=["a"], years=1)

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_get_historical_rates_df_multiple_tables(self):
        """Test pobrania danych z wielu tabel"""
        def mock_get_json(url, params=None):
            if "/tables/a/" in url:
                return [{"rates": [{"code": "EUR"}]}]
            elif "/tables/b/" in url:
                return [{"rates": [{"code": "USD"}]}]
            elif "/rates/" in url:
                return {"rates": [{"effectiveDate": "2025-01-01", "mid": 4.00}]}
            return None

        self.mock_client.get_json.side_effect = mock_get_json

        history = HistoricalData(self.mock_client)
        df = history.get_historical_rates_df(tables=["a", "b"], years=1)

        assert isinstance(df, pd.DataFrame)

    def test_get_historical_gold_prices_success(self):
        """Test pomyślnego pobrania historycznych cen złota"""
        mock_data = [
            {"data": "2025-01-01", "cena": 250.50},
            {"data": "2025-01-02", "cena": 251.00},
            {"data": "2025-01-03", "cena": 250.75}
        ]
        self.mock_client.get_json.return_value = mock_data

        history = HistoricalData(self.mock_client)
        df = history.get_historical_gold_prices(months=1)

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert "date" in df.columns
        assert "price" in df.columns
        assert len(df) == 3
        assert df["price"].tolist() == [250.50, 251.00, 250.75]

    def test_get_historical_gold_prices_empty_response(self):
        """Test obsługi pustej odpowiedzi"""
        self.mock_client.get_json.return_value = []

        history = HistoricalData(self.mock_client)
        df = history.get_historical_gold_prices(months=1)

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_get_historical_gold_prices_none_response(self):
        """Test obsługi None z API"""
        self.mock_client.get_json.return_value = None

        history = HistoricalData(self.mock_client)
        df = history.get_historical_gold_prices(months=1)

        assert isinstance(df, pd.DataFrame)
        assert df.empty

    def test_get_historical_gold_prices_multiple_periods(self):
        """Test pobierania danych w wielu okresach (>93 dni)"""
        call_count = 0
        
        def mock_get_json(url, params=None):
            nonlocal call_count
            call_count += 1
            return [{"data": f"2025-01-{call_count:02d}", "cena": 250.0 + call_count}]

        self.mock_client.get_json.side_effect = mock_get_json

        history = HistoricalData(self.mock_client)
        df = history.get_historical_gold_prices(months=4)  # 120 dni - wymaga 2 wywołań API

        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        # Powinno być więcej niż 1 wywołanie API
        assert call_count >= 2

    def test_get_historical_gold_prices_date_conversion(self):
        """Test czy daty są poprawnie konwertowane na datetime"""
        mock_data = [
            {"data": "2025-01-01", "cena": 250.50}
        ]
        self.mock_client.get_json.return_value = mock_data

        history = HistoricalData(self.mock_client)
        df = history.get_historical_gold_prices(months=1)

        assert not df.empty
        assert pd.api.types.is_datetime64_any_dtype(df["date"])

    def test_get_historical_gold_prices_custom_months(self):
        """Test z różną liczbą miesięcy"""
        self.mock_client.get_json.return_value = [
            {"data": "2025-01-01", "cena": 250.50}
        ]

        history = HistoricalData(self.mock_client)
        
        # Test z różnymi wartościami miesięcy
        for months in [1, 3, 6, 12, 36]:
            df = history.get_historical_gold_prices(months=months)
            assert isinstance(df, pd.DataFrame)
