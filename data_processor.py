"""
Data processing module — Pandas-powered transformation of raw OpenWeatherMap payloads
into analysis-ready DataFrames, daily summaries, and structured KPI dictionaries.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import math
import pandas as pd
import numpy as np


# ── Utility helpers ───────────────────────────────────────────────────────────

def deg_to_compass(deg: float) -> str:
    """Convert 0–360° wind direction to 16-point cardinal string."""
    idx = int((float(deg) / 22.5) + 0.5) % 16
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    return directions[idx]


def get_uv_label(uvi: float) -> Dict[str, str]:
    if uvi < 3:
        return {"label": "Low", "color": "#10b981"}
    elif uvi < 6:
        return {"label": "Moderate", "color": "#eab308"}
    elif uvi < 8:
        return {"label": "High", "color": "#f97316"}
    elif uvi < 11:
        return {"label": "Very High", "color": "#ef4444"}
    return {"label": "Extreme", "color": "#a855f7"}


def get_aqi_label(aqi: int) -> Dict[str, str]:
    """Map OpenWeatherMap AQI (1–5) to label, color, badge, and description."""
    mapping = {
        1: {"label": "Good",      "color": "#10b981", "badge": "🟢 Good",      "desc": "Air quality is satisfactory — minimal risk."},
        2: {"label": "Fair",      "color": "#84cc16", "badge": "🟡 Fair",      "desc": "Acceptable air quality; sensitive groups may be mildly affected."},
        3: {"label": "Moderate",  "color": "#eab308", "badge": "🟠 Moderate",  "desc": "Sensitive individuals may experience health effects."},
        4: {"label": "Poor",      "color": "#f97316", "badge": "🔴 Poor",      "desc": "Everyone may begin to experience health effects."},
        5: {"label": "Very Poor", "color": "#ef4444", "badge": "🟣 Very Poor", "desc": "Health alert: serious effects for the entire population."},
    }
    return mapping.get(aqi, {"label": "Unknown", "color": "#94a3b8", "badge": "⚪ Unknown", "desc": "No AQI data available."})


# ── Forecast DataFrame builder ────────────────────────────────────────────────

def process_forecast_dataframe(raw_forecast: Dict[str, Any]) -> pd.DataFrame:
    """
    Transform the raw /forecast JSON into a clean, typed Pandas DataFrame.
    One row per 3-hour interval (up to 40 rows = 5 days).
    All timestamps are expressed in **city local time** using the API-supplied timezone offset.
    """
    if not raw_forecast or not raw_forecast.get("list"):
        return pd.DataFrame()

    tz_offset   = raw_forecast.get("city", {}).get("timezone", 0)   # seconds east of UTC
    sunrise_ts  = raw_forecast.get("city", {}).get("sunrise")
    sunset_ts   = raw_forecast.get("city", {}).get("sunset")

    records = []
    for item in raw_forecast["list"]:
        utc_ts    = item.get("dt", 0)
        local_ts  = utc_ts + tz_offset
        local_dt  = datetime.fromtimestamp(local_ts, tz=timezone.utc)

        wx    = item.get("weather", [{}])[0]
        main  = item.get("main", {})
        wind  = item.get("wind", {})
        rain  = item.get("rain", {})
        snow  = item.get("snow", {})

        rain_3h   = rain.get("3h", 0.0) if isinstance(rain, dict) else 0.0
        snow_3h   = snow.get("3h", 0.0) if isinstance(snow, dict) else 0.0
        precip_mm = round(rain_3h + snow_3h, 2)
        pop_pct   = round(item.get("pop", 0.0) * 100, 1)

        wind_deg  = wind.get("deg", 0)

        records.append({
            "timestamp":     local_dt,
            "date":          local_dt.strftime("%Y-%m-%d"),
            "day_name":      local_dt.strftime("%a, %b %d"),
            "time_str":      local_dt.strftime("%H:%M"),
            "temp":          round(main.get("temp", np.nan), 1),
            "feels_like":    round(main.get("feels_like", np.nan), 1),
            "temp_min":      round(main.get("temp_min", np.nan), 1),
            "temp_max":      round(main.get("temp_max", np.nan), 1),
            "humidity":      main.get("humidity", 0),
            "pressure":      main.get("pressure", 1013),
            "sea_level":     main.get("sea_level", main.get("pressure", 1013)),
            "grnd_level":    main.get("grnd_level", main.get("pressure", 1013)),
            "weather_main":  wx.get("main", "Clear"),
            "weather_desc":  wx.get("description", "").title(),
            "icon":          wx.get("icon", "01d"),
            "wind_speed":    round(wind.get("speed", 0.0), 1),
            "wind_deg":      wind_deg,
            "wind_dir":      deg_to_compass(wind_deg),
            "wind_gust":     round(wind.get("gust", wind.get("speed", 0.0)), 1),
            "cloudiness":    item.get("clouds", {}).get("all", 0),
            "pop_pct":       pop_pct,
            "precip_mm":     precip_mm,
            "visibility_km": round(item.get("visibility", 10000) / 1000, 1),
        })

    df = pd.DataFrame(records)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)
    return df


# ── Daily summary aggregation ─────────────────────────────────────────────────

def calculate_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate 3-hour intervals into per-day summaries.
    Returns one row per calendar date (city local time).
    """
    if df.empty:
        return pd.DataFrame()

    def mode_first(s: pd.Series):
        m = s.mode()
        return m.iloc[0] if not m.empty else s.iloc[0]

    agg = df.groupby("date").agg(
        day_name      = ("day_name",     "first"),
        temp_min      = ("temp_min",     "min"),
        temp_max      = ("temp_max",     "max"),
        temp_avg      = ("temp",         "mean"),
        humidity_avg  = ("humidity",     "mean"),
        pressure_avg  = ("pressure",     "mean"),
        wind_max      = ("wind_speed",   "max"),
        weather_main  = ("weather_main", mode_first),
        weather_desc  = ("weather_desc", mode_first),
        icon          = ("icon",         mode_first),
        pop_max       = ("pop_pct",      "max"),
        total_precip  = ("precip_mm",    "sum"),
        cloudiness    = ("cloudiness",   "mean"),
    ).reset_index()

    for col in ("temp_min", "temp_max", "temp_avg", "wind_max"):
        agg[col] = agg[col].round(1)
    agg["humidity_avg"]  = agg["humidity_avg"].round(0).astype(int)
    agg["pressure_avg"]  = agg["pressure_avg"].round(0).astype(int)
    agg["pop_max"]       = agg["pop_max"].round(0).astype(int)
    agg["total_precip"]  = agg["total_precip"].round(1)
    agg["cloudiness"]    = agg["cloudiness"].round(0).astype(int)

    return agg


# ── Current weather KPI extractor ─────────────────────────────────────────────

def extract_current_kpis(current: Dict[str, Any], unit_symbol: str) -> Dict[str, Any]:
    """
    Extract all display-ready KPIs from the /weather JSON response.
    Sunrise & sunset are converted to city local time using the API timezone offset.
    """
    main   = current.get("main", {})
    wind   = current.get("wind", {})
    wx     = current.get("weather", [{}])[0]
    sys    = current.get("sys", {})
    coord  = current.get("coord", {})
    tz_off = current.get("timezone", 0)      # seconds east of UTC

    def _ts_to_local(ts: Optional[int]) -> str:
        if not ts:
            return "N/A"
        dt = datetime.fromtimestamp(ts + tz_off, tz=timezone.utc)
        return dt.strftime("%H:%M")

    temp_val    = main.get("temp", 0.0)
    feels_val   = main.get("feels_like", 0.0)
    temp_diff   = round(feels_val - temp_val, 1)
    diff_str    = (f"+{temp_diff}" if temp_diff > 0 else str(temp_diff)) + unit_symbol

    wind_deg    = wind.get("deg", 0)
    vis_m       = current.get("visibility", 10000)

    # Compute comfort index (0–100): low humidity + moderate temp → higher comfort
    humidity    = main.get("humidity", 50)
    comfort_raw = max(0, 100 - abs(temp_val - 22) * 3 - max(0, humidity - 60) * 0.8)
    comfort_idx = round(min(100, comfort_raw))

    return {
        "city_name":    current.get("name", "Unknown"),
        "country":      sys.get("country", ""),
        "lat":          coord.get("lat", 0.0),
        "lon":          coord.get("lon", 0.0),
        "temp":         round(temp_val, 1),
        "feels_like":   round(feels_val, 1),
        "temp_diff":    diff_str,
        "temp_min":     round(main.get("temp_min", temp_val), 1),
        "temp_max":     round(main.get("temp_max", temp_val), 1),
        "condition":    wx.get("main", "Clear"),
        "description":  wx.get("description", "").title(),
        "icon":         wx.get("icon", "01d"),
        "humidity":     humidity,
        "pressure":     main.get("pressure", 1013),
        "sea_level":    main.get("sea_level", main.get("pressure", 1013)),
        "wind_speed":   round(wind.get("speed", 0.0), 1),
        "wind_deg":     wind_deg,
        "wind_compass": deg_to_compass(wind_deg),
        "wind_gust":    round(wind.get("gust", wind.get("speed", 0.0)), 1),
        "visibility_km": round(vis_m / 1000, 1),
        "cloudiness":   current.get("clouds", {}).get("all", 0),
        "sunrise":      _ts_to_local(sys.get("sunrise")),
        "sunset":       _ts_to_local(sys.get("sunset")),
        "comfort_idx":  comfort_idx,
        "is_demo":      current.get("_is_demo", False),
    }
