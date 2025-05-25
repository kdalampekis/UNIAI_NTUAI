import streamlit as st

import sqlite3
import uuid
import datetime
import os
from PIL import Image
from ui.components.clothe_card import display_clothe_preview


DB_PATH = 'data/wardrobe.db'
UPLOAD_FOLDER = 'data/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_user_items(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM wardrobe_items WHERE user_id = ?", (user_id,))
    items = [dict(row) for row in c.fetchall()]
    conn.close()
    return items

def get_username(user_id: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else "User"


def render():
    # ----- User Setup -----
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("Unauthorized access. Please login first.")
        st.stop()
        username = get_username(user_id)

    # ----- Header + Button layout -----
    col1, col2 = st.columns([6, 2])

    with col1:
        st.markdown(
            "<div style='padding-top: 8px;'><h3>My Closet</h3></div>",
            unsafe_allow_html=True
        )

#     with col2:
#         st.markdown("<div style='padding-top: 16px;'>", unsafe_allow_html=True)
#
#         if st.button("➕ Add New Clothe"):
#             st.session_state.page = "add_clothe"
#             st.rerun()
#
#         if st.button("🧠 Plan Outfit"):   # <-- New button
#             st.session_state.page = "outfit_chooser"
#             st.rerun()
#
#         st.markdown("</div>", unsafe_allow_html=True)



    # ----- Load Items -----
    items = get_user_items(user_id)

    # ----- Sidebar Filters -----
    with st.sidebar:
        st.header("Filters")

        filter_fields = {
            "type": "👕 Clothing Type",
            "sub_type": "🔍 Subtype",
            "size": "📏 Size",
            "brand": "🏷️ Brand",
            "style": "🧣 Style",
            "material": "🧵 Material",
            "season": "🌦️ Season",
            "mood": "😊 Mood",
        }

        selected_filters = {}

        for field, label in filter_fields.items():
            with st.expander(label):
                all_values = sorted(set(item[field] for item in items if item.get(field)))
                selected = [val for val in all_values if st.checkbox(val, key=f"{field}_{val}")]
                selected_filters[field] = selected

        # ----- Color Filter with Swatches -----
        with st.expander("🎨 Color"):
            color_map = {}
            for item in items:
                color = item.get("color")
                hex_code = item.get("color_hex")
                if color and hex_code:
                    color_map[color] = hex_code
            selected_colors = []
            for color, hex_code in sorted(color_map.items()):
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.checkbox(color, key=f"color_{color}"):
                        selected_colors.append(color)
                with col2:
                    st.markdown(
                        f"""<div style="width: 18px; height: 18px; background-color: {hex_code};
                                    border: none; border-radius: 3px; margin-top: 7px;"></div>""",
                        unsafe_allow_html=True
                    )

        # ----- Tags Filter -----
        with st.expander("🏷️ Tags"):
            tag_set = set()
            for item in items:
                if item.get("tags"):
                    tag_set.update(tag.strip() for tag in item["tags"].split(","))
            all_tags = sorted(tag_set)
            selected_tags = [tag for tag in all_tags if st.checkbox(tag, key=f"tag_{tag}")]

    # ----- Apply Filters -----
    filtered_items = items

    for field, selected in selected_filters.items():
        if selected:
            filtered_items = [item for item in filtered_items if item.get(field) in selected]

    if selected_colors:
        filtered_items = [item for item in filtered_items if item.get("color") in selected_colors]

    if selected_tags:
        filtered_items = [
            item for item in filtered_items
            if item.get("tags") and any(tag in item["tags"].split(",") for tag in selected_tags)
        ]

    # ----- Display Results -----
    if not filtered_items:
        st.info("No matching clothes found.")
    else:
        for item in filtered_items:
            with st.container():
                display_clothe_preview(item)
                st.markdown("---")
