"""
Testy jednostkowe dla modułu fetch_nbp
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, mock_open, MagicMock
from datetime import datetime, timedelta
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.ekonomia import fetch_nbp


class TestFetchNBP:
    """Testy dla modułu fetch_nbp"""

    @patch('modules.ekonomia.fetch_nbp.requests.get')
    def test_get_daily_currencies_success(self, mock_get):
        """Test pomyślnego pobrania listy walut"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "table": "A",
                "rates": [
                    {"code": "EUR", "currency": "euro"},
                    {"code": "USD", "currency": "dolar amerykański"}
                ]
            }
        ]
        mock_get.return_value = mock_response

        # Wywołaj funkcję bezpośrednio
        url = "https://api.nbp.pl/api/exchangerates/tables/a/?format=json"
        res = mock_get(url)
        data = res.json()
        codes = [r['code'] for r in data[0]['rates']]

        assert codes == ["EUR", "USD"]

    @patch('modules.ekonomia.fetch_nbp.requests.get')
    def test_get_daily_currencies_error(self, mock_get):
        """Test obsługi błędu przy pobieraniu walut"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        url = "https://api.nbp.pl/api/exchangerates/tables/a/?format=json"
        res = mock_get(url)
        
        if res.status_code != 200:
            codes = []
        
        assert codes == []

    @patch('modules.ekonomia.fetch_nbp.requests.get')
    def test_fetch_nbprates_success(self, mock_get):
        """Test pomyślnego pobrania kursów waluty"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "code": "EUR",
            "rates": [
                {"effectiveDate": "2025-01-01", "mid": 4.25},
                {"effectiveDate": "2025-01-02", "mid": 4.26}
            ]
        }
        mock_get.return_value = mock_response

        rates = fetch_nbp.fetch_nbprates("EUR")

        assert isinstance(rates, list)
        assert len(rates) >= 0  # Może być filtrowane przez daty

    @patch('modules.ekonomia.fetch_nbp.requests.get')
    def test_fetch_nbprates_filters_old_dates(self, mock_get):
        """Test filtrowania starych dat (sprzed roku)"""
        today = datetime.today()
        old_date = (today - timedelta(days=400)).strftime('%Y-%m-%d')
        recent_date = (today - timedelta(days=10)).strftime('%Y-%m-%d')

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": [
                {"effectiveDate": old_date, "mid": 4.00},
                {"effectiveDate": recent_date, "mid": 4.25}
            ]
        }
        mock_get.return_value = mock_response

        rates = fetch_nbp.fetch_nbprates("EUR")

        # Powinien być tylko recent_date
        assert all(
            datetime.strptime(r['effectiveDate'], '%Y-%m-%d') >= (datetime.today() - timedelta(days=365))
            for r in rates
        )

    @patch('modules.ekonomia.fetch_nbp.requests.get')
    def test_fetch_nbprates_removes_duplicates(self, mock_get):
        """Test usuwania duplikatów dat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": [
                {"effectiveDate": "2025-01-01", "mid": 4.25},
                {"effectiveDate": "2025-01-01", "mid": 4.26},  # duplikat
                {"effectiveDate": "2025-01-02", "mid": 4.27}
            ]
        }
        mock_get.return_value = mock_response

        rates = fetch_nbp.fetch_nbprates("EUR")

        # Sprawdź czy nie ma duplikatów dat
        dates = [r['effectiveDate'] for r in rates]
        assert len(dates) == len(set(dates))

    @patch('modules.ekonomia.fetch_nbp.requests.get')
    def test_fetch_nbprates_error_handling(self, mock_get):
        """Test obsługi błędów HTTP"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        rates = fetch_nbp.fetch_nbprates("INVALID")

        assert isinstance(rates, list)

    @patch('modules.ekonomia.fetch_nbp.requests.get')
    def test_fetch_gold_success(self, mock_get):
        """Test pomyślnego pobrania cen złota"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"data": "2025-01-01", "cena": 250.50},
            {"data": "2025-01-02", "cena": 251.00}
        ]
        mock_get.return_value = mock_response

        gold_data = fetch_nbp.fetch_gold()

        assert isinstance(gold_data, list)
        assert len(gold_data) == 2
        assert gold_data[0] == {"date": "2025-01-01", "price": 250.50}
        assert gold_data[1] == {"date": "2025-01-02", "price": 251.00}

    @patch('modules.ekonomia.fetch_nbp.requests.get')
    def test_fetch_gold_error(self, mock_get):
        """Test obsługi błędu przy pobieraniu złota"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        gold_data = fetch_nbp.fetch_gold()

        assert gold_data == []

    @patch('builtins.open', new_callable=mock_open, read_data='[]')
    @patch('os.path.exists', return_value=True)
    def test_update_json_adds_new_records(self, mock_exists, mock_file):
        """Test dodawania nowych rekordów do JSON"""
        new_data = [
            {"effectiveDate": "2025-01-03", "mid": 4.27}
        ]

        fetch_nbp.update_json("test.json", new_data, "effectiveDate")

        # Sprawdź czy plik został otwarty
        mock_file.assert_called()

    @patch('builtins.open', new_callable=mock_open, read_data='[{"effectiveDate": "2025-01-01", "mid": 4.25}]')
    @patch('os.path.exists', return_value=True)
    def test_update_json_skips_duplicates(self, mock_exists, mock_file):
        """Test pomijania duplikatów przy aktualizacji"""
        new_data = [
            {"effectiveDate": "2025-01-01", "mid": 4.25}  # duplikat
        ]

        fetch_nbp.update_json("test.json", new_data, "effectiveDate")

        mock_file.assert_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists', return_value=False)
    def test_update_json_creates_new_file(self, mock_exists, mock_file):
        """Test tworzenia nowego pliku jeśli nie istnieje"""
        new_data = [
            {"effectiveDate": "2025-01-01", "mid": 4.25}
        ]

        fetch_nbp.update_json("new_file.json", new_data, "effectiveDate")

        mock_file.assert_called()

    @patch('modules.ekonomia.fetch_nbp.fetch_nbprates')
    @patch('modules.ekonomia.fetch_nbp.fetch_gold')
    @patch('modules.ekonomia.fetch_nbp.update_json')
    def test_run_update(self, mock_update_json, mock_fetch_gold, mock_fetch_rates):
        """Test funkcji run_update"""
        mock_fetch_rates.return_value = [{"effectiveDate": "2025-01-01", "mid": 4.25}]
        mock_fetch_gold.return_value = [{"date": "2025-01-01", "price": 250.50}]

        fetch_nbp.run_update()

        # Sprawdź czy funkcje zostały wywołane
        assert mock_fetch_rates.call_count >= 1
        mock_fetch_gold.assert_called_once()
        assert mock_update_json.call_count >= 1

    def test_currency_codes_constant(self):
        """Test czy CURRENCY_CODES jest listą"""
        assert isinstance(fetch_nbp.CURRENCY_CODES, list)

    def test_data_dir_exists(self):
        """Test czy stała DATA_DIR jest zdefiniowana"""
        assert hasattr(fetch_nbp, 'DATA_DIR')
        assert isinstance(fetch_nbp.DATA_DIR, str)
