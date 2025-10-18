import requests
import pandas as pd
import streamlit as st

def get_poster(imdb_id, use_tmdb=False):
    """
    Fetch movie poster using OMDb or TMDb.
    If use_tmdb=True, fetches from TMDb, otherwise OMDb.
    """
    if pd.isna(imdb_id):
        return None

    try:
        if use_tmdb:
            # TMDb version
            api_key = st.secrets.get("TMDB_API_KEY", "")
            if not api_key:
                return None
            # IMDb IDs need to be converted or you can use movieId->tmdbId mapping if available
            url = f"https://api.themoviedb.org/3/find/tt{int(imdb_id):07d}?api_key={api_key}&external_source=imdb_id"
            r = requests.get(url, timeout=5)
            data = r.json()
            results = data.get("movie_results", [])
            if results and results[0].get("poster_path"):
                return f"https://image.tmdb.org/t/p/w500{results[0]['poster_path']}"
            return None

        else:
            # OMDb version
            api_key = st.secrets.get("OMDB_API_KEY", "")
            if not api_key:
                return None
            imdb_id_str = f"tt{int(imdb_id):07d}"
            url = f"https://www.omdbapi.com/?i={imdb_id_str}&apikey={api_key}"
            r = requests.get(url, timeout=5)
            data = r.json()
            poster = data.get("Poster")
            if poster and poster != "N/A":
                return poster
            return None

    except Exception as e:
        print("Poster fetch error:", e)
        return None
