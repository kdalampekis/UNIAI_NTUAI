import itertools
import json
import random
import streamlit as st
import ffmpeg
import tempfile

from agents.clothes_finder_agent import ClothesFinder,ResponseModel,ClothingItem,create_outfit

import pandas as pd
from ui.displaying_utils import display_images,display_outfit,generate_and_display_outfits,display_category
from utils.image_generation import create_outfit
from utils.speech_to_text import get_text_from_speech

from audiorecorder import audiorecorder

def record_and_transcribe_file():
    audio_seg = audiorecorder("▶️ Click to record", "⏹️ Stop recording")
    if not audio_seg:
        return None

    # Export WAV (for playback)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_f:
        wav_path = wav_f.name
    audio_seg.export(wav_path, format="wav")
    st.audio(wav_path)

    # Now export MP4 (AAC @128k) in one go
    mp4_path = wav_path.replace(".wav", ".mp4")
    audio_seg.export(
        mp4_path,
        format="mp4",
        codec="aac",
        bitrate="128k"
    )

    # Transcribe
    transcript = get_text_from_speech(mp4_path)
    return transcript


def main():
    st.title("Smart Outfit Planner")
    st.header("🎤 Record & Transcribe")
    st.session_state.transcript=""
    transcript = record_and_transcribe_file()
    if transcript:
        st.subheader("📝 Transcript")
        st.write(transcript)
        st.session_state.transcript=transcript
    planner = ClothesFinder()

    st.title("Style Selector")
    # Button to generate three style images
    # st.button("Search")
    # 1️⃣ Initialize state
    for key, default in {
        "styles_generated": False,
        "style_urls": [],
        "styles": [],
        "selected_style_url": None,
        "selected_style": None
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

    # Your query input
    query = st.text_input("Describe the look you want:", value=st.session_state.transcript)

    print("The transcript is: ",st.session_state.transcript)

    # 2️⃣ Generation block (runs only once)
    if not st.session_state.styles_generated:
        if st.button("Generate Styles") and query:
            st.session_state.style_urls = []
            st.session_state.styles = []
            st.session_state.selected_style_url = None
            st.session_state.selected_style = None

            with st.spinner("Generating styles..."):
                for i in range(3):
                    try:
                        response, style = planner.create_styles(query)
                        query += f" Don't give me colors of type {style.needed_clothes[0].color}"

                        # extract URL
                        if hasattr(response, "data") and isinstance(response.data, list):
                            url = response.data[0].url
                        elif hasattr(response, "url"):
                            url = response.url
                        elif hasattr(response, "text") and response.text.startswith("http"):
                            url = response.text
                        else:
                            url = str(response)

                        st.session_state.style_urls.append(url)
                        st.session_state.styles.append(style)
                    except Exception as e:
                        st.error(f"Failed to generate style {i+1}: {e}")

            # flip the guard so we never generate again
            st.session_state.styles_generated = True
            
    # Display generated styles and allow user to select
    if st.session_state.style_urls:
        st.subheader("Choose your preferred style:")
        cols = st.columns(len(st.session_state.style_urls))
        for idx, url in enumerate(st.session_state.style_urls):
            with cols[idx]:
                try:
                    st.image(url, caption=f"Option {idx+1}", use_container_width=True)
                except Exception:
                    st.write(f"[Option {idx+1} URL]({url})")
        
        # Radio buttons for selection
        choice = st.radio(
            "Select an option:",
            options=[f"Option {i+1}" for i in range(len(st.session_state.style_urls))]
        )
        
        # Confirm button
        if st.button("Confirm Selection"):
            sel_idx = int(choice.split()[1]) - 1
            st.session_state.selected_style_url = st.session_state.style_urls[sel_idx]
            st.session_state.selected_style = st.session_state.styles[sel_idx]
            st.success(f"You selected Option {sel_idx+1}")

    # Display final selected style URL
    if st.session_state.selected_style:
        st.markdown("---")
        st.header("Selected Style Preview")
        try:
            st.image(st.session_state.selected_style_url, use_container_width=True)
        except Exception:
            st.write(f"[Selected Style URL]({st.session_state.selected_style})")
        st.write(st.session_state.selected_style.needed_clothes)

    # st.write(f"Now we are going to find you clothes from the Google Search based on the following style: {st.session_state.selected_style}")

    if st.session_state.styles_generated and st.session_state.selected_style != None:

        response= planner.find_clothes("Ignore",st.session_state.selected_style)
        style=response.needed_clothes

        print(style)
        create_outfit(style)

        # persist clothing_options across reruns
        if 'clothing_options' not in st.session_state:
            st.session_state.clothing_options = response.clothing_options

        options    = st.session_state.clothing_options
        categories = list(options.keys())

        # View-mode toggle
        st.sidebar.header("View Mode")
        view_mode = st.sidebar.radio("Show:", ["By Category", "All Outfits"])
        # view_mode = "All Outfits"

        if view_mode == "By Category":
            # category selector + gallery
            st.sidebar.header("Filter by category")
            choice = st.sidebar.selectbox("Choose a category", categories)
            display_category(name=choice, items=options.get(choice, []), cols=3)

        else:  # All Outfits
            st.markdown("## All Outfits")
            generate_and_display_outfits(response, categories)


if __name__ == '__main__':
    main()