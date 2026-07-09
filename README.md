# 🧳 AI Travel Planner

An AI-powered multi-agent travel planning application that generates personalized travel itineraries based on user preferences. The system uses multiple AI tools to recommend destinations, search for flights and hotels, check weather conditions, discover tourist attractions, estimate trip budgets, and create detailed day-wise travel plans.

## ✨ Features

- 🌍 Destination recommendations based on budget and preferences
- ✈️ Flight search
- 🏨 Hotel recommendations
- 🌦️ Weather forecasting
- 📍 Tourist attraction discovery
- 📅 Day-wise travel itinerary generation
- 💰 Budget estimation
- 📝 Personalized travel recommendations
- 🤖 AI-powered multi-agent workflow

## 🛠️ Tech Stack

- Python
- LangChain
- Streamlit
- Ollama / Groq
- Tavily Search API
- Pydantic

## 📂 Project Structure

```
ai_travel_planner/
│── app.py
│── pipeline.py
│── agent.py
│── prompts.py
│── llm.py
│
├── tools/
│   ├── destination_tool.py
│   ├── flight_tool.py
│   ├── hotel_tool.py
│   ├── places_tool.py
│   ├── weather_tool.py
│   └── itinerary_tool.py
│
├── prompts/
├── assets/
└── requirements.txt
```

## 🚀 Installation

Clone the repository

```bash
git clone https://github.com/your-username/ai_travel_planner.git
cd ai_travel_planner
```

Create a virtual environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run app.py
```

## 📌 How It Works

1. User provides travel details.
2. The AI analyzes the travel requirements.
3. Destination recommendations are generated (if required).
4. Flights, hotels, weather, and tourist attractions are retrieved.
5. A personalized day-wise itinerary is created.
6. Budget estimation and travel tips are included in the final response.

## 📸 Preview

Add screenshots of the application here.
<img width="973" height="419" alt="image" src="https://github.com/user-attachments/assets/ff81d855-aff5-41ad-a845-1a3fd8e952f3" />


## Future Improvements

- Google Maps integration
- Live flight pricing
- Hotel booking integration
- Visa information
- Currency conversion
- PDF itinerary download
- Email itinerary sharing

## License

This project is licensed under the MIT License.
