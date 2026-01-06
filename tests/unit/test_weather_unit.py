# tests/unit/test_weather_unit.py
import time
import pytest
import modules.weather_app as wa


# ----------------------------
# CACHE
# ----------------------------

def test_cache_set_get_roundtrip(monkeypatch):
    wa._OW_CACHE.clear()
    monkeypatch.setattr(wa, "_OW_CACHE_TTL", 60)

    wa._cache_set("k1", {"a": 1})
    assert wa._cache_get("k1") == {"a": 1}


def test_cache_expires(monkeypatch):
    wa._OW_CACHE.clear()
    monkeypatch.setattr(wa, "_OW_CACHE_TTL", 60)

    fake_now = 1_000_000.0
    monkeypatch.setattr(time, "time", lambda: fake_now)

    wa._cache_set("k1", {"a": 1})
    assert wa._cache_get("k1") == {"a": 1}

    fake_now += 61
    assert wa._cache_get("k1") is None


# ----------------------------
# NORMALIZE_FORECAST
# ----------------------------

def test_normalize_forecast_basic_shape():
    raw = {
        "city": {"name": "Kraków", "coord": {"lat": 50.06, "lon": 19.94}, "timezone": 3600},
        "list": [
            {
                "dt": 1700000000,
                "temp": {"min": 1.0, "max": 5.0, "day": 3.0},
                "pressure": 1012,
                "rain": 2.5,
                "weather": [{"icon": "10d", "description": "deszcz"}],
            }
        ],
    }

    out = wa.normalize_forecast(raw)
    assert out["city"] == "Kraków"
    assert out["lat"] == 50.06
    assert out["lon"] == 19.94
    assert isinstance(out["days"], list)
    assert len(out["days"]) == 1
    day0 = out["days"][0]
    assert day0["precip_mm"] == pytest.approx(2.5)
    assert isinstance(day0["precip_mm"], float)
    assert day0["icon"] == "10d"
    assert day0["description"] == "deszcz"
    assert day0["t_min"] == 1.0
    assert day0["t_max"] == 5.0
    assert day0["t_day"] == 3.0


def test_normalize_forecast_precip_defaults_to_0_float():
    raw = {
        "city": {"name": "X", "coord": {"lat": 1.0, "lon": 2.0}, "timezone": 0},
        "list": [
            {
                "dt": 1700000000,
                "temp": {"min": 0, "max": 1, "day": 0.5},
                "pressure": 1000,
                "weather": [{"icon": "01d", "description": "bezchmurnie"}],
            }
        ],
    }
    out = wa.normalize_forecast(raw)
    assert out["days"][0]["precip_mm"] == pytest.approx(0.0)
    assert isinstance(out["days"][0]["precip_mm"], float)


# ----------------------------
# EMAIL (SMTP mocked)
# ----------------------------

def test_send_email_does_nothing_when_no_rain(monkeypatch):
    called = {"smtp": 0}

    class DummySMTP:
        def __init__(self, *a, **k):
            called["smtp"] += 1
        def __enter__(self): return self
        def __exit__(self, *exc): pass
        def starttls(self): pass
        def login(self, user=None, password=None): pass
        def sendmail(self, from_addr=None, to_addrs=None, msg=None): pass

    monkeypatch.setattr(wa.smtplib, "SMTP", DummySMTP)

    wa.send_favorite_cities_rain_alert("x@test.com", rainy_cities=[])
    assert called["smtp"] == 0, "Nie powinno odpalać SMTP, gdy lista miast jest pusta"


def test_send_email_calls_smtp_when_rain(monkeypatch):
    sent = {"sendmail": 0}

    class DummySMTP:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *exc): pass
        def starttls(self): pass
        def login(self, user=None, password=None): pass
        def sendmail(self, from_addr=None, to_addrs=None, msg=None):
            sent["sendmail"] += 1
            assert to_addrs == "x@test.com"
            assert "Alert pogodowy" in msg  # subject jest w treści MIME

    monkeypatch.setattr(wa.smtplib, "SMTP", DummySMTP)
    monkeypatch.setattr(wa, "my_email", "from@test.com")
    monkeypatch.setattr(wa, "password", "pass")

    wa.send_favorite_cities_rain_alert("x@test.com", rainy_cities=["Kraków", "Gdańsk"])
    assert sent["sendmail"] == 1
