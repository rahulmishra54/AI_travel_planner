from pydantic import BaseModel, Field
from langchain.tools import tool
from tools.tavily_client import tavily


class HotelInput(BaseModel):
    locations: list[str] = Field(
        description="List of locations or tourist areas where hotels should be searched."
    )

    budget_per_night: int = Field(
        description="Maximum hotel budget per night."
    )


@tool(args_schema=HotelInput)
def search_hotels(
    locations: list[str],
    budget_per_night: int,
):
    """
    Search hotels near the given tourist locations.

    Returns:
        A structured list of hotels including:
        - Hotel name
        - Nearby attraction/location
        - Price per night
        - Rating
        - Distance from attraction
        - Amenities
        - Booking link (if available)
    """

    return tavily.search(
        query=f"""
Find the best hotels near the following locations:

{", ".join(locations)}

Budget: Under ₹{budget_per_night} per night.

For each hotel include:
- Hotel name
- Nearby attraction/location
- Price per night
- Rating
- Distance from attraction
- Amenities
- Booking link if available

Return the response in a structured format.
""",
        max_results=5
    )