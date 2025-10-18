import requests
import pandas as pd
import streamlit as st

def get_poster(imdb_id, use_tmdb=False):
    """Fetch movie poster using OMDb or TMDb with fallbacks."""
    fallback = "https://via.placeholder.com/300x450.png?text=No+Poster"
    if pd.isna(imdb_id):
        return fallback

    try:
        if use_tmdb:
            api_key = st.secrets.get("TMDB_API_KEY", "")
            if not api_key:
                return fallback
            url = f"https://api.themoviedb.org/3/find/tt{int(imdb_id):07d}?api_key={api_key}&external_source=imdb_id"
            r = requests.get(url, timeout=5)
            data = r.json()
            results = data.get("movie_results", [])
            if results and results[0].get("poster_path"):
                return f"https://image.tmdb.org/t/p/w500{results[0]['poster_path']}"
            return fallback
        else:
            api_key = st.secrets.get("OMDB_API_KEY", "")
            if not api_key:
                return fallback
            imdb_id_str = f"tt{int(imdb_id):07d}"
            url = f"https://www.omdbapi.com/?i={imdb_id_str}&apikey={api_key}"
            r = requests.get(url, timeout=5)
            data = r.json()
            poster = data.get("Poster")
            if poster and poster.startswith("http") and poster != "N/A":
                # Check if image is reachable
                try:
                    head = requests.head(poster, timeout=3)
                    if head.status_code == 200:
                        return poster
                except:
                    pass
            return fallback
    except Exception as e:
        print("Poster fetch error:", e)
        return fallback
