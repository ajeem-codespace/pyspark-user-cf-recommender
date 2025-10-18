import pandas as pd
import os

def get_recommendations(target_user: int, ratings_path=None, movies_path=None, links_path=None):
    """
    Load precomputed recommendations for the given user.
    These CSVs are generated offline in the notebook using Spark.
    """
    file_path = os.path.join("app", "data", "precomputed", f"predictions_user{target_user}.csv")

    if not os.path.exists(file_path):
        return pd.DataFrame(columns=["movieId", "title", "pred", "imdbId"])

    df = pd.read_csv(file_path)

    # make sure required columns exist
    expected_cols = ["movieId", "title", "pred", "imdbId"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None

    # return top 10 sorted by predicted rating
    df = df.sort_values(by="pred", ascending=False).head(10)
    return df
