import streamlit as st
import os
from recommender import get_recommendations
from utils import get_poster

#Initialize session state 
if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

# Page setup
st.set_page_config(page_title="MiniFlix", page_icon="🎬", layout="wide")

# Custom CSS for Netflix look 
st.markdown("""
<style>
.stApp {
    background-color: #141414;
    background-image: url("https://wallpapers.com/images/hd/dark-netflix-ls3t9oqfzknzkdp8.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: #fff;
}
h1, h2, h3, h4 {
    color: #e50914;
    font-family: "Helvetica Neue", sans-serif;
    font-weight: bold;
}
.user-card {
    text-align: center;
    border-radius: 15px;
    padding: 10px;
    transition: transform 0.3s;
}
.user-card:hover {
    transform: scale(1.08);
    cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# User avatars 
avatars = [
    os.path.join(os.path.dirname(__file__), "assets/avatar1.png"),
    os.path.join(os.path.dirname(__file__), "assets/avatar2.png"),
]

# Available users (choose 2 random or fixed)
users = [10, 20] 

# Display home if no user selected 
if st.session_state.selected_user is None:
    st.title("🎬 MiniFlix")
    st.subheader("Who's watching?")

    cols = st.columns(len(users))

    for i, user in enumerate(users):
        with cols[i]:
            # Safely load avatar (fallback to placeholder if missing)
            try:
                st.image(avatars[i % len(avatars)], width=180)
            except Exception:
                st.image("https://via.placeholder.com/180x180.png?text=User", width=180)

            # Button to select user
            if st.button(f"User {user}", key=f"user_{user}", use_container_width=True):
                st.session_state.selected_user = user
                st.rerun()

# If user selected: show recommendations
else:
    user_id = st.session_state.selected_user
    st.markdown(f"## 👤 Recommendations for User {user_id}")
    st.write("Fetching personalized recommendations...")

    try:
        topN = get_recommendations(
            target_user=user_id,
            ratings_path="data/ratings.csv",
            movies_path="data/movies.csv",
            links_path="data/links.csv"
        )

        if len(topN) == 0:
            st.warning("No recommendations found for this user. Try another profile.")
        else:
            st.success(f"Top {len(topN)} movie recommendations generated!")

            # Display recommendations in rows
            n_cols = 5
            cols = st.columns(n_cols)
            for i, (_, row) in enumerate(topN.iterrows()):
                poster = get_poster(row["imdbId"])
                with cols[i % n_cols]:
                    if poster:
                        st.image(poster, use_column_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x450.png?text=No+Poster", use_column_width=True)
                    st.caption(f"🎥 {row['title']}\n⭐ Predicted Rating: {row['pred']:.2f}")

    except Exception as e:
        st.error(f"Error generating recommendations: {e}")

    # Back button to go back to profile selection
    st.markdown("---")
    if st.button("⬅️ Back to profiles"):
        st.session_state.selected_user = None
        st.rerun()
