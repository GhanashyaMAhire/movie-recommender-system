import os
import pandas as pd
import streamlit as st
import pickle
import requests

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]

SIMILARITY_URL = "https://huggingface.co/mukund-m/movie-recommender-assets/resolve/main/similarity.pkl"
SIMILARITY_FILE = "similarity.pkl"

if not os.path.exists(SIMILARITY_FILE):
    try:
        st.info("Downloading similarity matrix from Hugging Face...")
        response = requests.get(SIMILARITY_URL)
        with open(SIMILARITY_FILE, 'wb') as f:
            f.write(response.content)

        if os.path.getsize(SIMILARITY_FILE) < 100000: 
            raise Exception("Downloaded file is too small. Likely failed or incomplete.")
    except Exception as e:
        st.error(f"Failed to download similarity.pkl: {e}")
        st.stop()

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
        response = requests.get(url)
        data = response.json()
        return "https://image.tmdb.org/t/p/w500" + data.get('poster_path', '')
    except:
        return "https://via.placeholder.com/500x750?text=No+Image"

def recommend(movie):
    if movie not in movies['title'].values:
        return [], []

    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters

try:
    with open("movie_dict.pkl", "rb") as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)

    with open(SIMILARITY_FILE, "rb") as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

st.title("Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])
    else:
        st.warning("No recommendations found.")
