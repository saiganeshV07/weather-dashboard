"""
Weather service module — production-grade OpenWeatherMap API integration.
Handles current weather, 5-day forecast, air quality, and reverse geocoding.
Provides realistic mock data fallback when no API key is configured.
"""
import os
import math
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple, Optional
import requests
from dotenv import load_dotenv

# Always load .env from the directory this file is in
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_BASE_DIR, ".env"), override=True)

BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL  = "https://api.openweathermap.org/geo/1.0"

# Session-level requests session for connection pooling
_session = requests.Session()
_session.headers.update({"User-Agent": "WeatherDashboard/1.0"})

# ── Preset city seed data for mock generator ──────────────────────────────────
CITY_SEEDS: Dict[str, Dict[str, Any]] = {
    "london":        {"name": "London",        "country": "GB", "lat":  51.5074, "lon":  -0.1278, "base_c": 15, "cond": "Clouds",       "desc": "Overcast Clouds",        "icon": "04d"},
    "new york":      {"name": "New York",       "country": "US", "lat":  40.7128, "lon": -74.0060, "base_c": 22, "cond": "Clear",        "desc": "Clear Sky",              "icon": "01d"},
    "tokyo":         {"name": "Tokyo",          "country": "JP", "lat":  35.6762, "lon": 139.6503, "base_c": 24, "cond": "Rain",         "desc": "Light Rain",             "icon": "10d"},
    "paris":         {"name": "Paris",          "country": "FR", "lat":  48.8566, "lon":   2.3522, "base_c": 18, "cond": "Clouds",       "desc": "Broken Clouds",          "icon": "04d"},
    "hyderabad":     {"name": "Hyderabad",      "country": "IN", "lat":  17.3850, "lon":  78.4867, "base_c": 31, "cond": "Clear",        "desc": "Sunny",                  "icon": "01d"},
    "sydney":        {"name": "Sydney",         "country": "AU", "lat": -33.8688, "lon": 151.2093, "base_c": 18, "cond": "Clouds",       "desc": "Few Clouds",             "icon": "02d"},
    "san francisco": {"name": "San Francisco",  "country": "US", "lat":  37.7749, "lon":-122.4194, "base_c": 17, "cond": "Mist",         "desc": "Foggy Mist",             "icon": "50d"},
    "dubai":         {"name": "Dubai",          "country": "AE", "lat":  25.2048, "lon":  55.2708, "base_c": 37, "cond": "Clear",        "desc": "Hot Clear Sky",          "icon": "01d"},
    "mumbai":        {"name": "Mumbai",         "country": "IN", "lat":  19.0760, "lon":  72.8777, "base_c": 29, "cond": "Rain",         "desc": "Moderate Rain",          "icon": "10d"},
    "singapore":     {"name": "Singapore",      "country": "SG", "lat":   1.3521, "lon": 103.8198, "base_c": 29, "cond": "Thunderstorm", "desc": "Thunderstorm With Rain", "icon": "11d"},
    "beijing":       {"name": "Beijing",        "country": "CN", "lat":  39.9042, "lon": 116.4074, "base_c": 20, "cond": "Haze",         "desc": "Haze",                   "icon": "50d"},
    "moscow":        {"name": "Moscow",         "country": "RU", "lat":  55.7558, "lon":  37.6173, "base_c":  9, "cond": "Clouds",       "desc": "Overcast Clouds",        "icon": "04d"},
    "cairo":         {"name": "Cairo",          "country": "EG", "lat":  30.0444, "lon":  31.2357, "base_c": 32, "cond": "Clear",        "desc": "Clear Sky",              "icon": "01d"},
    "toronto":       {"name": "Toronto",        "country": "CA", "lat":  43.6532, "lon": -79.3832, "base_c": 17, "cond": "Clouds",       "desc": "Partly Cloudy",          "icon": "02d"},
}


def get_default_api_key() -> str:
    """Returns the API key from .env / environment."""
    return os.getenv("OPENWEATHER_API_KEY", "").strip()


def _get(url: str, params: Dict[str, Any], timeout: int = 10) -> requests.Response:
    """Internal helper — DRY HTTP GET with consistent timeout."""
    return _session.get(url, params=params, timeout=timeout)


# ── Current Weather ───────────────────────────────────────────────────────────
def fetch_current_weather(
    city: str,
    api_key: str,
    units: str = "metric"
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fetch real-time current weather for *city*.
    Returns (data_dict, None) on success or (None, error_str) on failure.
    """
    if not api_key:
        return None, "No API key configured. Enter your OpenWeatherMap key in the sidebar."

    try:
        r = _get(BASE_URL + "/weather", {
            "q":     city.strip(),
            "appid": api_key,
            "units": units,
        })
        if r.status_code == 200:
            return r.json(), None
        elif r.status_code == 401:
            return None, "❌ Invalid API Key — please verify your OpenWeatherMap key."
        elif r.status_code == 404:
            return None, f"🔍 City **'{city}'** not found. Check spelling or try a more specific name (e.g. 'Mumbai, IN')."
        elif r.status_code == 429:
            return None, "⏱ API rate limit exceeded. Please wait a minute and try again."
        else:
            body = r.json()
            return None, f"API Error {r.status_code}: {body.get('message', r.text)}"

    except requests.exceptions.ConnectionError:
        return None, "🌐 No internet connection. Check your network and retry."
    except requests.exceptions.Timeout:
        return None, "⏳ Request timed out — the weather server took too long to respond."
    except Exception as e:
        return None, f"Unexpected error: {e}"


# ── 5-Day / 3-Hour Forecast ───────────────────────────────────────────────────
def fetch_weather_forecast(
    city: str,
    api_key: str,
    units: str = "metric"
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fetch 5-day / 3-hour interval forecast for *city*.
    """
    if not api_key:
        return None, "No API key configured."

    try:
        r = _get(BASE_URL + "/forecast", {
            "q":     city.strip(),
            "appid": api_key,
            "units": units,
            "cnt":   40,        # max 5 days × 8 intervals/day
        })
        if r.status_code == 200:
            return r.json(), None
        elif r.status_code == 401:
            return None, "❌ Invalid API Key for forecast endpoint."
        elif r.status_code == 404:
            return None, f"🔍 Forecast for '{city}' not found."
        else:
            body = r.json()
            return None, f"Forecast API Error {r.status_code}: {body.get('message', r.text)}"

    except requests.exceptions.ConnectionError:
        return None, "🌐 No internet connection for forecast fetch."
    except requests.exceptions.Timeout:
        return None, "⏳ Forecast request timed out."
    except Exception as e:
        return None, f"Forecast error: {e}"


# ── Air Quality ───────────────────────────────────────────────────────────────
def fetch_air_quality(
    lat: float,
    lon: float,
    api_key: str
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fetch air pollution / AQI for the given coordinates.
    """
    if not api_key:
        return None, "No API key for AQI."

    try:
        r = _get(BASE_URL + "/air_pollution", {
            "lat":   lat,
            "lon":   lon,
            "appid": api_key,
        }, timeout=8)
        if r.status_code == 200:
            return r.json(), None
        return None, f"AQI Error {r.status_code}"
    except Exception as e:
        return None, str(e)


# ── Geocoding helper ──────────────────────────────────────────────────────────
def geocode_city(city: str, api_key: str) -> Optional[Tuple[float, float, str, str]]:
    """
    Resolve city name → (lat, lon, resolved_name, country).
    Returns None on failure.
    """
    if not api_key:
        return None
    try:
        r = _get(GEO_URL + "/direct", {"q": city, "limit": 1, "appid": api_key}, timeout=6)
        if r.status_code == 200:
            results = r.json()
            if results:
                g = results[0]
                return g["lat"], g["lon"], g["name"], g.get("country", "")
    except Exception:
        pass
    return None


# ── Mock / Demo Data Generator ────────────────────────────────────────────────
def _celsius_to_unit(c: float, units: str) -> float:
    if units == "imperial":
        return round(c * 9 / 5 + 32, 1)
    if units == "standard":
        return round(c + 273.15, 1)
    return round(c, 1)


def generate_mock_weather(
    city: str,
    units: str = "metric"
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Generates realistic synthetic weather data for demo mode.
    Simulates real API response structures exactly.
    """
    key = city.lower().strip()
    seed = CITY_SEEDS.get(key, {
        "name":    city.title(),
        "country": "",
        "lat":     round(random.uniform(-40, 60), 4),
        "lon":     round(random.uniform(-120, 140), 4),
        "base_c":  20.0,
        "cond":    "Clouds",
        "desc":    "Partly Cloudy",
        "icon":    "02d",
    })

    base_c    = seed["base_c"] + random.uniform(-2, 2)
    humidity  = random.randint(45, 85)
    pressure  = random.randint(1008, 1022)
    wind_spd  = round(random.uniform(2, 9), 1)
    wind_deg  = random.randint(0, 359)
    clouds    = random.randint(10, 80)
    now_utc   = datetime.now(timezone.utc)
    ts_now    = int(now_utc.timestamp())

    current = {
        "coord":      {"lat": seed["lat"], "lon": seed["lon"]},
        "weather":    [{"id": 800, "main": seed["cond"], "description": seed["desc"], "icon": seed["icon"]}],
        "main": {
            "temp":       _celsius_to_unit(base_c, units),
            "feels_like": _celsius_to_unit(base_c + random.uniform(-2, 1), units),
            "temp_min":   _celsius_to_unit(base_c - random.uniform(2, 4), units),
            "temp_max":   _celsius_to_unit(base_c + random.uniform(2, 5), units),
            "pressure":   pressure,
            "humidity":   humidity,
            "sea_level":  pressure,
            "grnd_level": pressure - random.randint(2, 10),
        },
        "visibility": random.choice([8000, 9000, 10000, 10000]),
        "wind":       {"speed": wind_spd, "deg": wind_deg, "gust": round(wind_spd * 1.4, 1)},
        "clouds":     {"all": clouds},
        "dt":         ts_now,
        "sys": {
            "country": seed["country"],
            "sunrise": ts_now - 21600,
            "sunset":  ts_now + 21600,
        },
        "timezone": 0,
        "name":     seed["name"],
        "cod":      200,
        "_is_demo": True,
    }

    cond_pool = [
        ("Clear",        "Clear Sky",         "01", 0.02),
        ("Clouds",       "Few Clouds",         "02", 0.10),
        ("Clouds",       "Scattered Clouds",   "03", 0.15),
        ("Clouds",       "Broken Clouds",      "04", 0.20),
        ("Rain",         "Light Rain",         "10", 0.65),
        ("Rain",         "Moderate Rain",      "10", 0.85),
        ("Drizzle",      "Light Drizzle",      "09", 0.50),
        ("Thunderstorm", "Thunderstorm",       "11", 0.90),
    ]

    items = []
    for i in range(40):
        dt_i   = now_utc + timedelta(hours=i * 3)
        hour   = dt_i.hour
        diurnal = 5.0 * math.sin((hour - 8) * math.pi / 12)
        drift   = (i / 40) * random.uniform(-2, 2)
        c_i     = base_c + diurnal + drift + random.uniform(-0.8, 0.8)

        cond    = random.choice(cond_pool)
        icon_sfx = "d" if 6 <= hour <= 19 else "n"

        items.append({
            "dt": int(dt_i.timestamp()),
            "main": {
                "temp":       _celsius_to_unit(c_i, units),
                "feels_like": _celsius_to_unit(c_i + random.uniform(-1.5, 1), units),
                "temp_min":   _celsius_to_unit(c_i - 1.5, units),
                "temp_max":   _celsius_to_unit(c_i + 1.5, units),
                "pressure":   pressure + random.randint(-4, 4),
                "humidity":   max(25, min(95, humidity + int(diurnal * -3) + random.randint(-5, 5))),
                "sea_level":  pressure,
                "grnd_level": pressure - 5,
            },
            "weather": [{"main": cond[0], "description": cond[1], "icon": f"{cond[2]}{icon_sfx}"}],
            "clouds":  {"all": random.randint(10, 90)},
            "wind": {
                "speed": round(max(0.5, wind_spd + random.uniform(-2, 3)), 1),
                "deg":   (wind_deg + random.randint(-30, 30)) % 360,
                "gust":  round(wind_spd * 1.4 + random.uniform(0, 2), 1),
            },
            "visibility": random.choice([8000, 9000, 10000, 10000]),
            "pop":   cond[3],
            "rain":  {"3h": round(random.uniform(0.3, 5.0), 2)} if cond[0] in ("Rain", "Drizzle") else {},
            "dt_txt": dt_i.strftime("%Y-%m-%d %H:%M:%S"),
            "sys": {"pod": "d" if 6 <= hour <= 19 else "n"},
        })

    forecast = {
        "cod": "200",
        "cnt": 40,
        "list": items,
        "city": {
            "name":    seed["name"],
            "country": seed["country"],
            "coord":   {"lat": seed["lat"], "lon": seed["lon"]},
            "timezone": 0,
            "sunrise": ts_now - 21600,
            "sunset":  ts_now + 21600,
        },
        "_is_demo": True,
    }

    aqi_val = random.choice([1, 1, 2, 2, 3, 3, 4])
    aqi = {
        "list": [{
            "main": {"aqi": aqi_val},
            "components": {
                "co":    round(random.uniform(200, 600), 1),
                "no":    round(random.uniform(0.1, 5.0), 2),
                "no2":   round(random.uniform(10, 50), 1),
                "o3":    round(random.uniform(30, 100), 1),
                "so2":   round(random.uniform(2, 20), 1),
                "pm2_5": round(random.uniform(5, 60), 1),
                "pm10":  round(random.uniform(10, 90), 1),
                "nh3":   round(random.uniform(0.1, 3.0), 2),
            },
            "dt": ts_now,
        }],
    }

    return current, forecast, aqi
