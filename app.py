import streamlit as st
from pipeline import run_pipeline

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🧳",
    layout="centered",
)

st.title("🧳 AI Travel Planner")
st.caption("Describe your trip and let the multi-agent system build your itinerary.")

# --- Sidebar: structured inputs (optional helpers) ---
with st.sidebar:
    st.header("Trip Details")

    destination = st.text_input(
        "Destination",
        placeholder="e.g. Tokyo, Japan"
    )

    departure_city = st.text_input(
        "Departure City",
        placeholder="e.g. New Delhi"
    )

    start_date = st.date_input("Departure Date")
    end_date = st.date_input("Return Date")

    budget = st.number_input(
        "Budget (₹)",
        min_value=1000,
        step=1000,
        value=50000
    )

    travelers = st.number_input(
        "Number of Travelers",
        min_value=1,
        max_value=20,
        value=1
    )

    destination_type = st.selectbox(
        "Destination Type",
        [
            "city",
            "beach",
            "mountain",
            "adventure",
            "wildlife",
            "spiritual",
            "desert"
        ]
    )

    trip_type = st.selectbox(
        "Trip Type",
        [
            "domestic",
            "international"
        ]
    )

    interests = st.text_input(
        "Interests",
        placeholder="e.g. food, hiking, museums"
    )

    use_structured = st.checkbox(
        "Build request from these fields",
        value=True
    )
st.subheader("Your Travel Requirements")

free_text = st.text_area(
    "Describe what you're looking for",
    placeholder="e.g. Plan a 5-day trip to Tokyo in October for 2 people, interested in food and culture.",
    height=150,
)

def build_user_input() -> str:
    if use_structured:
        parts = []

        if departure_city:
            parts.append(f"Departure City: {departure_city}")

        if destination:
            parts.append(f"Destination: {destination}")

        if start_date and end_date:
            days = (end_date - start_date).days
            parts.append(f"Departure Date: {start_date}")
            parts.append(f"Return Date: {end_date}")
            parts.append(f"Trip Duration: {days} days")

        parts.append(f"Budget: ₹{budget}")
        parts.append(f"Number of Travelers: {travelers}")
        parts.append(f"Destination Type: {destination_type}")
        parts.append(f"Trip Type: {trip_type}")

        if interests:
            parts.append(f"Interests: {interests}")

        if free_text.strip():
            parts.append(f"Additional Requirements: {free_text.strip()}")

        return "\n".join(parts)

    return free_text.strip()
generate = st.button("✈️ Generate Travel Plan", type="primary", use_container_width=True)

if generate:
    user_input = build_user_input().strip()

    if not user_input:
        st.warning("Please enter your travel requirements before generating a plan.")
    else:
        with st.spinner("Planning your trip... this may take a minute."):
            try:
                response = run_pipeline(user_input)
            except Exception as e:
                st.error(f"Something went wrong while generating your plan:\n\n{e}")
                response = None

        if response:
            st.subheader("📋 Your Travel Plan")
            st.markdown(response)

            st.download_button(
                label="Download plan as .txt",
                data=response,
                file_name="travel_plan.txt",
                mime="text/plain",
                use_container_width=True,
            )

st.markdown("---")
st.caption("Powered by your multi-agent travel research pipeline.")