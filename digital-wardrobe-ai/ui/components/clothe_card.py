import streamlit as st

def display_clothe_preview(item: dict):
    col1, col2 = st.columns([1, 3])  # Image on the left, info on the right

    # --- Image on the Left ---
    with col1:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; height: 180px;">
                <img src="{item['image_url']}" width="160" height="180"
                     style="object-fit: cover; border-radius: 8px;" />
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- Info on the Right, vertically centered ---
    with col2:
        st.markdown(
            f"""
            <div style="display: flex; flex-direction: column; justify-content: center; height: 180px;">
                <h4 style="margin: 0;">{item['type']} — <i>{item['sub_type']}</i></h4>
                <p style="margin: 4px 0;"><strong>Tags:</strong> {' '.join(f'<code>{tag.strip()}</code>' for tag in item['tags'].split(',')) if item['tags'] else '—'}</p>
                <p style="margin: 0;"><strong>Mood:</strong> <i>{item['mood']}</i></p>
            </div>
            """,
            unsafe_allow_html=True
        )
