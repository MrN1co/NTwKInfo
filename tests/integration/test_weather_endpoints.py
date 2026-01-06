# tests/integration/test_weather_endpoints.py
from unittest.mock import Mock
import modules.weather_app as weather_app


# ======================================================
# 1️⃣ TEST ENDPOINTU HTML
# GET /weather/pogoda
# ======================================================

def test_weather_page_returns_html(client):
    """
    Integracyjny test endpointu HTML.
    Sprawdza:
    - czy route działa
    - czy zwraca HTML
    """

    response = client.get("/weather/pogoda")

    assert response.status_code == 200
    assert b"<html" in response.data


# ======================================================
# 2️⃣ TEST ENDPOINTU JSON
# GET /weather/api/forecast
# (z mockiem OpenWeather)
# ======================================================

def test_api_forecast_returns_normalized_json(client, monkeypatch):
    """
    Integracyjny test endpointu API:
    - mockujemy OpenWeather (requests.get)
    - sprawdzamy strukturę JSON
    - monkeypatch to fixture pytest do podmiany funkcji w locie
    """

    # --- FAKE RESPONSE Z OPENWEATHER ---
    fake_openweather_response = {
        "city": {
            "name": "Kraków",
            "coord": {"lat": 50.06, "lon": 19.94},
            "timezone": 3600,
        },
        "list": [
            {
                "dt": 1700000000,
                "temp": {
                    "min": 5.0,
                    "max": 10.0,
                    "day": 8.0,
                },
                "pressure": 1015,
                "rain": 1.2,
                "weather": [
                    {
                        "icon": "10d",
                        "description": "lekki deszcz",
                    }
                ],
            }
        ],
    }

    # --- MOCK requests.get ---
    def mock_requests_get(*args, **kwargs):
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = fake_openweather_response
        mock_resp.raise_for_status = lambda: None
        return mock_resp

    monkeypatch.setattr(weather_app.requests, "get", mock_requests_get)

    # --- WYWOŁANIE ENDPOINTU ---
    response = client.get("/weather/api/forecast")

    assert response.status_code == 200

    data = response.get_json()

    # --- ASERCJE STRUKTURY ---
    assert "city" in data
    assert data["city"] == "Kraków"

    assert "days" in data
    assert isinstance(data["days"], list)
    assert len(data["days"]) == 1

    day = data["days"][0]

    assert day["t_min"] == 5.0
    assert day["t_max"] == 10.0
    assert day["t_day"] == 8.0
    assert day["precip_mm"] == 1.2
    assert day["description"] == "lekki deszcz"
