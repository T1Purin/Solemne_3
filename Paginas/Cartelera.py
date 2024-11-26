import pandas as pd
import streamlit as st

def cartelera():
    st.image("Archivos/logo.png")
    
    # funcion de reseñas
    def cargar_reseñas(archivo='Archivos/reseñas.csv'):
        try:
            df = pd.read_csv(archivo)
            df.columns = df.columns.str.strip()  # Limpiar columnas de posibles espacios
            if 'id' not in df.columns or 'name' not in df.columns or 'review' not in df.columns:
                st.error("El archivo CSV no tiene las columnas necesarias: 'id', 'name', 'review'.")
                return {}
            df = df.dropna(subset=['id', 'name', 'review'])  # eliminar valores nulos
            
            reseñas_dict = {}
            for _, row in df.iterrows():
                movie_id = row['id']
                if movie_id not in reseñas_dict:
                    reseñas_dict[movie_id] = []
                reseñas_dict[movie_id].append({'name': row['name'], 'review': row['review']})
            return reseñas_dict
        except FileNotFoundError:
            st.error("El archivo de reseñas no se encuentra.")
            return {}
        except Exception as e:
            st.error(f"Error al cargar las reseñas: {e}")
            return {}

    #agregar reseña
    def agregar_pelicula(id, name, review, archivo='Archivos/reseñas.csv'):
        new_movie = {'id': id, 'name': name, 'review': review}
        new_movie_df = pd.DataFrame([new_movie])
        try:
            new_movie_df.to_csv(archivo, mode='a', header=False, index=False)
            st.write(f"Gracias {name} por tu reseña:")
            st.write(review)
        except FileNotFoundError:
            new_movie_df.to_csv(archivo, mode='w', header=True, index=False)
            st.write(f"Archivo CSV creado y película '{name}' agregada.")

    if "selected_movie_genre" in st.session_state:
        cartelera_data = st.session_state.selected_movie_genre
        cartelera_id = cartelera_data['id']  # ID de la película actual

        # mostrar pelicula
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(cartelera_data['poster_url'], caption=cartelera_data['name'], width=230)
        with col2:
            minute_value = cartelera_data['minute'][0]
            try:
                minute_value = int(minute_value)  # Intentamos convertirlo a entero
            except (ValueError, TypeError):  # Capturamos posibles errores de conversión
                minute_value = 0  # Asignamos un valor predeterminado si no se puede convertir
            st.title(cartelera_data['name'])
            st.caption(f"Géneros: {cartelera_data['genres']}, Duración: {minute_value} minutos.")
            st.write(cartelera_data['tagline'][0])
            st.write(f"Actores: {cartelera_data['actors']}")
            st.write(cartelera_data['description'][0])
            rating_value = cartelera_data["rating"][0]
            try:
                rating_value = float(rating_value) if rating_value else 0  # Usar 0 si rating es vacío o no válido
            except ValueError:
                rating_value = 0  # Asignamos 0 si no se puede convertir a float
            st.write(f'Calificación: {rating_value}')
            st.progress(rating_value / 5)  # Asegúrate de que rating esté en el formato adecuado (0-5)

        name = st.text_input("Ingresa tu nombre:")
        review = st.text_area("Escribe tu reseña:")

        if "reviews" not in st.session_state:
            st.session_state.reviews = cargar_reseñas()  # Cargar reseñas desde el archivo CSV

        # mostrar reseñas
        if cartelera_id in st.session_state.reviews:
            st.subheader("Reseñas:")
            for review_entry in st.session_state.reviews[cartelera_id]:
                st.write(f"{review_entry['name']}: {review_entry['review']}")

        if st.button("Enviar reseña"):
            if name and review:
                # Guardar la reseña en el diccionario de reseñas
                if cartelera_id not in st.session_state.reviews:
                    st.session_state.reviews[cartelera_id] = [] 
                st.session_state.reviews[cartelera_id].append({'name': name, 'review': review})
                
                agregar_pelicula(cartelera_data['id'], name, review)

            elif not name:
                st.write("Por favor, ingresa tu nombre.")
            elif not review:
                st.write("Por favor, escribe una reseña.")

        st.subheader('Puede que te interesen...')

        if 'genres_3' in cartelera_data and not cartelera_data['genres_3'].empty:
            cols = st.columns(6)
            filtered_similar_movies = cartelera_data['genres_3'][cartelera_data['genres_3']['id'] != cartelera_id]
            displayed_movie_ids = [cartelera_id] 
            for col in cols:
                displayed_movie_ids += [movie['id'] for movie in st.session_state.get('displayed_movies', [])]
            filtered_similar_movies = filtered_similar_movies[~filtered_similar_movies['id'].isin(displayed_movie_ids)]

            if len(filtered_similar_movies) < 6:
                other_movies = cartelera_data['genres_3'][cartelera_data['genres_3']['id'] != cartelera_id]
                other_movies = other_movies[~other_movies['id'].isin(filtered_similar_movies['id'])]
 
                additional_movies = other_movies.head(6 - len(filtered_similar_movies))
                filtered_similar_movies = pd.concat([filtered_similar_movies, additional_movies], ignore_index=True)

            filtered_similar_movies = filtered_similar_movies.head(6)
          
            st.session_state['displayed_movies'] = filtered_similar_movies.to_dict(orient='records')
          
            for idx, (index, row) in enumerate(filtered_similar_movies.iterrows()):
                with cols[idx]:  
                    st.image(row['link'], caption=row['name'], width=220)
                  
                    if st.button(f"{row['name']}", key=f"movie_button_{row['id']}"):

                        genre_files = [f'Archivos/genres_part{i}.csv' for i in range(1, 2)]  

                        actor_files = [f'Archivos/actors_part{i}.csv' for i in range(1, 8)]  

                        dg_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in genre_files], ignore_index=True)

                        da_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in actor_files], ignore_index=True)

                        dp_chunks = pd.read_csv('Archivos/posters_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000)
                        dp = next(dp_chunks).fillna('')  

                        dm_chunks = pd.read_csv('Archivos/movies_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000)
                        dm = next(dm_chunks).fillna('')  

                        if row['id'] in dm['id'].values:

                            movie_id = row['id']
                            movie_genres = dg_combined[dg_combined['id'] == movie_id]['genre'].unique()
                            movie_actors = da_combined[da_combined['id'] == movie_id]['name'].unique()[:5]
                            movie_tagline = dm[dm['id'] == movie_id]['tagline'].unique()
                            movie_description = dm[dm['id'] == movie_id]['description'].unique()
                            movie_rating = dm[dm['id'] == movie_id]['rating'].unique()
                            movie_minute = dm[dm['id'] == movie_id]['minute'].unique()
                            movie_poster_url = dp[dp['id'] == movie_id]['link'].values[0]

                            if len(movie_genres) > 0:
            
                                movie_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in movie_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True)
                                
                                if movie_genres_3.empty:
                                    st.write("No se encontraron películas similares para los géneros seleccionados.")
                                else:
            
                                    movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left')
                
                                    movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left')

                                    movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7)

                                    # guardar datos seleccionados en session_state para usarlos en la página personal
                                    st.session_state.selected_movie = {
                                        'name': row['name'],
                                        'id': movie_id,
                                        'genres': ', '.join(movie_genres),
                                        'actors': ', '.join(movie_actors),
                                        'tagline': movie_tagline,
                                        'description': movie_description,
                                        'rating': movie_rating,
                                        'minute': movie_minute,
                                        'poster_url': movie_poster_url,
                                        'genres_3': movie_genres_3  # peliculas similares
                                    }
                                    # Cambiar la página a "DPeliculas" (detalles de la película)
                                    st.session_state.page = "DPeliculas"
                                    st.rerun()
    else:
        st.write("No se ha seleccionado ninguna película aún.")
    
    if st.button("Regresar a la Página Principal"):
        st.session_state.page = "Main"  # Cambiar a la página principal
        st.rerun()

