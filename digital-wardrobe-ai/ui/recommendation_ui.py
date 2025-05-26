import streamlit as st
import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, '..', '..')))
from agents.recommender_agent import *
import requests
from PIL import Image
import io


es = initialize()
index_name = "digital_wardrobe"
create_index(es, index_name)

# Image size
TARGET_H = 300

# --- Session State Initialization ---
def select_item(cat: str, desc: str):
    """Callback when a user selects an item."""
    st.session_state.selections[cat] = desc
    st.session_state.step += 1


def fetch_and_resize(url):
    resp = requests.get(url, stream=True)
    img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    w, h = img.size
    new_w = int(w * (TARGET_H / h))
    return img.resize((new_w, TARGET_H), Image.LANCZOS)

# --- Session State Initialization ---
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.analysis = None
    st.session_state.selections = {}       # { category: desc }
    st.session_state.recs_by_cat = {}

# --- Title & Sidebar Summary ---
st.title("👗 AI Fashion Recommender")
st.sidebar.header("🛍️ Your Selections")
if st.session_state.selections:
    for cat, desc in st.session_state.selections.items():
        st.sidebar.markdown(f"**{cat.capitalize()}:** {desc}")
else:
    st.sidebar.write("_No items selected yet_")

# --- Step 0: Initial Prompt Form ---
if st.session_state.step == 0:
    prompt = st.text_input(
        "Describe your outfit or ask for suggestions:",
        placeholder="e.g. a summer date night outfit",
        key="init_prompt"
    )
    if st.button("Start Recommendation") and st.session_state.init_prompt:
        st.session_state.analysis = parse_fashion_prompt(st.session_state.init_prompt)
        st.session_state.step = 1


# --- Steps 1…N: One Category at a Time ---
elif 1 <= st.session_state.step <= len(st.session_state.analysis.requested_categories):
    cat_index = st.session_state.step - 1
    cat = st.session_state.analysis.requested_categories[cat_index]
    st.header(f"🎯 Suggestions for **{cat.capitalize()}**")

    # Fetch once per category and cache
    if cat not in st.session_state.recs_by_cat:
        selected_desc = ", ".join(st.session_state.selections.values()) or "nothing"
        prompt = (
            f"The user has selected: {selected_desc}. "
            f"Suggest a {cat} for: {st.session_state.analysis.scenario}."
        )
        st.session_state.recs_by_cat[cat] = search_similar_items(prompt, cat, es)

    hits = st.session_state.recs_by_cat[cat]

    # Display as cards in three columns
    cols = st.columns(3)
    for idx, hit in enumerate(hits):
        src = hit["_source"]
        with cols[idx]:
            thumb = fetch_and_resize(src["image_url"])
            st.image(thumb)   
            st.markdown(f"**{src['brand']}** — {src['color'].capitalize()} {src['type']}")

            key = f"select_{cat}_{idx}"
            disabled = cat in st.session_state.selections

            st.button(
                "Select",
                key=key,
                disabled=disabled,
                on_click=select_item,
                args=(cat, f"{src['brand']} — {src['color']} {src['type']}")
            )



# --- Final: Show Complete Outfit ---
else:
    st.header("🎉 Your Final Outfit")
    for category, desc in st.session_state.selections.items():
        st.markdown(f"- **{category.capitalize()}:** {desc}")
    if st.button("🔄 Start Over"):
        for k in ("step", "analysis", "selections", "recs_by_cat", "init_prompt"):
            if k in st.session_state:
                del st.session_state[k]