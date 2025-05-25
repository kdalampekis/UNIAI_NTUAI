from models.clip_model import generate_clip_embedding
from models.fashion_models import AgentClothingAnalysis
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
from openai import OpenAI
import openai
import pandas as pd
import json
import os
import urllib3

# Suppress SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Environment config
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST")
ELASTICSEARCH_USERNAME = os.getenv("ELASTICSEARCH_USERNAME")
ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
openai.api_key = os.getenv("OPENAI_API_KEY")

CATEGORIES = ["top", "bottom", "shoes"]

# Elasticsearch client
def initialize():
    es_client = Elasticsearch(
        ELASTICSEARCH_HOST,
        basic_auth=(ELASTICSEARCH_USERNAME, ELASTICSEARCH_PASSWORD),
        verify_certs=False,
        request_timeout=10000,
        headers={
            "Accept": "application/vnd.elasticsearch+json; compatible-with=8",
            "Content-Type": "application/vnd.elasticsearch+json; compatible-with=8"
        }
    )
    if not es_client.ping():
        raise ConnectionError("❌ Failed to connect to Elasticsearch")
    return es_client

# Create index with schema
def create_index(es, index_name):
    if not es.indices.exists(index=index_name):
        mapping = {
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "user_id": {"type": "keyword"},
                    "filename": {"type": "text"},
                    "image_url": {"type": "text"},
                    "type": {"type": "keyword"},
                    "sub_type": {"type": "keyword"},
                    "color": {"type": "keyword"},
                    "color_hex": {"type": "keyword"},
                    "material": {"type": "keyword"},
                    "pattern": {"type": "keyword"},
                    "size": {"type": "keyword"},
                    "brand": {"type": "text"},
                    "style": {"type": "keyword"},
                    "season": {"type": "keyword"},
                    "mood": {"type": "keyword"},
                    "favorite": {"type": "boolean"},
                    "date_added": {"type": "date"},
                    "last_worn": {"type": "date"},
                    "wear_count": {"type": "integer"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 512,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }
        es.indices.create(index=index_name, body=mapping)
        print(f"✅ Index '{index_name}' created.")
    else:
        print(f"ℹ️ Index '{index_name}' already exists.")

# Insert items from CSV with CLIP embeddings
def insert_items_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        
        print(row.to_json(orient='records', lines=False, indent=2))
        document = {
            "id": row["id"],
            "user_id": row["user_id"],
            "filename": row["filename"],
            "image_url": row["image_url"],
            "type": row["type"],
            "sub_type": row["sub_type"],
            "color": row["color"],
            "color_hex": row["color_hex"],
            "material": row["material"],
            "pattern": row["pattern"],
            "size": row["size"],
            "brand": row["brand"],
            "style": row["style"],
            "season": row["season"],
            "mood": row["mood"],
            "favorite": bool(row["favorite"]),
            "date_added": row["date_added"],
            "last_worn": row["last_worn"] if pd.notnull(row["last_worn"]) else None,
            "wear_count": int(row["wear_count"])
        }
        text = f"{document['color']} {document['material']} {document['pattern']} {document['type']} from {document['brand']}, style: {document['style']}, season: {document['season']}, mood: {document['mood']}"
        embedding = generate_clip_embedding(text)
        document["embedding"] = embedding
        es.index(index=index_name, id=document["id"], document=document)
        print(f"✅ Inserted: {document['brand']}_{document['color']}_{document['type']}")

# Find and delete items by name
def find_and_delete_by_name(name):
    result = es.search(index=index_name, query={"match": {"name": name}})
    for hit in result["hits"]["hits"]:
        doc_id = hit["_id"]
        es.delete(index=index_name, id=doc_id)
        print(f"🗑️ Deleted item with ID: {doc_id}")

# Search for similar items based on text description
def search_similar_items(query_text, category, es: Elasticsearch, index_name="digital_wardrobe"):
    embedding = generate_clip_embedding(query_text)

    body = {
        "knn": {
            "field": "embedding",
            "query_vector": embedding,
            "k": 30,
            "num_candidates": 100
        }
    }

    hits = es.search(index=index_name, body=body)["hits"]["hits"]
    filtered = [h for h in hits if h["_source"]["type"] == category]
    return filtered[:3]




system_prompt = """
You are a helpful fashion assistant.

You will receive a user's prompt. Extract:
1. The overall styling scenario (e.g., "a beach party", "formal dinner", etc.)
2. What clothing categories the user already has (from: top, bottom, shoes)
3. What categories they are asking for suggestions on (from: top, bottom, shoes)

If nothing is mentioned as selected, assume selected_categories is empty.
If they want a full outfit or say "suggest everything", include all categories in requested_categories.

Return only valid JSON using this schema:
{
  "scenario": "...",
  "selected_categories": [...],
  "requested_categories": [...]
}
"""

def parse_fashion_prompt(user_input: str) -> AgentClothingAnalysis:
    client = OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )
    print("Response from OpenAI:", response)
    content = response.choices[0].message.content
    parsed = json.loads(content)
    return AgentClothingAnalysis(**parsed)


def handle_user_prompt(prompt: str):
    analysis = parse_fashion_prompt(prompt)

    print("🧠 Scenario:", analysis.scenario)
    print("👚 Already selected:", analysis.selected_categories)
    print("🛍️ Looking for:", analysis.requested_categories)

    recommendations = []
    for category in analysis.requested_categories:
        print(f"\n🔍 Searching for {category}...")
        full_prompt = f"""
        The user has already selected: {', '.join(recommendations) or 'nothing'}.
        He is looking for a {category} that matches the scenario: {analysis.scenario}.
        Search for an item in that category only and ignore the rest of the categories.
        """
        print("Full prompt for search:", full_prompt)
        results = search_similar_items(full_prompt, category, es)

        for i, item in enumerate(results):
            source = item['_source']
            print(f"[{i+1}] {source['brand']} - {source['color']} {source['type']}")

        # Simulate user selection
        choice = int(input(f"Choose one for {category} (1-3): "))
        if choice < 1 or choice > len(results):
            print("Invalid choice, skipping...")
            continue
        chosen_item = results[choice - 1]['_source']
        recommendations.append(chosen_item['brand'] + " - " + chosen_item['color'] + " " + chosen_item['type'])

    return recommendations


def handle_user_step(analysis: AgentClothingAnalysis, selections: dict):
    """
    Determine next category and fetch 3 recommendations.
    Returns (category, list_of_hits) or (None, None) when done.
    """
    remaining = [c for c in analysis.requested_categories if c not in selections]
    if not remaining:
        return None, None
    cat = remaining[0]
    selected_desc = ", ".join(selections.values()) or "nothing"
    prompt = f"The user has selected: {selected_desc}. Suggest a {cat} for: {analysis.scenario}."
    recs = search_similar_items(prompt, cat)
    return cat, recs



if __name__ == "__main__":
    es = initialize()
    index_name = "digital_wardrobe"
    create_index(es, index_name)
    insert_items_from_csv("Generated_Wardrobe_Items.csv")
    
    user_prompt = input("Enter your fashion prompt: ")
    recommendations = handle_user_prompt(user_prompt)