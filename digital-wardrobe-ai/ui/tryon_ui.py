import streamlit as st
import os
import sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..')))
from agents.tryon_agent import generate_prompt_from_images, generate_image_with_dalle3

# === Streamlit Page Config
st.set_page_config(page_title="Virtual Try-On", layout="centered")
st.title("🧥 AI Virtual Try-On")

# === Upload inputs
person_file = st.file_uploader("📷 Upload a photo of yourself", type=["png", "jpg", "jpeg"])
shirt_file = st.file_uploader("👕 Upload a T-shirt or top", type=["png", "jpg", "jpeg"])

# === Handle try-on trigger
if person_file and shirt_file:
    st.image(person_file, caption="👤 Person Image", width=256)
    st.image(shirt_file, caption="👕 Clothing Image", width=256)

    if st.button("✨ Try it on!"):
        with st.spinner("Analyzing user input ..."):
            # Save uploaded images temporarily
            os.makedirs("tmp", exist_ok=True)
            person_path = "tmp/person.png"
            shirt_path = "tmp/shirt.png"
            with open(person_path, "wb") as f: f.write(person_file.read())
            with open(shirt_path, "wb") as f: f.write(shirt_file.read())

            # === Step 1: Generate prompt
            prompt = generate_prompt_from_images(person_path, shirt_path)

        with st.spinner("Creating synthetic image ..."):
            # === Step 2: Generate final image
            image_url = generate_image_with_dalle3(prompt)

        st.success("✅ Image ready!")
        st.image(image_url, caption="🧥 Virtual Try-On Result", use_container_width=True)

elif person_file or shirt_file:
    st.warning("Please upload both images to proceed.")
