from pydantic import BaseModel, Field
from langchain.tools import tool
from tools.tavily_client import tavily


class PlacesInput(BaseModel):
    """Input schema for tourist attractions."""

    city: str = Field(
        description="Destination city for which tourist attractions are required."
    )


@tool(args_schema=PlacesInput)
def search_places(city: str):
    """
    Find the top tourist attractions for a destination.

    Returns:
        A structured list of attractions containing:
        - Attraction name
        - Exact area/location
        - Short description
        - Entry fee
        - Best visiting time
        - Time required to explore
        - Category (Adventure, Nature, Temple, Shopping, Museum, etc.)
    """

    return tavily.search(
        query=f"""
Find the top tourist attractions in {city}.

For each attraction provide:

- Attraction name
- Exact area/location
- Short description
- Entry fee
- Best visiting time
- Time required to explore
- Category (Adventure, Nature, Temple, Shopping, Museum, etc.)

Return the response in a structured format.
""",
        max_results=5
    )