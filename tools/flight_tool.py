from pydantic import BaseModel, Field
from langchain.tools import tool
from tools.tavily_client import tavily


class FlightInput(BaseModel):
    source: str

    destination: str

    departure_date: str


@tool(args_schema=FlightInput)
def search_flights(
    source: str,
    destination: str,
    departure_date: str
):
    """Search flights."""

    return tavily.search(
        query=f"""
Find flights from {source}
to {destination}
on {departure_date}.

Include:
- Airline
- Approximate fare
- Duration
- Departure time
""",
        max_results=5
    )