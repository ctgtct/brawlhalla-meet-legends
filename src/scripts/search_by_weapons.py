from utils.data_access import WEAPONS_DICT
from typing import List
import streamlit as st
from scripts.legend_viewer import display_legends  # add import

def get_legends_by_weapon(weapon) -> List[str]:
    if weapon is None:
        return []
    return WEAPONS_DICT[weapon]

def get_legends_by_weapons(w1, w2) -> List[str]:
    if w1 is None:
        return get_legends_by_weapon(w2)
    if w2 is None:
        return get_legends_by_weapon(w1)
    legends_with_w1 = get_legends_by_weapon(w1)
    return [legend for legend in legends_with_w1 if legend in WEAPONS_DICT[w2]]


def handle_legends_by_weapons():
    col1, col2 = st.columns(2)
    with col1:
        weapon_1 = st.selectbox("Weapon 1", options=WEAPONS_DICT.keys(), index=None, placeholder="Select a weapon...")
    with col2:
        weapon_2 = st.selectbox("Weapon 2", options=WEAPONS_DICT.keys(), index=None, placeholder="Select a weapon...")
    
    if weapon_1 or weapon_2:
        legends = get_legends_by_weapons(weapon_1, weapon_2)
        if legends:
            display_legends(legends)
        else:
            st.write("No legends with that weapon combo")
