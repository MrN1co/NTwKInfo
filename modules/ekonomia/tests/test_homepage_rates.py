"""
Testy dla get_homepage_rates (homepage currency rates helper)
"""

import os
import sys
from unittest.mock import patch
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.ekonomia.ekonomia import get_homepage_rates


class TestHomepageRates:
    def test_json_only_all_present_no_api(self):
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
        with patch('modules.ekonomia.ekonomia.load_currency_json', return_value=None), \
             patch('modules.ekonomia.ekonomia.Manager') as mock_mgr:
            mock_mgr.return_value.currencies.get_current_rates.return_value = {}
            rates = get_homepage_rates(["USD", "EUR"])

        assert rates == []
        mock_mgr.return_value.currencies.get_current_rates.assert_called_once()
