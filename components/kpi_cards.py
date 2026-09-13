import streamlit as st

def kpi(title, value, delta=None):
    with st.container(border=True):
        st.metric(
            label=title,
            value=value,
            delta=delta
        )