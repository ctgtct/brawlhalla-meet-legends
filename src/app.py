import streamlit as st
import pandas as pd
import json
from typing import List
from scripts.search_by_stats import handle_legends_by_stats
from scripts.search_by_tags import handle_legends_by_tags
from scripts.search_by_weapons import handle_legends_by_weapons

st.set_page_config(
    page_title="Meet The Legends",
    page_icon="resources/title/title_icon.jpg",
    layout='wide'
)
st.title('Brawlhalla: Meet the Legends')

options = [
    "Find legends by weapons",
    "Find legends by tags",
    "Find legends by stats"
]

selection = st.selectbox("What would you like to do?", options=options, index=None, placeholder="Select an option...")

if selection == options[0]:
    handle_legends_by_weapons()
elif selection == options[1]:
    handle_legends_by_tags()
elif selection == options[2]:
    handle_legends_by_stats()