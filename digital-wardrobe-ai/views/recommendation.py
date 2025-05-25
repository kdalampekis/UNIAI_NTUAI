import sys
import os
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import ui.recommendation_ui  # 👈 this triggers the full UI when called

def render():
    pass
