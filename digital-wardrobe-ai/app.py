import streamlit as st
from views import login, my_closet, add_clothe, outfit_chooser, recommendation

st.set_page_config(page_title="Digital Wardrobe", page_icon="🧥", layout="wide")

# Initialize session variables
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "My Closet"  # default after login

# --- 1️⃣ Login Page ---
if st.session_state.user_id is None:
    login.render()

# --- 2️⃣ Main App After Login ---
else:
    st.markdown("<h1 style='text-align: center;'>👗 Digital Wardrobe</h1>", unsafe_allow_html=True)

    nav = st.radio(
        label="Navigation",
        options=["My Closet", "Add New Clothe", "Choose Outfit", "Recommendation"],
        horizontal=True,
        label_visibility="collapsed",
        index=["My Closet", "Add New Clothe", "Choose Outfit", "Recommendation"].index(
            st.session_state.page
        )
    )

    # Update current page
    st.session_state.page = nav

    # --- Routing based on top nav ---
    if nav == "My Closet":
        my_closet.render()
    elif nav == "Add New Clothe":
        add_clothe.render()
    elif nav == "Choose Outfit":
        outfit_chooser.render()
    elif nav == "Recommendation":
        recommendation.render()
