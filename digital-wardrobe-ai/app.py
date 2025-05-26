import streamlit as st

# 1️⃣ Must be the very first Streamlit call
st.set_page_config(page_title="Digital Wardrobe", page_icon="🧥", layout="wide")

# 2️⃣ Import your views after set_page_config
from views import login, my_closet, add_clothe, recommendation

# 3️⃣ Initialize session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "My Closet"  # default page after login

# 4️⃣ If not logged in, render login & stop
if st.session_state.user_id is None:
    st.markdown("<h1 style='text-align: center;'>🧥 Digital Wardrobe</h1>", unsafe_allow_html=True)
    login.render()
    st.stop()

# 5️⃣ Once logged in, show sidebar + pages
st.sidebar.title("👗 Digital Wardrobe")
pages = ["My Closet", "Add New Clothe", "Choose Outfit", "Recommendation"]

# Safely clamp page to our list
if st.session_state.page not in pages:
    st.session_state.page = "My Closet"

nav = st.sidebar.radio(
    "Navigate",
    options=pages,
    index=pages.index(st.session_state.page)
)
st.session_state.page = nav

# 6️⃣ Render the selected view
if nav == "My Closet":
    my_closet.render()
elif nav == "Add New Clothe":
    add_clothe.render()
elif nav == "Choose Outfit":
    # lazy-import if outfit_chooser is heavy
    from views import outfit_chooser
    outfit_chooser.render()
elif nav == "Recommendation":
    recommendation.render()
