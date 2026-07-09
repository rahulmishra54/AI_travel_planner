from pydantic import BaseModel, Field
from typing import Literal
from langchain.tools import tool
from tools.tavily_client import tavily


class DestinationInput(BaseModel):
    """Input schema for destination recommendation."""

    budget: int = Field(description="Maximum trip budget")

    destination_type: Literal[
        "mountain",
        "beach",
        "city",
        "adventure",
        "wildlife",
        "spiritual",
        "desert"
    ] = Field(description="Preferred destination type")

    trip_type: Literal[
        "domestic",
        "international"
    ] = Field(description="Type of trip")

    days: int = Field(description="Number of travel days")


@tool(args_schema=DestinationInput)
def search_destinations(
    budget: int,
    destination_type: str,
    trip_type: str,
    days: int
):
    """
    Recommend the best travel destinations.

    Returns:
        A structured list of recommended destinations containing:
        - Destination name
        - Why it is recommended
        - Estimated trip budget
        - Best time to visit
        - Ideal trip duration
    """

    return tavily.search(
        query=f"""
Recommend the best {destination_type} destinations
for a {days}-day {trip_type} trip
under a budget of ₹{budget}.

For each destination include:

- Destination name
- Reason for recommendation
- Estimated total trip budget
- Best time to visit
- Ideal trip duration

Do NOT include tourist attractions.

Return the response in a structured format.
""",
        max_results=5
    )