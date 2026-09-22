import streamlit as st
import pickle
import requests
import os

movies_df = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Load API key from environment variable or Streamlit secrets
API_KEY = os.environ.get("TMDB_API_KEY") or st.secrets.get("TMDB_API_KEY", "")
#@st.cache_data
def fetch_posters(movie_id):
    if not API_KEY:
        return None  # avoid making a doomed request
    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/movie/{movie_id}",
            params={"api_key": API_KEY, "language": "en-US"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    except requests.exceptions.RequestException:
        # st.warning(f"Could not fetch poster: {e}")
        pass
    return None

def recommend(movie):
    recommended = []
    recommended_posters = []
    movies_index = movies_df[movies_df['title'] == movie].index[0]
    row = similarity[movies_index]
    movies_list = sorted(list(enumerate(row)), reverse=True, key=lambda x: x[1])[1:6]
    for i in movies_list:
        movie_id = movies_df.iloc[i[0]].movie_id
        movie_title = movies_df.iloc[i[0]].title
        recommended.append(movie_title)
        recommended_posters.append(fetch_posters(movie_id))
    return recommended, recommended_posters

st.title('Movie Recommender System')

selected_movie_name = st.selectbox('Select a movie', movies_df['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.header(name)
            if poster:
                st.image(poster)
            else:
                st.write("No poster available")