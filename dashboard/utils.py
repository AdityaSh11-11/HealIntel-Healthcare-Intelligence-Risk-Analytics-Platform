import pandas as pd
import streamlit as st
from database import get_engine

engine = get_engine()

@st.cache_data(ttl=60)
def load_view(view_name: str):
    return pd.read_sql(f"SELECT * FROM {view_name}", engine)

def clear_cache():
    st.cache_data.clear()