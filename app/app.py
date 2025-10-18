# app/app.py
import streamlit as st
import os
from recommender import get_recommendations
from utils import get_poster


#  INITIALIZATION

st.set_page_config(page_title="MiniFlix", layout="wide", page_icon="🎬")

if "selected_user" not in st.session_state:
    st.session_state.selected_user = None


#  CSS STYLING
st.markdown("""
<style>
/* Global App Styling */
.stApp {
    background-color: #141414;
    background-image: url("https://wallpapers.com/images/hd/dark-netflix-ls3t9oqfzknzkdp8.jpg");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: 'Helvetica Neue', sans-serif;
    color: #ffffff;
}

/* Headings */
h1, h2, h3 {
    font-weight: bold;
    text-align: center;
    color: #e50914;
}

/* Avatar hover effects */
.avatar {
    transition: all 0.3s ease-in-out;
    border-radius: 50%;
    filter: grayscale(60%);
    box-shadow: 0px 0px 10px rgba(0,0,0,0.8);
}
.avatar:hover {
    transform: scale(1.15);
    filter: grayscale(0%);
    box-shadow: 0px 0px 25px rgba(229,9,20,0.8);
    cursor: pointer;
}

/* User button styling */
.stButton>button {
    background-color: transparent;
    border: none;
    color: #ffffff;
    font-weight: bold;
    font-size: 18px;
    text-align: center;
}
.stButton>button:hover {
    color: #e50914;
    transform: scale(1.05);
}

/* Movie cards styling */
.movie-card {
    text-align: center;
    padding: 10px;
}
.movie-card img {
    border-radius: 10px;
    transition: transform 0.2s ease;
}
.movie-card img:hover {
    transform: scale(1.05);
}
.movie-title {
    color: white;
    font-size: 15px;
    font-weight: bold;
    margin-top: 8px;
}
.movie-rating {
    color: #e50914;
    font-size: 14px;
}
.back-btn {
    background-color: #e50914;
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 16px;
    font-weight: bold;
    cursor: pointer;
    margin-top: 20px;
}
.back-btn:hover {
    background-color: #f40612;
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)


# USER AVATARS AND PROFILES

avatars = [
    "https://cdn-icons-png.flaticon.com/512/4140/4140048.png",
    "https://cdn-icons-png.flaticon.com/512/4140/4140037.png",
    "https://cdn-icons-png.flaticon.com/512/4140/4140061.png",
    "https://cdn-icons-png.flaticon.com/512/4140/4140056.png"
]

users = [10, 20, 30, 40] 


# HOME SCREEN (PROFILE SELECTION)

if st.session_state.selected_user is None:
    st.markdown("<h1>MINIFLIX</h1>", unsafe_allow_html=True)
    st.markdown("<h3>Who's watching?</h3>", unsafe_allow_html=True)
    st.write("")  # Add spacing

    cols = st.columns(len(users))

    for i, user in enumerate(users):
        with cols[i]:
            try:
                st.image(avatars[i], width=160, caption="", output_format="auto", use_container_width=False, clamp=True, channels="RGB")
            except Exception:
                st.image(fallback_avatars[i], width=160)

            # Add hoverable avatar (CSS handles animation)
            if st.button(f"User {user}", key=f"user_{user}", use_container_width=True):
                st.session_state.selected_user = user
                st.rerun()

# RECOMMENDATION SCREEN
else:
    user_id = st.session_state.selected_user
    st.markdown(f"<h2>Welcome back, User {user_id}</h2>", unsafe_allow_html=True)
    st.markdown("<h3>Because you watched similar movies...</h3>", unsafe_allow_html=True)

    # Generate recommendations
    try:
        topN = get_recommendations(
        target_user=user_id,
        ratings_path="app/data/ratings.csv",
        movies_path="app/data/movies.csv",
        links_path="app/data/links.csv"
        )


        if len(topN) == 0:
            st.warning("No recommendations found for this user.")
        else:
            # Display movies like a Netflix carousel grid
            n_cols = 5
            cols = st.columns(n_cols)
            for i, (_, row) in enumerate(topN.iterrows()):
                poster = get_poster(row["imdbId"])
                with cols[i % n_cols]:
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                    st.image(poster if poster else "https://via.placeholder.com/300x450/141414/FFFFFF?text=No+Poster", use_container_width=True)

                    st.markdown(f"<div class='movie-title'>{row['title']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='movie-rating'>⭐ {row['pred']:.2f}</div>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error generating recommendations: {e}")

    # Back button
    st.markdown("<br><hr>", unsafe_allow_html=True)
    if st.button("⬅️ Back to profiles", key="back"):
        st.session_state.selected_user = None
        st.rerun()
