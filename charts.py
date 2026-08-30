"""
Plotly visualization module — industry-level interactive charts for the
Weather Analytics Dashboard. All charts use a unified dark theme.
"""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# ── Shared theme ──────────────────────────────────────────────────────────────
_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color="#e2e8f0", size=13),
    hoverlabel=dict(bgcolor="#1e293b", font_size=13, font_family="Inter, sans-serif", bordercolor="#334155"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=20, r=20, t=55, b=20),
)
_GRID = dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)", zeroline=False)
_XTIME = dict(**_GRID, tickformat="%a\n%b %d\n%H:%M", title="")


def _apply(fig: go.Figure, title: str = "", height: int = 380) -> go.Figure:
    fig.update_layout(title=f"<b>{title}</b>", height=height, **_THEME)
    return fig


# ── 1. Temperature trend ──────────────────────────────────────────────────────
def create_temp_trend_chart(df: pd.DataFrame, unit_symbol: str) -> go.Figure:
    """5-day temperature + feels-like spline with min/max confidence band."""
    fig = go.Figure()
    if df.empty:
        return _apply(fig, "Temperature Trend")

    # Shaded range band
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["temp_max"], mode="lines",
                             line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["temp_min"], mode="lines",
                             line=dict(width=0), fill="tonexty",
                             fillcolor="rgba(56,189,248,0.10)", name="Min–Max Range",
                             hoverinfo="skip"))

    # Temperature
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["temp"],
        mode="lines+markers", name=f"Temperature ({unit_symbol})",
        line=dict(color="#38bdf8", width=3, shape="spline"),
        marker=dict(size=5, color="#0ea5e9"),
        customdata=df[["weather_desc", "humidity", "wind_speed"]].values,
        hovertemplate=(
            "<b>%{x|%a %b %d, %H:%M}</b><br>"
            f"🌡 Temp: %{{y:.1f}}{unit_symbol}<br>"
            "🌤 %{customdata[0]}<br>"
            "💧 Humidity: %{customdata[1]}%<br>"
            "💨 Wind: %{customdata[2]} m/s<extra></extra>"
        ),
    ))

    # Feels-like
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["feels_like"],
        mode="lines", name=f"Feels Like ({unit_symbol})",
        line=dict(color="#fb923c", width=2, dash="dot", shape="spline"),
        hovertemplate=f"<b>%{{x|%a %H:%M}}</b><br>Feels Like: %{{y:.1f}}{unit_symbol}<extra></extra>",
    ))

    fig.update_xaxes(**_XTIME)
    fig.update_yaxes(title=f"Temperature ({unit_symbol})", **_GRID)
    return _apply(fig, f"5-Day Temperature Trend ({unit_symbol})", height=400)


# ── 2. Precipitation chart ────────────────────────────────────────────────────
def create_precipitation_chart(df: pd.DataFrame) -> go.Figure:
    """Dual-axis: precipitation volume (bars) + rain probability (line)."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if df.empty:
        return _apply(fig, "Precipitation")

    fig.add_trace(go.Bar(
        x=df["timestamp"], y=df["precip_mm"],
        name="Precipitation (mm)",
        marker_color="rgba(56,189,248,0.60)",
        marker_line=dict(color="#0284c7", width=0.5),
        hovertemplate="<b>%{x|%a %H:%M}</b><br>Precip: %{y:.1f} mm<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["pop_pct"],
        mode="lines+markers", name="Rain Probability (%)",
        line=dict(color="#a78bfa", width=2.5, shape="spline"),
        marker=dict(size=4, color="#7c3aed"),
        hovertemplate="<b>%{x|%a %H:%M}</b><br>Rain Chance: %{y:.0f}%<extra></extra>",
    ), secondary_y=True)

    fig.update_xaxes(**_XTIME)
    fig.update_yaxes(title="Precipitation (mm)", rangemode="tozero", secondary_y=False, **_GRID)
    fig.update_yaxes(title="Rain Probability (%)", range=[0, 105], showgrid=False, secondary_y=True)
    fig.update_layout(height=380, **_THEME)
    fig.update_layout(title="<b>Precipitation & Rain Probability</b>")
    return fig


# ── 3. Wind polar chart ───────────────────────────────────────────────────────
def create_wind_polar_chart(df: pd.DataFrame, speed_unit: str) -> go.Figure:
    """Polar scatter: wind direction vs speed, coloured by speed magnitude."""
    fig = go.Figure()
    if df.empty:
        return _apply(fig, "Wind Rose")

    fig.add_trace(go.Scatterpolar(
        r=df["wind_speed"], theta=df["wind_deg"],
        mode="markers",
        marker=dict(
            size=9, color=df["wind_speed"],
            colorscale="Viridis", showscale=True,
            colorbar=dict(title=f"Speed<br>({speed_unit})", thickness=14, len=0.70),
            opacity=0.85,
        ),
        hovertemplate=(
            f"Speed: %{{r:.1f}} {speed_unit}<br>"
            "Direction: %{theta:.0f}°<extra></extra>"
        ),
    ))

    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, showline=False, gridcolor="rgba(255,255,255,0.12)", tickfont=dict(size=10)),
            angularaxis=dict(
                direction="clockwise", rotation=90,
                gridcolor="rgba(255,255,255,0.12)",
                ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
            ),
        ),
        showlegend=False,
        height=380,
        **_THEME,
    )
    fig.update_layout(title="<b>Wind Direction & Speed Distribution</b>")
    return fig


# ── 4. Wind speed trend ───────────────────────────────────────────────────────
def create_wind_trend_chart(df: pd.DataFrame, speed_unit: str) -> go.Figure:
    """Timeline of sustained wind speed and gust velocity."""
    fig = go.Figure()
    if df.empty:
        return _apply(fig, "Wind Trend")

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["wind_gust"],
        mode="lines", name=f"Gust ({speed_unit})",
        line=dict(color="#f43f5e", width=1.5, dash="dash"),
        hovertemplate=f"<b>%{{x|%a %H:%M}}</b><br>Gust: %{{y:.1f}} {speed_unit}<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["wind_speed"],
        mode="lines+markers", name=f"Sustained Wind ({speed_unit})",
        line=dict(color="#10b981", width=3, shape="spline"),
        marker=dict(size=5, color="#059669"),
        fill="tozeroy", fillcolor="rgba(16,185,129,0.10)",
        customdata=df["wind_dir"],
        hovertemplate=(
            f"<b>%{{x|%a %H:%M}}</b><br>"
            f"Speed: %{{y:.1f}} {speed_unit}<br>"
            "Direction: %{customdata}<extra></extra>"
        ),
    ))

    fig.update_xaxes(**_XTIME)
    fig.update_yaxes(title=f"Wind Speed ({speed_unit})", rangemode="tozero", **_GRID)
    return _apply(fig, f"Wind Speed & Gust Forecast ({speed_unit})", height=380)


# ── 5. Humidity + Pressure dual axis ─────────────────────────────────────────
def create_humidity_pressure_chart(df: pd.DataFrame) -> go.Figure:
    """Dual-axis: atmospheric humidity (%) vs barometric pressure (hPa)."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if df.empty:
        return _apply(fig, "Humidity & Pressure")

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["humidity"],
        mode="lines", name="Humidity (%)",
        line=dict(color="#06b6d4", width=2.5, shape="spline"),
        fill="tozeroy", fillcolor="rgba(6,182,212,0.10)",
        hovertemplate="<b>%{x|%a %H:%M}</b><br>Humidity: %{y}%<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["pressure"],
        mode="lines", name="Pressure (hPa)",
        line=dict(color="#a855f7", width=2, shape="spline"),
        hovertemplate="<b>%{x|%a %H:%M}</b><br>Pressure: %{y} hPa<extra></extra>",
    ), secondary_y=True)

    fig.update_xaxes(**_XTIME)
    fig.update_yaxes(title="Humidity (%)", range=[0, 105], secondary_y=False, **_GRID)
    fig.update_yaxes(title="Pressure (hPa)", showgrid=False, secondary_y=True)
    fig.update_layout(height=380, **_THEME)
    fig.update_layout(title="<b>Atmospheric Humidity & Barometric Pressure</b>")
    return fig


# ── 6. Diurnal temperature heatmap ────────────────────────────────────────────
def create_temp_heatmap(df: pd.DataFrame, unit_symbol: str) -> go.Figure:
    """Day-vs-Hour temperature matrix heatmap."""
    fig = go.Figure()
    if df.empty:
        return _apply(fig, "Temperature Heatmap")

    pivot = df.pivot_table(index="day_name", columns="time_str", values="temp", aggfunc="mean")
    day_order = df["day_name"].drop_duplicates().tolist()
    pivot = pivot.reindex(day_order)

    fig.add_trace(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale="Turbo",
        colorbar=dict(title=f"Temp ({unit_symbol})", len=0.80, thickness=14),
        hovertemplate=f"<b>%{{y}} at %{{x}}</b><br>Temp: %{{z:.1f}}{unit_symbol}<extra></extra>",
        xgap=1, ygap=1,
    ))

    fig.update_xaxes(title="Time of Day (Local)", showgrid=False, tickfont=dict(size=11))
    fig.update_yaxes(title="", showgrid=False, autorange="reversed")
    return _apply(fig, f"Diurnal Temperature Heatmap — Day vs Hour ({unit_symbol})", height=320)


# ── 7. City comparison chart ──────────────────────────────────────────────────
def create_comparison_chart(
    df1: pd.DataFrame, df2: pd.DataFrame,
    city1: str, city2: str,
    metric_col: str, metric_label: str, unit_symbol: str,
) -> go.Figure:
    """Overlay two cities' metric forecasts on the same axes."""
    fig = go.Figure()

    if not df1.empty and metric_col in df1.columns:
        fig.add_trace(go.Scatter(
            x=df1["timestamp"], y=df1[metric_col],
            mode="lines+markers", name=f"{city1.title()}",
            line=dict(color="#38bdf8", width=3, shape="spline"),
            marker=dict(size=5),
            hovertemplate=(
                f"<b>{city1.title()}</b> (%{{x|%a %H:%M}})<br>"
                f"{metric_label}: %{{y:.1f}} {unit_symbol}<extra></extra>"
            ),
        ))

    if not df2.empty and metric_col in df2.columns:
        fig.add_trace(go.Scatter(
            x=df2["timestamp"], y=df2[metric_col],
            mode="lines+markers", name=f"{city2.title()}",
            line=dict(color="#f43f5e", width=3, shape="spline"),
            marker=dict(size=5),
            hovertemplate=(
                f"<b>{city2.title()}</b> (%{{x|%a %H:%M}})<br>"
                f"{metric_label}: %{{y:.1f}} {unit_symbol}<extra></extra>"
            ),
        ))

    fig.update_xaxes(**_XTIME)
    fig.update_yaxes(title=f"{metric_label} ({unit_symbol})", **_GRID)
    return _apply(
        fig,
        f"Side-by-Side Comparison: {city1.title()} vs {city2.title()} — {metric_label}",
        height=400,
    )


# ── 8. Geographic map ─────────────────────────────────────────────────────────
def create_weather_map(
    lat: float, lon: float,
    city_name: str, temp_str: str, condition: str,
) -> go.Figure:
    """Interactive dark-themed map pinning the city location with weather details."""
    fig = go.Figure()

    hover_text = (
        f"<b>{city_name}</b><br>"
        f"📍 {lat:.3f}°, {lon:.3f}°<br>"
        f"🌡 {temp_str}<br>"
        f"🌤 {condition}"
    )

    # Plotly ≥5.24 introduced go.Scattermap; fall back to go.Scattermapbox
    if hasattr(go, "Scattermap"):
        fig.add_trace(go.Scattermap(
            lat=[lat], lon=[lon],
            mode="markers+text",
            marker=dict(size=18, color="#38bdf8"),
            text=[f"  {city_name}"],
            textfont=dict(size=14, color="#ffffff"),
            hoverinfo="text", hovertext=hover_text,
        ))
        fig.update_layout(map=dict(style="carto-darkmatter", center=dict(lat=lat, lon=lon), zoom=7))
    else:
        fig.add_trace(go.Scattermapbox(
            lat=[lat], lon=[lon],
            mode="markers+text",
            marker=dict(size=18, color="#38bdf8"),
            text=[f"  {city_name}"],
            textfont=dict(size=14, color="#ffffff"),
            hoverinfo="text", hovertext=hover_text,
        ))
        fig.update_layout(mapbox=dict(style="carto-darkmatter", center=dict(lat=lat, lon=lon), zoom=7))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#e2e8f0"),
    )
    return fig
