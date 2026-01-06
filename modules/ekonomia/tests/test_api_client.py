"""
Testy jednostkowe dla klasy APIClient
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from modules.ekonomia.klasy_api_obsluga.APIClient import APIClient


class TestAPIClient:
    """Testy dla klasy APIClient"""

    def test_init_default_base_url(self):
        """Test inicjalizacji z domyślnym base_url"""
        client = APIClient()
        assert client.base_url == "https://api.nbp.pl/api"

    def test_init_custom_base_url(self):
        """Test inicjalizacji z niestandardowym base_url"""
        custom_url = "https://custom.api.pl"
        client = APIClient(base_url=custom_url)
        assert client.base_url == custom_url

    @patch('requests.get')
    def test_get_json_success(self, mock_get):
        """Test pomyślnego pobrania danych JSON"""
        # Przygotowanie mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        client = APIClient()
        result = client.get_json("https://api.nbp.pl/api/test")

        assert result == {"data": "test"}
        mock_get.assert_called_once_with("https://api.nbp.pl/api/test", params=None)

    @patch('requests.get')
    def test_get_json_with_params(self, mock_get):
        """Test pobrania danych z parametrami"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_get.return_value = mock_response

        client = APIClient()
        params = {"format": "json"}
        result = client.get_json("https://api.nbp.pl/api/test", params=params)

        assert result == {"data": "test"}
        mock_get.assert_called_once_with("https://api.nbp.pl/api/test", params=params)

    @patch('requests.get')
    def test_get_json_request_exception(self, mock_get):
        """Test obsługi wyjątku RequestException"""
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        client = APIClient()
        result = client.get_json("https://api.nbp.pl/api/test")

        assert result is None

    @patch('requests.get')
    def test_get_json_http_error(self, mock_get):
        """Test obsługi błędu HTTP (404, 500, etc.)"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        client = APIClient()
        result = client.get_json("https://api.nbp.pl/api/test")

        assert result is None

    @patch('requests.get')
    def test_get_json_timeout(self, mock_get):
        """Test obsługi timeoutu"""
        mock_get.side_effect = requests.exceptions.Timeout("Request timeout")

        client = APIClient()
        result = client.get_json("https://api.nbp.pl/api/test")

        assert result is None
