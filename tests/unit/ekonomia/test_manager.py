"""
Testy jednostkowe dla klasy Manager
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import io
import base64

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.ekonomia.klasy_api_obsluga.Manager import Manager


class TestManager:
    """Testy dla klasy Manager"""

    def setup_method(self):
        """Przygotowanie przed każdym testem"""
        self.manager = Manager()

    def test_init(self):
        """Test inicjalizacji klasy Manager"""
        manager = Manager()
        
        assert hasattr(manager, 'client')
        assert hasattr(manager, 'currencies')
        assert hasattr(manager, 'gold')
        assert manager.client is not None
        assert manager.currencies is not None
        assert manager.gold is not None

    def test_update_all_success(self):
        """Test pomyślnej aktualizacji wszystkich danych"""
        # Mock metod
        mock_rates = {"eur": 4.25, "usd": 4.00}
        mock_gold = 250.50
        
        self.manager.currencies.get_current_rates = Mock(return_value=mock_rates)
        self.manager.gold.get_current_price = Mock(return_value=mock_gold)

        rates, gold_price = self.manager.update_all()

        assert rates == mock_rates
        assert gold_price == mock_gold
        self.manager.currencies.get_current_rates.assert_called_once()
        self.manager.gold.get_current_price.assert_called_once()

    def test_list_currencies_default_table(self):
        """Test listowania walut z domyślnej tabeli A"""
        mock_entries = [
            {"code": "EUR", "table": "a"},
            {"code": "USD", "table": "a"},
            {"code": "EUR", "table": "a"}  # duplikat do sprawdzenia unikalności
        ]
        
        with patch('modules.ekonomia.klasy_api_obsluga.Manager.CurrencyRates') as MockCurrencyRates:
            mock_instance = Mock()
            mock_instance.get_currency_list.return_value = mock_entries
            MockCurrencyRates.return_value = mock_instance
            
            manager = Manager()
            result = manager.list_currencies()
            
            assert isinstance(result, list)
            assert set(result) == {"EUR", "USD"}  # sprawdza unikalność
            assert all(isinstance(code, str) for code in result)

    def test_list_currencies_custom_table(self):
        """Test listowania walut z niestandardowej tabeli"""
        mock_entries = [
            {"code": "CHF", "table": "b"}
        ]
        
        with patch('modules.ekonomia.klasy_api_obsluga.Manager.CurrencyRates') as MockCurrencyRates:
            mock_instance = Mock()
            mock_instance.get_currency_list.return_value = mock_entries
            MockCurrencyRates.return_value = mock_instance
            
            manager = Manager()
            result = manager.list_currencies(table='b')
            
            assert isinstance(result, list)

    def test_create_plot_image_success(self):
        """Test tworzenia wykresu z danymi"""
        df = pd.DataFrame({
            "date": pd.date_range("2025-01-01", periods=10),
            "price": [250.0 + i for i in range(10)]
        })
        
        result = self.manager.create_plot_image(df)
        
        assert isinstance(result, str)
        assert len(result) > 0
        # Sprawdź czy to poprawny base64
        try:
            decoded = base64.b64decode(result)
            assert len(decoded) > 0
        except Exception:
            pytest.fail("Result is not valid base64")

    def test_create_plot_image_empty_dataframe(self):
        """Test tworzenia wykresu z pustym DataFrame"""
        df = pd.DataFrame()
        
        result = self.manager.create_plot_image(df)
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_create_plot_image_none_dataframe(self):
        """Test tworzenia wykresu z None"""
        result = self.manager.create_plot_image(None)
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_create_plot_image_custom_parameters(self):
        """Test tworzenia wykresu z niestandardowymi parametrami"""
        df = pd.DataFrame({
            "custom_date": pd.date_range("2025-01-01", periods=5),
            "custom_value": [1, 2, 3, 4, 5]
        })
        
        result = self.manager.create_plot_image(
            df,
            x_col='custom_date',
            y_col='custom_value',
            title='Custom Title',
            color='#ff0000',
            y_label='Custom Y',
            x_label='Custom X'
        )
        
        assert isinstance(result, str)
        assert len(result) > 0

    def test_create_plot_image_different_colors(self):
        """Test tworzenia wykresów z różnymi kolorami"""
        df = pd.DataFrame({
            "date": pd.date_range("2025-01-01", periods=5),
            "price": [250, 251, 252, 253, 254]
        })
        
        colors = ['#fbc531', '#6c7c40', '#ff0000', '#0000ff']
        
        for color in colors:
            result = self.manager.create_plot_image(df, color=color)
            assert isinstance(result, str)
            assert len(result) > 0

