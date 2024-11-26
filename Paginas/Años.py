import streamlit as st
import pandas as pd
import requests
import json

def años():
    st.image("Archivos/logo.png")

    # Token de acceso personal de GitHub
    GITHUB_TOKEN = "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"
    GITHUB_REPO = "T1Purin/Solemne_3"  # Nombre del repositorio (usuario/repositorio)
    FILE_PATH = "Archivos/reseñas.csv"  # Ruta del archivo en el repositorio

    # Función para obtener el archivo desde GitHub
    def obtener_contenido_archivo():
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()  # Devuelve la metadata del archivo
        else:
            print("Error al obtener el archivo:", response.status_code)
            return None

    # Función para actualizar el archivo en GitHub
    def actualizar_archivo_github(id, name, review):
        contenido = obtener_contenido_archivo()
        if contenido is None:
            return "No se pudo obtener el archivo."
        
        # Leer el archivo CSV desde el contenido obtenido
        file_content = requests.get(contenido['download_url']).text
        df = pd.read_csv(pd.compat.StringIO(file_content))  # Leer el contenido del CSV
        
        # Crear un nuevo registro con la reseña
        new_movie = {'id': id, 'name': name, 'review': review}
        new_movie_df = pd.DataFrame([new_movie])
        
        # Agregar la nueva reseña al DataFrame
        df = pd.concat([df, new_movie_df], ignore_index=True)
        
        # Convertir el DataFrame actualizado a CSV
        updated_csv = df.to_csv(index=False)
        
        # Realizar la petición PUT para actualizar el archivo en GitHub
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        # Necesitamos el sha del archivo actual para actualizarlo
        data = {
            "message": "Actualizar reseña",  # Mensaje del commit
            "content": updated_csv.encode('utf-8').decode('utf-8'),  # Contenido actualizado
            "sha": contenido['sha'],  # SHA del archivo original
        }
        
        response = requests.put(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            return "Reseña guardada correctamente en GitHub."
        else:
            return f"Error al guardar la reseña: {response.status_code}"

    # Función para agregar una reseña al archivo CSV
    def agregar_reseña(id, name, review, archivo='Archivos/reseñas.csv'):
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

    # Función para cargar reseñas desde el archivo CSV
    def cargar_reseñas(archivo='Archivos/reseñas.csv'):
        try:
            df = pd.read_csv(archivo)
            
            # Limpiar los nombres de las columnas para eliminar espacios extra
            df.columns = df.columns.str.strip()
            
            # Verificar que las columnas esenciales existen
            if 'id' not in df.columns or 'name' not in df.columns or 'review' not in df.columns:
                st.error("El archivo CSV no tiene las columnas necesarias: 'id', 'name', 'review'.")
                return {}
            
            # Eliminar filas con valores nulos en 'id', 'name' o 'review'
            df = df.dropna(subset=['id', 'name', 'review'])
            
            # Inicializar un diccionario para almacenar reseñas por id de película
            reseñas_dict = {}
            
            # Iterar sobre las filas del DataFrame y agregar las reseñas al diccionario
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
    
    # Cargar las reseñas desde el archivo CSV al iniciar
    if "reviews" not in st.session_state:
        st.session_state.reviews = cargar_reseñas()  # Cargar reseñas desde el archivo CSV

    # Verificar si ya hay una película seleccionada en session_state
    if "selected_movie" in st.session_state:
        años_data = st.session_state.selected_movie_años
        años_id = años_data['id']  # ID de la película actual

        # Mostrar la información de la película seleccionada (columna 1)
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image(años_data['poster_url'], caption=años_data['name'], width=230)

        with col2:
            minute_value = años_data['minute'][0]
            try:
                minute_value = int(minute_value)  # Intentamos convertirlo a entero
            except (ValueError, TypeError):  # Capturamos posibles errores de conversión
                minute_value = 0  # Asignamos un valor predeterminado si no se puede convertir
            st.title(años_data['name'])
            st.caption(f"Géneros: {años_data['genres']}, Duración: {minute_value} minutos.")
            st.write(años_data['tagline'][0])
            st.write(f"Actores: {años_data['actors']}")
            st.write(años_data['description'][0])
            # Verificar que la calificación no esté vacía o sea inválida antes de convertirla a float
            rating_value = años_data["rating"][0]
            try:
                rating_value = float(rating_value) if rating_value else 0  # Usar 0 si rating es vacío o no válido
            except ValueError:
                rating_value = 0  # Asignamos 0 si no se puede convertir a float
            st.write(f'Calificación: {rating_value}')
            st.progress(rating_value / 5)  # Asegúrate de que rating esté en el formato adecuado (0-5)

        # Crear la caja para ingresar el nombre y la reseña
        name = st.text_input("Ingresa tu nombre:")
        review = st.text_area("Escribe tu reseña:")

        # Mostrar reseñas ya existentes para esta película
        if años_id in st.session_state.reviews:
            st.subheader("Reseñas:")
            for review_entry in st.session_state.reviews[años_id]:
                st.write(f"{review_entry['name']}: {review_entry['review']}")

        # Botón para enviar la reseña
        if st.button("Enviar reseña"):
            if name and review:
                # Guardar la reseña en el diccionario de reseñas
                if años_id not in st.session_state.reviews:
                    st.session_state.reviews[años_id] = []  # Inicializa la lista si es la primera reseña

                st.session_state.reviews[años_id].append({'name': name, 'review': review})

                # Llamamos a la función para guardar la reseña en el archivo CSV
                agregar_reseña(años_data['id'], name, review)
                actualizar_archivo_github(id, name, review)

                st.write(f"Gracias {name} por tu reseña:")
                st.write(review)
            elif not name:
                st.write("Por favor, ingresa tu nombre.")
            elif not review:
                st.write("Por favor, escribe una reseña.")

        st.subheader('Puede que te interesen...')

        # Mostrar las 6 películas similares (si existen)
        if 'genres_3' in años_data and not años_data['genres_3'].empty:
            cols = st.columns(6)  # Usamos 6 columnas para las películas similares

            # Filtrar las películas similares para excluir la película actual
            filtered_similar_movies = años_data['genres_3'][años_data['genres_3']['id'] != años_id]

            # Asegurarse de que no haya duplicados de las películas ya mostradas
            displayed_movie_ids = [años_id]  # Inicializamos con el ID de la película seleccionada

            # Iteramos sobre las columnas para obtener los IDs de las películas que ya están en la barra
            for col in cols:
                displayed_movie_ids += [movie['id'] for movie in st.session_state.get('displayed_movies', [])]

            # Excluir cualquier película que ya se haya mostrado previamente
            filtered_similar_movies = filtered_similar_movies[~filtered_similar_movies['id'].isin(displayed_movie_ids)]

            # Si hay menos de 6 películas similares, reemplazamos las faltantes con otras películas
            if len(filtered_similar_movies) < 6:
                other_movies = años_data['genres_3'][años_data['genres_3']['id'] != años_id]
                other_movies = other_movies[~other_movies['id'].isin(filtered_similar_movies['id'])]

                # Añadimos más películas hasta completar 6
                additional_movies = other_movies.head(6 - len(filtered_similar_movies))
                filtered_similar_movies = pd.concat([filtered_similar_movies, additional_movies], ignore_index=True)

            # Asegurarse de que haya exactamente 6 películas
            filtered_similar_movies = filtered_similar_movies.head(6)

            # Guardamos los IDs de las películas que vamos a mostrar en la barra para evitar duplicados en futuras consultas
            st.session_state['displayed_movies'] = filtered_similar_movies.to_dict(orient='records')

            # Iterar sobre las películas similares y asignar cada una a una columna
            for idx, (index, row) in enumerate(filtered_similar_movies.iterrows()):
                with cols[idx]:  # Usar la columna correspondiente
                    st.image(row['link'], caption=row['name'], width=220)
                    
                    # Crear un botón para cada película que redirige a la página de detalles
                    if st.button(f"{row['name']}", key=f"movie_button_{row['id']}"):
                        # Archivos de géneros (divididos en múltiples archivos)
                        genre_files = [f'Archivos/genres_part{i}.csv' for i in range(1, 2)]  # Suponiendo que hay 1 archivo de géneros

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

                                    # Obtener las 6 primeras películas por género
                                    movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7)

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

                                    # Cambiar la página a "DPeliculas" (detalles de la película)
                                    st.session_state.page = "DPeliculas"
                                    st.rerun()
        else:
            st.write("No se ha seleccionado ninguna película aún.")

        # Crear un botón para regresar a la página principal
        if st.button("Regresar a la Página Principal"):
            st.session_state.page = "Main"  # Cambiar a la página principal
            st.rerun()
