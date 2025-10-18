import requests
import pandas as pd
import streamlit as st

def get_poster(imdb_id):
    """Fetch poster from OMDb API"""
    api_key = st.secrets.get("OMDB_API_KEY", "")
    if not api_key or pd.isna(imdb_id):
        return None
    imdb_id_str = f"tt{int(imdb_id):07d}"
    try:
        r = requests.get("https://www.omdbapi.com/", params={"i": imdb_id_str, "apikey": api_key}, timeout=5)
        j = r.json()
        return None if j.get("Poster") in (None, "N/A") else j["Poster"]
    except Exception:
        return None
