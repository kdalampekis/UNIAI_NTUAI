import streamlit as st

def display_images(category, items):
    st.subheader(category.capitalize())
    cols = st.columns(3)
    for idx, item in enumerate(items):
        col = cols[idx % 3]
        with col:
            st.image(item['photo'], use_container_width=True)
            st.markdown(f"[{item['title']}]({item['link']})")
            st.write(item['price'])

st.set_page_config(layout="wide")

def display_outfit(outfit_items, categories):
    st.markdown("---")

    # Shared CSS for cards with a slightly white background
    st.markdown(
        """
        <style>
          .card {
            background: rgba(255,255,255,0.9);
            border:1px solid #ddd;
            border-radius:8px;
            padding:12px;
            box-shadow:2px 2px 6px rgba(0,0,0,0.05);
            transition: transform 0.1s, box-shadow 0.1s;
          }
          .card:hover {
            transform: translateY(-4px);
            box-shadow:4px 4px 12px rgba(0,0,0,0.1);
          }
          .badge {
            display:inline-block;
            background:#f0f0f0;
            color:#333;
            font-size:0.75rem;
            padding:2px 6px;
            border-radius:4px;
            margin-bottom:6px;
          }
        </style>
        """,
        unsafe_allow_html=True
    )

    cols = st.columns(len(outfit_items), gap="large")
    for col, category, item in zip(cols, categories, outfit_items):
        with col:

            # Category badge
            st.markdown(f"<div class='badge'>{category.upper()}</div>", unsafe_allow_html=True)

            # Image
            if img := item.get("photo"):
                st.image(img, use_container_width=True)
            else:
                st.write("_No image available_")

            # Title
            st.markdown(f"**{item.get('title','Untitled')}**")

            # Price as metric
            price = item.get("price", "—")
            st.metric(label="", value=f"{price}")

            # Optional rating
            if (r := item.get("rating")) is not None:
                stars = "★" * int(r) + "☆" * (5-int(r))
                st.markdown(f"<small>{stars} ({r:.1f})</small>", unsafe_allow_html=True)

            # Button-style link
            if (link := item.get("link")):
                st.markdown(
                    f"<a href='{link}' target='_blank'>"
                    "<button style='"
                    "padding:6px 12px;"
                    "border:none;"
                    "background:#52c41a;"
                    "color:white;"
                    "border-radius:4px;"
                    "font-size:0.9rem;"
                    "cursor:pointer;"
                    "'>View product</button></a>",
                    unsafe_allow_html=True
                )
            else:
                st.write("_No link available_")

            st.markdown("</div>", unsafe_allow_html=True)





import random
import streamlit as st

def generate_and_display_outfits(response, categories):
    """
    Given a response.model with `clothing_options` per category and a list of categories:
      1) Compute how many fully-unique outfits you can make
      2) Shuffle each category’s options
      3) Build all unique outfits
      4) Store them in session_state and render each via display_outfit()
    """
    # 1) Figure out the maximum number of full outfits
    max_outfits = min(len(response.clothing_options[c]) for c in categories)

    # 2) Shuffle each category’s list in place
    shuffled = {c: list(response.clothing_options[c]) for c in categories}
    for lst in shuffled.values():
        random.shuffle(lst)

    # 3) Build each outfit as a dict mapping category → item
    unique_outfits = [
        {c: shuffled[c][i] for c in categories}
        for i in range(max_outfits)
    ]

    # 4) Persist to session_state and display them
    st.session_state['unique_outfits'] = unique_outfits

    for idx, outfit in enumerate(unique_outfits, start=1):
        st.write(f"### Outfit #{idx}")
        outfit_items = [outfit[cat] for cat in categories]
        display_outfit(outfit_items, categories)

    return unique_outfits
    

def display_category(name: str, items: list, cols: int = 3):
    """Renders a header and a clickable image gallery for one category."""
    st.markdown(f"## {name.capitalize()}")
    grid = st.columns(cols)
    for i, item in enumerate(items):
        with grid[i % cols]:
            md = f"[![{item['title']}]({item['photo']})]({item['link']})"
            st.markdown(md, unsafe_allow_html=True)
            st.caption(f"**{item['title']}**  \n{item['price']}")