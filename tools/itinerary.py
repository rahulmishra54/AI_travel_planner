from pydantic import BaseModel, Field
from langchain.tools import tool


class ItineraryInput(BaseModel):
    destination: str = Field(
        description="Selected travel destination."
    )

    days: int = Field(
        description="Number of travel days."
    )

    interests: str = Field(
        description="Traveler interests such as adventure, food, nature, shopping, etc."
    )

    attractions: str = Field(
        description="Tourist attractions recommended by the Places Tool."
    )

    weather: str = Field(
        description="Weather forecast returned by the Weather Tool."
    )

    hotels: str = Field(
        description="Recommended hotels returned by the Hotel Tool."
    )


@tool(args_schema=ItineraryInput)
def generate_itinerary(
    destination: str,
    days: int,
    interests: str,
    attractions: str,
    weather: str,
    hotels: str,
):
    """
    Generate a personalized day-wise travel itinerary.

    Returns:
    - Day-wise itinerary
    - Morning, Afternoon and Evening activities
    - Recommended attractions
    - Recommended hotel for each day
    - Restaurant suggestions
    - Local transport suggestions
    - Weather-based travel advice
    - Daily travel tips
    """

    return f"""
Generate a complete {days}-day travel itinerary.

Destination:
{destination}

Traveler Interests:
{interests}

Tourist Attractions:
{attractions}

Weather Forecast:
{weather}

Recommended Hotels:
{hotels}

For each day include:

- Morning activities
- Afternoon activities
- Evening activities
- Attractions to visit
- Recommended hotel
- Breakfast, lunch and dinner suggestions
- Local transport
- Estimated daily budget
- Weather precautions
- Travel tips

Return the itinerary in a clear day-wise structured format.
"""