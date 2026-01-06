# weather_app.py
import os
import io
from datetime import datetime, timezone, timedelta
from flask import jsonify


import requests
import matplotlib
matplotlib.use("Agg")  # backend bez GUI
import matplotlib.pyplot as plt
import numpy as np

import smtplib
from email.mime.text import MIMEText

from flask import Blueprint, request, jsonify, render_template, send_file, abort, session
from dotenv import load_dotenv
from modules.database import Favorite
from modules.auth import api_login_required
import time
from threading import Lock
import logging
from modules.database import User


load_dotenv()

logger = logging.getLogger(__name__)

my_email = os.environ.get("MY_EMAIL")
password = os.environ.get("EMAIL_PASSW")

weather_bp = Blueprint('weather', __name__)

# Prosty lokalny cache dla wyników zapytań do OpenWeather
# Klucz: string, wartość: (timestamp_seconds, data)
# in-memory cache for OpenWeather responses
_OW_CACHE = {}
# lock to protect cache in multi-threaded environments
_OW_CACHE_LOCK = Lock()
# TTL cache w sekundach
_OW_CACHE_TTL = 60  # 1 minuta

def _cache_get(key):
    with _OW_CACHE_LOCK:
        rec = _OW_CACHE.get(key)
        if not rec:
            return None
        ts, data = rec
        if time.time() - ts > _OW_CACHE_TTL:
            try:
                del _OW_CACHE[key]
            except KeyError:
                pass
            return None
        return data

def _cache_set(key, data):
    with _OW_CACHE_LOCK:
        _OW_CACHE[key] = (time.time(), data)


# ======================= WYSYŁANIE MAILI =======================
def send_favorite_cities_rain_alert(user_email, rainy_cities):
    """
    Wysyła e-mail z listą ulubionych miast, w których pada deszcz.
    rainy_cities: lista miast (stringów) w których pada deszcz.
    """
    if not rainy_cities:
        return  # Nie wysyłaj maila jeśli nie ma opadów w żadnym mieście
    
    cities_list = "\n".join([f"• {city}" for city in rainy_cities])
    message_text = f"""Cześć!

Dziś prognozowane są opady w Twoich ulubionych miastach:

{cities_list}

Pamiętaj, aby przygotować się i zabrać parasol!

Pozdrawiamy,
NTwKInfo
"""
    msg = MIMEText(message_text, "plain", "utf-8")
    msg['Subject'] = "Alert pogodowy"
    msg['From'] = my_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email, to_addrs=user_email, msg=msg.as_string())
            print(f"✓ Mail wysłany do {user_email} z alertem o opadach w {len(rainy_cities)} miastach.")
    except Exception as e:
        print(f"✗ Błąd wysyłania maila do {user_email}: {e}")


# --- ENDPOINTY OPENWEATHER ---

# 7-dniowa prognoza dzienna (dla kafelków)
DAILY_URL = "https://api.openweathermap.org/data/2.5/forecast/daily"
# 5-dniowa prognoza co 3 godziny (dla wykresu 24h)
HOURLY_URL = "https://api.openweathermap.org/data/2.5/forecast"
# geokodowanie nazw miast
GEOCODE_URL = "https://api.openweathermap.org/geo/1.0/direct"

# DOMYŚLNA LOKALIZACJA – KRAKÓW
DEFAULT_LAT = 50.0647
DEFAULT_LON = 19.9450

def get_api_key(): 
    """Pobierz API key dynamicznie z zmiennych środowiskowych"""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("Ustaw OPENWEATHER_API_KEY w pliku .env")
    return api_key


# ======================= FUNKCJE DO PROGNOZY 7-DNIOWEJ =======================

def fetch_daily_forecast(lat: float, lon: float, cnt: int = 7, units: str = "metric") -> dict:
    params = {
        "lat": lat,
        "lon": lon,
        "appid": get_api_key(),
        "cnt": cnt,
        "units": units,
        "lang": "pl",
    }
    # Spróbuj pobrać z cache
    key = f"daily:{lat}:{lon}:{cnt}:{units}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(DAILY_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        _cache_set(key, data)
        return data
    except requests.HTTPError as e:
        body = None
        try:
            body = resp.text
        except Exception:
            body = None
        raise requests.HTTPError(f"HTTP {resp.status_code} from OpenWeather: {body}") from e
    except requests.RequestException as e:
        raise


def normalize_forecast(raw: dict) -> dict:
    """Normalizacja danych 7-dniowych na prosty format dla frontu."""
    city = raw.get("city", {})
    city_name = city.get("name")
    coord = city.get("coord", {})
    lat = coord.get("lat")
    lon = coord.get("lon")
    # timezone offset in seconds (if API provides it) to align dates to city local time
    tz_offset = city.get("timezone") or 0

    days = []
    for item in raw.get("list", []):
        dt = item.get("dt")
        if dt:
            # API dt is a UNIX timestamp (UTC). Add city timezone offset to get local date.
            date_dt = datetime.utcfromtimestamp(dt) + timedelta(seconds=tz_offset)
            date = date_dt.date().isoformat()
        else:
            date = None
        temp = item.get("temp", {})
        weather_list = item.get("weather") or [{}]
        weather = weather_list[0]

        days.append({
            "timestamp": dt,
            "date": date,
            "t_min": temp.get("min"),
            "t_max": temp.get("max"),
            "t_day": temp.get("day"),
            "pressure": item.get("pressure"),
            "precip_mm": float(item.get("rain", 0.0)),
            "icon": weather.get("icon"),
            "description": weather.get("description"),
        })

    return {
        "city": city_name,
        "lat": lat,
        "lon": lon,
        "days": days,
    }


# ======================= FUNKCJE DO WYKRESU 24H =======================

def fetch_hourly_forecast(lat: float, lon: float, units: str = "metric") -> dict:
    """
    5-dniowa prognoza co 3h.
    Zwracamy surowy JSON z /data/2.5/forecast
    """
    params = {
        "lat": lat,
        "lon": lon,
        "appid": get_api_key(),
        "units": units,
    }
    # Cache results briefly to avoid repeated external calls when user refreshuje
    key = f"hourly:{lat}:{lon}:{units}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    try:
        resp = requests.get(HOURLY_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        _cache_set(key, data)
        return data
    except requests.HTTPError as e:
        body = None
        try:
            body = resp.text
        except Exception:
            body = None
        raise requests.HTTPError(f"HTTP {resp.status_code} from OpenWeather: {body}") from e
    except requests.RequestException:
        raise


def get_hourly_window(lat: float, lon: float, day_offset: int = 0):
    """
    Zwraca listę punktów co 3h z zakresu:
    - day_offset=0 (dziś): od bieżącej godziny do jutro (~24-36h)
    - day_offset=1+ (inne dni): od północy (00:00) danego dnia do północy następnego
    Każdy punkt: { "dt": datetime, "temp": float, "precip_mm": float }
    """
    raw = fetch_hourly_forecast(lat, lon, units="metric")

    # Use city's timezone (offset in seconds) to compute local start/end windows
    tz_offset = raw.get("city", {}).get("timezone", 0)
    target_tz = timezone(timedelta(seconds=tz_offset))

    # current time in city's local timezone
    now_local = datetime.now(timezone.utc).astimezone(target_tz)

    if day_offset == 0:
        # Today: from now (local) to ~30h ahead (local)
        start_local = now_local
        end_local = now_local + timedelta(days=1, hours=6)  # ~30h
    else:
        # Other days: from local midnight of that day to next local midnight
        today_local_midnight = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        start_local = today_local_midnight + timedelta(days=day_offset)
        end_local = start_local + timedelta(days=1)

    # convert local window back to UTC for comparison with API timestamps
    start = start_local.astimezone(timezone.utc)
    end = end_local.astimezone(timezone.utc)

    points = []
    for item in raw.get("list", []):
        ts = item.get("dt")
        if ts is None:
            continue
        t_utc = datetime.fromtimestamp(ts, tz=timezone.utc)
        if not (start <= t_utc < end):
            continue

        main = item.get("main", {})
        temp = main.get("temp")

        # opady: deszcz + śnieg (jeśli są)
        rain = 0.0
        snow = 0.0
        if isinstance(item.get("rain"), dict):
            rain = float(item["rain"].get("3h", 0.0))
        if isinstance(item.get("snow"), dict):
            snow = float(item["snow"].get("3h", 0.0))
        precip = rain + snow

        points.append({
            "dt": t_utc,
            "temp": temp,
            "precip_mm": precip,
        })

    points.sort(key=lambda p: p["dt"])
    return points


# ======================= ROUTY FLASKA =======================

@weather_bp.route("/pogoda")
def weather_index():
    # Show a different template for authenticated users (contains favorites).
    # Session-based auth: modules.auth sets `session['user_id']`
    if session.get("user_id"):
        return render_template("weather/weather-login.html")
    # Default for anonymous users
    return render_template("weather/weather.html")


# --------- API: prognoza 7-dniowa (dla kafelków) ---------

@weather_bp.get("/api/forecast")
def api_forecast():
    """GET /api/forecast?lat=...&lon=... – jeśli brak, bierze domyślny Kraków."""
    lat_param = request.args.get("lat")
    lon_param = request.args.get("lon")
    label = request.args.get("label")

    try:
        lat = float(lat_param) if lat_param is not None else DEFAULT_LAT
        lon = float(lon_param) if lon_param is not None else DEFAULT_LON
    except (TypeError, ValueError):
        return jsonify({"error": "Błędne lat/lon"}), 400

    try:
        raw = fetch_daily_forecast(lat, lon, cnt=7, units="metric")
        data = normalize_forecast(raw)
        if label:
            data["city"] = label 
        else:
            # jeśli to domyślna lokalizacja – wymuś "Kraków"
            if lat == DEFAULT_LAT and lon == DEFAULT_LON:
                data["city"] = "Kraków"
        
        # Sprawdzenie opadów na informacyjnym poziomie
        if data["days"] and data["days"][0].get("precip_mm", 0) > 0:
            print("Dziś zapowiadane są opady.")
        else:
            print("Dziś nie ma opadów.")

        return jsonify(data)
    except requests.HTTPError as e:
        return jsonify({"error": "Błąd OpenWeather", "details": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Błąd backendu", "details": str(e)}), 500


# --------- API: geokodowanie ---------

@weather_bp.get("/api/geocode")
def api_geocode():
    """GET /api/geocode?q=Kraków – wyszukiwanie miasta."""
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "Brak parametru q"}), 400

    params = {"q": q, "appid": get_api_key(), "limit": 5}
    try:
        resp = requests.get(GEOCODE_URL, params=params, timeout=10)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            # include response body if available for easier debugging
            body = None
            try:
                body = resp.text
            except Exception:
                body = None
            return jsonify({"error": "Błąd geokodowania", "status": resp.status_code, "details": str(e), "response": body}), 502
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({"error": "Błąd sieci podczas geokodowania", "details": str(e)}), 502
    except Exception as e:
        return jsonify({"error": "Błąd backendu", "details": str(e)}), 500


# --------- API: ulubione miasta (GET/POST/DELETE) ---------
@weather_bp.get("/api/favorites")
@api_login_required
def api_get_favorites():
    """Zwraca listę ulubionych miast zalogowanego użytkownika (sesja)."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not_authenticated"}), 401
    favs = Favorite.get_for_user(user_id)
    out = []
    for f in favs:
        out.append({"id": f.id, "city": f.city, "lat": f.lat, "lon": f.lon})
    return jsonify({"favorites": out})


@weather_bp.post("/api/favorites")
@api_login_required
def api_add_favorite():
    """Dodaj ulubione miasto dla zalogowanego użytkownika. Body JSON: { city, lat, lon }"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not_authenticated"}), 401
    body = request.get_json() or {}
    city = body.get("city")
    lat = body.get("lat")
    lon = body.get("lon")
    if not city:
        return jsonify({"error": "city required"}), 400

    # unikaj duplikatów
    exists = Favorite.query.filter_by(user_id=user_id, city=city).first()
    if exists:
        return jsonify({"error": "exists", "favorite": {"id": exists.id}}), 409

    fav = Favorite.create(user_id=user_id, city=city, lat=lat, lon=lon)
    return jsonify({"id": fav.id, "city": fav.city, "lat": fav.lat, "lon": fav.lon}), 201


@weather_bp.delete("/api/favorites")
@api_login_required
def api_delete_favorite():
    """Usuń ulubione miasto. Body JSON: { id } lub { city }"""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not_authenticated"}), 401
    body = request.get_json() or {}
    fav_id = body.get("id")
    city = body.get("city")
    fav = None
    if fav_id:
        fav = Favorite.query.filter_by(id=fav_id, user_id=user_id).first()
    elif city:
        fav = Favorite.query.filter_by(user_id=user_id, city=city).first()
    else:
        return jsonify({"error": "id or city required"}), 400

    if not fav:
        return jsonify({"error": "not found"}), 404
    fav.delete()
    return jsonify({"ok": True})


# --------- API: godzinowa prognoza (JSON) ---------

@weather_bp.get("/api/hourly")
def api_hourly():
    """GET /api/hourly?lat=...&lon=...&day=0  -> zwraca listę punktów godzinowych dla wykresu

    Każdy punkt: { dt: ISO-string (lokalny czas miasta), temp: float, precip_mm: float }
    """
    lat_param = request.args.get("lat")
    lon_param = request.args.get("lon")
    day_param = request.args.get("day", default="0")

    try:
        lat = float(lat_param) if lat_param is not None else DEFAULT_LAT
        lon = float(lon_param) if lon_param is not None else DEFAULT_LON
    except (TypeError, ValueError):
        return jsonify({"error": "Błędne lat/lon"}), 400

    try:
        day_offset = int(day_param)
    except ValueError:
        day_offset = 0

    if day_offset < 0:
        day_offset = 0
    if day_offset > 4:
        day_offset = 4

    try:
        # zwróć punkty godzinowe (datetimes w UTC tz-aware)
        points = get_hourly_window(lat, lon, day_offset=day_offset)

        # Dla poprawnego wyświetlania czasu skonwertuj do strefy miasta
        raw = fetch_hourly_forecast(lat, lon, units="metric")
        tz_offset = raw.get("city", {}).get("timezone", 0)
        target_tz = timezone(timedelta(seconds=tz_offset))

        out = []
        for p in points:
            dt_local = p["dt"].astimezone(target_tz)
            out.append({
                "dt": dt_local.isoformat(),
                "temp": p.get("temp"),
                "precip_mm": p.get("precip_mm"),
            })

        return jsonify({"points": out, "tz_offset": tz_offset})
    except requests.HTTPError as e:
        body = None
        try:
            body = str(e)
        except Exception:
            body = None
        return jsonify({"error": "Błąd OpenWeather", "details": body}), 502
    except Exception as e:
        return jsonify({"error": "Błąd backendu", "details": str(e)}), 500


# --------- Wykres 24h z temperaturą i opadami ---------

@weather_bp.route("/plot.png")
def plot_png():
    """
    /plot.png?lat=...&lon=...&day=0
    day = 0 -> najbliższe 24h od teraz
    day = 1 -> kolejne 24h itd. (max 4)
    """
    lat_param = request.args.get("lat")
    lon_param = request.args.get("lon")
    day_param = request.args.get("day", default="0")

    try:
        lat = float(lat_param) if lat_param is not None else DEFAULT_LAT
        lon = float(lon_param) if lon_param is not None else DEFAULT_LON
    except (TypeError, ValueError):
        abort(400)

    try:
        day_offset = int(day_param)
    except ValueError:
        day_offset = 0

    if day_offset < 0:
        day_offset = 0
    if day_offset > 4:  # mamy ~5 dni /forecast
        day_offset = 4

    try:
        points = get_hourly_window(lat, lon, day_offset=day_offset)
    except Exception:
        abort(500)

    if not points:
        abort(404)

    raw = fetch_hourly_forecast(lat, lon, units="metric")
    tz_offset = raw.get("city", {}).get("timezone", 0)  # sekundy od UTC
    target_tz = timezone(timedelta(seconds=tz_offset))

    labels = []
    temps = []
    precip = []

    for p in points:
    # p["dt"] jest datetime w UTC
       dt_local = p["dt"].astimezone(target_tz)
       labels.append(dt_local.strftime("%H:%M"))
       temps.append(p["temp"])
       precip.append(p["precip_mm"])

    # --- STYL WYKRESU (bardziej estetyczny) ---
    fig, ax1 = plt.subplots(figsize=(8.0, 3.2), dpi=160)

    # lekkie ustawienia czcionki
    plt.rcParams.update({"font.family": "sans-serif", "font.size": 10})

    # tło przezroczyste i wyłącz górne/prawe spiny
    fig.patch.set_alpha(0)
    ax1.set_facecolor("none")
    for spine in ["top", "right"]:
        ax1.spines[spine].set_visible(False)

    # Przygotuj dane X jako indeksy (ułatwia interpolację)
    x = np.arange(len(temps))
    temps_arr = np.array([np.nan if t is None else t for t in temps], dtype=float)
    # interpoluj ewentualne braki
    if np.isnan(temps_arr).any():
        nans = np.isnan(temps_arr)
        good = ~nans
        if good.sum() >= 2:
            temps_arr[nans] = np.interp(x[nans], x[good], temps_arr[good])
        else:
            temps_arr[nans] = 0.0

    # wygładź krzywą liniową (interpolacja) dla estetyki
    xp = np.linspace(x.min(), x.max(), max(200, len(x) * 50))
    temps_smooth = np.interp(xp, x, temps_arr)

    # Kolory
    temp_color = "#2B7A78"  # teal
    precip_color = "#8AA24A"  # łagodny oliwkowy

    # narysuj gładką linię temperatury i znaczniki punktów (bez wypełnienia)
    ax1.plot(xp, temps_smooth, color=temp_color, linewidth=2.2, zorder=3)
    ax1.scatter(x, temps_arr, s=26, color=temp_color, edgecolor="white", zorder=4)

    # Oś X: etykiety godzin, pokazuj co drugi jeśli jest ich dużo
    ax1.set_xticks(x)
    if len(labels) > 8:
        display_labels = [lbl if i % 2 == 0 else "" for i, lbl in enumerate(labels)]
    else:
        display_labels = labels
    ax1.set_xticklabels(display_labels, rotation=0)

    ax1.set_ylabel("Temperatura [°C]", color=temp_color)
    ax1.tick_params(axis="y", labelcolor=temp_color)
    ax1.grid(axis="y", linestyle="--", linewidth=0.6, color="#E9E9E9")

    # opady jako cienkie słupki na tle, poniżej linii
    ax2 = ax1.twinx()
    precip_vals = [0.0 if p is None else p for p in precip]
    ax2.bar(x, precip_vals, color=precip_color, alpha=0.65, width=0.5, zorder=1)
    ax2.set_ylim(0, max(max(precip_vals) * 1.6, 1.0))
    ax2.set_ylabel("Opady [mm]", color=precip_color)
    ax2.tick_params(axis="y", labelcolor=precip_color)

    fig.tight_layout(pad=0.6)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", transparent=True)
    plt.close(fig)
    buf.seek(0)

    return send_file(buf, mimetype="image/png")


# --------- TEST ENDPOINT: wysłanie maila testowego ---------

@weather_bp.get("/api/test-email")
def test_email():
    """
    Test endpoint: wysyła testowy email z opadami w ulubionych miastach.
    GET /weather/api/test-email

    Zwraca:
    - 401 jeśli brak logowania (bez redirectu)
    - 404 jeśli user nie istnieje
    - 400 jeśli brak ulubionych
    - 200 jeśli wysłano maila lub jeśli nie ma opadów
    - 502 jeśli błąd OpenWeather
    - 500 jeśli błąd wysyłki maila lub inny błąd
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "not_authenticated"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "user_not_found"}), 404

    favs = Favorite.get_for_user(user_id) or []
    if not favs:
        return jsonify({
            "error": "no_favorites",
            "message": "Dodaj ulubione miasta aby testować"
        }), 400

    rainy_cities = []

    for fav in favs:
        lat = fav.lat if fav.lat is not None else DEFAULT_LAT
        lon = fav.lon if fav.lon is not None else DEFAULT_LON

        try:
            raw = fetch_daily_forecast(lat, lon, cnt=7, units="metric")
            data = normalize_forecast(raw)
        except requests.HTTPError as e:
            # dla testów i poprawnego API lepiej jasno powiedzieć "problem z upstreamem"
            return jsonify({"error": "openweather_error", "details": str(e)}), 502
        except Exception as e:
            return jsonify({"error": "backend_error", "details": str(e)}), 500

        if data.get("days") and float(data["days"][0].get("precip_mm", 0.0)) > 0.0:
            rainy_cities.append(fav.city)

    # Mail tylko jeśli są opady
    if rainy_cities:
        try:
            send_favorite_cities_rain_alert(user.email, rainy_cities)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": "email_send_failed",
                "details": str(e),
                "message": "Błąd wysyłania emaila"
            }), 500

        return jsonify({
            "success": True,
            "message": f"Email wysłany do {user.email}",
            "rainy_cities": rainy_cities
        }), 200

    return jsonify({
        "success": False,
        "message": "Brak opadów w żadnym z ulubionych miast",
        "checked_cities": [f.city for f in favs]
    }), 200
