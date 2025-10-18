# app/recommender.py
import pandas as pd
import os

def get_recommendations(target_user: int, ratings_path=None, movies_path=None, links_path=None):
    """Load precomputed recommendations for the given user."""
    file_path = os.path.join("app", "data", "precomputed", f"predictions_user{target_user}.csv")

    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["movieId", "title", "pred", "imdbId"])

    df = pd.read_csv(file_path)

    # Ensure required columns exist
    for col in ["movieId", "title", "pred"]:
        if col not in df.columns:
            df[col] = None

    return df.sort_values(by="pred", ascending=False).reset_index(drop=True).head(10)
