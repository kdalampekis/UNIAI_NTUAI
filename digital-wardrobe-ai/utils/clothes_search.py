import time
import requests
from apify_client import ApifyClient
from typing import List
from pydantic import BaseModel, Field


def get_asos_clothes_search(query: str, max_items: int = 10) -> list:
    """
    Search for clothes on ASOS using the Apify ASOS Scraper actor.
    
    Args:
        query (str): The search term (e.g., 'women dress').
        max_items (int): Max number of results to fetch.
        
    Returns:
        list: A list of result dictionaries.
    """
    # Initialize the ApifyClient with your Apify API token
    client = ApifyClient("apify_api_RfVMdzhcpr2hKnufbUvSOxhcGljqXK3eMx8x")
    
    # Prepare the Actor input
    run_input = {
        "search": query,
        "startUrls": [
            f"https://www.asos.com/search/?q={query.replace(' ', '+')}"
        ],
        "maxItems": max_items,
        "endPage": 1,
        "extendOutputFunction": "($) => { return {} }",
        "customMapFunction": "(object) => { return {...object} }",
        "proxy": { "useApifyProxy": True },
    }
    
    # Run the Actor and wait for it to finish
    run = client.actor("epctex/asos-scraper").call(run_input=run_input)
    
    # Fetch Actor results from the run's dataset
    results = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        results.append(item)
    
    print("💾 Check your data here: https://console.apify.com/storage/datasets/" + run["defaultDatasetId"])
    return results


class SerpiClothesItem(BaseModel):
    title: str = Field(..., description="Name or title of the product")
    price: str = Field(..., description="Price as shown (with currency)")
    photo: str = Field(..., description="URL to the main product image")
    link: str = Field(..., description="URL to the product's detail page")

class SerpiClothesSearchResponse(BaseModel):
    results: List[SerpiClothesItem]

def get_serpi_clothes_search(query: str, limit: int=5) -> SerpiClothesSearchResponse:
    print(f"Tool called with: {query}")
    print(f"Limit = {limit}")
    start_time= time.time()

    params = {
        "engine": "google_shopping",
        "q": query,
        "api_key": "447e4d74df788b90a28f4ef1efa570a1149298250be98a826c25362c7902b8f7",
        "num": limit 
    }

    response = requests.get("https://serpapi.com/search", params=params)
    data = response.json()
    results = data.get('shopping_results', [])
    
    cleaned_results = []
    for i, item in enumerate(results):
        if isinstance(item, dict):
            cleaned_item = SerpiClothesItem(
                title=item.get("title", ""),
                price=item.get("price", ""),
                photo=item.get("thumbnail", ""),
                link=item.get("product_link", ""),
            )
            cleaned_results.append(cleaned_item)
        if i>5: 
            break
    # print(cleaned_results)
    print(f"Time taken {time.time()-start_time}")
    return SerpiClothesSearchResponse(results=cleaned_results)

# Example usage:
if __name__ == "__main__":
    response = get_serpi_clothes_search("yellow floral dress",limit=3)
    print(response.model_dump_json(indent=2))