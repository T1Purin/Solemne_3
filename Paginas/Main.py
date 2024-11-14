import streamlit as st
import pandas as pd
import os

def load_data():
    # Verificar si los datos ya están cargados en session_state
    if 'actors_df' not in st.session_state:
        st.session_state.actors_df = load_csv_chunks('actors_part', 'actors')
        st.session_state.movies_df = load_csv_chunks('movies_part', 'movies')
        st.session_state.posters_df = load_csv_chunks('posters_part', 'posters')
        st.session_state.genres_df = load_csv_chunks('genres_part', 'genres')

def load_csv_chunks(prefix, name):
    """Carga los CSVs de manera eficiente por chunks y los concatena."""
    directorio = 'Archivos'
    csv_files = [f for f in os.listdir(directorio) if f.startswith(prefix) and f.endswith('.csv')]
    chunk_size = 50000  # Ajustar según la memoria y tamaño del archivo
    
    # Lista para almacenar los chunks
    dfs = []
    
    # Leer todos los archivos correspondientes por chunks
    for csv_file in csv_files:
        file_path = os.path.join(directorio, csv_file)
        for chunk in pd.read_csv(file_path, sep=',', encoding='ISO-8859-1', engine='python', on_bad_lines='skip', chunksize=chunk_size):
            dfs.append(chunk.fillna(0))  # Unir los chunks en la lista

    # Concatenar todos los chunks en un solo DataFrame
    return pd.concat(dfs, ignore_index=True)

def main():
    # Cargar los datos si no se han cargado
    load_data()

    st.title("Cinnaboxd")
    
    # Usar los datos de session_state
    actors_df = st.session_state.actors_df
    movies_df = st.session_state.movies_df
    posters_df = st.session_state.posters_df
    genres_df = st.session_state.genres_df

    # Crear una lista de nombres de películas para que el usuario elija
    movie_names = movies_df['name'].unique()
    movie_selected = st.selectbox("Selecciona una película", movie_names)

    if movie_selected:
        movie_id = movies_df[movies_df['name'] == movie_selected]['id'].values[0]

        # Buscar géneros, actores y la URL del poster para esta película
        movie_genres = genres_df[genres_df['id'] == movie_id]['genre'].unique()
        movie_actors = actors_df[actors_df['id'] == movie_id]['name'].unique()[:5]
        movie_tagline = movies_df[movies_df['id'] == movie_id]['tagline'].unique()
        movie_description = movies_df[movies_df['id'] == movie_id]['description'].unique()
        movie_rating = movies_df[movies_df['id'] == movie_id]['rating'].unique()
        movie_minute = movies_df[movies_df['id'] == movie_id]['minute'].unique()
        movie_poster_url = posters_df[posters_df['id'] == movie_id]['link'].values[0]

        movie_genres_3 = pd.concat([genres_df[genres_df['genre'] == genre] for genre in movie_genres])
        movie_genres_3 = movie_genres_3.merge(movies_df[['id', 'name']], on='id', how='left')
        movie_genres_3 = movie_genres_3.merge(posters_df[['id', 'link']], on='id', how='left')
        movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(4)

        st.session_state.selected_movie = {
            'name': movie_selected,
            'id': movie_id,
            'genres': ', '.join(movie_genres),
            'actors': ', '.join(movie_actors),
            'tagline': movie_tagline,
            'description': movie_description,
            'rating': movie_rating,
            'minute': movie_minute,
            'poster_url': movie_poster_url,
            'genres_3': movie_genres_3
        }

    st.write('Dale dos clicks al botón después de seleccionar la película: ')
    if st.button("Buscar"):
        st.session_state.page = "Personal"  # Cambiar a la página personal

