import streamlit as st
import pandas as pd
import requests
from urllib.parse import quote_plus
import difflib

# === Load Data ===
movies = pd.read_csv("tmdb_5000_movies.csv")

# === YouTube Search & Poster ===
def fetch_youtube_trailer_id(movie_title):
    query = f"{movie_title} official trailer"
    search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"

    try:
        response = requests.get(search_url)
        if "/watch?v=" in response.text:
            start = response.text.find("/watch?v=")
            video_id = response.text[start + 9:start + 20]
            return video_id
    except:
        return None

# === Recommender Logic (simple matching without similarity.pkl) ===
def recommend(movie):
    movie = movie.lower()
    all_titles = movies['title'].str.lower().tolist()
    close_matches = difflib.get_close_matches(movie, all_titles, n=5, cutoff=0.5)

    recommended_titles = []
    youtube_ids = []
    wiki_links = []

    for title in close_matches:
        actual_title = movies[movies['title'].str.lower() == title].iloc[0].title
        yt_id = fetch_youtube_trailer_id(actual_title)
        wiki_link = f"https://en.wikipedia.org/wiki/{actual_title.replace(' ', '_')}"
        recommended_titles.append(actual_title)
        youtube_ids.append(yt_id)
        wiki_links.append(wiki_link)

    return recommended_titles, youtube_ids, wiki_links

# === Streamlit App UI ===
st.set_page_config(page_title="🎬 Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender with Trailers & Wiki")

movie_list = movies['title'].values
selected_movie = st.selectbox("Select or type a movie name:", movie_list)

if st.button("Show Recommendation"):
    names, yt_ids, wikis = recommend(selected_movie)

    if names:
        cols = st.columns(len(names))
        for idx, col in enumerate(cols):
            with col:
                st.markdown(f"**{names[idx]}**")
                if yt_ids[idx]:
                    yt_thumb = f"https://img.youtube.com/vi/{yt_ids[idx]}/hqdefault.jpg"
                    yt_link = f"https://www.youtube.com/watch?v={yt_ids[idx]}"
                    st.markdown(f"[![Trailer]({yt_thumb})]({yt_link})", unsafe_allow_html=True)
                else:
                    st.markdown("_Trailer not found_")
                st.markdown(f"[📖 Wikipedia]({wikis[idx]})", unsafe_allow_html=True)
    else:
        st.warning("No similar movies found.")

st.markdown("""
<hr style="margin-top: 50px;">
<div style='text-align: center; font-size: 14px; color: grey;'>
    Made with ❤️ by <b>Shravani</b>
</div>
""", unsafe_allow_html=True)
