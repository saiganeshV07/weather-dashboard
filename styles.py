"""
CSS Styles and UI layout enhancements for the Weather Analytics Dashboard.
"""
import streamlit as st

def apply_custom_styles():
    """Injects custom CSS to style metrics, cards, tabs, and headers."""
    st.markdown(
        """
        <style>
        /* Global & Font Adjustments */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Hero Banner */
        .hero-container {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            padding: 24px;
            border-radius: 16px;
            color: #ffffff;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin: 0;
            color: #ffffff !important;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .hero-subtitle {
            font-size: 1.05rem;
            color: rgba(255, 255, 255, 0.85);
            margin-top: 4px;
            font-weight: 400;
        }

        .hero-temp-badge {
            font-size: 3rem;
            font-weight: 800;
            color: #ffffff;
            text-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }

        .hero-condition {
            text-transform: capitalize;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.95rem;
            font-weight: 600;
            display: inline-block;
        }

        /* Glassmorphism Metric Card */
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .metric-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
            border-color: rgba(64, 158, 255, 0.4);
        }

        .metric-icon {
            font-size: 1.6rem;
            margin-bottom: 6px;
        }

        .metric-label {
            font-size: 0.85rem;
            font-weight: 500;
            color: #8c9ba5;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }

        .metric-value {
            font-size: 1.7rem;
            font-weight: 700;
            color: var(--text-color, #ffffff);
            line-height: 1.2;
        }

        .metric-subtext {
            font-size: 0.8rem;
            color: #7b8b98;
            margin-top: 4px;
        }

        /* Forecast Daily Card */
        .forecast-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 16px;
            text-align: center;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .forecast-card:hover {
            transform: translateY(-4px);
            border-color: #3b82f6;
            background: rgba(59, 130, 246, 0.08);
        }

        .forecast-date {
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 8px;
            color: #94a3b8;
        }

        .forecast-temp {
            font-size: 1.35rem;
            font-weight: 700;
            margin: 6px 0;
        }

        .forecast-condition {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: capitalize;
        }

        /* Alert / Status pill */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 12px;
            border-radius: 16px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .status-live {
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }

        .status-demo {
            background: rgba(245, 158, 11, 0.15);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        /* Streamlit UI cleanups */
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            font-weight: 700 !important;
        }
        
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }

        /* Tab styling */
        button[data-baseweb="tab"] {
            font-size: 1rem !important;
            font-weight: 600 !important;
            padding: 10px 18px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
