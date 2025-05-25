import streamlit as st
st.set_page_config(page_title="Digital Wardrobe", page_icon="🧥", layout="centered")


from views import login, my_closet, add_clothe

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# Page router
if st.session_state.page == "login":
    login.render()
elif st.session_state.page == "my_closet":
    my_closet.render()
elif st.session_state.page == "add_clothe":
    add_clothe.render()
