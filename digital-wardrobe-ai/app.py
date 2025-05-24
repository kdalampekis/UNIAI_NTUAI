import itertools
import json
import random
import streamlit as st
from agents.event_planner_agent import EventPlanner
# Assume `response` dict is already defined and available
import pandas as pd

def display_images(category, items):
    st.subheader(category.capitalize())
    cols = st.columns(3)
    for idx, item in enumerate(items):
        col = cols[idx % 3]
        with col:
            st.image(item['photo'], use_container_width=True)
            st.markdown(f"[{item['title']}]({item['link']})")
            st.write(item['price'])

def display_outfit(outfit_items, categories):
    st.markdown("---")
    cols = st.columns(len(categories))
    for idx, (category, item) in enumerate(zip(categories, outfit_items)):
        with cols[idx]:
            st.subheader(category.capitalize())
            st.image(item['photo'], use_container_width=True)
            st.markdown(f"**{item['title']}**")
            st.write(item['price'])
            st.markdown(f"[View product]({item['link']})")

def main():
    st.title("Smart Outfit Planner")

    # User input for dynamic search
    query = st.text_input("Describe your event or outfit needs:", value="I have a wedding in Athens on June 14th")
    search_button = st.button("Search")
    planner = EventPlanner()
    # On search, fetch and store results in session_state
    if search_button and query:
        with st.spinner("Fetching clothing options..."):
            response = planner.find_clothes(query)
            with open("clothing_response.json", "w") as f:
                f.write(response.json())


        # Store in session state
        st.session_state['clothing_options'] = response.clothing_options
        # Prepare outfits
        categories = list(response.clothing_options.keys())

        # 1) Build a dict of DataFrames
        category_dfs = {}
        for category, items in response.clothing_options.items():
            # if items is a list of dicts, DataFrame will pick up the fields as columns
            df = pd.DataFrame(items)
            category_dfs[category] = df

        # outfits = list(itertools.product(*response.clothing_options.values()))
        st.session_state['categories'] = categories
        # st.session_state['outfits'] = outfits

        for category, df in category_dfs.items():
            st.write(f"### Category: {category.capitalize()}")
            st.dataframe(df)    # or st.table(df) for a static table
        # print(f"Types of outfits {outfits}")

        categories = list(response.clothing_options.keys())


        # 3) Create fully-unique outfits
        categories = list(response.clothing_options.keys())
        max_outfits = min(len(response.clothing_options[c]) for c in categories)

        shuffled = {c: list(response.clothing_options[c]) for c in categories}
        for lst in shuffled.values():
            random.shuffle(lst)

        unique_outfits = []
        for i in range(max_outfits):
            outfit = {c: shuffled[c][i] for c in categories}
            unique_outfits.append(outfit)

        st.session_state['unique_outfits'] = unique_outfits

        # 4) Display each outfit with your helper
        for outfit in st.session_state['unique_outfits']:
            # grab items in the right order
            outfit_items = [outfit[cat] for cat in categories]
            display_outfit(outfit_items, categories)

        # If we have outfits stored, allow slider selection and display
    if 'outfits' in st.session_state:
        outfits = st.session_state['outfits']
        categories = st.session_state['categories']
        st.success(f"Found {len(outfits)} possible outfits.")
        # Slider to choose how many outfits to display
        max_display = st.slider(
            "Number of outfits to show:", min_value=1, max_value=len(outfits), value=min(5, len(outfits))
        )
        for i, outfit in enumerate(outfits[:max_display], start=1):
            st.subheader(f"Outfit #{i}")
            display_outfit(outfit, categories)

# def main():
#     st.title("Smart Outfit Planner")

#     planner = EventPlanner()
#     response = planner.find_clothes("I have a wedding in Athens on June 14th")

#     # The planner returns a dict of categories to lists of items
#     categories = list(response.clothing_options.keys())
#     print(f"Here are the categories:{categories}")
#     all_item_lists = list(response.clothing_options.values())
#     print(f"This is the all items list {all_item_lists}")
#     # Generate all combinations: one item per category
#     outfits = list(itertools.product(*all_item_lists))
#     st.write(f"Found {len(outfits)} possible outfits.")

#     max_display = st.number_input(
#         "How many outfits to show?", min_value=1, max_value=len(outfits), value=min(10, len(outfits))
#     )

#     for i, outfit in enumerate(outfits[:int(max_display)], start=1):
#         st.subheader(f"Outfit #{i}")
#         display_outfit(outfit, categories)

if __name__ == '__main__':
    main()