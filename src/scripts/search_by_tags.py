from utils.data_access import (
    BASE_DATA,
    TAGS
)
from typing import List
import streamlit as st
from scripts.legend_viewer import display_legends  # add import

def get_legends_by_tag(tag) -> List[str]:
    return list(BASE_DATA[BASE_DATA[tag] == 1]['Legend'])

def handle_legends_by_tags():
    selected_tag = st.selectbox("Select the tag you're looking for", options=TAGS, index=None, placeholder='Select a tag...')
    if selected_tag:
        legends = get_legends_by_tag(selected_tag)
        if legends:
            display_legends(legends)
        else:
            st.write('No legends with selected tag')