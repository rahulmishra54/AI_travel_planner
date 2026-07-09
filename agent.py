from langchain.agents import create_agent
from llm import get_llm
from tools.flight_tool import search_flights
from tools.places_tool import search_places
from tools.destination_tool import search_destinations
from tools.itinerary import generate_itinerary
from tools.weather_tool import search_weather
from tools.hotel_tool import search_hotels
def run_agent(prompt:str):
    llm = get_llm()
    tools = [search_flights, search_places, search_destinations, generate_itinerary, search_weather, search_hotels]
    agent = create_agent(model=llm, tools=tools)
    response = agent.invoke(prompt)
    return response