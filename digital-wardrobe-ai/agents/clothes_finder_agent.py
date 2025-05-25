import asyncio
from dotenv import load_dotenv  # load environment variables from .env file
load_dotenv()
import requests
import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..')))
from utils.weather_data_tool import get_daily_forecast, DailyForecast
from utils.clothes_search import get_serpi_clothes_search
from utils.image_generation import create_outfit
from typing import Optional, List
from pydantic_ai import Agent
from pydantic_ai.messages import FunctionToolCallEvent, FunctionToolResultEvent, FinalResultEvent

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from pydantic_ai import Agent

class ClothingItem(BaseModel):
    gender: str = Field(..., description="Gender of the proposed item")
    color: str = Field(..., description="Primary color of the clothing item")
    type: str = Field(..., description="Type of clothing, e.g., 'shirt', 'trousers', 'jacket'")
    brand: Optional[str] = Field(None, description="Preferred brand or leave None for any")
    tags: List[str] = Field(default_factory=list, description="Additional style tags, e.g., ['formal', 'summer', 'lightweight']")

    def to_string(self) -> str:
        """Return a concise description of the clothing item."""
        brand_part = f" by {self.brand}" if self.brand else ""
        tags_part = f" [{', '.join(self.tags)}]" if self.tags else ""
        return f"{self.color.capitalize()} {self.type}{brand_part} for {self.gender}{tags_part}"



class ResponseModel(BaseModel):
    # Upfront identification of needed clothes with structured fields
    needed_clothes: List[ClothingItem] = Field(
        ..., description="List of structured clothing items the user needs."
    )
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

class ClothesFinder:
    def __init__(self, model: str = "openai:gpt-4.1"):
        # Agent only for weather and identification
        self.agent = Agent(
            model=model,
            system_prompt=(
                "You are an event planning assistant. "
                "Extract the list of clothing items the user needs as `needed_clothes`. "
                "Each item must include fields: color, type, brand (optional), and tags. "
                "If the user provides a city and date, also provide a `forecast` dict via get_daily_forecast(city, date). "
                "Output only JSON conforming to the updated ResponseModel fields. "
                "Important: The person is either Male or Female; choose items accordingly; items combined should form a cohesive outfit up to 5 pieces."
            ),
            tools=[get_daily_forecast],
            output_type=ResponseModel
        )
        self.photos: List[str] = []

    def create_styles(self, query: str):

        style = self.agent.run_sync(query).output
        
        needed_clothes = style.needed_clothes

        response = create_outfit(needed_clothes)

        return response,style

    def find_clothes(self, query: str,style) -> ResponseModel:
        # 1. Ask the agent to identify needed clothes (and forecast)
        if query !="Ignore":
            style = self.agent.run_sync(query).output
            print(f"The initial call: {style}")

        print("Not used the Agent")
        # print(style.needed_clothes[0].color)

        # return True
        # 2. For each needed clothing item, perform a SerpAPI search
        options: Dict[str, List[Dict[str, Any]]] = {}
        for item in style.needed_clothes:
            print(type(item))
            search_resp = get_serpi_clothes_search(item.to_string())
            # convert Pydantic models to dicts if needed
            opts = [r.model_dump() if hasattr(r, 'model_dump') else r for r in search_resp.results]
            options[item.type] = opts

        # 3. Build narrative text including weather and items
        lines: List[str] = []
        if style.forecast:
            lines.append(f"Weather forecast: {style.forecast}")

        for item, opts in options.items():
            lines.append(f"Options for {item}:")
            for o in opts:
                lines.append(f"- {o.get('title')} at {o.get('price')}")
            lines.append("")
        narrative = "\n".join(lines)

        # 5. Return full ResponseModel
        return ResponseModel(
            needed_clothes=style.needed_clothes,
            forecast=style.forecast,
            text=narrative,
            clothing_options=options
        )

# if __name__ == "__main__":
#     finder = ClothesFinder()
#     style=0
#     response = finder.find_clothes("I have a wedding in Athens in Summer",style)

#     print("**"*20)
#     # print(response.clothing_options)