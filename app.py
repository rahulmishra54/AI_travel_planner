import io
import re
import threading
import time

import streamlit as st
from pipeline import run_pipeline

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib import colors as rl_colors
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        HRFlowable,
    )

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🧳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

INTEREST_COLORS = {
    "adventure": ("#fff4e6", "#c2410c", "🧗"),
    "food": ("#fef2f2", "#b91c1c", "🍜"),
    "nature": ("#ecfdf5", "#047857", "🌿"),
    "culture": ("#f5f3ff", "#6d28d9", "🏛"),
    "shopping": ("#fdf2f8", "#be185d", "🛍"),
    "wildlife": ("#f0fdf4", "#15803d", "🦁"),
    "spiritual": ("#fffbeb", "#b45309", "🕉"),
    "relaxation": ("#eff6ff", "#1d4ed8", "🧘"),
    "history": ("#f8fafc", "#334155", "🏺"),
    "nightlife": ("#faf5ff", "#7e22ce", "🌃"),
    "beach": ("#ecfeff", "#0e7490", "🏖"),
    "photography": ("#f1f5f9", "#0f172a", "📸"),
}
DEFAULT_BADGE = ("#f1f5f9", "#334155", "✨")

DESTINATION_THEME = {
    "beach": ("#0ea5e9", "#38bdf8", "🏖"),
    "mountain": ("#0f766e", "#14b8a6", "⛰"),
    "city": ("#4f46e5", "#818cf8", "🏙"),
    "adventure": ("#c2410c", "#fb923c", "🧗"),
    "wildlife": ("#15803d", "#4ade80", "🦁"),
    "spiritual": ("#b45309", "#fbbf24", "🕉"),
    "desert": ("#b45309", "#f59e0b", "🏜"),
}

GENERIC_TRAVEL_TIPS = [
    ("✈️", "Book flights on Tuesday", "Mid-week fares tend to run lower than weekend bookings."),
    ("🎒", "Pack light, travel smart", "Versatile layers and a capsule wardrobe make transit far easier."),
    ("🍽️", "Explore local cuisine", "Street food and neighborhood spots often beat tourist-trap menus."),
]


# --------------------------------------------------------------------------
# Styling
# --------------------------------------------------------------------------
def inject_css() -> None:
    """Inject the premium light-theme visual system for the app."""
    st.markdown(
        """
        <style>
            :root { color-scheme: light; }

            #MainMenu, footer { visibility: hidden; }

            .stApp {
                background: #f6f8fc;
            }

            .block-container {
                max-width: 1440px;
                padding-top: 1.1rem;
                padding-bottom: 3rem;
            }

            html, body, [class*="css"] {
                font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
            }

            /* ---------- App shell layout ---------- */
            .app-shell { display: flex; gap: 0; }

            /* ---------- Sidebar ---------- */
            .app-sidebar {
                background: linear-gradient(180deg, #0f1330 0%, #12172f 100%);
                border-radius: 22px;
                padding: 1.3rem 1.1rem;
                color: #e2e8f0;
                height: 100%;
                box-shadow: 0 20px 45px rgba(15, 15, 35, 0.18);
            }
            .sb-logo {
                display: flex;
                align-items: center;
                gap: 0.7rem;
                padding-bottom: 1.1rem;
                margin-bottom: 1rem;
                border-bottom: 1px solid rgba(255,255,255,0.08);
            }
            .sb-logo-badge {
                width: 42px; height: 42px;
                border-radius: 13px;
                display: grid;
                place-items: center;
                font-size: 1.2rem;
                background: linear-gradient(135deg, #4f46e5, #818cf8);
                box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4);
                flex-shrink: 0;
            }
            .sb-logo-title { font-weight: 750; font-size: 1rem; color: #ffffff; line-height: 1.2; }
            .sb-logo-sub { font-size: 0.74rem; color: #94a3b8; }

            div[data-testid="stVerticalBlock"] .app-sidebar .stButton > button {
                width: 100%;
                text-align: left;
                justify-content: flex-start;
                background: transparent !important;
                color: #cbd5e1 !important;
                box-shadow: none !important;
                border: 1px solid transparent !important;
                border-radius: 12px !important;
                font-weight: 600 !important;
                padding: 0.6rem 0.8rem !important;
                margin-bottom: 0.2rem;
            }
            div[data-testid="stVerticalBlock"] .app-sidebar .stButton > button:hover {
                background: rgba(255,255,255,0.06) !important;
                transform: none;
            }
            div[data-testid="stVerticalBlock"] .app-sidebar .stButton > button:disabled {
                color: #4b5573 !important;
                cursor: default;
            }
            .nav-active > button {
                background: linear-gradient(135deg, #4f46e5, #6d5bf0) !important;
                color: white !important;
                box-shadow: 0 10px 22px rgba(79, 70, 229, 0.35) !important;
            }
            .nav-soon {
                font-size: 0.62rem;
                font-weight: 700;
                color: #64748b;
                background: rgba(255,255,255,0.06);
                border-radius: 999px;
                padding: 0.1rem 0.5rem;
                display: inline-block;
                margin: -0.35rem 0 0.35rem 0.9rem;
            }

            /* ---------- Header ---------- */
            .greeting-row h1 { font-size: 1.55rem; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: -0.02em; }
            .greeting-row p { color: #64748b; margin: 0.15rem 0 0 0; font-size: 0.95rem; }

            /* ---------- Hero banner ---------- */
            .hero-banner {
                position: relative;
                border-radius: 26px;
                overflow: hidden;
                min-height: 260px;
                margin: 1.1rem 0 1.3rem 0;
                display: flex;
                align-items: center;
                box-shadow: 0 25px 55px rgba(30, 41, 89, 0.18);
                background-image:
                    linear-gradient(115deg, rgba(30,27,110,0.86) 0%, rgba(56,60,150,0.55) 45%, rgba(20,30,60,0.15) 100%),
                    url('https://images.unsplash.com/photo-1507525428034-b723cf961d3e?q=80&w=1740&auto=format&fit=crop');
                background-size: cover;
                background-position: center;
            }
            .hero-banner-inner { padding: 2.1rem 2.3rem; position: relative; z-index: 1; max-width: 560px; }
            .hero-banner h2 { color: white; font-size: 2rem; font-weight: 800; margin: 0 0 0.5rem 0; letter-spacing: -0.02em; }
            .hero-banner p { color: rgba(255,255,255,0.92); font-size: 1rem; margin-bottom: 1.1rem; }
            .hero-cta {
                display: inline-flex;
                align-items: center;
                gap: 0.4rem;
                background: white;
                color: #3730a3;
                font-weight: 750;
                padding: 0.65rem 1.2rem;
                border-radius: 12px;
                text-decoration: none;
                font-size: 0.92rem;
                box-shadow: 0 12px 24px rgba(0,0,0,0.18);
            }

            /* ---------- Stat tiles ---------- */
            .stat-tile-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.85rem;
                margin-bottom: 1.3rem;
            }
            .stat-tile {
                background: white;
                border: 1px solid rgba(15, 23, 42, 0.06);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                display: flex;
                align-items: center;
                gap: 0.8rem;
                box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
            }
            .stat-tile-icon {
                width: 44px; height: 44px;
                border-radius: 13px;
                display: grid;
                place-items: center;
                font-size: 1.15rem;
                flex-shrink: 0;
            }
            .stat-tile-value { font-size: 1.3rem; font-weight: 800; color: #0f172a; line-height: 1.1; }
            .stat-tile-label { font-size: 0.82rem; color: #0f172a; font-weight: 650; }
            .stat-tile-sub { font-size: 0.74rem; color: #94a3b8; }

            @media (max-width: 1100px) {
                .stat-tile-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            }

            /* ---------- Generic cards ---------- */
            .card {
                background: rgba(255,255,255,0.98);
                border: 1px solid rgba(15, 23, 42, 0.06);
                border-radius: 20px;
                padding: 1.3rem 1.4rem;
                box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);
                margin-bottom: 1.1rem;
                animation: fadeUp 0.5s ease both;
            }

            .form-card { padding: 1.4rem 1.5rem; border-radius: 24px; }

            .card h3, .section-title {
                margin-top: 0;
                margin-bottom: 0.7rem;
                font-size: 1.05rem;
                font-weight: 750;
                color: #0f172a;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            .card p, .card li, .card td { color: #334155; line-height: 1.65; }
            .card ul { padding-left: 1.1rem; margin-bottom: 0; }

            /* ---------- Destination quick-picks ---------- */
            .quickpick-row { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 0.2rem; }
            div[data-testid="column"] .quickpick-btn > button {
                width: 100%;
                border-radius: 14px !important;
                background: #f8fafc !important;
                color: #0f172a !important;
                border: 1px solid rgba(15,23,42,0.08) !important;
                box-shadow: none !important;
                font-weight: 650 !important;
                padding: 0.6rem 0.5rem !important;
            }
            .quickpick-selected > button {
                background: linear-gradient(135deg, #4f46e5, #6d5bf0) !important;
                color: white !important;
                border: none !important;
                box-shadow: 0 10px 22px rgba(79, 70, 229, 0.3) !important;
            }

            /* ---------- Tips ---------- */
            .tip-item {
                display: flex;
                gap: 0.8rem;
                align-items: flex-start;
                padding: 0.65rem 0.2rem;
                border-bottom: 1px solid rgba(15,23,42,0.05);
            }
            .tip-item:last-child { border-bottom: none; }
            .tip-icon {
                width: 38px; height: 38px;
                border-radius: 11px;
                background: #f5f3ff;
                display: grid;
                place-items: center;
                flex-shrink: 0;
                font-size: 1rem;
            }
            .tip-title { font-weight: 700; font-size: 0.9rem; color: #0f172a; }
            .tip-sub { font-size: 0.8rem; color: #64748b; }

            /* ---------- Destination hero (post-generation) ---------- */
            .dest-hero {
                border-radius: 24px;
                padding: 2.1rem 2rem;
                color: white;
                margin-bottom: 1.2rem;
                position: relative;
                overflow: hidden;
                box-shadow: 0 20px 45px rgba(15, 23, 42, 0.16);
            }
            .dest-hero .icon-badge {
                font-size: 2.6rem;
                display: inline-block;
                margin-bottom: 0.5rem;
                filter: drop-shadow(0 6px 10px rgba(0,0,0,0.18));
            }
            .dest-hero h2 { margin: 0 0 0.3rem 0; font-size: 1.9rem; font-weight: 800; letter-spacing: -0.02em; }
            .dest-hero .sub { opacity: 0.95; font-size: 0.98rem; max-width: 620px; }
            .dest-hero::after {
                content: "";
                position: absolute;
                inset: 0;
                background: radial-gradient(circle at 85% 15%, rgba(255,255,255,0.25), transparent 55%);
            }

            /* ---------- Metric / summary cards ---------- */
            .metric-grid {
                display: grid;
                grid-template-columns: repeat(5, minmax(0, 1fr));
                gap: 0.75rem;
                margin-bottom: 1.1rem;
            }
            .metric-card {
                background: linear-gradient(160deg, #ffffff, #f5f8ff);
                border: 1px solid rgba(79, 70, 229, 0.14);
                border-radius: 16px;
                padding: 0.9rem 0.95rem;
                box-shadow: 0 8px 22px rgba(79, 70, 229, 0.07);
            }
            .metric-label {
                font-size: 0.74rem;
                color: #64748b;
                margin-bottom: 0.3rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                display: flex; align-items: center; gap: 0.3rem;
            }
            .metric-value { font-size: 1.02rem; font-weight: 750; color: #0f172a; word-break: break-word; }

            @media (max-width: 1100px) {
                .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
            }

            /* ---------- Badges ---------- */
            .badge-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.3rem 0 0.9rem 0; }
            .badge {
                border-radius: 999px;
                padding: 0.32rem 0.8rem;
                font-size: 0.83rem;
                font-weight: 700;
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                border: 1px solid rgba(0,0,0,0.04);
            }

            /* ---------- CTA banner ---------- */
            .cta-banner {
                background: linear-gradient(135deg, #eef2ff, #f5f3ff);
                border: 1px solid rgba(79, 70, 229, 0.14);
                border-radius: 22px;
                padding: 1.2rem 1.5rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                flex-wrap: wrap;
                margin-bottom: 1.2rem;
            }
            .cta-left { display: flex; align-items: center; gap: 0.9rem; }
            .cta-icon {
                width: 46px; height: 46px;
                border-radius: 14px;
                background: linear-gradient(135deg, #4f46e5, #6d5bf0);
                display: grid;
                place-items: center;
                font-size: 1.2rem;
                color: white;
                flex-shrink: 0;
            }
            .cta-title { font-weight: 750; color: #0f172a; font-size: 1rem; }
            .cta-sub { color: #64748b; font-size: 0.85rem; }

            /* ---------- Empty state ---------- */
            .empty-state {
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 24px;
                padding: 3rem 2rem;
                text-align: center;
                color: #475569;
                background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(245,249,255,0.95));
                box-shadow: 0 18px 42px rgba(15, 23, 42, 0.06);
                position: relative;
                overflow: hidden;
            }
            .empty-icon { font-size: 2.6rem; margin-bottom: 0.6rem; display: inline-block; animation: float 3.6s ease-in-out infinite; }
            .empty-state h3 { margin-bottom: 0.35rem; font-weight: 750; color: #0f172a; }

            /* ---------- Inputs ---------- */
            .stButton > button {
                background: linear-gradient(135deg, #4f46e5, #6d5bf0);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0.75rem 1rem;
                font-weight: 750;
                box-shadow: 0 10px 24px rgba(79, 70, 229, 0.24);
                transition: transform 160ms ease, box-shadow 160ms ease;
            }
            .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 14px 28px rgba(79, 70, 229, 0.28); }

            div[data-testid="stTextInput"] > div > div > input,
            div[data-testid="stTextArea"] > div > div > textarea,
            div[data-testid="stNumberInput"] > div > div > input,
            div[data-testid="stSelectbox"] > div > div > div,
            div[data-testid="stDateInput"] > div > div > input {
                border-radius: 12px;
                border: 1px solid rgba(15, 23, 42, 0.1);
                padding: 0.65rem 0.8rem;
                background: #ffffff;
            }
            div[data-testid="stTextInput"] > div > div > input:focus,
            div[data-testid="stTextArea"] > div > div > textarea:focus,
            div[data-testid="stNumberInput"] > div > div > input:focus {
                border-color: #4f46e5;
                box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
            }

            .stDownloadButton > button {
                width: 100%;
                border-radius: 12px;
                border: none;
                background: #0f172a;
                color: white;
                padding: 0.7rem 1rem;
                font-weight: 700;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 4px;
                background: rgba(255,255,255,0.7);
                padding: 6px;
                border-radius: 14px;
                border: 1px solid rgba(15,23,42,0.06);
            }
            .stTabs [data-baseweb="tab"] {
                border-radius: 10px;
                padding: 0.5rem 1rem;
                font-weight: 650;
                color: #475569;
            }
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, #4f46e5, #6d5bf0) !important;
                color: white !important;
            }

            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #0f172a; }
            .stDataFrame, table { border-radius: 12px; overflow: hidden; }
            .stAlert { border-radius: 14px; }

            ::-webkit-scrollbar { width: 8px; height: 8px; }
            ::-webkit-scrollbar-thumb { background: rgba(148, 163, 184, 0.5); border-radius: 999px; }

            @keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-8px); } }
            @keyframes fadeUp { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Sidebar (only "Plan New Trip" is a real, working destination — the rest
# of the app is a single flow, so the other nav items are intentionally
# shown as disabled / "Soon" rather than faked as working pages)
# --------------------------------------------------------------------------
def render_sidebar() -> None:
    st.markdown('<div class="app-sidebar">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sb-logo">
            <div class="sb-logo-badge">🧳</div>
            <div>
                <div class="sb-logo-title">AI Travel Planner</div>
                <div class="sb-logo-sub">Your smart travel companion ✈</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="nav-active">', unsafe_allow_html=True)
    st.button("✨  Plan New Trip", disabled=True, use_container_width=True, key="nav_plan")
    st.markdown("</div>", unsafe_allow_html=True)

    other_nav = [
        ("🗂", "My Trips"),
        ("📍", "Destinations"),
        ("🗓", "Itinerary"),
        ("💼", "Budget Planner"),
        ("📖", "Travel Guide"),
        ("⚙️", "Settings"),
    ]
    for icon, label in other_nav:
        st.button(f"{icon}  {label}", disabled=True, use_container_width=True, key=f"nav_{label}")
        st.markdown('<div class="nav-soon">SOON</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
def render_header() -> None:
    st.markdown(
        """
        <div class="greeting-row">
            <h1>Welcome 👋</h1>
            <p>Where are we planning your next adventure?</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_hero_banner() -> None:
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-banner-inner">
                <h2>Explore. Dream. Discover.</h2>
                <p>AI-powered travel planning made simple and personalized.</p>
                <a class="hero-cta" href="#trip-form">Plan Your Trip ✨</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats_row() -> None:
    """Small stat tiles built only from real, session-derived values —
    no fabricated aggregate numbers."""
    last_meta = st.session_state.get("last_meta") or {}
    stats = [
        ("🧭", "#eef2ff", st.session_state.get("plans_generated", 0), "Plans Generated", "This session"),
        ("📍", "#ecfdf5", last_meta.get("destination", "—"), "Last Destination", "Most recent plan"),
        ("💰", "#fffbeb", f"₹{st.session_state.get('budget', 0):,}", "Budget Set", "Current form value"),
        ("👥", "#fdf2f8", st.session_state.get("travelers", 1), "Travelers", "Current form value"),
    ]
    st.markdown('<div class="stat-tile-grid">', unsafe_allow_html=True)
    for icon, bg, value, label, sub in stats:
        st.markdown(
            f"""
            <div class="stat-tile">
                <div class="stat-tile-icon" style="background:{bg};">{icon}</div>
                <div>
                    <div class="stat-tile-value">{value}</div>
                    <div class="stat-tile-label">{label}</div>
                    <div class="stat-tile-sub">{sub}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Trip form (all backend wiring unchanged — session-state keys identical)
# --------------------------------------------------------------------------
def render_trip_form() -> bool:
    """Render the trip details card and return whether generation was requested."""
    defaults = {
        "destination": "",
        "departure_city": "",
        "start_date": None,
        "end_date": None,
        "budget": 50000,
        "travelers": 1,
        "destination_type": "city",
        "trip_type": "domestic",
        "interests": "",
        "use_structured": True,
        "free_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.markdown('<div id="trip-form"></div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="card form-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">✨ Plan a New Trip</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.text_input("📍 Destination", key="destination", placeholder="e.g. Tokyo, Japan")
            st.text_input("✈ Departure City", key="departure_city", placeholder="e.g. New Delhi")
            st.date_input("📅 Departure Date", key="start_date")

        with col2:
            st.number_input(
                "💰 Budget (₹)", min_value=1000, step=1000,
                value=st.session_state.budget, key="budget",
            )
            st.number_input(
                "👨‍👩‍👧 Travelers", min_value=1, max_value=20,
                value=st.session_state.travelers, key="travelers",
            )
            st.date_input("📅 Return Date", key="end_date")

        render_destination_quickpicks()

        st.selectbox("🌎 Trip Type", ["domestic", "international"], key="trip_type")
        st.text_input(
            "❤️ Interests", key="interests",
            placeholder="e.g. food, adventure, nature, culture",
        )
        render_interest_badges(st.session_state.interests)

        st.text_area(
            "📝 Describe what you're looking for",
            key="free_text",
            placeholder="e.g. Plan a 5-day trip to Tokyo in October for 2 people, interested in food and culture.",
            height=130,
        )
        st.checkbox("Build request from these fields", key="use_structured")

        generate = st.button("✨ Generate AI Itinerary", type="primary", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return generate


def render_destination_quickpicks() -> None:
    """Quick-select chips that set the same destination_type used by the form."""
    st.markdown('<div class="metric-label" style="margin-top:0.2rem;">🏕 Destination Type</div>', unsafe_allow_html=True)
    options = list(DESTINATION_THEME.keys())
    cols = st.columns(len(options))
    for col, option in zip(cols, options):
        _, _, icon = DESTINATION_THEME[option]
        selected = st.session_state.destination_type == option
        css_class = "quickpick-selected" if selected else "quickpick-btn"
        with col:
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(f"{icon}\n{option.title()}", key=f"quickpick_{option}", use_container_width=True):
                st.session_state.destination_type = option
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def render_interest_badges(interests_text: str) -> None:
    """Render colored badges for whatever interests the user has typed so far."""
    items = [i.strip() for i in interests_text.split(",") if i.strip()]
    if not items:
        return
    html = ['<div class="badge-row">']
    for item in items:
        bg, fg, icon = INTEREST_COLORS.get(item.lower(), DEFAULT_BADGE)
        html.append(
            f'<span class="badge" style="background:{bg};color:{fg};">{icon} {item.title()}</span>'
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)


def render_tips_panel() -> None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💡 Smart Travel Tips</div>', unsafe_allow_html=True)
    for icon, title, sub in GENERIC_TRAVEL_TIPS:
        st.markdown(
            f"""
            <div class="tip-item">
                <div class="tip-icon">{icon}</div>
                <div>
                    <div class="tip-title">{title}</div>
                    <div class="tip-sub">{sub}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_cta_banner() -> None:
    st.markdown(
        """
        <div class="cta-banner">
            <div class="cta-left">
                <div class="cta-icon">✨</div>
                <div>
                    <div class="cta-title">Let AI create your perfect itinerary</div>
                    <div class="cta-sub">Fill in your trip details and get a personalized, day-by-day plan.</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<a class="hero-cta" style="background:#0f172a;color:white;" href="#trip-form">Start Planning Now ✨</a>',
        unsafe_allow_html=True,
    )


def build_user_input() -> str:
    """Build the user prompt from the structured fields while keeping the backend flow intact."""
    if st.session_state.use_structured:
        parts = []

        if st.session_state.departure_city:
            parts.append(f"Departure City: {st.session_state.departure_city}")

        if st.session_state.destination:
            parts.append(f"Destination: {st.session_state.destination}")

        if st.session_state.start_date and st.session_state.end_date:
            days = (st.session_state.end_date - st.session_state.start_date).days
            parts.append(f"Departure Date: {st.session_state.start_date}")
            parts.append(f"Return Date: {st.session_state.end_date}")
            parts.append(f"Trip Duration: {days} days")

        parts.append(f"Budget: ₹{st.session_state.budget}")
        parts.append(f"Number of Travelers: {st.session_state.travelers}")
        parts.append(f"Destination Type: {st.session_state.destination_type}")
        parts.append(f"Trip Type: {st.session_state.trip_type}")

        if st.session_state.interests:
            parts.append(f"Interests: {st.session_state.interests}")

        if st.session_state.free_text.strip():
            parts.append(f"Additional Requirements: {st.session_state.free_text.strip()}")

        return "\n".join(parts)

    return st.session_state.free_text.strip()


# --------------------------------------------------------------------------
# Parsing helpers (frontend-only; no fabricated data, only reshaping the
# AI response text that the backend already returned)
# --------------------------------------------------------------------------
def extract_section(response: str, keywords: list[str]) -> str | None:
    """Extract a section from the markdown response based on heading keywords."""
    pattern = r"^#{1,4}\s*(.+?)\s*$"
    matches = list(re.finditer(pattern, response, re.M))

    for index, match in enumerate(matches):
        heading = match.group(1).lower()
        if any(keyword in heading for keyword in keywords):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(response)
            section = response[start:end].strip()
            return section or None
    return None


def split_into_days(itinerary_text: str) -> list[tuple[str, str]]:
    """Split a day-wise itinerary block into (day title, day content) pairs."""
    if not itinerary_text:
        return []
    pattern = re.compile(r"(?im)^.*\bday\s*\d+\b.*$")
    matches = list(pattern.finditer(itinerary_text))
    if not matches:
        return [("Itinerary", itinerary_text)]

    days = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(itinerary_text)
        title = re.sub(r"[#*_:\-]+", " ", match.group(0)).strip()
        body = itinerary_text[start:end].strip()
        if body:
            days.append((title, body))
    return days or [("Itinerary", itinerary_text)]


def extract_budget_table(budget_text: str) -> list[tuple[str, str]]:
    """Try to pull (label, amount) rows out of the budget section for a styled table."""
    if not budget_text:
        return []
    rows = []
    for line in budget_text.splitlines():
        match = re.match(r"^[-*]?\s*\**([\w \/&']+?)\**\s*[:\-]\s*₹?\s*([\d,]+(?:\s?-\s?₹?\s?[\d,]+)?)\s*$", line.strip())
        if match:
            label, amount = match.groups()
            rows.append((label.strip(), amount.strip()))
    return rows


def get_trip_meta(response: str) -> dict:
    """Pull the headline facts used in the trip-summary metric cards."""
    duration_match = re.search(r"Trip Duration:\s*(\d+)\s*days", response, re.I) or re.search(
        r"(\d+)\s*-?\s*[Dd]ay", response
    )
    best_time_match = re.search(r"Best [Tt]ime[^:\n]*:\s*(.+)", response)
    destination_match = extract_section(response, ["recommended destination"])
    if destination_match:
        name_match = re.search(r"\*{0,2}([A-Z][A-Za-z\s,]+)\*{0,2}", destination_match)
        destination_name = name_match.group(1).strip() if name_match else destination_match.splitlines()[0][:40]
    else:
        destination_name = st.session_state.get("destination") or "—"

    duration = None
    if st.session_state.get("start_date") and st.session_state.get("end_date"):
        duration = (st.session_state.end_date - st.session_state.start_date).days
    elif duration_match:
        duration = duration_match.group(1)

    return {
        "destination": destination_name or "—",
        "duration": f"{duration} days" if duration else "—",
        "budget": f"₹{st.session_state.get('budget', '—'):,}" if st.session_state.get("budget") else "—",
        "travelers": st.session_state.get("travelers", "—"),
        "best_time": best_time_match.group(1).strip()[:40] if best_time_match else "—",
    }


def get_packing_checklist(destination_type: str, trip_type: str) -> list[str]:
    """A rule-based packing checklist derived purely from the user's own selections."""
    base = ["Passport / ID & travel documents", "Phone charger & power bank", "Basic first-aid kit", "Reusable water bottle"]
    by_type = {
        "beach": ["Swimwear", "Sunscreen (SPF 50+)", "Flip-flops", "Light cotton clothing"],
        "mountain": ["Thermal layers", "Trekking shoes", "Windproof jacket", "Lip balm & moisturizer"],
        "city": ["Comfortable walking shoes", "Day backpack", "Portable umbrella"],
        "adventure": ["Quick-dry clothing", "Sturdy footwear", "Rain jacket", "Dry bag for electronics"],
        "wildlife": ["Neutral-colored clothing", "Binoculars", "Insect repellent", "Wide-brim hat"],
        "spiritual": ["Modest clothing to cover shoulders/knees", "Comfortable slip-on footwear"],
        "desert": ["Sunglasses & scarf", "Sunscreen", "Light long-sleeve clothing", "Extra water bottle"],
    }
    checklist = base + by_type.get(destination_type, [])
    if trip_type == "international":
        checklist += ["Valid visa / entry documents", "Universal power adapter", "Travel insurance copy"]
    return checklist


# --------------------------------------------------------------------------
# Results
# --------------------------------------------------------------------------
def render_metrics(meta: dict) -> None:
    metrics = [
        ("📍 Destination", meta["destination"]),
        ("📅 Duration", meta["duration"]),
        ("💰 Budget", meta["budget"]),
        ("👨‍👩‍👧 Travelers", meta["travelers"]),
        ("🌤 Best Time", meta["best_time"]),
    ]
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    for label, value in metrics:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_destination_hero(meta: dict) -> None:
    dest_type = st.session_state.get("destination_type", "city")
    color_a, color_b, icon = DESTINATION_THEME.get(dest_type, DESTINATION_THEME["city"])
    st.markdown(
        f"""
        <div class="dest-hero" style="background: linear-gradient(135deg, {color_a}, {color_b});">
            <span class="icon-badge">{icon}</span>
            <h2>{meta['destination']}</h2>
            <div class="sub">{meta['duration']} · {meta['travelers']} traveler(s) · Budget {meta['budget']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_card(title: str, content: str, icon: str = "") -> None:
    st.markdown(f'<div class="card"><h3>{icon} {title}</h3>', unsafe_allow_html=True)
    st.markdown(content if content else "_Not available for this trip._")
    st.markdown("</div>", unsafe_allow_html=True)


def render_overview_tab(response: str, meta: dict) -> None:
    render_destination_hero(meta)
    render_metrics(meta)

    interests = st.session_state.get("interests", "")
    if interests.strip():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3>❤️ Your Interests</h3>', unsafe_allow_html=True)
        render_interest_badges(interests)
        st.markdown("</div>", unsafe_allow_html=True)

    summary = extract_section(response, ["trip summary"])
    destination_reason = extract_section(response, ["recommended destination"])
    assumptions = extract_section(response, ["assumption"])
    weather = extract_section(response, ["weather"])
    attractions = extract_section(response, ["attraction"])

    render_card("Trip Summary", summary or (response.splitlines()[0] if response else ""), "🌍")
    if destination_reason:
        render_card("Why This Destination", destination_reason, "🧭")
    render_card("Assumptions", assumptions or "No assumptions were needed — all key details were provided.", "📌")
    render_card("Weather Forecast", weather or "Weather details will appear here once available.", "🌤")
    render_card("Top Attractions", attractions or "Attraction suggestions will appear here.", "📍")


def render_itinerary_tab(response: str) -> None:
    itinerary = extract_section(response, ["itinerary"])
    transport_section = extract_section(response, ["transport"])
    transport_matches = re.findall(r"Local Transport:\s*(.+)", response)
    transport_content = transport_section or (
        "\n".join(f"- {item.strip()}" for item in transport_matches if item.strip())
    )

    st.markdown('<div class="section-title">🗓 Day-wise Itinerary</div>', unsafe_allow_html=True)
    days = split_into_days(itinerary or "")
    if not days:
        st.info("A detailed day-by-day itinerary will appear here once generated.")
    else:
        for i, (title, body) in enumerate(days):
            label = title if title else f"Day {i + 1}"
            with st.expander(f"📅 {label}", expanded=(i == 0)):
                st.markdown(body)

    render_card("Transportation", transport_content or "Local transport suggestions will appear here.", "🚖")


def render_budget_tab(response: str) -> None:
    budget = extract_section(response, ["budget"])
    st.markdown('<div class="section-title">💰 Estimated Budget Breakdown</div>', unsafe_allow_html=True)

    rows = extract_budget_table(budget or "")
    if rows:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.table({"Category": [r[0] for r in rows], "Estimated Amount": [r[1] for r in rows]})
        st.markdown("</div>", unsafe_allow_html=True)
    elif budget:
        render_card("Estimated Budget", budget, "💰")
    else:
        st.info("A full cost breakdown will appear here once your plan is generated.")


def render_hotels_tab(response: str) -> None:
    hotels = extract_section(response, ["hotel"])
    render_card("Hotel Recommendations", hotels or "Hotel suggestions will appear here once generated.", "🏨")


def render_food_tab(response: str) -> None:
    food_matches = re.findall(r"Restaurant Suggestions:\s*(.+)", response)
    food_section = extract_section(response, ["food"])
    food_content = food_section or "\n".join(f"- {item.strip()}" for item in food_matches if item.strip())
    render_card("Local Food Recommendations", food_content or "Food recommendations will appear here.", "🍜")


def render_tips_tab(response: str) -> None:
    tips = extract_section(response, ["travel tips"])
    render_card("Travel Tips", tips or "Helpful travel notes will appear here.", "💡")

    checklist = get_packing_checklist(
        st.session_state.get("destination_type", "city"),
        st.session_state.get("trip_type", "domestic"),
    )
    checklist_md = "\n".join(f"- {item}" for item in checklist)
    render_card("Suggested Packing Checklist", checklist_md, "🎒")


def render_result_sections(response: str) -> None:
    st.markdown('<div class="section-title" style="font-size:1.3rem;">📋 Your Travel Plan</div>', unsafe_allow_html=True)
    meta = get_trip_meta(response)
    st.session_state.last_meta = meta

    tab_overview, tab_itinerary, tab_budget, tab_hotels, tab_food, tab_tips = st.tabs(
        ["🌍 Overview", "🗓 Itinerary", "💰 Budget", "🏨 Hotels", "🍜 Food", "💡 Tips"]
    )

    with tab_overview:
        render_overview_tab(response, meta)
    with tab_itinerary:
        render_itinerary_tab(response)
    with tab_budget:
        render_budget_tab(response)
    with tab_hotels:
        render_hotels_tab(response)
    with tab_food:
        render_food_tab(response)
    with tab_tips:
        render_tips_tab(response)


# --------------------------------------------------------------------------
# PDF export (frontend presentation only — reformats the existing response)
# --------------------------------------------------------------------------
def build_pdf(response: str) -> bytes | None:
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=22 * mm, bottomMargin=18 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleX", parent=styles["Title"], textColor=rl_colors.HexColor("#3730a3"))
    h_style = ParagraphStyle("HeadingX", parent=styles["Heading2"], textColor=rl_colors.HexColor("#0f172a"), spaceBefore=14)
    body_style = ParagraphStyle("BodyX", parent=styles["BodyText"], leading=16)
    bullet_style = ParagraphStyle("BulletX", parent=styles["BodyText"], leading=15, leftIndent=12)

    story = [Paragraph("AI Travel Planner — Your Trip Plan", title_style), Spacer(1, 10)]

    for raw_line in response.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 4))
            continue
        heading_match = re.match(r"^#{1,4}\s*(.+)$", line)
        if heading_match:
            story.append(HRFlowable(width="100%", color=rl_colors.HexColor("#e2e8f0")))
            story.append(Paragraph(heading_match.group(1), h_style))
            continue
        clean = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", line)
        if clean.startswith(("- ", "* ")):
            story.append(Paragraph(f"• {clean[2:]}", bullet_style))
        else:
            story.append(Paragraph(clean, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --------------------------------------------------------------------------
# Pipeline execution with a polished loading experience
# --------------------------------------------------------------------------
def run_pipeline_with_status(user_input: str) -> str:
    response_holder: dict[str, object] = {}
    done = threading.Event()

    def worker() -> None:
        try:
            response_holder["response"] = run_pipeline(user_input)
        except Exception as exc:
            response_holder["error"] = exc
        finally:
            done.set()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    pipeline_steps = [
        "Selecting destination",
        "Finding hotels",
        "Checking weather",
        "Discovering attractions",
        "Searching flights",
        "Building itinerary",
    ]
    step_icons = ["🧠", "🏨", "🌦", "📍", "✈", "📅"]

    with st.spinner(""):
        pipeline_placeholder = st.empty()
        progress_bar = st.progress(0)
        step = 0
        start_time = time.time()

        while not done.is_set():
            active_index = step % len(pipeline_steps)
            elapsed = time.time() - start_time
            render_pipeline_status(pipeline_placeholder, pipeline_steps, step_icons, active_index, elapsed)
            progress_bar.progress(min(95, (step + 1) * (100 // len(pipeline_steps))))
            step += 1
            time.sleep(0.8)

        render_pipeline_status(pipeline_placeholder, pipeline_steps, step_icons, len(pipeline_steps), time.time() - start_time)
        progress_bar.progress(100)
        time.sleep(0.4)

    pipeline_placeholder.empty()
    progress_bar.empty()

    if "error" in response_holder:
        raise response_holder["error"]

    return response_holder.get("response", "")


def render_pipeline_status(placeholder, steps: list[str], icons: list[str], active_index: int, elapsed: float) -> None:
    rows = []
    for i, (label, icon) in enumerate(zip(steps, icons)):
        if i < active_index:
            rows.append(f"<div class='tip-item'><div class='tip-icon' style='background:#ecfdf5;'>✅</div><div><div class='tip-title'>{label}</div><div class='tip-sub'>Done</div></div></div>")
        elif i == active_index:
            rows.append(f"<div class='tip-item'><div class='tip-icon' style='background:#eef2ff;'>{icon}</div><div><div class='tip-title'>{label}...</div><div class='tip-sub'>In progress</div></div></div>")
        else:
            rows.append(f"<div class='tip-item'><div class='tip-icon' style='background:#f8fafc;color:#94a3b8;'>{icon}</div><div><div class='tip-title' style='color:#94a3b8;'>{label}</div><div class='tip-sub'>Pending</div></div></div>")

    placeholder.markdown(
        f"""
        <div class="card">
            <div class="section-title">🧠 Crafting Your Itinerary <span style="margin-left:auto;font-weight:600;font-size:0.8rem;color:#64748b;">{elapsed:.0f}s elapsed</span></div>
            {''.join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
inject_css()

if "last_response" not in st.session_state:
    st.session_state.last_response = ""
if "plans_generated" not in st.session_state:
    st.session_state.plans_generated = 0
if "last_meta" not in st.session_state:
    st.session_state.last_meta = None

sidebar_col, main_col = st.columns([0.22, 0.78], gap="large")

with sidebar_col:
    render_sidebar()

with main_col:
    render_header()
    render_hero_banner()
    render_stats_row()

    generate = render_trip_form()
    render_tips_panel()

    if generate:
        user_input = build_user_input().strip()

        if not user_input:
            st.warning("Please enter your travel requirements before generating a plan.")
        else:
            response = None
            try:
                response = run_pipeline_with_status(user_input)
            except Exception as exc:
                st.error(f"Something went wrong while generating your plan:\n\n{exc}")

            if response:
                st.session_state.last_response = response
                st.session_state.plans_generated += 1
                st.success("Your personalized travel plan is ready! 🎉")
                st.rerun()

    if st.session_state.last_response:
        render_result_sections(st.session_state.last_response)
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">✈️</div>
                <h3>Ready for your next adventure?</h3>
                <p>Fill in your trip details above, hit generate, and watch a beautifully
                crafted itinerary come to life here.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_cta_banner()

    if st.session_state.last_response:
        st.markdown("### 📥 Export Your Plan")
        export_col1, export_col2 = st.columns(2)

        with export_col1:
            st.download_button(
                label="⬇ Download as .txt",
                data=st.session_state.last_response,
                file_name="travel_plan.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with export_col2:
            pdf_bytes = build_pdf(st.session_state.last_response)
            if pdf_bytes:
                st.download_button(
                    label="⬇ Download as PDF",
                    data=pdf_bytes,
                    file_name="travel_plan.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            else:
                st.info("Install `reportlab` (`pip install reportlab`) to enable PDF export.")

    st.markdown("---")
    st.caption("Powered by your multi-agent travel research pipeline.")
