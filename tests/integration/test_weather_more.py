# tests/integration/test_weather_more.py
import pytest
import modules.weather_app as wa


class DummyResp:
    def __init__(self, status_code=200, payload=None, text="OK"):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise wa.requests.HTTPError(f"HTTP {self.status_code}")


# ----------------------------
# /weather/api/forecast
# ----------------------------

def test_api_forecast_invalid_lat_lon(client):
    r = client.get("/weather/api/forecast?lat=abc&lon=19")
    assert r.status_code == 400
    assert r.is_json
    assert "error" in r.get_json()


def test_api_forecast_label_overrides_city(client, monkeypatch):
    monkeypatch.setattr(wa, "get_api_key", lambda: "TESTKEY")

    fake_daily = {
        "city": {"name": "OryginalneMiasto", "coord": {"lat": 50.0, "lon": 19.0}, "timezone": 0},
        "list": [
            {
                "dt": 1700000000,
                "temp": {"min": 1, "max": 4, "day": 2},
                "pressure": 1010,
                "rain": 1.0,
                "weather": [{"icon": "10d", "description": "deszcz"}],
            }
        ],
    }

    def fake_get(url, params=None, timeout=None):
        assert url == wa.DAILY_URL
        return DummyResp(200, payload=fake_daily)

    monkeypatch.setattr(wa.requests, "get", fake_get)

    r = client.get("/weather/api/forecast?lat=50&lon=19&label=MojeMiasto")
    assert r.status_code == 200
    data = r.get_json()
    assert data["city"] == "MojeMiasto"


def test_api_forecast_openweather_http_error_returns_502(client, monkeypatch):
    monkeypatch.setattr(wa, "get_api_key", lambda: "TESTKEY")

    def fake_get(url, params=None, timeout=None):
        return DummyResp(404, payload={"message": "not found"}, text="not found")

    monkeypatch.setattr(wa.requests, "get", fake_get)

    r = client.get("/weather/api/forecast?lat=50&lon=19")
    assert r.status_code == 502
    assert r.is_json
    assert r.get_json()["error"] == "Błąd OpenWeather"


# ----------------------------
# /weather/api/geocode
# ----------------------------

def test_api_geocode_requires_q(client):
    r = client.get("/weather/api/geocode?q=")
    assert r.status_code == 400
    assert r.is_json


def test_api_geocode_ok(client, monkeypatch):
    monkeypatch.setattr(wa, "get_api_key", lambda: "TESTKEY")

    fake_geo = [{"name": "Kraków", "lat": 50.06, "lon": 19.94, "country": "PL"}]

    def fake_get(url, params=None, timeout=None):
        assert url == wa.GEOCODE_URL
        return DummyResp(200, payload=fake_geo)

    monkeypatch.setattr(wa.requests, "get", fake_get)

    r = client.get("/weather/api/geocode?q=Krakow")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)
    assert r.get_json()[0]["name"] == "Kraków"


def test_api_geocode_http_error_returns_502(client, monkeypatch):
    monkeypatch.setattr(wa, "get_api_key", lambda: "TESTKEY")

    def fake_get(url, params=None, timeout=None):
        return DummyResp(500, payload={"error": "server"}, text="server error")

    monkeypatch.setattr(wa.requests, "get", fake_get)

    r = client.get("/weather/api/geocode?q=Krakow")
    assert r.status_code == 502
    assert r.is_json
    assert r.get_json()["error"] == "Błąd geokodowania"


# ----------------------------
# /weather/api/hourly
# ----------------------------

def test_api_hourly_invalid_lat_lon(client):
    r = client.get("/weather/api/hourly?lat=abc&lon=19")
    assert r.status_code == 400
    assert r.is_json


def test_api_hourly_day_clamped_and_returns_points(client, monkeypatch):
    monkeypatch.setattr(wa, "get_api_key", lambda: "TESTKEY")

    fake_hourly = {
        "city": {"timezone": 0},
        "list": [
            {"dt": 1700000000, "main": {"temp": 2.0}, "rain": {"3h": 0.5}},
            {"dt": 1700010800, "main": {"temp": 3.0}, "snow": {"3h": 0.2}},
        ],
    }

    def fake_get(url, params=None, timeout=None):
        assert url == wa.HOURLY_URL
        return DummyResp(200, payload=fake_hourly)

    monkeypatch.setattr(wa.requests, "get", fake_get)

    r = client.get("/weather/api/hourly?lat=50&lon=19&day=999")  # clamp to 4
    assert r.status_code == 200
    data = r.get_json()
    assert "points" in data
    assert "tz_offset" in data
    assert isinstance(data["points"], list)


# ----------------------------
# /weather/plot.png
# ----------------------------

def test_plot_png_returns_png(client, monkeypatch):
    # zamiast bawić się w całe OpenWeather, mockujemy okno i tz
    from datetime import datetime, timezone

    def fake_get_hourly_window(lat, lon, day_offset=0):
        return [
            {"dt": datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc), "temp": 2.0, "precip_mm": 0.1},
            {"dt": datetime(2026, 1, 1, 3, 0, tzinfo=timezone.utc), "temp": 3.0, "precip_mm": 0.0},
        ]

    def fake_fetch_hourly_forecast(lat, lon, units="metric"):
        return {"city": {"timezone": 0}}

    monkeypatch.setattr(wa, "get_hourly_window", fake_get_hourly_window)
    monkeypatch.setattr(wa, "fetch_hourly_forecast", fake_fetch_hourly_forecast)

    r = client.get("/weather/plot.png?lat=50&lon=19&day=0")
    assert r.status_code == 200
    assert r.mimetype == "image/png"


def test_plot_png_returns_404_when_no_points(client, monkeypatch):
    def fake_get_hourly_window(lat, lon, day_offset=0):
        return []

    monkeypatch.setattr(wa, "get_hourly_window", fake_get_hourly_window)

    r = client.get("/weather/plot.png?lat=50&lon=19&day=0")
    assert r.status_code == 404
