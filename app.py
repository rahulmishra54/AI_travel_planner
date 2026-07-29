import re
import threading
import time

import streamlit as st
from pipeline import run_pipeline


st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🧳",
    layout="wide",
)


def inject_css() -> None:
    """Inject a polished SaaS-style visual theme for the app."""
    st.markdown(
        """
        <style>
            :root {
                color-scheme: light;
            }

            .stApp {
                background: linear-gradient(135deg, #f8fbff 0%, #f4f7ff 45%, #ffffff 100%);
            }

            .block-container {
                max-width: 1400px;
                padding-top: 1.2rem;
                padding-bottom: 3rem;
            }

            .hero-shell {
                background: linear-gradient(135deg, rgba(28, 60, 162, 0.98), rgba(55, 125, 255, 0.92));
                border-radius: 28px;
                padding: 1.6rem 1.7rem;
                margin-bottom: 1.3rem;
                color: white;
                box-shadow: 0 25px 60px rgba(26, 66, 168, 0.22);
                position: relative;
                overflow: hidden;
            }

            .hero-shell::before,
            .hero-shell::after {
                content: "";
                position: absolute;
                border-radius: 50%;
                filter: blur(14px);
                opacity: 0.4;
            }

            .hero-shell::before {
                width: 220px;
                height: 220px;
                background: rgba(255,255,255,0.18);
                top: -70px;
                right: -40px;
            }

            .hero-shell::after {
                width: 180px;
                height: 180px;
                background: rgba(255,255,255,0.12);
                bottom: -70px;
                left: -30px;
            }

            .hero-grid {
                display: grid;
                grid-template-columns: 1.05fr 0.95fr;
                align-items: center;
                gap: 1.2rem;
                position: relative;
                z-index: 1;
            }

            .hero-shell h1 {
                font-size: 2.2rem;
                margin-bottom: 0.35rem;
                font-weight: 800;
                letter-spacing: -0.03em;
            }

            .hero-shell p {
                font-size: 1rem;
                opacity: 0.95;
                margin-bottom: 1rem;
            }

            .pill-row {
                display: flex;
                flex-wrap: wrap;
                gap: 0.6rem;
            }

            .pill {
                background: rgba(255,255,255,0.16);
                border: 1px solid rgba(255,255,255,0.25);
                border-radius: 999px;
                padding: 0.42rem 0.8rem;
                font-size: 0.9rem;
                font-weight: 600;
                backdrop-filter: blur(10px);
            }

            .hero-visual {
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 250px;
            }

            .visual-shell {
                position: relative;
                width: 300px;
                height: 240px;
                border-radius: 24px;
                background: rgba(255,255,255,0.14);
                border: 1px solid rgba(255,255,255,0.22);
                backdrop-filter: blur(16px);
                box-shadow: inset 0 1px 0 rgba(255,255,255,0.2);
                overflow: hidden;
            }

            .orbit-globe {
                position: absolute;
                inset: 28px 35px 26px;
                border-radius: 50%;
                background: radial-gradient(circle at 30% 30%, #f8fbff 0%, #8fceff 32%, #2b73ff 70%, #153da8 100%);
                box-shadow: 0 0 45px rgba(255,255,255,0.2), inset -10px -10px 20px rgba(0,0,0,0.24);
                animation: float 5s ease-in-out infinite;
            }

            .orbit-globe::before {
                content: "";
                position: absolute;
                inset: 12px;
                border-radius: 50%;
                border: 2px solid rgba(255,255,255,0.22);
            }

            .plane {
                position: absolute;
                top: 28px;
                left: 34px;
                font-size: 1.5rem;
                animation: orbit 7s linear infinite;
                filter: drop-shadow(0 6px 10px rgba(0,0,0,0.18));
            }

            .cloud {
                position: absolute;
                font-size: 1.35rem;
                opacity: 0.85;
                animation: drift 9s linear infinite;
            }

            .cloud.one { top: 26px; right: 32px; }
            .cloud.two { bottom: 40px; left: 28px; animation-duration: 11s; }
            .cloud.three { bottom: 20px; right: 48px; animation-duration: 10s; }

            .card {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(15, 23, 42, 0.06);
                border-radius: 20px;
                padding: 1.1rem 1.15rem;
                box-shadow: 0 14px 40px rgba(15, 23, 42, 0.07);
                margin-bottom: 1rem;
                transition: transform 180ms ease, box-shadow 180ms ease;
                backdrop-filter: blur(12px);
                animation: fadeUp 0.65s ease both;
            }

            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 18px 44px rgba(15, 23, 42, 0.1);
            }

            .form-card {
                padding: 1.2rem 1.25rem;
                border-radius: 24px;
                box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
            }

            .section-card h3 {
                margin-top: 0;
                margin-bottom: 0.5rem;
                font-size: 1.05rem;
                font-weight: 700;
            }

            .section-card p,
            .section-card li {
                color: #334155;
                line-height: 1.6;
            }

            .section-card ul {
                padding-left: 1rem;
            }

            .metric-grid {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.8rem;
                margin-bottom: 1rem;
            }

            .metric-card {
                background: linear-gradient(135deg, #ffffff, #f7faff);
                border: 1px solid rgba(52, 112, 255, 0.12);
                border-radius: 16px;
                padding: 0.85rem 0.9rem;
                box-shadow: 0 8px 24px rgba(52, 112, 255, 0.08);
            }

            .metric-label {
                font-size: 0.8rem;
                color: #64748b;
                margin-bottom: 0.3rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }

            .metric-value {
                font-size: 1.05rem;
                font-weight: 700;
                color: #0f172a;
            }

            .empty-state {
                border: 1px solid rgba(148, 163, 184, 0.22);
                border-radius: 24px;
                padding: 2rem;
                text-align: center;
                color: #475569;
                background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(245,249,255,0.95));
                box-shadow: 0 18px 42px rgba(15, 23, 42, 0.06);
                position: relative;
                overflow: hidden;
            }

            .empty-state::before,
            .empty-state::after {
                content: "";
                position: absolute;
                border-radius: 50%;
                opacity: 0.28;
                filter: blur(12px);
            }

            .empty-state::before {
                width: 150px;
                height: 150px;
                background: #93c5fd;
                top: -40px;
                right: -25px;
            }

            .empty-state::after {
                width: 120px;
                height: 120px;
                background: #bfdbfe;
                bottom: -30px;
                left: -20px;
            }

            .empty-icon {
                font-size: 2.5rem;
                margin-bottom: 0.6rem;
                display: inline-block;
                animation: float 3.6s ease-in-out infinite;
            }

            .empty-state h3 {
                margin-bottom: 0.35rem;
                font-weight: 700;
                color: #0f172a;
            }

            .empty-state p {
                margin-top: 0.25rem;
                line-height: 1.6;
            }

            .stButton > button {
                background: linear-gradient(135deg, #2563eb, #3b82f6);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0.75rem 1rem;
                font-weight: 700;
                box-shadow: 0 10px 24px rgba(37, 99, 235, 0.2);
                transition: transform 180ms ease, box-shadow 180ms ease;
            }

            .stButton > button:hover {
                transform: translateY(-1px);
                box-shadow: 0 14px 28px rgba(37, 99, 235, 0.24);
            }

            div[data-testid="stTextInput"] > div > div > input,
            div[data-testid="stTextArea"] > div > div > textarea,
            div[data-testid="stNumberInput"] > div > div > input,
            div[data-testid="stSelectbox"] > div > div > div,
            div[data-testid="stDateInput"] > div > div > input {
                border-radius: 12px;
                border: 1px solid rgba(15, 23, 42, 0.1);
                padding: 0.7rem 0.8rem;
                background: #ffffff;
            }

            div[data-testid="stTextInput"] > div > div > input:focus,
            div[data-testid="stTextArea"] > div > div > textarea:focus,
            div[data-testid="stNumberInput"] > div > div > input:focus,
            div[data-testid="stSelectbox"] > div > div > div:focus,
            div[data-testid="stDateInput"] > div > div > input:focus {
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
            }

            .stDownloadButton > button {
                width: 100%;
                border-radius: 12px;
                border: none;
                background: #0f172a;
                color: white;
                padding: 0.7rem 1rem;
            }

            .stSidebar {
                background: transparent;
            }

            section[data-testid="stSidebar"] {
                background: rgba(255,255,255,0.72);
                backdrop-filter: blur(14px);
                border-right: 1px solid rgba(15, 23, 42, 0.06);
            }

            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
                color: #0f172a;
            }

            .stDataFrame, table {
                border-radius: 12px;
                overflow: hidden;
            }

            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }

            ::-webkit-scrollbar-thumb {
                background: rgba(148, 163, 184, 0.5);
                border-radius: 999px;
            }

            .stAlert {
                border-radius: 14px;
            }

            @keyframes float {
                0%, 100% { transform: translateY(0px); }
                50% { transform: translateY(-8px); }
            }

            @keyframes orbit {
                0% { transform: translate(-6px, -8px) rotate(0deg); }
                50% { transform: translate(18px, 8px) rotate(20deg); }
                100% { transform: translate(-6px, -8px) rotate(360deg); }
            }

            @keyframes drift {
                0% { transform: translateX(0px); opacity: 0.75; }
                50% { transform: translateX(10px); opacity: 1; }
                100% { transform: translateX(24px); opacity: 0.7; }
            }

            @keyframes fadeUp {
                from { opacity: 0; transform: translateY(8px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    """Render the premium hero section with an animated travel visualization."""
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-grid">
                <div>
                    <h1>🧳 AI Travel Planner</h1>
                    <p>Plan personalized trips with a multi-agent AI system that blends hotels, weather, flights, attractions, and itinerary planning into one seamless experience.</p>
                    <div class="pill-row">
                        <span class="pill">🏨 Hotels</span>
                        <span class="pill">🌤 Weather</span>
                        <span class="pill">✈ Flights</span>
                        <span class="pill">📍 Attractions</span>
                        <span class="pill">🗺 Itinerary</span>
                    </div>
                </div>
                <div class="hero-visual">
                    <div class="visual-shell">
                        <div class="orbit-globe"></div>
                        <div class="plane">✈</div>
                        <div class="cloud one">☁</div>
                        <div class="cloud two">☁</div>
                        <div class="cloud three">☁</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_trip_form() -> bool:
    """Render the trip details card and return whether generation was requested."""
    with st.container():
        st.markdown('<div class="card form-card">', unsafe_allow_html=True)
        st.markdown("### 📍 Trip Details")

        if "destination" not in st.session_state:
            st.session_state.destination = ""
        if "departure_city" not in st.session_state:
            st.session_state.departure_city = ""
        if "start_date" not in st.session_state:
            st.session_state.start_date = None
        if "end_date" not in st.session_state:
            st.session_state.end_date = None
        if "budget" not in st.session_state:
            st.session_state.budget = 50000
        if "travelers" not in st.session_state:
            st.session_state.travelers = 1
        if "destination_type" not in st.session_state:
            st.session_state.destination_type = "city"
        if "trip_type" not in st.session_state:
            st.session_state.trip_type = "domestic"
        if "interests" not in st.session_state:
            st.session_state.interests = ""
        if "use_structured" not in st.session_state:
            st.session_state.use_structured = True
        if "free_text" not in st.session_state:
            st.session_state.free_text = ""

        col1, col2 = st.columns(2)
        with col1:
            st.text_input(
                "📍 Destination",
                key="destination",
                placeholder="e.g. Tokyo, Japan",
            )
            st.text_input(
                "✈ Departure City",
                key="departure_city",
                placeholder="e.g. New Delhi",
            )
            st.date_input("📅 Departure Date", key="start_date")

        with col2:
            st.number_input(
                "💰 Budget (₹)",
                min_value=1000,
                step=1000,
                value=st.session_state.budget,
                key="budget",
            )
            st.number_input(
                "👨‍👩‍👧 Travelers",
                min_value=1,
                max_value=20,
                value=st.session_state.travelers,
                key="travelers",
            )
            st.date_input("📅 Return Date", key="end_date")

        st.selectbox(
            "🏕 Destination Type",
            ["city", "beach", "mountain", "adventure", "wildlife", "spiritual", "desert"],
            key="destination_type",
        )
        st.selectbox(
            "🌎 Trip Type",
            ["domestic", "international"],
            key="trip_type",
        )
        st.text_input(
            "❤️ Interests",
            key="interests",
            placeholder="e.g. food, hiking, museums",
        )
        st.text_area(
            "📝 Describe what you're looking for",
            key="free_text",
            placeholder="e.g. Plan a 5-day trip to Tokyo in October for 2 people, interested in food and culture.",
            height=140,
        )
        st.checkbox("Build request from these fields", key="use_structured")

        generate = st.button("✨ Generate AI Itinerary", type="primary", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)
        return generate


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


def render_metrics(response: str) -> None:
    """Render compact metric cards above the itinerary content."""
    budget_match = re.search(r"(?:Budget|Total Estimated Budget|₹)([\d,]+)", response)
    duration_match = re.search(r"Trip Duration:\s*(\d+)\s*days", response, re.I)
    if not duration_match:
        duration_match = re.search(r"(\d+)\s*Days", response)

    weather_match = re.search(r"Weather Condition:\s*(.+)", response)
    if not weather_match:
        weather_match = re.search(r"Temperature:\s*(.+)", response)

    hotels_match = re.findall(r"\*\s+\*\*.+?\*\*", response)
    hotel_count = len(hotels_match) if hotels_match else "5+"

    metrics = [
        ("💰 Budget", f"₹{budget_match.group(1) if budget_match else '—'}"),
        ("📅 Duration", f"{duration_match.group(1) if duration_match else '?'} days"),
        ("🌤 Weather", weather_match.group(1).strip()[:40] if weather_match else "—"),
        ("🏨 Hotels Found", str(hotel_count)),
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


def render_section_card(title: str, content: str) -> None:
    """Render a single content card with polished spacing and a subtle entrance animation."""
    st.markdown(f"<div class=\"card section-card\"><h3>{title}</h3>", unsafe_allow_html=True)
    st.markdown(content)
    st.markdown("</div>", unsafe_allow_html=True)


def extract_section(response: str, keywords: list[str]) -> str | None:
    """Extract a section from markdown response based on heading keywords."""
    pattern = r"^###\s+(.+)$"
    matches = list(re.finditer(pattern, response, re.M))

    for index, match in enumerate(matches):
        heading = match.group(1).lower()
        if any(keyword in heading for keyword in keywords):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(response)
            section = response[start:end].strip()
            return section or None

    return None


def render_result_sections(response: str) -> None:
    """Render the travel plan as distinct UI cards."""
    st.subheader("📋 Your Travel Plan")
    render_metrics(response)

    summary = extract_section(response, ["trip summary"])
    assumptions = extract_section(response, ["assumption"])
    weather = extract_section(response, ["weather"])
    hotels = extract_section(response, ["hotel"])
    attractions = extract_section(response, ["attraction"])
    itinerary = extract_section(response, ["itinerary"])
    budget = extract_section(response, ["budget"])
    food_matches = re.findall(r"Restaurant Suggestions:\s*(.+)", response)
    food_content = "\n".join(f"- {item.strip()}" for item in food_matches if item.strip())
    transport_matches = re.findall(r"Local Transport:\s*(.+)", response)
    transport_content = "\n".join(f"- {item.strip()}" for item in transport_matches if item.strip())
    tips = extract_section(response, ["travel tips"])

    sections = [
        ("🌍 Trip Summary", summary or response.splitlines()[0] if response else "Your travel plan is ready."),
        ("📌 Assumptions", assumptions or "The itinerary is built from your travel preferences, estimated availability, and budget range."),
        ("🌤 Weather", weather or "Weather guidance will appear here based on your selected destination and trip dates."),
        ("🏨 Hotels", hotels or "Hotel suggestions will appear here once the itinerary is generated."),
        ("📍 Attractions", attractions or "Popular attractions and experiences will appear here."),
        ("🗓 Day-wise Itinerary", itinerary or "A detailed day-by-day itinerary will appear here."),
        ("💰 Estimated Budget", budget or "Estimated costs will be summarized here."),
        ("🍜 Food Recommendations", food_content or "Food recommendations will be highlighted here."),
        ("🚖 Transportation", transport_content or "Transportation suggestions will be listed here."),
        ("💡 Travel Tips", tips or "Helpful travel notes and preparation tips will be shown here."),
    ]

    for title, content in sections:
        render_section_card(title, content)


def run_pipeline_with_status(user_input: str) -> str:
    """Run the pipeline while showing a polished loading experience."""
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

    with st.spinner("Crafting your itinerary..."):
        status_placeholder = st.empty()
        messages = [
            "🧠 Selecting destination...",
            "🏨 Finding hotels...",
            "🌦 Checking weather...",
            "📍 Discovering attractions...",
            "✈ Searching flights...",
            "📅 Building itinerary...",
        ]

        while not done.is_set():
            for message in messages:
                if done.is_set():
                    break
                status_placeholder.info(message)
                time.sleep(0.8)

    if "error" in response_holder:
        raise response_holder["error"]

    return response_holder.get("response", "")


inject_css()
render_header()

left_col, right_col = st.columns([0.95, 1.05], gap="large")
with left_col:
    generate = render_trip_form()

with right_col:
    if "last_response" not in st.session_state:
        st.session_state.last_response = ""

    if st.session_state.last_response:
        render_result_sections(st.session_state.last_response)
    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">✈️</div>
                <h3>Ready for your next adventure?</h3>
                <p>Fill in your trip details, hit the button, and watch a beautifully crafted itinerary come to life.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

if generate:
    user_input = build_user_input().strip()

    if not user_input:
        st.warning("Please enter your travel requirements before generating a plan.")
    else:
        try:
            response = run_pipeline_with_status(user_input)
        except Exception as exc:
            st.error(f"Something went wrong while generating your plan:\n\n{exc}")
            response = None

        if response:
            st.session_state.last_response = response
            render_result_sections(response)

            st.download_button(
                label="Download plan as .txt",
                data=response,
                file_name="travel_plan.txt",
                mime="text/plain",
                use_container_width=True,
            )

st.markdown("---")
st.caption("Powered by your multi-agent travel research pipeline.")