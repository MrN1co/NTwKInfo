# tests/integration/test_weather_test_email_endpoint.py
import modules.weather_app as wa


def test_test_email_endpoint_sends_alert_when_rain(client, monkeypatch):
    # symulacja zalogowania
    with client.session_transaction() as sess:
        sess["user_id"] = 1

    # mock user
    class DummyUser:
        email = "u@test.com"

    monkeypatch.setattr(
        wa.User,
        "query",
        type("Q", (), {"get": staticmethod(lambda _id: DummyUser())})()
    )

    # mock favorites
    class DummyFav:
        city = "Kraków"
        lat = 50.0
        lon = 19.0

    monkeypatch.setattr(wa.Favorite, "get_for_user", staticmethod(lambda user_id: [DummyFav()]))

    # mock prognozy -> opady
    monkeypatch.setattr(wa, "fetch_daily_forecast", lambda *a, **k: {"dummy": True})
    monkeypatch.setattr(wa, "normalize_forecast", lambda raw: {"days": [{"precip_mm": 1.0}]})

    # mock wysyłki maila
    called = {"sent": 0, "to": None, "rainy": None, "cold": None, "snowy": None}

    def fake_send_email(to_email, rainy_cities, cold_cities, snowy_cities):
        called["sent"] += 1
        called["to"] = to_email
        called["rainy"] = rainy_cities
        called["cold"] = cold_cities
        called["snowy"] = snowy_cities

    monkeypatch.setattr(wa, "send_favorite_cities_weather_alert", fake_send_email)

    r = client.get("/weather/api/test-email")
    assert r.status_code == 200
    data = r.get_json()
    assert data["success"] is True
    assert called["sent"] == 1
    assert called["to"] == "u@test.com"
    assert "Kraków" in called["rainy"]


def test_test_email_endpoint_returns_401_when_not_logged_in(client):
    r = client.get("/weather/api/test-email")
    assert r.status_code == 401
    assert r.is_json
