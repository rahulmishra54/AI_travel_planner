from pydantic import BaseModel, Field
from langchain.tools import tool
from tools.tavily_client import tavily


class WeatherInput(BaseModel):
    locations: list[str] = Field(
        description="List of tourist locations whose weather should be checked."
    )

    travel_dates: str = Field(
        description="Travel dates or date range for the weather forecast (e.g. '15 July to 21 July')."
    )


@tool(args_schema=WeatherInput)
def search_weather(
    locations: list[str],
    travel_dates: str,
):
    """
    Get weather forecasts for tourist locations during the user's travel dates.

    Returns:
    - Location
    - Weather for the specified dates
    - Temperature
    - Rain probability
    - Weather condition
    - Travel advice
    """

    return tavily.search(
        query=f"""
Provide the weather forecast for the following locations
during {travel_dates}:

{", ".join(locations)}

For each location include:
- Date
- Temperature
- Weather condition
- Rain probability
- Travel advice

Return the response in a structured format.
""",
        max_results=5
    )