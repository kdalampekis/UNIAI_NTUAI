import uuid, os
from PIL import Image
from rembg import remove
import pytesseract
from transformers import BlipProcessor, BlipForConditionalGeneration
from utils.db import init_db, insert_item, attach_tag_to_item
from openai import OpenAI
import datetime
import json
from dotenv import load_dotenv

# Initialize DB
init_db()

# Load BLIP model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

WARDROBE_DIR = "data/user_wardrobes"

# Load OpenAI credentials
load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_key)

def process_image(img: Image.Image) -> Image.Image:
    no_bg = remove(img.convert("RGB"))
    white_bg = Image.new("RGB", no_bg.size, (255,255,255))
    white_bg.paste(no_bg, mask=no_bg.split()[3])
    return white_bg

def extract_caption(img: Image.Image) -> str:
    inputs = processor(images=img, return_tensors="pt")
    out = model.generate(**inputs, max_new_tokens=20)
    return processor.decode(out[0], skip_special_tokens=True)

def extract_ocr(img: Image.Image) -> str:
    return pytesseract.image_to_string(img).strip()

def enrich_metadata_with_openai(
    caption: str,
    ocr_text: str,
    vision_labels: list[str],
    vision_logos: list[str]
) -> dict:
    schema = {
        "type": "object",
        "properties": {
            "type": {"type": "string"},
            "sub_type": {"type": "string"},
            "color": {"type": "string"},
            "material": {"type": "string"},
            "style": {"type": "string"},
            "season": {"type": "string"},
            "brand": {"type": "string"},
            "pattern": {"type": "string"},
            "mood": {"type": "string"},
            "size": {"type": "string"}
        },
        "required": ["type", "color"]
    }

    full_prompt = f"""
You are an assistant extracting structured fashion metadata from image analysis.

Image Caption: {caption}
OCR Text: {ocr_text}
Detected Labels: {', '.join(vision_labels)}
Detected Logos: {', '.join(vision_logos)}

Based on this information, extract metadata fields like type, sub_type, color, size, style, season, brand, material, mood, etc.
  """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "user",
            "content": full_prompt
        }],
        functions=[{"name": "extract_metadata", "parameters": schema}],
        function_call={"name": "extract_metadata"}
    )
    return json.loads(response.choices[0].message.function_call.arguments)

def save_item_with_metadata(
    image: Image.Image,
    user_id: str,
    metadata: dict,
    tags: list[str] = None,
    image_url: str = None
) -> dict:
    item_id = str(uuid.uuid4())[:8]
    filename = f"{metadata.get('type', 'item')}_{item_id}.jpg"
    user_folder = os.path.join(WARDROBE_DIR, user_id)
    os.makedirs(user_folder, exist_ok=True)
    path = os.path.join(user_folder, filename)
    image.save(path)

    item_record = {
        "id": item_id,
        "user_id": user_id,
        "filename": filename,
        "type": metadata.get("type"),
        "sub_type": metadata.get("sub_type"),
        "color": metadata.get("color"),
        "color_hex": metadata.get("color_hex"),
        "material": metadata.get("material"),
        "pattern": metadata.get("pattern"),
        "size": metadata.get("size"),
        "brand": metadata.get("brand"),
        "style": metadata.get("style"),
        "season": metadata.get("season"),
        "mood": metadata.get("mood"),
        "favorite": metadata.get("favorite", 0),
        "date_added": metadata.get("date_added", datetime.datetime.now().isoformat()),
        "last_worn": None,
        "wear_count": 0
    }

    insert_item(item_record)



    return item_record