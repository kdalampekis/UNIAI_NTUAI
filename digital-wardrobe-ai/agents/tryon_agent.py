# generator_agent.py
import base64
from openai import OpenAI
import os
import torch
from PIL import Image
from diffusers import StableDiffusionXLPipeline, ControlNetModel
from ip_adapter import IPAdapterXL
from controlnet_aux.open_pose import OpenposeDetector
import open_clip
# Load environment variables
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Set securely

def generate_tryon_image(
    person_img_path: str,
    cloth_img_path: str,
    output_path: str = "outputs/tryon_result.png",
    config_path: str = "checkpoints/ip_adapter_fashion/ip-adapter-plus_sdxl_fashion.safetensors",
    weight_path: str = "checkpoints/ip_adapter_fashion/ip-adapter-plus_sdxl_fashion.bin"
):
    # === Load and preprocess images ===
    person_img = Image.open(person_img_path).convert("RGB").resize((768, 1024))
    cloth_img = Image.open(cloth_img_path).convert("RGB").resize((512, 512))

    # === Load image encoder ===
    image_encoder, _, _ = open_clip.create_model_and_transforms(
        model_name="ViT-H-14",
        pretrained="laion2b_s32b_b79k",
        device="cpu",
        precision="fp32"
    )

    # === Generate pose from person image ===
    openpose = OpenposeDetector.from_pretrained("lllyasviel/ControlNet")
    pose_image = openpose(person_img)

    # === Load ControlNet and SDXL pipeline ===
    controlnet = ControlNetModel.from_pretrained(
        "thibaud/controlnet-openpose-sdxl-1.0",
        torch_dtype=torch.float32,
    )
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        controlnet=controlnet,
        torch_dtype=torch.float32,
        variant="fp16"
    )
    pipe.enable_xformers_memory_efficient_attention()

    # === Load IP-Adapter-Fashion ===
    ip_adapter = IPAdapterXL(
        pipe,
        image_encoder=image_encoder,
        config_path=config_path,
        weight_path=weight_path,
    )
    ip_adapter.set_image(cloth_img)

    # === Generate the image ===
    prompt = "A man wearing the shirt shown in the reference image, front pose, realistic lighting"
    negative_prompt = "blurry, missing logo, distorted face, bad hands"

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=person_img,
        controlnet_conditioning_image=pose_image,
        num_inference_steps=30,
        guidance_scale=7.5
    ).images[0]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    result.save(output_path)
    print(f"✅ Saved to {output_path}")
    return result



# === Utility: Encode image as base64
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# === Function 1: Generate a prompt from GPT-4 Vision
def generate_prompt_from_images(person_image_path, shirt_image_path):
    person_b64 = encode_image(person_image_path)
    shirt_b64 = encode_image(shirt_image_path)

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Please describe a photo-realistic image where the man in the first image "
                        "is wearing the T-shirt shown in the second image. The description should help an AI "
                        "generate the image accurately. Preserve his facial features, pose, and lighting. "
                        "Describe the shirt texture, style, and logo precisely."
                    )
                },
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{person_b64}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{shirt_b64}"}},
            ],
        }
    ]

    print("🧠 Generating image prompt with GPT-4 Vision...")
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        max_tokens=600,
    )
    prompt = response.choices[0].message.content.strip()
    print(f"\n📝 Prompt Generated:\n{prompt}")
    return prompt

# === Function 2: Generate image with DALL·E 3
def generate_image_with_dalle3(prompt, output_path="outputs/dalle_result.txt"):
    print("🎨 Generating image with DALL·E 3...")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    print(f"\n✅ Image URL: {image_url}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(image_url)

    return image_url