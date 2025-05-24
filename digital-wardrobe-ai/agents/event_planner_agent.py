import asyncio
from dotenv import load_dotenv  # load environment variables from .env file
load_dotenv()
import requests
import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..')))
from utils.weather_data_tool import get_daily_forecast, DailyForecast
from utils.clothes_search import get_serpi_clothes_search
from typing import Optional, List
from pydantic_ai import Agent
from pydantic_ai.messages import FunctionToolCallEvent, FunctionToolResultEvent, FinalResultEvent

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent


class ResponseModel(BaseModel):
    # Upfront identification of needed clothes
    needed_clothes: List[str] = Field(..., description="List of clothing item names the user needs.")
    # Weather forecast data
    forecast: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Weather forecast info if get_daily_forecast was used."
    )
    # Final narrative after searches
    text: str = Field(..., description="Narrative summary, including weather and clothing recommendations.")
    # Clothing search results filled in by code
    clothing_options: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Mapping from clothing item to list of options (title, price, photo, link)."
    )

class EventPlanner:
    def __init__(self, model: str = "openai:gpt-4.1"):
        # Agent only for weather and identification
        self.agent = Agent(
            model=model,
            system_prompt=(
                "You are an event planning assistant. "
                "Extract the list of clothing items the user needs for their event as `needed_clothes`. "
                "If the user provides a city and date, also provide a `forecast` dict via get_daily_forecast(city, date). "
                "Output only JSON conforming to ResponseModel fields: needed_clothes and optional forecast."
                "*Important*: "
                "       - The person is either Male of Female, understand from the input and choose clothes respectively"
                "       - Each item must be distinct (no 'shoes or sneakers' search)            "
                "       - The items needed combined should make a comprehensive outfit, it should include a styling part (for example not a suit and jeans toghether)"
                "       - Keep the number of clothes up to 5"
            ),
            tools=[get_daily_forecast],
            output_type=ResponseModel
        )
        self.photos: List[str] = []

    def find_clothes(self, query: str) -> ResponseModel:
        # 1. Ask the agent to identify needed clothes (and forecast)
        initial = self.agent.run_sync(query).output

        print(f"The initial call: {initial}")
    
        # 2. For each needed clothing item, perform a SerpAPI search
        options: Dict[str, List[Dict[str, Any]]] = {}
        for item in initial.needed_clothes:
            search_resp = get_serpi_clothes_search(item)
            # convert Pydantic models to dicts if needed
            opts = [r.model_dump() if hasattr(r, 'model_dump') else r for r in search_resp.results]
            options[item] = opts

        # 3. Build narrative text including weather and items
        lines: List[str] = []
        if initial.forecast:
            lines.append(f"Weather forecast: {initial.forecast}")
        for item, opts in options.items():
            lines.append(f"Options for {item}:")
            for o in opts:
                lines.append(f"- {o.get('title')} at {o.get('price')}")
            lines.append("")
        narrative = "\n".join(lines)

        # 4. Store photos
        self.photos = []
        for opts in options.values():
            for o in opts:
                photo = o.get('photo') or o.get('thumbnail')
                if photo:
                    self.photos.append(photo)

        print(self.photos)

        # 5. Return full ResponseModel
        return ResponseModel(
            needed_clothes=initial.needed_clothes,
            forecast=initial.forecast,
            text=narrative,
            clothing_options=options
        )

# if __name__ == "__main__":
#     planner = EventPlanner()
#     response = planner.find_clothes("I have a wedding in Athens on June 14th")
#     print("**"*20)
#     print(response.clothing_options)