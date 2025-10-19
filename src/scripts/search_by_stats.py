from utils.data_access import (
    BASE_DATA,
    STAT_NAMES,
    COMPARATORS
)
from typing import List
import streamlit as st
from scripts.legend_viewer import display_legends  # add import

def get_legends_by_stat(stat_name, stat_val) -> List[str]:
    return list(BASE_DATA[BASE_DATA[stat_name] == stat_val]['Legend'])

def get_legends_by_stat_comparison(stat_name, stat_val, comparator='='):
    if comparator == '=':
        return get_legends_by_stat(stat_name, stat_val)
    elif comparator == '<=':
        vals = [i for i in range(stat_val+1)]
        legends = []
        for val in vals:
            legends.extend(get_legends_by_stat(stat_name, val))
        return legends
    elif comparator == '<':
        vals = [i for i in range(stat_val)]
        legends = []
        for val in vals:
            legends.extend(get_legends_by_stat(stat_name, val))
        return legends
    elif comparator == '>=':
        vals = [i for i in range(stat_val, 11)]
        legends = []
        for val in vals:
            legends.extend(get_legends_by_stat(stat_name, val))
        return legends
    elif comparator == '>':
        vals = [i for i in range(stat_val+1, 11)]
        legends = []
        for val in vals:
            legends.extend(get_legends_by_stat(stat_name, val))
        return legends
    else:
        return []
    
def get_legends_with_stat_between(stat_name, stat_lower, stat_upper):
    if stat_upper < stat_lower:
        return []

    legends_ge_lower = get_legends_by_stat_comparison(stat_name, stat_lower, '>=')
    legends_gt_upper = get_legends_by_stat_comparison(stat_name, stat_upper, '>')
    return [legend for legend in legends_ge_lower if legend not in legends_gt_upper]



def handle_legends_by_stats():
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_stat = st.selectbox("Which stat do you want to filter on?", options=STAT_NAMES, index=None, placeholder="Select a stat")
    with col2:
        selected_comp = st.selectbox("", options=COMPARATORS, index=None, placeholder="Select a comparator...")
    with col3:
        if selected_comp == 'between':
            lower = st.number_input(
                "Lower Bound",
                min_value=0,
                max_value=10,
                value=0,
                step=1 
            )
            upper = st.number_input(
                "Upper Bound:",
                min_value=0,
                max_value=10,
                value=0,
                step=1 
            )
            legends = get_legends_with_stat_between(selected_stat, lower, upper)
        else:
            selected_val = st.number_input(
                "Enter an integer:",
                min_value=0,
                max_value=10,
                value=0,
                step=1 
            )
            legends = get_legends_by_stat_comparison(selected_stat, selected_val, selected_comp)

    if legends:
        display_legends(legends)
