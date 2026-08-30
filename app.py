"""
Weather Analytics Dashboard — main Streamlit application.
Tech: Python · Streamlit · OpenWeatherMap API · Pandas · Plotly
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timezone

from styles import apply_custom_styles
from weather_service import (
    get_default_api_key,
    fetch_current_weather,
    fetch_weather_forecast,
    fetch_air_quality,
    generate_mock_weather,
)
from data_processor import (
    process_forecast_dataframe,
    calculate_daily_summary,
    extract_current_kpis,
    get_aqi_label,
)
from charts import (
    create_temp_trend_chart,
    create_precipitation_chart,
    create_wind_polar_chart,
    create_wind_trend_chart,
    create_humidity_pressure_chart,
    create_temp_heatmap,
    create_comparison_chart,
    create_weather_map,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Weather Analytics Dashboard",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_custom_styles()

# ── Load API key silently from .env — never shown in UI ───────────────────────
_API_KEY = get_default_api_key()
_IS_LIVE = bool(_API_KEY)

# ── Session state defaults ────────────────────────────────────────────────────
if "city"         not in st.session_state: st.session_state.city         = "Hyderabad"
if "compare_city" not in st.session_state: st.session_state.compare_city = "London"

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  (no API key input — credentials loaded securely from .env)
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🌦️ Weather Analytics")
    st.caption("Real-Time Global Weather Intelligence")

    # Connection status badge
    if _IS_LIVE:
        st.markdown(
            '<span class="status-pill status-live">🟢 Live API Connected</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-pill status-demo">🟡 Demo Simulation Mode</span>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Temperature unit selector
    unit_choice = st.radio(
        "🌡 Temperature Units",
        ["Celsius (°C)", "Fahrenheit (°F)", "Kelvin (K)"],
        index=0,
    )
    if "Celsius" in unit_choice:
        units, unit_symbol, speed_unit = "metric",   "°C", "m/s"
    elif "Fahrenheit" in unit_choice:
        units, unit_symbol, speed_unit = "imperial", "°F", "mph"
    else:
        units, unit_symbol, speed_unit = "standard", "K",  "m/s"

    st.divider()

    # City search
    search = st.text_input(
        "🔍 Search City",
        value=st.session_state.city,
        placeholder="e.g. Mumbai, Berlin, New York…",
    )
    if st.button("📡 Get Weather", use_container_width=True, type="primary"):
        if search.strip():
            st.session_state.city = search.strip()
            st.rerun()

    # Quick preset buttons
    st.markdown("##### 📌 Quick Presets")
    left, right = st.columns(2)
    presets = [
        ("🇮🇳 Hyderabad",    "Hyderabad"),
        ("🇬🇧 London",       "London"),
        ("🇺🇸 New York",     "New York"),
        ("🇯🇵 Tokyo",        "Tokyo"),
        ("🇫🇷 Paris",        "Paris"),
        ("🇦🇺 Sydney",       "Sydney"),
        ("🇦🇪 Dubai",        "Dubai"),
        ("🇸🇬 Singapore",    "Singapore"),
        ("🇮🇳 Mumbai",       "Mumbai"),
        ("🇺🇸 San Francisco","San Francisco"),
    ]
    for i, (label, val) in enumerate(presets):
        col = left if i % 2 == 0 else right
        if col.button(label, use_container_width=True, key=f"pre_{val}"):
            st.session_state.city = val
            st.rerun()

    st.divider()
    st.caption("Python · Streamlit · Pandas · Plotly")

# ═══════════════════════════════════════════════════════════════════════════════
# DATA FETCHING
# ═══════════════════════════════════════════════════════════════════════════════
city = st.session_state.city

curr_raw  = None
fore_raw  = None
aqi_raw   = None
error_msg = None

if _IS_LIVE:
    with st.spinner(f"⛅ Fetching live weather for **{city}**…"):
        curr_raw, err1 = fetch_current_weather(city, _API_KEY, units=units)
        if err1:
            error_msg = err1
        else:
            fore_raw, err2 = fetch_weather_forecast(city, _API_KEY, units=units)
            if err2:
                error_msg = err2
            else:
                lat = curr_raw["coord"]["lat"]
                lon = curr_raw["coord"]["lon"]
                aqi_raw, _ = fetch_air_quality(lat, lon, _API_KEY)
else:
    curr_raw, fore_raw, aqi_raw = generate_mock_weather(city, units=units)

# Graceful error display
if error_msg or not curr_raw or not fore_raw:
    st.error(f"⚠️ {error_msg or 'Failed to load weather data.'}")
    st.info(
        "**Suggestions:**\n"
        "- Check the city spelling.\n"
        "- Add country code for precision: **'Mumbai, IN'** or **'Paris, FR'**.\n"
        "- Try a nearby major city name."
    )
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# DATA PROCESSING  (Pandas)
# ═══════════════════════════════════════════════════════════════════════════════
kpis        = extract_current_kpis(curr_raw, unit_symbol)
forecast_df = process_forecast_dataframe(fore_raw)
daily_df    = calculate_daily_summary(forecast_df)

# ═══════════════════════════════════════════════════════════════════════════════
# HERO HEADER
# ═══════════════════════════════════════════════════════════════════════════════
icon_url   = f"https://openweathermap.org/img/wn/{kpis['icon']}@4x.png"
now_utc    = datetime.now(timezone.utc)
mode_badge = (
    "<span class='status-pill status-demo'>🟡 Demo Simulation</span>"
    if kpis["is_demo"] else
    "<span class='status-pill status-live'>🟢 Live Data</span>"
)

st.markdown(f"""
<div class="hero-container">
  <div>
    <div class="hero-title">📍 {kpis['city_name']}, {kpis['country']}</div>
    <div class="hero-subtitle">
      {kpis['lat']:.3f}°, {kpis['lon']:.3f}°
      &nbsp;|&nbsp;
      Updated: {now_utc.strftime('%d %b %Y, %H:%M')} UTC
    </div>
    <div style="margin-top:12px; display:flex; gap:10px; flex-wrap:wrap;">
      <span class="hero-condition">{kpis['description']}</span>
      {mode_badge}
    </div>
  </div>
  <div style="display:flex; align-items:center; gap:16px;">
    <img src="{icon_url}" width="90" height="90"
         style="filter:drop-shadow(0 4px 8px rgba(0,0,0,0.35));" />
    <div>
      <div class="hero-temp-badge">{kpis['temp']}{unit_symbol}</div>
      <div style="font-size:0.95rem; color:rgba(255,255,255,0.85); margin-top:4px;">
        Feels like {kpis['feels_like']}{unit_symbol} &nbsp;({kpis['temp_diff']})
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# KPI METRICS ROW  (6 cards)
# ═══════════════════════════════════════════════════════════════════════════════
def _card(icon: str, label: str, value: str, sub: str) -> str:
    return (
        f'<div class="metric-card">'
        f'<div class="metric-icon">{icon}</div>'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-subtext">{sub}</div>'
        f'</div>'
    )

c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.markdown(
    _card("🌡️", "Min / Max Temp",
          f"{kpis['temp_min']} / {kpis['temp_max']} {unit_symbol}",
          "Today's range"),
    unsafe_allow_html=True
)
c2.markdown(
    _card("💧", "Humidity",
          f"{kpis['humidity']}%",
          "High Moisture" if kpis["humidity"] > 70 else "Comfortable"),
    unsafe_allow_html=True
)
c3.markdown(
    _card("💨", "Wind",
          f"{kpis['wind_speed']} {speed_unit}",
          f"{kpis['wind_compass']} · Gust {kpis['wind_gust']} {speed_unit}"),
    unsafe_allow_html=True
)
c4.markdown(
    _card("⏲️", "Pressure",
          f"{kpis['pressure']} hPa",
          "Normal" if 1008 <= kpis["pressure"] <= 1020 else "Variable"),
    unsafe_allow_html=True
)
c5.markdown(
    _card("👁️", "Visibility",
          f"{kpis['visibility_km']} km",
          "Clear" if kpis["visibility_km"] >= 10 else "Reduced"),
    unsafe_allow_html=True
)
c6.markdown(
    _card("🌅", "Sunrise / Sunset",
          f"↑ {kpis['sunrise']}  ↓ {kpis['sunset']}",
          f"Cloud cover: {kpis['cloudiness']}%"),
    unsafe_allow_html=True
)

# ── Comfort index progress bar ────────────────────────────────────────────────
ci     = kpis["comfort_idx"]
ci_col = "#10b981" if ci >= 70 else ("#eab308" if ci >= 45 else "#f97316")
ci_txt = ("Great outdoor conditions" if ci >= 70
          else "Moderate comfort" if ci >= 45
          else "Uncomfortable — consider staying indoors")
st.markdown(f"""
<div style="margin:10px 0 4px 0; font-size:0.85rem; color:#94a3b8; font-weight:500;">
  🌿 Comfort Index:
  <b style="color:{ci_col};">{ci} / 100</b>
  &nbsp;—&nbsp;{ci_txt}
</div>
<div style="background:rgba(255,255,255,0.08);border-radius:8px;height:8px;
            overflow:hidden;margin-bottom:18px;">
  <div style="background:{ci_col};width:{ci}%;height:100%;border-radius:8px;"></div>
</div>
""", unsafe_allow_html=True)

# ── Air Quality expander ──────────────────────────────────────────────────────
if aqi_raw and aqi_raw.get("list"):
    aqi_item = aqi_raw["list"][0]
    aqi_num  = aqi_item.get("main", {}).get("aqi", 1)
    aqi_inf  = get_aqi_label(aqi_num)
    comp     = aqi_item.get("components", {})

    with st.expander(
        f"🌿 Air Quality: **{aqi_inf['badge']}** — {aqi_inf['desc']}",
        expanded=False
    ):
        a1, a2, a3, a4, a5, a6, a7 = st.columns(7)
        a1.metric("AQI Level", aqi_inf["label"])
        a2.metric("PM2.5",     f"{comp.get('pm2_5', '—')} µg/m³")
        a3.metric("PM10",      f"{comp.get('pm10',  '—')} µg/m³")
        a4.metric("CO",        f"{comp.get('co',    '—')} µg/m³")
        a5.metric("NO₂",       f"{comp.get('no2',   '—')} µg/m³")
        a6.metric("O₃",        f"{comp.get('o3',    '—')} µg/m³")
        a7.metric("SO₂",       f"{comp.get('so2',   '—')} µg/m³")

# ═══════════════════════════════════════════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 5-Day Forecast",
    "💨 Wind & Atmosphere",
    "🗺️ Geographic View",
    "⚖️ City Comparison",
    "📥 Data Explorer",
])

# ── Tab 1 — 5-Day Forecast ────────────────────────────────────────────────────
with tab1:
    st.markdown("#### 📅 5-Day Daily Outlook")

    if not daily_df.empty:
        n    = min(len(daily_df), 5)
        cols = st.columns(n)
        for i in range(n):
            row       = daily_df.iloc[i]
            card_icon = f"https://openweathermap.org/img/wn/{row['icon']}@2x.png"
            cols[i].markdown(f"""
<div class="forecast-card">
  <div class="forecast-date">{row['day_name']}</div>
  <img src="{card_icon}" width="50" height="50" />
  <div class="forecast-temp">
    {row['temp_max']}{unit_symbol}
    <span style="font-size:0.85rem;color:#94a3b8;">/ {row['temp_min']}{unit_symbol}</span>
  </div>
  <div class="forecast-condition">{row['weather_desc']}</div>
  <div style="font-size:0.75rem;color:#38bdf8;margin-top:6px;">
    🌧️ {row['pop_max']}% &nbsp;·&nbsp; {row['total_precip']} mm
  </div>
  <div style="font-size:0.75rem;color:#94a3b8;margin-top:2px;">
    💧 {row['humidity_avg']}% &nbsp;·&nbsp; 💨 {row['wind_max']} {speed_unit}
  </div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    p1, p2 = st.columns([3, 2])
    with p1:
        st.plotly_chart(
            create_temp_trend_chart(forecast_df, unit_symbol),
            use_container_width=True,
        )
    with p2:
        st.plotly_chart(
            create_precipitation_chart(forecast_df),
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown("#### 🌡️ Diurnal Temperature Heatmap (Day vs Hour)")
    st.plotly_chart(
        create_temp_heatmap(forecast_df, unit_symbol),
        use_container_width=True,
    )

# ── Tab 2 — Wind & Atmosphere ─────────────────────────────────────────────────
with tab2:
    st.markdown("#### 💨 Wind Dynamics & Barometric Profile")

    w1, w2 = st.columns([3, 2])
    with w1:
        st.plotly_chart(
            create_wind_trend_chart(forecast_df, speed_unit),
            use_container_width=True,
        )
    with w2:
        st.plotly_chart(
            create_wind_polar_chart(forecast_df, speed_unit),
            use_container_width=True,
        )

    st.markdown("---")
    st.plotly_chart(
        create_humidity_pressure_chart(forecast_df),
        use_container_width=True,
    )

# ── Tab 3 — Geographic View ───────────────────────────────────────────────────
with tab3:
    st.markdown("#### 🗺️ City Location & Spatial Metadata")

    st.plotly_chart(
        create_weather_map(
            kpis["lat"], kpis["lon"],
            kpis["city_name"],
            f"{kpis['temp']}{unit_symbol}",
            kpis["description"],
        ),
        use_container_width=True,
    )

    g1, g2, g3, g4 = st.columns(4)
    g1.info(f"**Latitude:**  {kpis['lat']:.4f}°")
    g2.info(f"**Longitude:** {kpis['lon']:.4f}°")
    g3.info(f"**Cloud Cover:** {kpis['cloudiness']}%")
    g4.info(f"**Visibility:** {kpis['visibility_km']} km")

# ── Tab 4 — City Comparison ───────────────────────────────────────────────────
with tab4:
    st.markdown("#### ⚖️ Side-by-Side City Comparison")
    st.caption("Compare real-time conditions and 5-day forecasts between two cities.")

    cc1, cc2 = st.columns(2)
    with cc1:
        st.info(f"**Primary city:** {city.title()}")
    with cc2:
        comp_in = st.text_input(
            "Comparison city",
            value=st.session_state.compare_city,
            key="comp_inp",
            placeholder="e.g. Tokyo, Paris…",
        )
        if comp_in.strip():
            st.session_state.compare_city = comp_in.strip()

    comp_city = st.session_state.compare_city

    if _IS_LIVE:
        comp_curr, _e1 = fetch_current_weather(comp_city, _API_KEY, units=units)
        comp_fore, _e2 = fetch_weather_forecast(comp_city, _API_KEY, units=units)
    else:
        comp_curr, comp_fore, _ = generate_mock_weather(comp_city, units=units)

    if comp_curr and comp_fore:
        ck  = extract_current_kpis(comp_curr, unit_symbol)
        cdf = process_forecast_dataframe(comp_fore)

        kk1, kk2 = st.columns(2)
        with kk1:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-label">{kpis['city_name']}, {kpis['country']}</div>
  <div class="metric-value">{kpis['temp']}{unit_symbol}</div>
  <div class="metric-subtext">{kpis['description']} · Feels {kpis['feels_like']}{unit_symbol}</div>
  <div style="font-size:0.85rem;margin-top:8px;">
    💧 {kpis['humidity']}% &nbsp;·&nbsp; 💨 {kpis['wind_speed']} {speed_unit} ({kpis['wind_compass']})
  </div>
</div>""", unsafe_allow_html=True)

        with kk2:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-label">{ck['city_name']}, {ck['country']}</div>
  <div class="metric-value">{ck['temp']}{unit_symbol}</div>
  <div class="metric-subtext">{ck['description']} · Feels {ck['feels_like']}{unit_symbol}</div>
  <div style="font-size:0.85rem;margin-top:8px;">
    💧 {ck['humidity']}% &nbsp;·&nbsp; 💨 {ck['wind_speed']} {speed_unit} ({ck['wind_compass']})
  </div>
</div>""", unsafe_allow_html=True)

        metric_opt = st.selectbox(
            "Metric to compare",
            ["Temperature", "Humidity", "Wind Speed"],
        )
        col_map = {
            "Temperature": ("temp",       "Temperature", unit_symbol),
            "Humidity":    ("humidity",   "Humidity",    "%"),
            "Wind Speed":  ("wind_speed", "Wind Speed",  speed_unit),
        }
        mc, ml, mu = col_map[metric_opt]
        st.plotly_chart(
            create_comparison_chart(forecast_df, cdf, city, comp_city, mc, ml, mu),
            use_container_width=True,
        )
    else:
        st.warning(
            f"Could not load data for **'{comp_city}'**. "
            "Try a different city name or add a country code (e.g. 'Berlin, DE')."
        )

# ── Tab 5 — Data Explorer ─────────────────────────────────────────────────────
with tab5:
    st.markdown("#### 📥 Forecast Dataset — Pandas DataFrame")
    st.caption("3-hour interval records. All timestamps are in city local time.")

    if not forecast_df.empty:
        display_cols = [
            "timestamp", "day_name", "time_str",
            "temp", "feels_like", "temp_min", "temp_max",
            "humidity", "pressure", "weather_main", "weather_desc",
            "wind_speed", "wind_dir", "wind_gust",
            "cloudiness", "pop_pct", "precip_mm", "visibility_km",
        ]
        st.dataframe(
            forecast_df[display_cols],
            use_container_width=True,
            height=380,
        )

        st.markdown("---")
        e1, e2, _ = st.columns([1, 1, 2])
        e1.download_button(
            label="📥 Download CSV",
            data=forecast_df.to_csv(index=False).encode("utf-8"),
            file_name=f"{city.lower().replace(' ', '_')}_weather.csv",
            mime="text/csv",
            use_container_width=True,
        )
        e2.download_button(
            label="📥 Download JSON",
            data=forecast_df.to_json(orient="records", date_format="iso").encode("utf-8"),
            file_name=f"{city.lower().replace(' ', '_')}_weather.json",
            mime="application/json",
            use_container_width=True,
        )

        st.markdown("---")
        st.markdown("##### 📊 Statistical Summary (Pandas describe)")
        stat_cols = ["temp", "feels_like", "humidity", "pressure",
                     "wind_speed", "pop_pct", "precip_mm"]
        st.dataframe(
            forecast_df[stat_cols].describe().round(2),
            use_container_width=True,
        )
    else:
        st.info("No forecast data available to display.")
