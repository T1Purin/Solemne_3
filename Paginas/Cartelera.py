import streamlit as st
import pandas as pd

def cartelera():
    st.title("Detalles de la Película Seleccionada")
    # Verificar si ya hay una película seleccionada en session_state
    if "selected_movie_genre" in st.session_state:
        cartelera_data = st.session_state.selected_movie_genre
        cartelera_id = cartelera_data['id']  # ID de la película actual
        # Mostrar la información de la película seleccionada (columna 1)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(cartelera_data['poster_url'], caption=cartelera_data['name'], width=230)
        with col2:
            st.title(cartelera_data['name'])
            st.write(f'Calificación: {cartelera_data["rating"][0]}')
            st.progress(float(cartelera_data["rating"][0]) / 5)  # Asegúrate de que rating esté en el formato adecuado (0-5)
            st.caption(f"Géneros: {cartelera_data['genres']}, Duración: {int(cartelera_data['minute'][0])} minutos.")
            st.write(cartelera_data['tagline'][0])
            st.write(f"Actores: {cartelera_data['actors']}")
            st.write(cartelera_data['description'][0])

        # Crear la caja para ingresar el nombre y la reseña
        name = st.text_input("Ingresa tu nombre:")
        review = st.text_area("Escribe tu reseña:")

        # Crear un espacio para mostrar las reseñas anteriores 
        if "reviews" not in st.session_state:
            st.session_state.reviews = {}  # Inicializar un diccionario para almacenar reseñas por película

        # Mostrar reseñas ya existentes para esta película
        if cartelera_id in st.session_state.reviews:
            st.subheader("Reseñas Anteriores:")
            for review_entry in st.session_state.reviews[cartelera_id]:
                st.write(f"{review_entry['name']}: {review_entry['review']}")

        # Botón para enviar la reseña
        if st.button("Enviar reseña"):
            if name and review:
                # Guardar la reseña en el diccionario de reseñas
                if cartelera_id not in st.session_state.reviews:
                    st.session_state.reviews[cartelera_id] = []  # Inicializa la lista si es la primera reseña
                st.session_state.reviews[cartelera_id].append({'name': name, 'review': review})
                def agregar_pelicula(id, name, review, archivo='Archivos/reseñas.csv'):
                    # Crear un diccionario con los datos de la película
                    new_movie = {'id': id, 'name': name, 'review': review}
                    
                    # Crear un DataFrame con los datos de la nueva película
                    new_movie_df = pd.DataFrame([new_movie])
                    
                    # Verificar si el archivo CSV ya existe
                    try:
                        # Si el archivo ya existe, agregamos la nueva película al archivo sin sobrescribir
                        new_movie_df.to_csv(archivo, mode='a', header=False, index=False)
                        print(f"Película '{name}' agregada correctamente.")
                    except FileNotFoundError:
                        # Si el archivo no existe, lo creamos con los encabezados
                        new_movie_df.to_csv(archivo, mode='w', header=True, index=False)
                        print(f"Archivo CSV creado y película '{name}' agregada.")

                agregar_pelicula(cartelera_data['id'],name,review)
                st.write(f"Gracias {name} por tu reseña:")
                st.write(review)
            elif not name:
                st.write("Por favor, ingresa tu nombre.")
            elif not review:
                st.write("Por favor, escribe una reseña.")

    # Mostrar las 4 películas similares (si existen)
    if 'genres_3' in cartelera_data and not cartelera_data['genres_3'].empty:
        cols = st.columns(3)  # Usamos 3 columnas para las películas similares
        # Filtrar las películas similares para excluir la película actual
        filtered_similar_movies = cartelera_data['genres_3'][cartelera_data['genres_3']['id'] != cartelera_id]
        # Asegurarse de que no haya duplicados de las películas ya mostradas
        displayed_movie_ids = [cartelera_id]  # Inicializamos con el ID de la película seleccionada
        # Iteramos sobre las columnas para obtener los IDs de las películas que ya están en la barra
        for col in cols:
            displayed_movie_ids += [movie['id'] for movie in st.session_state.get('displayed_movies', [])]
        # Excluir cualquier película que ya se haya mostrado previamente
        filtered_similar_movies = filtered_similar_movies[~filtered_similar_movies['id'].isin(displayed_movie_ids)]
        # Si hay menos de 3 películas similares, reemplazamos las faltantes con otras películas
        if len(filtered_similar_movies) < 3:
            other_movies = cartelera_data['genres_3'][cartelera_data['genres_3']['id'] != cartelera_id]
            other_movies = other_movies[~other_movies['id'].isin(filtered_similar_movies['id'])]
            # Añadimos más películas hasta completar 3
            additional_movies = other_movies.head(3 - len(filtered_similar_movies))
            filtered_similar_movies = pd.concat([filtered_similar_movies, additional_movies], ignore_index=True)
        # Asegurarse de que haya exactamente 3 películas
        filtered_similar_movies = filtered_similar_movies.head(3)
        # Guardamos los IDs de las películas que vamos a mostrar en la barra para evitar duplicados en futuras consultas
        st.session_state['displayed_movies'] = filtered_similar_movies.to_dict(orient='records')
        # Iterar sobre las películas similares y asignar cada una a una columna
        for idx, (index, row) in enumerate(filtered_similar_movies.iterrows()):
            with cols[idx]:  # Usar la columna correspondiente
                st.image(row['link'], caption=row['name'], width=220)
                # Crear un botón para cada película que redirige a la página de detalles
                if st.button(f"{row['name']}", key=f"movie_button_{row['id']}"):
                    # Archivos de géneros (divididos en múltiples archivos)
                    genre_files = [f'Archivos/genres_part{i}.csv' for i in range(1, 2)]  # Suponiendo que hay 11 archivos de géneros
                    # Archivos de actores (58 partes)
                    actor_files = [f'Archivos/actors_part{i}.csv' for i in range(1, 8)]  # Cargar los 58 archivos de actores
                    # Cargar y concatenar los archivos de géneros
                    dg_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in genre_files], ignore_index=True)
                    # Cargar y concatenar los archivos de actores
                    da_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in actor_files], ignore_index=True)
                    # Cargar los CSV de películas y pósters
                    dp_chunks = pd.read_csv('Archivos/posters_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000)
                    dp = next(dp_chunks).fillna('')  # Llenar los valores nulos de los pósters con una cadena vacía
                    dm_chunks = pd.read_csv('Archivos/movies_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000)
                    dm = next(dm_chunks).fillna('')  # Llenar los valores nulos de las películas  
                    if row['id'] in dm['id'].values:
                        movie_id = row['id']
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
                                    'name': row['name'],
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

        else:
            st.write("No hay películas similares disponibles.")
    else:
        st.write("No se ha seleccionado ninguna película aún.")
    # Crear un botón para regresar a la página principal
    st.write('Dale dos clics al botón para regresar:')
    if st.button("Regresar a la Página Principal"):
        st.session_state.page = "Main"  # Cambiar a la página principal
        st.session_state.selected_movie = None  # Limpiar la película seleccionada

