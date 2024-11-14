import streamlit as st
import pandas as pd

def main():
    st.title("Cinnaboxd")
    
    # Cargar los CSV y mostrar las películas disponibles
    dp_chunks = pd.read_csv('Archivos/posters.csv', sep=',', encoding='ISO-8859-1', engine='python', on_bad_lines='skip', chunksize=25000)
    dp = next(dp_chunks).fillna(0)

    dm_chunks = pd.read_csv('Archivos/movies.csv', sep=',', encoding='ISO-8859-1', engine='python', on_bad_lines='skip', chunksize=25000)
    dm = next(dm_chunks).fillna(0)

    da_chunks = pd.read_csv('Archivos/actors.csv', sep=',', encoding='ISO-8859-1', engine='python', on_bad_lines='skip', chunksize=25000)
    da = next(da_chunks).fillna(0)

    dg_chunks = pd.read_csv('Archivos/genres.csv', sep=',', encoding='ISO-8859-1', engine='python', on_bad_lines='skip', chunksize=25000)
    dg = next(dg_chunks).fillna(0)

    # Crear una lista de nombres de películas para que el usuario elija
    movie_names = dm['name'].unique()
    movie_selected = st.selectbox("Selecciona una película", movie_names)

    if movie_selected:
        # Buscar los datos relacionados con la película seleccionada
        movie_id = dm[dm['name'] == movie_selected]['id'].values[0]

        # Buscar géneros, actores y la URL del poster para esta película
        movie_genres = dg[dg['id'] == movie_id]['genre'].unique()
        movie_actors = da[da['id'] == movie_id]['name'].unique()[:5]
        movie_tagline = dm[dm['id'] == movie_id]['tagline'].unique()
        movie_description = dm[dm['id'] == movie_id]['description'].unique()
        movie_rating = dm[dm['id'] == movie_id]['rating'].unique()
        movie_minute = dm[dm['id'] == movie_id]['minute'].unique()
        movie_poster_url = dp[dp['id'] == movie_id]['link'].values[0]

        # Filtrar las películas de todos los géneros y obtener las tres primeras de cada uno
        # Primero, obtener las películas de los géneros de la película seleccionada
        movie_genres_3 = pd.concat([dg[dg['genre'] == genre] for genre in movie_genres])

        # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas
        movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left')

        # Unir los datos con el DataFrame de pósters (dp) para obtener las URLs de los pósters
        movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left')

        # Obtener las tres primeras películas por género (esto puede ser ajustado si lo deseas)
        movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(4)

        # Guardar todos los datos seleccionados en session_state para usarlos en la página personal
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
            'genres_3': movie_genres_3  # Aquí están las películas similares
        }
    
    st.write('Dale dos clicks al botón después de seleccionar la película: ')
    # Crear botones para cambiar a la página personal
    if st.button("Buscar"):
        st.session_state.page = "Personal"  # Cambiar a la página personal





