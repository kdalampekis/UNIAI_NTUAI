# weather_tool.py
import os
from dotenv import load_dotenv  # load environment variables from .env file

# Load .env file contents into environment
load_dotenv()
import requests
from typing import List, Optional
from pydantic import BaseModel

# Base URL for the weather service
BASE_URL = ("https://weather.visualcrossing.com"
            "/VisualCrossingWebServices/rest/services/timeline")

class GetDailyForecastInput(BaseModel):
    city: str  # City name (e.g., "Athens,GR") or "lat,lon" format

class DailyForecast(BaseModel):
    datetime: str    # Date in YYYY-MM-DD format
    tempmin: float   # Minimum temperature (°C)
    tempmax: float   # Maximum temperature (°C)
    conditions: str  # Weather summary (e.g., "Partly Cloudy")

def get_daily_forecast(input: GetDailyForecastInput) -> Optional[List[DailyForecast]]:
    """
    Fetch the daily weather forecasts for the next period for a given city.

    Args:
        input.city: City name (e.g., "Athens,GR") or "lat,lon" format.

    Returns:
        A list of DailyForecast models, or None if the request failed.
    """
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("WEATHER_API_KEY environment variable is required")

    url = f"{BASE_URL}/{input.city}"
    params = {
        "unitGroup": "metric",  # Celsius output
        "key": api_key,          # API authentication
        "contentType": "json", # JSON response
        "include": "days"      # Only daily data
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Error fetching weather data: {e}")

    data = resp.json()
    days = data.get("days", [])
    forecasts: List[DailyForecast] = []
    for day in days:
        forecasts.append(
            DailyForecast(
                datetime=day["datetime"],
                tempmin=day["tempmin"],
                tempmax=day["tempmax"],
                conditions=day["conditions"],
            )
        )
    return forecasts