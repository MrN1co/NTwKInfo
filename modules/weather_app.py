# weather_app.py
import os
import io
from datetime import datetime, timezone, timedelta

import requests
import matplotlib
matplotlib.use("Agg")  # backend bez GUI
import matplotlib.pyplot as plt
import numpy as np

from flask import Blueprint, request, jsonify, render_template, send_file, abort

weather_bp = Blueprint('weather', __name__)

# --- ENDPOINTY OPENWEATHER ---

# 7-dniowa prognoza dzienna (dla kafelków)
DAILY_URL = "https://api.openweathermap.org/data/2.5/forecast/daily"
# 5-dniowa prognoza co 3 godziny (dla wykresu 24h)
HOURLY_URL = "https://api.openweathermap.org/data/2.5/forecast"
# geokodowanie nazw miast
GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"

# DOMYŚLNA LOKALIZACJA – KRAKÓW
DEFAULT_LAT = 50.0647
DEFAULT_LON = 19.9450

def get_api_key(): # nie działa pobieranie api key z .env więc trzeba wstawić na sztywno
    """Pobierz API key dynamicznie z zmiennych środowiskowych"""
    api_key = '3c4d926e6a63030571954b43415a7367' #os.getenv("OPENWEATHER_APPID")
    if not api_key:
        raise RuntimeError("Ustaw OPENWEATHER_APPID w pliku .env")
    print("API Key:", api_key)
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
    resp = requests.get(DAILY_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


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
    resp = requests.get(HOURLY_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def get_hourly_window(lat: float, lon: float, day_offset: int = 0):
    """
    Zwraca listę punktów co 3h z zakresu:
    - day_offset=0 (dziś): od bieżącej godziny do jutro (~24-36h)
    - day_offset=1+ (inne dni): od północy (00:00) danego dnia do północy następnego
    Każdy punkt: { "dt": datetime, "temp": float, "precip_mm": float }
    """
    raw = fetch_hourly_forecast(lat, lon, units="metric")
    now_utc = datetime.now(timezone.utc)

    if day_offset == 0:
        # Dziś: od teraz do jutra rano (dłuższy zakres czasu na wykresie)
        start = now_utc
        end = now_utc + timedelta(days=1, hours=6)  # ~30h
    else:
        # Inne dni: od północy danego dnia do północy następnego
        today_utc = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        start = today_utc + timedelta(days=day_offset)
        end = start + timedelta(days=1)

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
    # templates/main/weather_index.html
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
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.HTTPError as e:
        return jsonify({"error": "Błąd geokodowania", "details": str(e)}), 502
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



