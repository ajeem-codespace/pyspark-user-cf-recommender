import streamlit as st
import pandas as pd
from recommender import get_recommendations
from utils import get_poster
import random

st.set_page_config(page_title="MiniFlix", layout="wide", page_icon="🎬")

# Load basic data
movies = pd.read_csv("data/movies.csv")
ratings = pd.read_csv("data/ratings.csv")

# Custom CSS for Netflix look
st.markdown("""
<style>
body {
  background-color: #141414;
  color: #fff;
}
h1, h2, h3 {
  color: #e50914;
  font-family: 'Helvetica Neue', sans-serif;
}
.user-card {
  text-align: center;
  border-radius: 10px;
  padding: 10px;
  transition: 0.3s;
}
.user-card:hover {
  transform: scale(1.05);
  cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# Choose users (pick 2 random ones)
users = random.sample(sorted(ratings["userId"].unique().tolist()), 2)

st.title("🎬 MiniFlix")
st.subheader("Who's watching?")

cols = st.columns(2)
avatars = ["assets/avatar1.png", "assets/avatar2.png"]

# store state
if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

# Profile selection
for i, user in enumerate(users):
    with cols[i]:
        if st.button(f"**User {user}**", key=f"user_{user}"):
            st.session_state.selected_user = user
        st.image(avatars[i % len(avatars)], width=180, use_container_width=False)

# If user selected → show recommendations
if st.session_state.selected_user:
    user_id = st.session_state.selected_user
    st.markdown(f"### 👤 Recommendations for **User {user_id}**")

    topN = get_recommendations(
        target_user=user_id,
        ratings_path="data/ratings.csv",
        movies_path="data/movies.csv",
        links_path="data/links.csv"
    )

    cols = st.columns(5)
    for i, (_, row) in enumerate(topN.iterrows()):
        poster = get_poster(row["imdbId"])
        with cols[i % 5]:
            if poster:
                st.image(poster, use_column_width=True)
            st.caption(f"{row['title']}\n⭐ {row['pred']:.2f}")
