import streamlit as st
import pandas as pd

def principal():

    st.image("Archivos/logo.png") # Imagen de la aplicación y nuestro logo principal :D

    # Función para agregar una reseña al archivo CSV
    def agregar_reseña(id, name, review, archivo='Archivos/reseñas.csv'):

        new_movie = {'id': id, 'name': name, 'review': review} # Crear un diccionario con los datos de la película
        new_movie_df = pd.DataFrame([new_movie]) # Crear un DataFrame con los datos de la nueva película
        
        # Verificar si el archivo CSV ya existe
        try: # Intentar abrir el archivo CSV
            new_movie_df.to_csv(archivo, mode='a', header=False, index=False) # Si el archivo ya existe, agregamos la nueva película al archivo sin sobrescribir
            print(f"Película '{name}' agregada correctamente.") # Imprimir un mensaje de confirmación
       
        except FileNotFoundError: # Si el archivo no existe, crear el archivo CSV y agregar la nueva película
            new_movie_df.to_csv(archivo, mode='w', header=True, index=False) # Si el archivo no existe, lo creamos con los encabezados
            print(f"Archivo CSV creado y película '{name}' agregada.") # Imprimir un mensaje de confirmación

    # Función para cargar reseñas desde el archivo CSV
    def cargar_reseñas(archivo='Archivos/reseñas.csv'):

        try: # Intentar abrir el archivo CSV
            df = pd.read_csv(archivo) # Leer el archivo CSV
            df.columns = df.columns.str.strip() # Limpiar los nombres de las columnas para eliminar espacios extra
            
            # Verificar que las columnas esenciales existen
            if 'id' not in df.columns or 'name' not in df.columns or 'review' not in df.columns: # Si alguna columna esencial no existe
                st.error("El archivo CSV no tiene las columnas necesarias: 'id', 'name', 'review'.") # Imprimir un mensaje de error
                return {} # Devolver un Diccionario vacío
            
            df = df.dropna(subset=['id', 'name', 'review']) # Eliminar filas con valores nulos en 'id', 'name' o 'review'
            
            reseñas_dict = {} # Inicializar un diccionario para almacenar reseñas por id de película
            
            for _, row in df.iterrows(): # Iterar sobre las filas del DataFrame y agregar las reseñas al diccionario
                movie_id = row['id'] # Obtener el id de la película

                if movie_id not in reseñas_dict: # Si el id de la película no está en el diccionario
                    reseñas_dict[movie_id] = [] # Agregar una lista vacía para la película

                reseñas_dict[movie_id].append({'name': row['name'], 'review': row['review']}) # Agregar la reseña a la lista de la película

            return reseñas_dict # Devolver el diccionario con las reseñas por id de película
        
        except FileNotFoundError:  # Si el archivo no existe
            st.error("El archivo de reseñas no se encuentra.") # Imprimir un mensaje de error
            return {} # Devolver un Diccionario vacío
        
        except Exception as e: # Si ocurre cualquier otro error
            st.error(f"Error al cargar las reseñas: {e}") # Imprimir un mensaje de error
            return {} # Devolver un Diccionario vacío
    
    # Cargar las reseñas desde el archivo CSV al iniciar
    if "reviews" not in st.session_state: # Verificar si las reseñas ya se han cargado
        st.session_state.reviews = cargar_reseñas()  # Cargar reseñas desde el archivo CSV

    # Verificar si ya hay una película seleccionada en session_state
    if "selected_movie" in st.session_state: # Verificar si ya hay una película seleccionada
        movie_data = st.session_state.selected_movie # Obtener los datos de la película seleccionada
        movie_id = movie_data['id']  # ID de la película actual

        # Mostrar la información de la película seleccionada (columna 1)
        col1, col2 = st.columns([1, 5])

        with col1: 
            st.image(movie_data['poster_url'], caption=movie_data['name'], width=230) # Mostrar la imagen de la película

        with col2:
            minute_value = movie_data['minute'][0] # Obtener el valor de minutos de la película

            try:
                minute_value = int(minute_value)  # Intentamos convertirlo a entero

            except (ValueError, TypeError):  # Capturamos posibles errores de conversión
                minute_value = 0  # Asignamos un valor predeterminado si no se puede convertir

            st.title(movie_data['name']) # Mostrar el título de la película
            st.caption(f"Géneros: {movie_data['genres']}, Duración: {minute_value} minutos.") # Mostrar la duración de la película
            st.write(movie_data['tagline'][0]) # Mostrar la sinopsis de la película
            st.write(f"Actores: {movie_data['actors']}") # Mostrar los actores de la película
            st.write(movie_data['description'][0]) # Mostrar la descripción de la película
            rating_value = movie_data["rating"][0] # Obtener la calificación de la película

            try: # Intentar convertir la calificación a float
                rating_value = float(rating_value) if rating_value else 0  # Usar 0 si rating es vacío o no válido

            except ValueError: # Si la conversión a float falla
                rating_value = 0  # Asignamos 0 si no se puede convertir a float

            st.write(f'Calificación: {rating_value}') # Mostrar la calificación de la película
            st.progress(rating_value / 5) # Mostrar el progreso de la calificación

        # Crear la caja para ingresar el nombre y la reseña
        name = st.text_input("Ingresa tu nombre:") # Ingresar el nombre
        review = st.text_area("Escribe tu reseña:") # Ingresar la reseña

        # Mostrar reseñas ya existentes para esta película
        if movie_id in st.session_state.reviews: # Verificar si hay reseñas para esta película
            st.subheader("Reseñas:") # Título de la sección de reseñas

            for review_entry in st.session_state.reviews[movie_id]: # Iterar sobre las reseñas
                st.write(f"{review_entry['name']}: {review_entry['review']}") # Mostrar la reseña

        # Botón para enviar la reseña
        if st.button("Enviar reseña"): # Verificar si se ha presionado el botón

            if name and review: # Verificar si se han ingresado el nombre y la reseña
                # Guardar la reseña en el diccionario de reseñas 

                if movie_id not in st.session_state.reviews: # Verificar si ya hay reseñas para esta película
                    st.session_state.reviews[movie_id] = []  # Crear una lista vacía para esta película

                st.session_state.reviews[movie_id].append({'name': name, 'review': review}) # Agregar la reseña a la lista
                agregar_reseña(movie_data['id'], name, review)  # Llamamos a la función para guardar la reseña en el archivo CSV
                st.write(f"Gracias {name} por tu reseña:") # Mensaje de agradecimiento
                st.write(review) # Mostrar la reseña ingresada

            elif not name: # Verificar si no se ha ingresado el nombre
                st.write("Por favor, ingresa tu nombre.") # Mensaje de error si no se ingresa el nombre

            elif not review: # Verificar si no se ha ingresado la reseña
                st.write("Por favor, escribe una reseña.") # Mensaje de error si no se ingresa la reseña

        st.subheader('Puede que te interesen...') # Título de la sección de recomendaciones

        # Mostrar las 6 películas similares (si existen)
        if 'genres_3' in movie_data and not movie_data['genres_3'].empty: # Verificar si hay películas similares
            cols = st.columns(6)  # Usamos 6 columnas para las películas similares
            filtered_similar_movies = movie_data['genres_3'][movie_data['genres_3']['id'] != movie_id] # Filtrar las películas similares y excluimos la actual
            displayed_movie_ids = [movie_id]  # Inicializamos con el ID de la película seleccionada

            for col in cols: # Iterar sobre las columnas
                displayed_movie_ids += [movie['id'] for movie in st.session_state.get('displayed_movies', [])] # get('displayed_movies', []) intenta obtener el valor de la clave 'displayed_movies' en el diccionario st.session_state. Si no existe una clave con ese nombre, [] (una lista vacía) es devuelta por defecto.

            filtered_similar_movies = filtered_similar_movies[~filtered_similar_movies['id'].isin(displayed_movie_ids)] # ~ (el operador de negación): Este operador invierte los valores booleanos. Al usarlo antes de isin(), estamos seleccionando las filas donde el 'id' no está en displayed_movie_ids.

            if len(filtered_similar_movies) < 6: # Verificar si hay menos de 6 películas similares
                other_movies = movie_data['genres_3'][movie_data['genres_3']['id'] != movie_id] # get('displayed_movies', []) intenta obtener el valor de la clave 'displayed_movies' en el diccionario st.session_state. Si no existe una clave con ese nombre, [] (una lista vacía) es devuelta por defecto.
                other_movies = other_movies[~other_movies['id'].isin(filtered_similar_movies['id'])]  # ~ (el operador de negación): Este operador invierte los valores booleanos. Al usarlo antes de isin(), estamos seleccionando las filas donde el 'id' no está en displayed_movie_ids.
                additional_movies = other_movies.head(6 - len(filtered_similar_movies)) # Obtener las 6 películas adicionales que se necesitan para completar las 6
                filtered_similar_movies = pd.concat([filtered_similar_movies, additional_movies], ignore_index=True) # Concatenar las películas similares y las adicionales

            filtered_similar_movies = filtered_similar_movies.head(6) # Limitar a 6 las películas similares
            st.session_state['displayed_movies'] = filtered_similar_movies.to_dict(orient='records') # Guardar las películas similares en el diccionario de la sesión

            for idx, (index, row) in enumerate(filtered_similar_movies.iterrows()): # Iterar sobre las películas similares

                with cols[idx]:  # Usar la columna correspondiente
                    st.image(row['link'], caption=row['name'], width=220) # Mostrar la imagen de la película
                    
                    # Crear un botón para cada película que redirige a la página de detalles
                    if st.button(f"{row['name']}", key=f"movie_button_{row['id']}"): # key es único para cada botón
                        
                        # Archivo de generos (11 partes)
                        genre_files = [f'Archivos/genres_part{i}.csv' for i in range(1, 2)] # Generar la lista de archivos de géneros
                        # Archivos de actores (58 partes)
                        actor_files = [f'Archivos/actors_part{i}.csv' for i in range(1, 8)] # Generar la lista de archivos de actores
                        dg_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in genre_files], ignore_index=True) # Cargar y concatenar los archivos de géneros
                        da_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in actor_files], ignore_index=True) # Cargar y concatenar los archivos de actores
                        # Cargar los CSV de películas y pósters
                        dp_chunks = pd.read_csv('Archivos/posters_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000) # Cargar el archivo de pósters en chunks de 25.000 filas
                        dp = next(dp_chunks).fillna('') # Llenar los valores nulos de los pósters con una cadena vacía
                        dm_chunks = pd.read_csv('Archivos/movies_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000) # Cargar el archivo de películas en chunks de 25.000 filas
                        dm = next(dm_chunks).fillna('') # Llenar los valores nulos de las películas con una cadena vacía

                        if row['id'] in dm['id'].values: # Verificar si la película existe en el archivo de películas

                            movie_id = row['id'] # Obtener el ID de la película
                            movie_genres = dg_combined[dg_combined['id'] == movie_id]['genre'].unique() 
                            movie_actors = da_combined[da_combined['id'] == movie_id]['name'].unique()[:5] # Obtener los 5 primeros actores de la película
                            movie_tagline = dm[dm['id'] == movie_id]['tagline'].unique()
                            movie_description = dm[dm['id'] == movie_id]['description'].unique()
                            movie_rating = dm[dm['id'] == movie_id]['rating'].unique()
                            movie_minute = dm[dm['id'] == movie_id]['minute'].unique()
                            movie_poster_url = dp[dp['id'] == movie_id]['link'].values[0]

                            if len(movie_genres) > 0: # Verificar si la película tiene géneros

                                movie_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in movie_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True) # Obtener los géneros de la película
                                
                                if movie_genres_3.empty: # Verificar si los géneros están vacíos
                                    st.write("No se encontraron películas similares para los géneros seleccionados.") # Mostrar un mensaje de error

                                else: # Si los géneros no están vacíos
                                    movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left') # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas por id y la funcion se realizara hacia la izquiera buscado por el id.
                                    movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left')  # Unir los datos con el DataFrame de películas (dp) para obtener los posters de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                                    movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7) # Obtiene las primeras siete peliculas y el drop_duplicates() elimina las filas duplicadas del DataFrame por la columna id

                                    # Guardar todos los datos seleccionados en session_state_movie para usarlos en la página personal
                                    st.session_state.selected_movie = {
                                        'name': row['name'],
                                        'id': movie_id,
                                        'genres': ', '.join(movie_genres), # Convertir la lista de géneros a una cadena separada por comas
                                        'actors': ', '.join(movie_actors), # Convertir la lista de actores a una cadena separada por comas
                                        'tagline': movie_tagline,
                                        'description': movie_description,
                                        'rating': movie_rating,
                                        'minute': movie_minute,
                                        'poster_url': movie_poster_url,
                                        'genres_3': movie_genres_3  # Aquí están las películas similares
                                    }

                                    # Cambiar la página a "DPeliculas" (detalles de la película)
                                    st.session_state.page = "DPeliculas" # Cambiar la página a "DPeliculas"
                                    st.rerun() # Recargar la página
        else:
            st.write("No se ha seleccionado ninguna película aún.") 

        # Crear un botón para regresar a la página principal
        if st.button("Regresar a la Página Principal"): # Si se presiona el botón "Regresar a la Página Principal"
            st.session_state.page = "Main"  # Cambiar a la página principal
            st.rerun() # Recargar la página
