import streamlit as st
from PIL import Image
import os
import sys

from agents.wardrobe_agent import (
    process_image,
    extract_caption,
    extract_ocr,
    enrich_metadata_with_openai,
    save_item_with_metadata
)

from services.vision_api import web_detection, extract_vision_metadata


def render():
    # 🔒 Access restriction
    if "user_id" not in st.session_state or not st.session_state.user_id:
        st.error("🔐 You must be logged in to access this page.")
        st.stop()

    USER_ID = st.session_state.user_id

    # Initialize session state
    for key, default in {
        "processed": None,
        "caption": "",
        "ocr_text": "",
        "enriched": {},
        "web_results": [],
        "image_url": None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # ----- Header + Button layout -----
    col1, col2 = st.columns([6, 1.5])

    with col1:
        st.markdown(
            "<div style='padding-top: 8px;'><h3>Digital Wardrobe Importer</h3></div>",
            unsafe_allow_html=True
        )

#     with col2:
#         st.markdown("<div style='padding-top: 16px;'>", unsafe_allow_html=True)
#         if st.button("👕 My Closet"):
#             st.session_state.page = "my_closet"
#             st.rerun()
#
#         st.markdown("</div>", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload a clothing photo", type=['jpg', 'jpeg', 'png'])

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, caption="🖼️ Original Image", use_container_width=True)

        if st.button("✨ Process & Auto-Tag"):
            with st.spinner("Processing..."):
                processed = process_image(img)
                st.session_state.processed = processed
                caption = extract_caption(processed)

                temp_path = "data/user_wardrobes/user001/temp.jpg"
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                processed.save(temp_path)

                ocr_text = extract_ocr(processed)
                vision_metadata = extract_vision_metadata(temp_path)
                vision_labels = vision_metadata.get("labels", [])
                vision_logos = vision_metadata.get("logos", [])

                enriched = enrich_metadata_with_openai(
                    caption,
                    ocr_text,
                    vision_labels,
                    vision_logos
                )

                web_results = web_detection(temp_path)

                st.session_state.caption = caption
                st.session_state.ocr_text = ocr_text
                st.session_state.enriched = enriched
                st.session_state.web_results = web_results
                st.session_state.image_url = None

    if st.session_state.processed:
        st.image(st.session_state.processed, caption="🧼 Cleaned Image", use_container_width=True)
        enriched = st.session_state.enriched

        if st.session_state.web_results:
            st.markdown("### 🌐 Is this your item?")
            for i, res in enumerate(st.session_state.web_results):
                url = res.get("page_url") or res.get("url")
                if res.get("img"):
                    st.image(res["img"], width=150)
                if res.get("title"):
                    st.caption(res["title"])
                if url:
                    st.markdown(f"🔗 [Preview Link]({url})")
                    if st.button(f"✅ Yes! Use this link", key=f"select_{i}"):
                        st.session_state.image_url = url
                        st.success("✅ Link selected and will be saved with the item.")

        with st.form("metadata_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_type = st.text_input("Type", enriched.get("type", ""))
                sub_type = st.text_input("Sub Type", enriched.get("sub_type", ""))
                color = st.text_input("Color", enriched.get("color", ""))
                color_hex = st.text_input("Color Hex", enriched.get("color_hex", "#FFFFFF"))
                material = st.text_input("Material", enriched.get("material", ""))
                pattern = st.text_input("Pattern", enriched.get("pattern", ""))
            with col2:
                size = st.text_input("Size", enriched.get("size", ""))
                brand = st.text_input("Brand", enriched.get("brand", ""))
                style = st.text_input("Style", enriched.get("style", ""))
                season = st.text_input("Season", enriched.get("season", ""))
                mood = st.text_input("Mood", enriched.get("mood", ""))
                tags_input = st.text_input("Tags (comma separated)", "daily,favorite")

            submitted = st.form_submit_button("💾 Save to Wardrobe")
            if submitted:
                try:
                    metadata = {
                        "type": item_type,
                        "sub_type": sub_type,
                        "color": color,
                        "color_hex": color_hex,
                        "material": material,
                        "pattern": pattern,
                        "size": size,
                        "brand": brand,
                        "style": style,
                        "season": season,
                        "mood": mood,
                        "favorite": 1 if "favorite" in tags_input.lower() else 0,
                    }
                    tags = [t.strip() for t in tags_input.split(",") if t.strip()]
                    record = save_item_with_metadata(
                        st.session_state.processed,
                        USER_ID,
                        metadata,
                        tags,
                        image_url=st.session_state.get("image_url")
                    )

                    st.success(f"✅ Saved item: {record['filename']}")
                    if record.get("image_url"):
                        st.markdown(f"🌐 [View similar item online]({record['image_url']})")
                except Exception as e:
                    st.error(f"❌ Error during saving: {e}")
