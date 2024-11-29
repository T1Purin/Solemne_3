import pandas as pd
import streamlit as st

def cartelera():

    st.image("Archivos/logo.png") # Imagen de la aplicación y nuestro logo principal :D
        
    # Funcion de reseña
    def cargar_reseñas(archivo='Archivos/reseñas.csv'): # Cargar reseñas de archivo csv

        try:
            df = pd.read_csv(archivo) # Cargar archivo csv
            df.columns = df.columns.str.strip()  # Limpiar columnas de posibles espacios

            if 'id' not in df.columns or 'name' not in df.columns or 'review' not in df.columns: # Si no tiene las columnas
                st.error("El archivo CSV no tiene las columnas necesarias: 'id', 'name', 'review'.") # Error
                return {} # Devuelve un diccionario vacío
            
            df = df.dropna(subset=['id', 'name', 'review'])  # Eliminar valores nulos 
            reseñas_dict = {} # Diccionario para almacenar las reseñas

            for _, row in df.iterrows(): # Iterar sobre cada fila
                movie_id = row['id'] # Obtener id de la película

                if movie_id not in reseñas_dict: # Si no está en el diccionario
                    reseñas_dict[movie_id] = [] # Agregar una lista vacía

                reseñas_dict[movie_id].append({'name': row['name'], 'review': row['review']}) # Agregar reseña a la lista

            return reseñas_dict # Devuelve el diccionario con las reseñas
        
        except FileNotFoundError: # Si el archivo no existe
            st.error("El archivo de reseñas no se encuentra.") # Error
            return {} # Devuelve un diccionario vacío
        
        except Exception as e: # Si hay algún otro error
            st.error(f"Error al cargar las reseñas: {e}") # Error
            return {} # Devuelve un diccionario vacío

    # Agregar reseña
    def agregar_pelicula(id, name, review, archivo='Archivos/reseñas.csv'): # Agregar película a archivo csv

        new_movie = {'id': id, 'name': name, 'review': review} # Diccionario con la nueva película
        new_movie_df = pd.DataFrame([new_movie]) # DataFrame con la nueva película

        try: # Intentar agregar la película
            new_movie_df.to_csv(archivo, mode='a', header=False, index=False) # Agregar película al archivo csv
            st.write(f"Gracias {name} por tu reseña:") # Mensaje de agradecimiento
            st.write(review) # Mostrar la reseña

        except FileNotFoundError: # Si el archivo no existe
            new_movie_df.to_csv(archivo, mode='w', header=True, index=False) # Crear archivo csv
            st.write(f"Archivo CSV creado y película '{name}' agregada.") # Mensaje de éxito

    if "selected_movie_genre" in st.session_state: # Si hay una película seleccionada
        cartelera_data = st.session_state.selected_movie_genre # Obtener los datos de select_movie_genre
        cartelera_id = cartelera_data['id']  # ID de la película actual

        # Mostrar pelicula
        col1, col2 = st.columns([1, 5]) # Dividir la pantalla en dos columnas de tamaño 1 y 5

        with col1: # Columna 1
            st.image(cartelera_data['poster_url'], caption=cartelera_data['name'], width=230) # Mostrar imagen de la película, caption = título de la película y width = ancho de la imagen

        with col2: # Columna 2
            minute_value = cartelera_data['minute'][0] # Obtener el valor de minutos de la película

            try: # Intentar convertir minutos a horas y minutos
                minute_value = int(minute_value)  # Intentamos convertirlo a entero

            except (ValueError, TypeError):  # Capturamos posibles errores de conversión
                minute_value = 0  # Asignamos un valor predeterminado si no se puede convertir

            st.title(cartelera_data['name']) # Título de la película
            st.caption(f"Géneros: {cartelera_data['genres']}, Duración: {minute_value} minutos.") # Géneros y duración de la película
            st.write(cartelera_data['tagline'][0]) # Sinopsis de la película
            st.write(f"Actores: {cartelera_data['actors']}") # Actores de la película
            st.write(cartelera_data['description'][0]) # Descripción de la película
            rating_value = cartelera_data["rating"][0] # Obtener el valor de la calificación

            try: # Intentar convertir la calificación a un valor numérico
                rating_value = float(rating_value) if rating_value else 0  # Usar 0 si rating es vacío o no válido

            except ValueError: # Capturamos posibles errores de conversión
                rating_value = 0  # Asignamos 0 si no se puede convertir a float

            st.write(f'Calificación: {rating_value}') # Calificación de la película
            st.progress(rating_value / 5) # Progreso de la calificación

        name = st.text_input("Ingresa tu nombre:") # Ingresar nombre
        review = st.text_area("Escribe tu reseña:") # Ingresar reseña

        if "reviews" not in st.session_state: # Si no hay reseñas
            st.session_state.reviews = cargar_reseñas()  # Cargar reseñas desde el archivo CSV

        # Mostrar reseñas
        if cartelera_id in st.session_state.reviews: # Si hay reseñas para la película actual
            st.subheader("Reseñas:") # Título de las reseñas

            for review_entry in st.session_state.reviews[cartelera_id]: # Recorrer las reseñas
                st.write(f"{review_entry['name']}: {review_entry['review']}") # Mostrar la reseña

        if st.button("Enviar reseña"): # Botón para enviar reseña

            if name and review: # Si se ingresaron nombre y reseña

                # Guardar la reseña en el diccionario de reseñas
                if cartelera_id not in st.session_state.reviews: # Si no hay reseñas para la película actual
                    st.session_state.reviews[cartelera_id] = [] # Crear lista vacía para la película actual

                st.session_state.reviews[cartelera_id].append({'name': name, 'review': review}) # Agregar la reseña a la lista
                agregar_pelicula(cartelera_data['id'], name, review) # Agregar la película y la reseña al archivo CSV

            elif not name: # Si no se ingresó nombre
                st.write("Por favor, ingresa tu nombre.") # Mensaje de error

            elif not review: # Si no se ingresó reseña
                st.write("Por favor, escribe una reseña.") # Mensaje de error

        st.subheader('Puede que te interesen...') # Título de recomendaciones

        if 'genres_3' in cartelera_data and not cartelera_data['genres_3'].empty: # Si hay géneros adicionales
            cols = st.columns(6) # Crear 6 columnas para mostrar recomendaciones
            filtered_similar_movies = cartelera_data['genres_3'][cartelera_data['genres_3']['id'] != cartelera_id] # Filtrar películas con géneros adicionales
            displayed_movie_ids = [cartelera_id] # Inicializar lista de IDs de películas mostradas

            for col in cols: # Recorrer las columnas
                displayed_movie_ids += [movie['id'] for movie in st.session_state.get('displayed_movies', [])] # get('displayed_movies', []) intenta obtener el valor de la clave 'displayed_movies' en el diccionario st.session_state. Si no existe una clave con ese nombre, [] (una lista vacía) es devuelta por defecto.

            filtered_similar_movies = filtered_similar_movies[~filtered_similar_movies['id'].isin(displayed_movie_ids)] # ~ (el operador de negación): Este operador invierte los valores booleanos. Al usarlo antes de isin(), estamos seleccionando las filas donde el 'id' no está en displayed_movie_ids.

            if len(filtered_similar_movies) < 6: # Si hay menos de 6 películas recomendadas
                other_movies = cartelera_data['genres_3'][cartelera_data['genres_3']['id'] != cartelera_id] # Obtener películas con géneros adicionales
                other_movies = other_movies[~other_movies['id'].isin(filtered_similar_movies['id'])] # ~ (el operador de negación): Este operador invierte los valores booleanos. Al usarlo antes de isin(), estamos seleccionando las filas donde el 'id' no está en displayed_movie_ids.
                additional_movies = other_movies.head(6 - len(filtered_similar_movies)) # Se obtiene las primeras n películas de un DataFrame llamado other_movies
                filtered_similar_movies = pd.concat([filtered_similar_movies, additional_movies], ignore_index=True) # Concatena los DataFrames filtered_similar_movies y additional_movies, ignorando el índice

            filtered_similar_movies = filtered_similar_movies.head(6) # Se obtiene las primeras 6 películas de un DataFrame llamado filtered_similar_movies
          
            st.session_state['displayed_movies'] = filtered_similar_movies.to_dict(orient='records') # Se convierte el DataFrame filtered_similar_movies a una lista de diccionarios y se asigna a la clave 'displayed_movies' en el diccionario st.session_state
          
            for idx, (index, row) in enumerate(filtered_similar_movies.iterrows()): # Recorrer las películas recomendadas

                with cols[idx]: # Seleccionar la columna correspondiente
                    st.image(row['link'], caption=row['name'], width=220) # Mostrar la imagen de la película y su nombre
                  
                    if st.button(f"{row['name']}", key=f"movie_button_{row['id']}"): #  El parámetro key es un identificador único para el botón, usado por Streamlit para distinguir entre varios botones
                        genre_files = [f'Archivos/genres_part{i}.csv' for i in range(1, 2)]  # Se obtiene la lista de archivos de géneros
                        actor_files = [f'Archivos/actors_part{i}.csv' for i in range(1, 8)]  # Se obtiene la lista de archivos de actores
                        dg_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in genre_files], ignore_index=True) # Se concatenan los archivos de géneros
                        da_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in actor_files], ignore_index=True) # Se concatenan los archivos de actores
                        dp_chunks = pd.read_csv('Archivos/posters_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000) # Se lee el archivo de imágenes de películas en chunks de 25.000 filas
                        dp = next(dp_chunks).fillna('') # Se obtiene el primer chunk y se reemplazan los valores NaN por strings vacías
                        dm_chunks = pd.read_csv('Archivos/movies_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000) # Se lee el archivo de películas en chunks de 25.000 filas
                        dm = next(dm_chunks).fillna('') # Se obtiene el primer chunk y se reemplazan los valores NaN por strings vacías

                        if row['id'] in dm['id'].values: # Si la película está en el archivo de películas
                            movie_id = row['id'] # Se obtiene el ID de la película
                            movie_genres = dg_combined[dg_combined['id'] == movie_id]['genre'].unique()
                            movie_actors = da_combined[da_combined['id'] == movie_id]['name'].unique()[:5] # Se obtienen los 5 primeros actores de la película
                            movie_tagline = dm[dm['id'] == movie_id]['tagline'].unique()
                            movie_description = dm[dm['id'] == movie_id]['description'].unique()
                            movie_rating = dm[dm['id'] == movie_id]['rating'].unique()
                            movie_minute = dm[dm['id'] == movie_id]['minute'].unique()
                            movie_poster_url = dp[dp['id'] == movie_id]['link'].values[0]

                            if len(movie_genres) > 0: # Si la película tiene géneros
                                # Concatenar las películas de los géneros seleccionados
                                movie_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in movie_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True) #Se verifica si lo que buscas esta vacio para evitar errores y si no esta vacio se ejecuta el for para buscarlo
                                
                                if movie_genres_3.empty: # Si no hay películas con los géneros seleccionados
                                    st.write("No se encontraron películas similares para los géneros seleccionados.")

                                else: # Si hay películas con los géneros seleccionados
                                    movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left')  # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                                    movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left') # Unir los datos con el DataFrame de películas (dp) para obtener los posters de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                                    movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7) # Obtiene las primeras siete peliculas y el drop_duplicates() elimina las filas duplicadas del DataFrame por la columna id

                                    # guardar datos seleccionados en session_state_movie para usarlos en la página personal
                                    st.session_state.selected_movie = {
                                        'name': row['name'],
                                        'id': movie_id,
                                        'genres': ', '.join(movie_genres), # Se unen los géneros con comas
                                        'actors': ', '.join(movie_actors), # Se unen los actores con comas
                                        'tagline': movie_tagline,
                                        'description': movie_description,
                                        'rating': movie_rating,
                                        'minute': movie_minute,
                                        'poster_url': movie_poster_url,
                                        'genres_3': movie_genres_3  # peliculas similares
                                    }
                                    # Cambiar la página a "DPeliculas" (detalles de la película)
                                    st.session_state.page = "DPeliculas" # Se cambia la página a "DPeliculas"
                                    st.rerun() # Se vuelve a ejecutar la página para reflejar los cambios
    else:
        st.write("No se ha seleccionado ninguna película aún.")
    
    if st.button("Regresar a la Página Principal"): # Si se presiona el botón "Regresar a la Página Principal"
        st.session_state.page = "Main"  # Cambiar a la página principal
        st.rerun() # Se vuelve a ejecutar la página para reflejar los cambios

