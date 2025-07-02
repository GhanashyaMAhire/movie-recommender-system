import os
import pandas as pd
import streamlit as st
import pickle
import requests

def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        response = requests.get(url)
        if response.status_code == 200:
            with open(local_filename, 'wb') as f:
                f.write(response.content)
        else:
            st.error(f"Failed to download {local_filename} from Google Drive.")
            st.stop()

def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=0d08609cee81e06af7a9986e742928ba&language=en-US"
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

# Download similarity.pkl from Google Drive
SIMILARITY_URL = "https://drive.google.com/uc?id=1JM3OAPxPSkqk_jJV6YO9ZIs3iSrnd2Zo"
download_file(SIMILARITY_URL, 'similarity.pkl')

# Load pickled files
try:
    with open('movie_dict.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)

    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

st.title('🎥 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movies['title'].values
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)

    if names:
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])
    else:
        st.warning("No recommendations found.")
