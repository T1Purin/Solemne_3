import streamlit as st
import pandas as pd

def años():
    st.image("Archivos/logo.png")

    # Función para agregar una reseña al archivo CSV
    def agregar_reseña(id, name, review, archivo='Archivos/reseñas.csv'): 

        new_movie = {'id': id, 'name': name, 'review': review} # Crear un diccionario con los datos de la película     
        new_movie_df = pd.DataFrame([new_movie]) # Crear un DataFrame con los datos de la nueva película
        
        try: # Intentar agregar la nueva película al archivo CSV
            new_movie_df.to_csv(archivo, mode='a', header=False, index=False) # Agregar la nueva película al archivo CSV
            print(f"Película '{name}' agregada correctamente.") # Imprimir un mensaje de confirmación
            
        except FileNotFoundError: # Si el archivo CSV no existe
            new_movie_df.to_csv(archivo, mode='w', header=True, index=False)
            print(f"Archivo CSV creado y película '{name}' agregada.")

    # Función para cargar reseñas desde el archivo CSV
    def cargar_reseñas(archivo='Archivos/reseñas.csv'):

        try: # Intentar cargar las reseñas del archivo CSV
            df = pd.read_csv(archivo) # Leer el archivo CSV
            df.columns = df.columns.str.strip() # Eliminar espacios en blanco de las columnas
            
            if 'id' not in df.columns or 'name' not in df.columns or 'review' not in df.columns: # Si alguna columna no existe
                st.error("El archivo CSV no tiene las columnas necesarias: 'id', 'name', 'review'.") # Imprimir un mensaje de error
                return {} # Devolver un DataFrame vacío
        
            df = df.dropna(subset=['id', 'name', 'review']) # Eliminar filas con valores nulos
            reseñas_dict = {} # Crear un diccionario para almacenar las reseñas
            
            for _, row in df.iterrows(): # Iterar sobre las filas del DataFrame
                movie_id = row['id'] # Obtener el ID de la película

                if movie_id not in reseñas_dict: # Si el ID no está en el diccionario
                    reseñas_dict[movie_id] = [] # Crear una lista vacía para el ID

                reseñas_dict[movie_id].append({'name': row['name'], 'review': row['review']}) # Agregar la reseña a la lista
            
            return reseñas_dict # Devolver el diccionario con las reseñas
        
        except FileNotFoundError:
            st.error("El archivo de reseñas no se encuentra.")
            return {}
        
        except Exception as e:
            st.error(f"Error al cargar las reseñas: {e}")
            return {}
    
    # Cargar las reseñas desde el archivo CSV al iniciar
    if "reviews" not in st.session_state: # Si no hay reseñas cargadas
        st.session_state.reviews = cargar_reseñas()  # Cargar reseñas desde el archivo CSV

    # Verificar si ya hay una película seleccionada en session_state
    if "selected_movie" in st.session_state: # Si hay una película seleccionada
        años_data = st.session_state.selected_movie_años # Obtener los años de la película seleccionada
        años_id = años_data['id']  # ID de la película actual
        col1, col2 = st.columns([1, 5]) # Dividir la columna en dos de tamaño 1 y 5

        with col1: # Columna 1
            st.image(años_data['poster_url'], caption=años_data['name'], width=230) # Mostrar la imagen de la película

        with col2: # Columna 2
            minute_value = años_data['minute'][0] # Obtener el valor de minutos de la película

            try: # Intentar convertir el valor a minutos
                minute_value = int(minute_value)  # Intentamos convertirlo a entero

            except (ValueError, TypeError):  # Capturamos posibles errores de conversión
                minute_value = 0  # Asignamos un valor predeterminado si no se puede convertir

            st.title(años_data['name']) # Mostrar el título de la película
            st.caption(f"Géneros: {años_data['genres']}, Duración: {minute_value} minutos.") # Mostrar la duración de la película
            st.write(años_data['tagline'][0]) # Mostrar la sinopsis de la película
            st.write(f"Actores: {años_data['actors']}") # Mostrar los actores de la película
            st.write(años_data['description'][0]) # Mostrar la descripción de la película
            rating_value = años_data["rating"][0] # Obtener la calificación de la película

            try: # Intentar convertir la calificación a float
                rating_value = float(rating_value) if rating_value else 0  # Usar 0 si rating es vacío o no válido

            except ValueError: # Capturamos posibles errores de conversión
                rating_value = 0  # Asignamos 0 si no se puede convertir a float

            st.write(f'Calificación: {rating_value}') # Mostrar la calificación de la película
            st.progress(rating_value / 5) # Mostrar la barra de progreso de la calificación

        # Crear la caja para ingresar el nombre y la reseña
        name = st.text_input("Ingresa tu nombre:") # Ingresar el nombre
        review = st.text_area("Escribe tu reseña:") # Ingresar la reseña

        if años_id in st.session_state.reviews: # Si hay reseñas para esta película
            st.subheader("Reseñas:") # Mostrar el título de las reseñas

            for review_entry in st.session_state.reviews[años_id]: # Recorrer las reseñas
                st.write(f"{review_entry['name']}: {review_entry['review']}") # Mostrar la reseña

        # Botón para enviar la reseña
        if st.button("Enviar reseña"): # Si se presiona el botón

            if name and review: # Si se ingresaron nombre y reseña

                # Guardar la reseña en el diccionario de reseñas
                if años_id not in st.session_state.reviews: # Si no hay reseñas para esta película
                    st.session_state.reviews[años_id] = []  # Inicializa la lista si es la primera reseña

                st.session_state.reviews[años_id].append({'name': name, 'review': review}) # Agregar la reseña

                # Llamamos a la función para guardar la reseña en el archivo CSV
                agregar_reseña(años_data['id'], name, review) # Guardar la reseña en el archivo CSV

                st.write(f"Gracias {name} por tu reseña:") # Mostrar un mensaje de agradecimiento
                st.write(review) # Mostrar la reseña ingresada

            elif not name: # Si no se ingresó nombre
                st.write("Por favor, ingresa tu nombre.") # Mostrar un mensaje de error si no se ingresó nombre

            elif not review: # Si no se ingresó reseña
                st.write("Por favor, escribe una reseña.") # Mostrar un mensaje de error si no se ingresó reseña

        st.subheader('Puede que te interesen...') # Mostrar el título de las películas relacionadas

        if 'genres_3' in años_data and not años_data['genres_3'].empty: # Si hay películas similares
            cols = st.columns(6)  # Usamos 6 columnas para las películas similares
            filtered_similar_movies = años_data['genres_3'][años_data['genres_3']['id'] != años_id] # Filtrar las películas similares
            displayed_movie_ids = [años_id] # Inicializar la lista de IDs de películas para mostrar

            for col in cols: # Recorrer las columnas
                displayed_movie_ids += [movie['id'] for movie in st.session_state.get('displayed_movies', [])] # get('displayed_movies', []) intenta obtener el valor de la clave 'displayed_movies' en el diccionario st.session_state. Si no existe una clave con ese nombre, [] (una lista vacía) es devuelta por defecto.

            filtered_similar_movies = filtered_similar_movies[~filtered_similar_movies['id'].isin(displayed_movie_ids)] # ~ (el operador de negación): Este operador invierte los valores booleanos. Al usarlo antes de isin(), estamos seleccionando las filas donde el 'id' no está en displayed_movie_ids.

            if len(filtered_similar_movies) < 6: # Si hay menos de 6 películas similares
                other_movies = años_data['genres_3'][años_data['genres_3']['id'] != años_id] # Obtener las películas similares
                other_movies = other_movies[~other_movies['id'].isin(filtered_similar_movies['id'])] # Obtener las películas que no están en filtered_similar_movies
                additional_movies = other_movies.head(6 - len(filtered_similar_movies)) # Obtener otras peliculas
                filtered_similar_movies = pd.concat([filtered_similar_movies, additional_movies], ignore_index=True) # Concatenar filtered_similar_movies y additional_movies 

            filtered_similar_movies = filtered_similar_movies.head(6) # Obtener las 6 películas similares

            st.session_state['displayed_movies'] = filtered_similar_movies.to_dict(orient='records') # Guardar las películas similares en el diccionario de la sesión

            for idx, (index, row) in enumerate(filtered_similar_movies.iterrows()): # Recorrer las películas similares

                with cols[idx]:  # Usar la columna correspondiente
                    st.image(row['link'], caption=row['name'], width=220) # Mostrar la imagen de la película
                    
                    # Crear un botón para cada película que redirige a la página de detalles
                    if st.button(f"{row['name']}", key=f"movie_button_{row['id']}"): # Mostrar el botón

                        # Archivos de géneros (divididos en múltiples archivos)
                        genre_files = [f'Archivos/genres_part{i}.csv' for i in range(1, 2)]  # Suponiendo que hay 1 archivo de géneros
                        # Archivos de actores (58 partes)
                        actor_files = [f'Archivos/actors_part{i}.csv' for i in range(1, 8)]  # Cargar los 58 archivos de actores
                        # Cargar y concatenar los archivos de géneros
                        dg_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in genre_files], ignore_index=True) # Cargar y concatenar los archivos de géneros
                        # Cargar y concatenar los archivos de actores
                        da_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in actor_files], ignore_index=True) # Cargar y concatenar los archivos de actores
                        # Cargar los CSV de películas y pósters
                        dp_chunks = pd.read_csv('Archivos/posters_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000) # Cargar los CSV de películas y pósters en chunks
                        dp = next(dp_chunks).fillna('')  # Llenar los valores nulos de los pósters con una cadena vacía
                        dm_chunks = pd.read_csv('Archivos/movies_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000) # Cargar los CSV de películas y pósters en chunks
                        dm = next(dm_chunks).fillna('')  # Llenar los valores nulos de las películas  

                        if row['id'] in dm['id'].values: # Si la película está en el DataFrame de películas

                            movie_id = row['id'] # Obtener el ID de la película
                            movie_genres = dg_combined[dg_combined['id'] == movie_id]['genre'].unique() 
                            movie_actors = da_combined[da_combined['id'] == movie_id]['name'].unique()[:5] # Obtener los 5 primeros actores de la película
                            movie_tagline = dm[dm['id'] == movie_id]['tagline'].unique()
                            movie_description = dm[dm['id'] == movie_id]['description'].unique()
                            movie_rating = dm[dm['id'] == movie_id]['rating'].unique()
                            movie_minute = dm[dm['id'] == movie_id]['minute'].unique()
                            movie_poster_url = dp[dp['id'] == movie_id]['link'].values[0]

                            if len(movie_genres) > 0: # Si la película tiene géneros
                                movie_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in movie_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True) # Obtener los géneros de la película
                                
                                if movie_genres_3.empty: # Si la película no tiene géneros
                                    st.write("No se encontraron películas similares para los géneros seleccionados.") # Mostrar un mensaje de error

                                else: # Si la película tiene géneros
                                    movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left') # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas por id y la funcion se realizara hacia la izquiera buscado por el id.
                                    movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left') # Unir los datos con el DataFrame de películas (dp) para obtener los posters de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                                    movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7) # Obtiene las primeras siete peliculas y el drop_duplicates() elimina las filas duplicadas del DataFrame por la columna id

                                    # Guardar todos los datos seleccionados en session_state_movie para usarlos en la página personal
                                    st.session_state.selected_movie = {
                                        'name': row['name'],
                                        'id': movie_id,
                                        'genres': ', '.join(movie_genres), # Concatenar los géneros
                                        'actors': ', '.join(movie_actors), # Concatenar los actores
                                        'tagline': movie_tagline,
                                        'description': movie_description,
                                        'rating': movie_rating,
                                        'minute': movie_minute,
                                        'poster_url': movie_poster_url,
                                        'genres_3': movie_genres_3  # Aquí están las películas similares
                                    }

                                    # Cambiar la página a "DPeliculas" (detalles de la película)
                                    st.session_state.page = "DPeliculas" # Cambiar la página a "DPeliculas"
                                    st.rerun() # Rerun la página para reflejar los cambios en la sesión de estado
        else:
            st.write("No se ha seleccionado ninguna película aún.")

        # Crear un botón para regresar a la página principal
        if st.button("Regresar a la Página Principal"):
            st.session_state.page = "Main"  # Cambiar a la página principal
            st.rerun() # Recargar la página
