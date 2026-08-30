# 🌦️ Weather Analytics Dashboard

An interactive, production-ready **Weather Analytics Dashboard** built with **Python, Streamlit, OpenWeatherMap API, Pandas, and Plotly**.

The application provides real-time meteorological observations, statistical forecasts, interactive time-series visualizations, polar wind dynamics, and multi-city comparative analytics.

---

## 🌟 Key Features

- **🌐 Real-Time Live API & Demo Simulation Mode**:
  - Direct integration with OpenWeatherMap API (`/weather`, `/forecast`, `/air_pollution`).
  - Built-in realistic synthetic data generator enabling seamless offline testing and demos without requiring an API key.
- **⚡ Pandas Data Pipeline & Time-Series Processing**:
  - Cleans, parses, and converts 3-hour interval forecast payloads into structured Pandas DataFrames.
  - Computes daily aggregations (Min/Max temperatures, average moisture, max wind gusts, cumulative precipitation, and dominant weather classifications).
- **📈 Interactive Plotly Visualizations**:
  - **Temperature & 'Feels Like' Trend**: Spline curves with shaded Min-Max uncertainty bands and custom tooltips.
  - **Precipitation & Rain Probability**: Dual-axis bar and line charts for rain volume (mm) and probability (%).
  - **Wind Dynamics**: Polar/Radar wind rose distribution and speed/gust timeline.
  - **Atmospheric Profile**: Humidity vs. barometric pressure correlation.
  - **Diurnal Matrix**: Day-vs-Hour temperature heatmap.
  - **Spatial Cartography**: Interactive dark-themed scatter map with geographic coordinates.
- **⚖️ Side-by-Side City Comparison**:
  - Simultaneously compare atmospheric KPIs and 5-day metric trends between two global cities.
- **📥 Data Explorer & Export**:
  - Inspect tabular forecast records with one-click **CSV** and **JSON** export buttons.

---

## 🛠️ Tech Stack

| Technology | Purpose |
| :--- | :--- |
| **Python 3.10+** | Core programming language |
| **Streamlit** | Web application framework and dynamic UI |
| **Pandas & NumPy** | Data ingestion, manipulation, and statistical aggregation |
| **Plotly** | Interactive high-resolution charts, heatmaps, and spatial maps |
| **OpenWeatherMap API** | Live global weather and air pollution data feeds |
| **Requests** | HTTP client for REST API communication |
| **Python-Dotenv** | Secure environment configuration |

---

## 📁 Project Architecture

```
weather/
├── app.py                   # Main Streamlit dashboard application
├── weather_service.py       # API client & mock generator for current, forecast & AQI
├── data_processor.py        # Pandas transformation, daily aggregation & KPI extraction
├── charts.py                # Plotly chart builders (Trends, Polar, Heatmaps, Maps)
├── styles.py                # Custom CSS styling & UI enhancements
├── test_weather_app.py      # Automated test suite
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variable template
└── README.md                # Project documentation
```

---

## 🚀 Quickstart & Setup

### 1. Clone & Navigate to Project
```bash
git clone <repo-url>
cd weather
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure OpenWeatherMap API Key
Create a `.env` file or enter your API key directly in the Streamlit sidebar:
```env
OPENWEATHER_API_KEY=your_openweathermap_api_key_here
```
> *Note: If no API key is provided, the dashboard automatically operates in **Demo Simulation Mode** with realistic data.*

### 4. Run the Dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Tests

Execute the unit and integration test suite:
```bash
python test_weather_app.py
```

---

## 📝 Resume Highlights

- **Developed a real-time weather analytics dashboard** using Streamlit and OpenWeatherMap API, supporting global city lookups, air quality monitoring, and automated offline simulation fallback.
- **Processed multi-day weather time-series data using Pandas**, calculating daily aggregations, diurnal temperature variances, and precipitation probabilities.
- **Engineered interactive data visualizations with Plotly**, including spline temperature trends with confidence bands, dual-axis precipitation charts, polar wind roses, and diurnal heatmaps.
- **Implemented multi-city comparative analytics and data export pipelines** (CSV/JSON) for data exploration.
