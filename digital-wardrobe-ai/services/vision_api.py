from google.cloud import vision
from dotenv import load_dotenv
import os
import io
import requests
from bs4 import BeautifulSoup

load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

client = vision.ImageAnnotatorClient()

def get_page_preview(url):
    try:
        r = requests.get(url, timeout=4)
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.text if soup.title else "No Title"
        og_img = soup.find("meta", property="og:image")
        img_url = og_img["content"] if og_img else None
        return {"title": title, "img": img_url}
    except Exception:
        return {"title": "No preview", "img": None}

def web_detection(image_path: str) -> list[dict]:
    with io.open(image_path, 'rb') as f:
        content = f.read()
    image = vision.Image(content=content)
    response = client.web_detection(image=image)
    web = response.web_detection

    if web.full_matching_images:
        return [{"type": "full", "url": web.full_matching_images[0].url}]
    elif web.visually_similar_images:
        return [{"type": "similar", "url": web.visually_similar_images[0].url}]
    elif web.pages_with_matching_images:
        page = web.pages_with_matching_images[0]
        preview = get_page_preview(page.url)
        return [{
            "type": "page",
            "page_url": page.url,
            "title": preview.get("title"),
            "img": preview.get("img")
        }]
    else:
        return []

def extract_vision_metadata(image_path: str) -> dict:
    with io.open(image_path, 'rb') as f:
        content = f.read()
    image = vision.Image(content=content)

    response = client.annotate_image({
        'image': image,
        'features': [
            {'type': vision.Feature.Type.LABEL_DETECTION},
            {'type': vision.Feature.Type.LOGO_DETECTION},
            {'type': vision.Feature.Type.TEXT_DETECTION}
        ]
    })

    labels = [label.description.lower() for label in response.label_annotations]
    logos = [logo.description for logo in response.logo_annotations]
    text = response.text_annotations[0].description if response.text_annotations else ""

    return {
        "labels": labels,
        "logos": logos,
        "ocr_text": text.strip()
    }