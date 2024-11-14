import streamlit as st
import pandas as pd

def main():
    st.title("Cinnaboxd")

    # Archivos de géneros (divididos en múltiples archivos)
    genre_files = [f'Archivos/genres_part{i}.csv' for i in range(1,2)]  # Suponiendo que hay 11 archivos de géneros

    # Archivos de actores (58 partes)
    actor_files = [f'Archivos/actors_part{i}.csv' for i in range(1, 8)]  # Cargar los 58 archivos de actores

    # Cargar y concatenar los archivos de géneros
    dg_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf-8', engine='python', on_bad_lines='skip') for file in genre_files], ignore_index=True)

    # Cargar y concatenar los archivos de actores
    da_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf-8', engine='python', on_bad_lines='skip') for file in actor_files], ignore_index=True)

    # Cargar los CSV de películas y pósters
    dp_chunks = pd.read_csv('Archivos/posters_part1.csv', sep=',', encoding='utf-8', engine='python', on_bad_lines='skip', chunksize=25000)
    dp = next(dp_chunks).fillna('')  # Llenar los valores nulos de los pósters con una cadena vacía

    dm_chunks = pd.read_csv('Archivos/movies_part1.csv', sep=',', encoding='utf-8', engine='python', on_bad_lines='skip', chunksize=25000)
    dm = next(dm_chunks).fillna('')  # Llenar los valores nulos de las películas con una cadena vacía

    # Crear una lista de nombres de películas para que el usuario elija
    movie_names = dm['name'].unique()
    movie_selected = st.selectbox("Selecciona una película", movie_names)

    if movie_selected:
        # Buscar los datos relacionados con la película seleccionada
        movie_id = dm[dm['name'] == movie_selected]['id'].values[0]

        # Buscar géneros, actores y la URL del póster para esta película
        movie_genres = dg_combined[dg_combined['id'] == movie_id]['genre'].unique()  # Usar los géneros combinados
        movie_actors = da_combined[da_combined['id'] == movie_id]['name'].unique()[:5]  # Usar los actores combinados
        movie_tagline = dm[dm['id'] == movie_id]['tagline'].unique()
        movie_description = dm[dm['id'] == movie_id]['description'].unique()
        movie_rating = dm[dm['id'] == movie_id]['rating'].unique()
        movie_minute = dm[dm['id'] == movie_id]['minute'].unique()
        movie_poster_url = dp[dp['id'] == movie_id]['link'].values[0]

        # Verificar que movie_genres no esté vacío antes de intentar concatenar
        if len(movie_genres) > 0:
            # Concatenar las películas de los géneros seleccionados
            movie_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in movie_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True)
            
            if movie_genres_3.empty:
                st.write("No se encontraron películas similares para los géneros seleccionados.")
            else:
                # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas
                movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left')

                # Unir los datos con el DataFrame de pósters (dp) para obtener las URLs de los pósters
                movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left')

                # Obtener las tres primeras películas por género
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
        else:
            st.write("No se encontraron géneros para esta película.")

    st.write('Dale dos clicks al botón después de seleccionar la película: ')
    # Crear botones para cambiar a la página personal
    if st.button("Buscar"):
        st.session_state.page = "Personal"  # Cambiar a la página personal

