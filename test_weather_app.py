"""
Automated test suite — Weather Analytics Dashboard.
Tests weather_service, data_processor, and charts modules end-to-end.
"""
import unittest
import pandas as pd
import plotly.graph_objects as go

from weather_service import (
    generate_mock_weather,
    _celsius_to_unit,
    get_default_api_key,
)
from data_processor import (
    process_forecast_dataframe,
    calculate_daily_summary,
    extract_current_kpis,
    deg_to_compass,
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


class TestWeatherService(unittest.TestCase):

    def setUp(self):
        self.curr, self.fore, self.aqi = generate_mock_weather("Hyderabad", "metric")

    def test_mock_structure_current(self):
        for field in ("coord", "weather", "main", "wind", "sys", "name", "_is_demo"):
            self.assertIn(field, self.curr)
        self.assertTrue(self.curr["_is_demo"])

    def test_mock_structure_forecast(self):
        self.assertIn("list", self.fore)
        self.assertEqual(len(self.fore["list"]), 40)
        item = self.fore["list"][0]
        for f in ("dt", "main", "weather", "wind", "pop", "dt_txt"):
            self.assertIn(f, item)

    def test_mock_structure_aqi(self):
        self.assertIn("list", self.aqi)
        aqi_item = self.aqi["list"][0]
        self.assertIn("main", aqi_item)
        self.assertIn("aqi", aqi_item["main"])
        self.assertIn("components", aqi_item)

    def test_temp_conversion_metric(self):
        self.assertEqual(_celsius_to_unit(0.0, "metric"), 0.0)
        self.assertEqual(_celsius_to_unit(100.0, "metric"), 100.0)

    def test_temp_conversion_imperial(self):
        self.assertEqual(_celsius_to_unit(0.0, "imperial"), 32.0)
        self.assertEqual(_celsius_to_unit(100.0, "imperial"), 212.0)

    def test_temp_conversion_kelvin(self):
        self.assertAlmostEqual(_celsius_to_unit(0.0, "standard"), 273.15, places=1)

    def test_api_key_loaded(self):
        key = get_default_api_key()
        # Key should be non-empty if .env is present (may be blank in CI)
        self.assertIsInstance(key, str)

    def test_known_city_seed(self):
        curr, _, _ = generate_mock_weather("London", "metric")
        self.assertEqual(curr["name"], "London")
        self.assertEqual(curr["sys"]["country"], "GB")

    def test_unknown_city_fallback(self):
        curr, fore, _ = generate_mock_weather("Atlantis", "metric")
        self.assertEqual(curr["name"], "Atlantis")
        self.assertEqual(len(fore["list"]), 40)


class TestDataProcessor(unittest.TestCase):

    def setUp(self):
        _, self.fore, _ = generate_mock_weather("London", "metric")
        self.curr, _, _ = generate_mock_weather("London", "metric")
        self.df = process_forecast_dataframe(self.fore)

    def test_dataframe_shape(self):
        self.assertIsInstance(self.df, pd.DataFrame)
        self.assertEqual(len(self.df), 40)

    def test_dataframe_required_columns(self):
        required = [
            "timestamp", "date", "day_name", "time_str",
            "temp", "feels_like", "temp_min", "temp_max",
            "humidity", "pressure", "weather_main", "weather_desc",
            "wind_speed", "wind_deg", "wind_dir", "wind_gust",
            "cloudiness", "pop_pct", "precip_mm", "visibility_km",
        ]
        for col in required:
            self.assertIn(col, self.df.columns, f"Missing column: {col}")

    def test_dataframe_sorted(self):
        ts = self.df["timestamp"].tolist()
        self.assertEqual(ts, sorted(ts))

    def test_daily_summary(self):
        daily = calculate_daily_summary(self.df)
        self.assertIsInstance(daily, pd.DataFrame)
        self.assertGreaterEqual(len(daily), 5)
        for col in ("temp_min", "temp_max", "humidity_avg", "total_precip", "pop_max"):
            self.assertIn(col, daily.columns)

    def test_daily_temp_ordering(self):
        daily = calculate_daily_summary(self.df)
        self.assertTrue((daily["temp_min"] <= daily["temp_max"]).all())

    def test_deg_to_compass_cardinals(self):
        self.assertEqual(deg_to_compass(0),   "N")
        self.assertEqual(deg_to_compass(90),  "E")
        self.assertEqual(deg_to_compass(180), "S")
        self.assertEqual(deg_to_compass(270), "W")
        self.assertEqual(deg_to_compass(360), "N")

    def test_aqi_labels(self):
        self.assertEqual(get_aqi_label(1)["label"], "Good")
        self.assertEqual(get_aqi_label(3)["label"], "Moderate")
        self.assertEqual(get_aqi_label(5)["label"], "Very Poor")
        self.assertEqual(get_aqi_label(99)["label"], "Unknown")

    def test_extract_kpis_fields(self):
        kpis = extract_current_kpis(self.curr, "°C")
        for field in ("city_name", "country", "temp", "feels_like", "humidity",
                      "wind_speed", "wind_compass", "sunrise", "sunset",
                      "visibility_km", "comfort_idx", "is_demo"):
            self.assertIn(field, kpis, f"Missing KPI: {field}")
        self.assertTrue(kpis["is_demo"])
        self.assertGreaterEqual(kpis["comfort_idx"], 0)
        self.assertLessEqual(kpis["comfort_idx"], 100)

    def test_empty_dataframe_safety(self):
        self.assertTrue(calculate_daily_summary(pd.DataFrame()).empty)
        self.assertTrue(process_forecast_dataframe({}).empty)
        self.assertTrue(process_forecast_dataframe({"list": []}).empty)


class TestCharts(unittest.TestCase):

    def setUp(self):
        _, fore, _ = generate_mock_weather("Tokyo", "metric")
        self.df = process_forecast_dataframe(fore)
        _, fore2, _ = generate_mock_weather("Paris", "metric")
        self.df2 = process_forecast_dataframe(fore2)

    def _is_fig(self, f):
        self.assertIsInstance(f, go.Figure)

    def test_temp_trend(self):
        self._is_fig(create_temp_trend_chart(self.df, "°C"))

    def test_precipitation(self):
        self._is_fig(create_precipitation_chart(self.df))

    def test_wind_polar(self):
        self._is_fig(create_wind_polar_chart(self.df, "m/s"))

    def test_wind_trend(self):
        self._is_fig(create_wind_trend_chart(self.df, "m/s"))

    def test_humidity_pressure(self):
        self._is_fig(create_humidity_pressure_chart(self.df))

    def test_temp_heatmap(self):
        self._is_fig(create_temp_heatmap(self.df, "°C"))

    def test_comparison(self):
        self._is_fig(create_comparison_chart(self.df, self.df2, "Tokyo", "Paris", "temp", "Temperature", "°C"))
        self._is_fig(create_comparison_chart(self.df, self.df2, "Tokyo", "Paris", "humidity", "Humidity", "%"))

    def test_weather_map(self):
        self._is_fig(create_weather_map(35.68, 139.65, "Tokyo", "24°C", "Clear Sky"))

    def test_empty_df_charts(self):
        empty = pd.DataFrame()
        self._is_fig(create_temp_trend_chart(empty, "°C"))
        self._is_fig(create_precipitation_chart(empty))
        self._is_fig(create_wind_polar_chart(empty, "m/s"))
        self._is_fig(create_temp_heatmap(empty, "°C"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
