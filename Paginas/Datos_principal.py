import streamlit as st
import pandas as pd
import altair as alt

def main():

    st.image("Archivos/logo.png") # Imagen de la aplicación y nuestro logo principal :D
    # Archivos de géneros hay como de 1 a 11 partes
    genre_files = [f'Archivos/genres_part{i}.csv' for i in range(1, 2)] 
    # Archivos de actores hay como de 1 a 58 partes
    actor_files = [f'Archivos/actors_part{i}.csv' for i in range(1, 8)]  # Cargar los 58 archivos de actores
    # Cargamos y combinamos los archivos
    dg_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in genre_files], ignore_index=True) 
    # Cargamos y combinamos los archivos 
    da_combined = pd.concat([pd.read_csv(file, sep=',', encoding='utf', engine='python', on_bad_lines='skip') for file in actor_files], ignore_index=True)
    # Cargar los CSV de películas y pósters
    dp_chunks = pd.read_csv('Archivos/posters_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000) #Carga los 25000 registros de la primera parte del archivo de pósters
    dp = next(dp_chunks).fillna('')  # Llenar los valores nulos de los pósters con una cadena vacía
    dm_chunks = pd.read_csv('Archivos/movies_part1.csv', sep=',', encoding='utf', engine='python', on_bad_lines='skip', chunksize=25000) #Este iterador devolverá (chunks) de tamaño 25,000 filas
    dm = next(dm_chunks).fillna('')  # la funcion next() obtendrá las primeras 25,000 filas del archivo CSV y las cargara como un DataFrame.
 
    def select_bar():

        # Crear una lista de nombres de películas para que el usuario elija
        movie_names = dm['name'].unique() # Unique() hace q te devuelvan los valores únicos de una columna 
        movie_selected = st.selectbox("Selecciona una película", movie_names) # Selecciona una película de la lista de películas

        if movie_selected:
            # Buscar los datos relacionados con la película seleccionada
            movie_id = dm[dm['name'] == movie_selected]['id'].values[0]
            # Buscar géneros, actores y la URL del póster para esta película
            movie_genres = dg_combined[dg_combined['id'] == movie_id]['genre'].unique()
            movie_actors = da_combined[da_combined['id'] == movie_id]['name'].unique()[:5]  # Obtendra los 5 primeros actores de la película
            movie_tagline = dm[dm['id'] == movie_id]['tagline'].unique()
            movie_description = dm[dm['id'] == movie_id]['description'].unique()
            movie_rating = dm[dm['id'] == movie_id]['rating'].unique()
            movie_minute = dm[dm['id'] == movie_id]['minute'].unique()
            movie_poster_url = dp[dp['id'] == movie_id]['link'].values[0]

            # Verificar que movie_genres no esté vacío antes de intentar concatenar
            if len(movie_genres) > 0:
                # Concatenar las películas de los géneros seleccionados
                movie_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in movie_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True) #Se verifica si lo que buscas esta vacio para evitar errores y si no esta vacio se ejecuta el for para buscarlo
                
                if movie_genres_3.empty: #Si el resultado de la búsqueda es vacío se ejecuta esto
                    st.write("No se encontraron películas similares para los géneros seleccionados.")

                else: # Si no este se ejecuta
                    movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left') # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                    movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left') # Unir los datos con el DataFrame de películas (dp) para obtener los posters de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                    movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7) # Obtiene las primeras siete peliculas y el drop_duplicates() elimina las filas duplicadas del DataFrame por la columna id

                    # Guardar todos los datos seleccionados en session_state_movie para usarlos en la página personal
                    st.session_state.selected_movie = {
                        'name': movie_selected,
                        'id': movie_id,
                        'genres': ', '.join(movie_genres), # Unir los géneros en una cadena
                        'actors': ', '.join(movie_actors), # Unir los actores en una cadena
                        'tagline': movie_tagline,
                        'description': movie_description,
                        'rating': movie_rating,
                        'minute': movie_minute,
                        'poster_url': movie_poster_url,
                        'genres_3': movie_genres_3  # Aquí están las películas similares
                    }
            else: # En caso de que no encuentre películas con los géneros seleccionados
                st.write("No se encontraron géneros para esta película.")
                
        # Crear botones para cambiar a la página personal
        if st.button("Buscar"):
            st.session_state.page = "DPeliculas"  # Cambiar a la página personal
            st.rerun() # Recarga la pagina para que se vea los cambios

    def cartelera_bar():

        # Crea un lista por todos los generos existentes
        name_genre = dg_combined["genre"].unique() # Obtiene todos los generos existentes en el DataFrame dg_combined
        genre_selection = st.selectbox("Seleccione un género", ["Seleccione un género"] + list(name_genre)) # Seleccionar un género para buscar películas similares

        if genre_selection != "Seleccione un género": # Si la seleccion es diferente a la seleccionada por defecto se ejecutara esto
            genero_movies = dg_combined[dg_combined["genre"] == genre_selection]["id"].unique() # Busca el genero seleccionado y devuelve los id de las películas que pertenecen a ese genero
            filtrar_movies = dm[dm["id"].isin(genero_movies)] # El método isin() verifica si cada valor de la columna 'id' está presente en la lista 'genero_movies'. Devuelve un DataFrame con las películas cuyo 'id' coincida con los valores en la lista.
            top12 = filtrar_movies.head(12) #Seleccion 12 peliculas del DataFrame filtrado
            st.write(f"Top 12 películas de {genre_selection}") #Escribe Top 12 peliculas del genero seleccionado

            # Inicializar el indice de pelicula en la sesión si no existe se le da un valor de 0
            if "movie_index" not in st.session_state:
                st.session_state.movie_index = 0

            col1, col2 = st.columns([17, 1]) # Divide la pagina en dos columnas una de un tamaño de 17 y la otra de un tamaño de 1

            # Botón anterior
            with col1: # Se ejecuta en la primera columna

                if st.session_state.movie_index > 0: # Si el indice de la pelicula es mayor a 0 se ejecutara esto

                    if st.button("←", use_container_width=False): # El use_container_width=False indica q no ocupara todo el ancho de la columna
                        st.session_state.movie_index -= 6 # Resta 6 al indice de la pelicula mostrando 6 peliculas por pagina 
                        #Muestra las primeras 6 peliculas

            # Botón siguiente
            with col2: # Se ejecuta en la segunda columna

                if st.session_state.movie_index < len(top12) - 6: # Si el indice de la pelicula es menor a  6 se ejecutara esto

                    if st.button("→", use_container_width=False): # El use_container_width=False indica q no ocupara todo el ancho de la columna
                        st.session_state.movie_index += 6 # Suma 6 al indice de la pelicula mostrando 6 peliculas por pagina
                        # Muestra de la pelicula 7 a la 12

            selected_movies = top12.iloc[st.session_state.movie_index:st.session_state.movie_index + 6] # Si movie_index = 0, se seleccionarán las filas de top10 desde el índice 0 hasta el índice 5 (es decir, las primeras 6 películas) y se guardaran las primeras 6 películas de la lista de películas filtradas.
            columns = st.columns(6) # Divide la pagina en 6 columnas

            for index, (col, row) in enumerate(zip(columns, selected_movies.iterrows())): # enumerate() es una función de Python que agrega un contador a un iterable, zip() es una función de Python que agrupa los elementos de dos o más iterables, iterrows() es un generador que permite iterar sobre las filas de un DataFrame En cada iteración, iterrows() devuelve una tupla con dos elementos.
                movie_name = row[1]["name"] # Obtiene el nombre de la película por la columna 'name'
                movie_poster_url = dp[dp["id"] == row[1]["id"]]["link"].values # Busca por id la url de la imagen de la película y devuelve la url 

                # Mostrar la imagen y el nombre de la película
                if len(movie_poster_url) > 0: # Si la lista de urls no está vacía
                    col.image(movie_poster_url[0], width=170) # Muestra la imagen de la película con un ancho de 170 pixeles

                else: # Si la lista de urls está vacía
                    col.write("Póster no disponible") # Escribe "Póster no disponible"

                # Botón para la película
                a = col.button(movie_name) # Crea un botón con el nombre de la película

                if a: # Si el botón es pulsado

                    movie_gen = row[1]["id"] # Obtener el id de la película
                    movie_genres = dg_combined[dg_combined['id'] == movie_gen]['genre'].unique()
                    movie_actors = da_combined[da_combined['id'] == movie_gen]['name'].unique()[:5] # Selecciona los primeros 5 actores
                    movie_tagline = dm[dm['id'] == movie_gen]['tagline'].unique()
                    movie_description = dm[dm['id'] == movie_gen]['description'].unique()
                    movie_rating = dm[dm['id'] == movie_gen]['rating'].unique()
                    movie_minute = dm[dm['id'] == movie_gen]['minute'].unique()
                    movie_poster_url = dp[dp['id'] == movie_gen]['link'].values[0] #.values[0] devuelve el primer elemento de la lista 


                    # Verificar que movie_genres no esté vacío antes de intentar concatenar
                    if len(movie_genres) > 0:
                        # Concatenar las películas de los géneros seleccionados
                        movie_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in movie_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True)  # Se verifica si lo que buscas esta vacio para evitar errores y si no esta vacio se ejecuta el for para buscarlo
                        
                        if movie_genres_3.empty: #Si el resultado de la búsqueda es vacío se ejecuta esto
                            st.write("No se encontraron películas similares para los géneros seleccionados.")

                        else: # Si no este se ejecuta
                            movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left') # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                            movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left') # Unir los datos con el DataFrame de películas (dp) para obtener los posters de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                            movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7) # Obtiene las primeras siete peliculas y el drop_duplicates() elimina las filas duplicadas del DataFrame por la columna id
                       
                    # Guardar todos los datos seleccionados en session_state_movie_genre para usarlos en la página personal
                    st.session_state.selected_movie_genre = {
                        'name': movie_name,
                        'id': movie_gen,
                        'genres': ', '.join(movie_genres), # Concatenar los géneros seleccionados
                        'actors': ', '.join(movie_actors), # Concatenar los actores seleccionados 
                        'tagline': movie_tagline,
                        'description': movie_description,
                        'rating': movie_rating,
                        'minute': movie_minute,
                        'poster_url': movie_poster_url,
                        'genres_3': movie_genres_3  # Aquí están las películas similares

                    }

                    st.session_state.page = "Cartelera" # Cambiar la página a "Cartelera" (detalles de la película)
                    st.rerun() # Recargar la página para mostrar los detalles de la película

    def años_bar(): 

        años_names = pd.to_numeric(dm['date'], errors='coerce').dropna().astype(int).unique() # pd.to_numeric() es una función intenta convertir los valores de la columna 'date' a valores numéricos (enteros o flotantes), errors='coerce' en caso de que no se pueda convertir algún valor a numérico (como texto no numérico), pandas lo convertirá a NaN (valor nulo), dropna() elimina cualquier valor NaN (no numérico) que se haya generado en el paso anterior, astype(int) convierte los valores restantes a enteros (int).
        años_names_sorted = sorted(años_names)  # La función sorted() en Python toma un iterable (como una lista) y devuelve una nueva lista ordenada de menor a mayor.
        años_selected = st.selectbox("Selecciona un año", ["Seleccione un año"] + list(años_names_sorted)) # st.selectbox() es una función que permite al usuario seleccionar un valor de una lista de

        if años_selected != "Seleccione un año": # Si el usuario selecciona un año
            años_movies = dm[dm["date"] == años_selected]["id"].unique() # Busca las películas del año seleccionado y devuelve sus ids
            filtrar_movies = dm[dm["id"].isin(años_movies)] # El método isin() verifica si cada valor de la columna 'id' está presente en la lista 'años_movies'. Devuelve un DataFrame con las películas cuyo 'id' coincida con los valores en la lista.
            top10 = filtrar_movies.head(12) # Obtiene las primeras 12 películas del año seleccionado

            st.write(f"Top 10 películas de {años_selected}") # Muestra el título del top 10 de películas del año seleccionado

            # Inicializar el indice de pelicula en la sesión si no existe el valor q se le dara es 0
            if "movie_index" not in st.session_state: 
                st.session_state.movie_index = 0

            col1, col2 = st.columns([17, 1]) # Divide la página en dos columnas de anchos 17 y 1

            # Botón anterior
            with col1: 
                
                if st.session_state.movie_index > 0: # Si el índice de película es mayor que 0

                    if st.button("←", use_container_width=False): # El use_container_width=False indica q no ocupara todo el ancho de la columna
                        st.session_state.movie_index -= 6 # Restar 6 al índice de película
                        # Muestra de la 0 a la 5 

            # Botón siguiente
            with col2:

                if st.session_state.movie_index < len(top10) - 6: # Si el índice de película es menor q 6

                    if st.button("→", use_container_width=False): # El use_container_width=False indica q no ocupara todo el ancho de la columna
                        st.session_state.movie_index += 6 # Sumar 6 al índice de película
                        #Muestra de la 7 a la 12

            selected_movies = top10.iloc[st.session_state.movie_index:st.session_state.movie_index + 6] # Si movie_index = 0, se seleccionarán las filas de top10 desde el índice 0 hasta el índice 5 (es decir, las primeras 6 películas) y se guardaran las primeras 6 películas de la lista de películas filtradas.
            columns = st.columns(6) # Divide la página en 6 columnas

            for index, (col, row) in enumerate(zip(columns, selected_movies.iterrows())): # enumerate() es una función de Python que agrega un contador a un iterable, zip() es una función de Python que agrupa los elementos de dos o más iterables, iterrows() es un generador que permite iterar sobre las filas de un DataFrame En cada iteración, iterrows() devuelve una tupla con dos elementos.
                movie_name = row[1]["name"] # Busca el nombre de la película en la fila actual 
                movie_poster_url = dp[dp["id"] == row[1]["id"]]["link"].values # Busca la URL de la imagen de la película en la fila actual

                # Mostrar la imagen y el nombre de la película
                if len(movie_poster_url) > 0 and movie_poster_url[0] != '': # Verificar si la URL de la imagen está vacía
                    col.image(movie_poster_url[0], width=170) # Mostrar la imagen y el nombre de la película con un tamaño de 170 pixeles

                else:
                    col.image("Archivos/404.png") # Mostrar una imagen por defecto si no hay imagen de la película

                # Botón para la película
                b = col.button(movie_name)

                if b: # Si el botón es pulsado
                    años_id = row[1]["id"] # Obtiene el id de la película pulsada
                    años_name = dm[dm["id"] == años_id]["name"].values[0]
                    años_genres = dg_combined[dg_combined['id'] == años_id]['genre'].unique() 
                    años_actors = da_combined[da_combined['id'] == años_id]['name'].unique()[:5] # Obtiene los 5 primeros actores de la película
                    años_tagline = dm[dm['id'] == años_id]['tagline'].unique()
                    años_description = dm[dm['id'] == años_id]['description'].unique()
                    años_rating = dm[dm['id'] == años_id]['rating'].unique()
                    años_minute = dm[dm['id'] == años_id]['minute'].unique()
                    años_poster_url = dp[dp['id'] == años_id]['link'].values[0] # Obtiene la URL del póster de la película

                    # Verificar que movie_genres no esté vacío antes de intentar concatenar
                    if len(años_genres) > 0:
                        # Concatenar las películas de los géneros seleccionados
                        años_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in años_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True) # Se verifica si lo que buscas esta vacio para evitar errores y si no esta vacio se ejecuta el for para buscarlo
                        
                        if años_genres_3.empty: #Si el resultado de la búsqueda es vacío se ejecuta esto
                            st.write("No se encontraron películas similares para los géneros seleccionados.")

                        else: # Si se encontraron películas similares
                            años_genres_3 = años_genres_3.merge(dm[['id', 'name']], on='id', how='left') # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                            años_genres_3 = años_genres_3.merge(dp[['id', 'link']], on='id', how='left') # Unir los datos con el DataFrame de películas (dp) para obtener los posters de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                            años_genres_3 = años_genres_3.drop_duplicates(subset=['id']).head(7) # Obtiene las primeras siete peliculas y el drop_duplicates() elimina las filas duplicadas del DataFrame por la columna id

                    # Guardar todos los datos seleccionados en session_state_movies_años para usarlos en la página personal
                    st.session_state.selected_movie_años = {
                        'name': años_name,
                        'id': años_id,
                        'genres': ', '.join(años_genres), # Concatenar los géneros seleccionados
                        'actors': ', '.join(años_actors), # Concatenar los actores seleccionados
                        'tagline': años_tagline,
                        'description': años_description,
                        'rating': años_rating,
                        'minute': años_minute,
                        'poster_url': años_poster_url,
                        'genres_3': años_genres_3  # Aquí están las películas similares
                    }

                    st.session_state.page = "Años" # Guardar la página actual en session_state_page y se guarda en la variable "Años"
                    st.rerun() # Rerun la página para refrescar los datos y mostrar la página personalizada

    opcion = st.sidebar.selectbox("Seleccione una sección:", ("Página principal", "Gráficos")) # Seleccionar una sección en el sidebar 

    if opcion == "Página principal": # Si se selecciona la sección "Página principal"
        
        # Verificar cuál opción fue elegida y mostrar el buscador correspondiente
        if 'search_type' not in st.session_state:
            st.session_state.search_type = 'movie'  # Valor por defecto (buscar por película)
    
        if st.session_state.search_type == 'movie': # Si se selecciona la opción "Buscar por película"
            st.write("Buscador de Películas:") # Mostrar el título del buscador
            select_bar()  # Llamar al buscador de películas

        elif st.session_state.search_type == 'genre': # Si se selecciona la opción "Buscar por género"
            st.write("Buscador de Géneros:") # Mostrar el título del buscador
            cartelera_bar()  # Llamar al buscador de géneros

        elif st.session_state.search_type == 'años': # Si se selecciona la opción "Buscar por años"
            st.write("Buscador por años:") # Mostrar el título del buscador
            años_bar() # Llamar al buscador de años
    
        # Mostrar la pregunta inicial para elegir entre los buscadores
        st.write("¿Qué tipo de buscador prefieres usar?")
        # Crear una fila de columnas para los botones (los botones estarán en una línea horizontal)
        col1, col2, col3 = st.columns([1, 1, 1])  # Crear 3 columnas con igual tamaño
    
        # Colocar un botón en cada columna
        with col1:

            if st.button('Buscar por película'): # Si se selecciona el botón "Buscar por película"
                st.session_state.search_type = 'movie'  # Guardar la elección en session_state
                st.rerun() # Rerun la página para refrescar los datos y mostrar la página personalizada
    
        with col2: # Si se selecciona el botón "Buscar por género"

            if st.button('Buscar por género'): # Si se selecciona el botón "Buscar por género"
                st.session_state.search_type = 'genre'  # Guardar la elección en session_state
                st.rerun() # Rerun la página para refrescar los datos y mostrar la página personalizada
        
        with col3: # Si se selecciona el botón "Buscar por años"

            if st.button('Buscar por años'): # Si se selecciona el botón "Buscar por años"
                st.session_state.search_type = 'años' # Guardar la elección en session_state
                st.rerun() # Rerun la página para refrescar los datos y mostrar la página personalizada

        st.subheader('Tendencias del momento') # Mostrar el título de la sección de tendencias
        tendencias = ['Wicked', 'Gladiator II', 'The Substance', 'Deadpool & Wolverine', 'Anora', 'Terrifier 3'] # Listado de tendencias (Buscado)
        ids = pd.concat([dm[dm['name'] == tendencia] for tendencia in tendencias if not dm[dm['name'] == tendencia].empty], ignore_index=True) # Concatenar las películas de los géneros seleccionados
        
        if ids.empty: 
            st.write("No se encontraron películas similares para los géneros seleccionados.")

        else:
            ids = ids.merge(dm[['id', 'name']]) # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas
            ids = ids.merge(dp[['id', 'link']]) # Unir los datos con el DataFrame de pósters (dp) para obtener las URLs de los pósters

        columns = st.columns(6) # Crear las 6 columnas para mostrar las películas de manera lateral

        # Mostrar las películas en las 6 columnas
        for i, (col, row) in enumerate(zip(columns, ids.iterrows())): # enumerate() es una función de Python que agrega un contador a un iterable, zip() es una función de Python que agrupa los elementos de dos o más iterables, iterrows() es un generador que permite iterar sobre las filas de un DataFrame En cada iteración, iterrows() devuelve una tupla con dos elementos.
            movie_name = row[1]['name'] # Obtener el nombre de la película
            movie_poster_url = dp[dp['id'] == row[1]['id']]['link'].values # Obtener la URL del póster de la película
            
            # Mostrar el nombre de la película y el póster en cada columna
            with col:

                if len(movie_poster_url) > 0: # Si la película tiene póster
                    st.image(movie_poster_url[0], width=170) # Mostrar el póster
                    a = col.button(movie_name) # Mostrar el nombre de la película como botón

                    if a: # Si se selecciona el botón

                        movie_gen = row[1]["id"] # Obtener el id de la película 
                        movie_genres = dg_combined[dg_combined['id'] == movie_gen]['genre'].unique()
                        movie_actors = da_combined[da_combined['id'] == movie_gen]['name'].unique()[:5] # Obtener los 5 primeros actores de la película
                        movie_tagline = dm[dm['id'] == movie_gen]['tagline'].unique()
                        movie_description = dm[dm['id'] == movie_gen]['description'].unique()
                        movie_rating = dm[dm['id'] == movie_gen]['rating'].unique()
                        movie_minute = dm[dm['id'] == movie_gen]['minute'].unique()
                        movie_poster_url = dp[dp['id'] == movie_gen]['link'].values[0] # Obtener la URL del póster de la película
    
    
                        # Verificar que movie_genres no esté vacío antes de intentar concatenar
                        if len(movie_genres) > 0: # Si la película tiene géneros
                            # Concatenar las películas de los géneros seleccionados
                            movie_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in movie_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True) # Se verifica si lo que buscas esta vacio para evitar errores y si no esta vacio se ejecuta el for para buscarlo.
                            
                            if movie_genres_3.empty: # Si no se encontraron películas similares para los géneros seleccionados
                                st.write("No se encontraron películas similares para los géneros seleccionados.")

                            else: # Si se encontraron películas similares para los géneros seleccionados
                                movie_genres_3 = movie_genres_3.merge(dm[['id', 'name']], on='id', how='left') # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                                movie_genres_3 = movie_genres_3.merge(dp[['id', 'link']], on='id', how='left') # Unir los datos con el DataFrame de películas (dp) para obtener los posters de las películas por id y la funcion se realizara hacia la izquiera buscado por el id 
                                movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7) # Obtiene las primeras siete peliculas y el drop_duplicates() elimina las filas duplicadas del DataFrame por la columna id
                        
                        # Guardar los detalles de la película seleccionada en session_state_genre
                        st.session_state.selected_movie_genre = {
                            'name': movie_name,
                            'id': movie_gen,
                            'genres': ', '.join(movie_genres), # Concatenar los géneros de la película
                            'actors': ', '.join(movie_actors), # Concatenar los actores de la película
                            'tagline': movie_tagline,
                            'description': movie_description,
                            'rating': movie_rating,
                            'minute': movie_minute,
                            'poster_url': movie_poster_url,
                            'genres_3': movie_genres_3  # Aquí están las películas similares
    
                        }
    
                        # Cambiar la página a "Cartelera" (detalles de la película)
                        st.session_state.page = "Cartelera" # Se cambia la pagina a cartelera
                        st.rerun() # Se vuelve a ejecutar la página para reflejar los cambios
    
                else:
                    st.write("Póster no disponible")
    
        st.subheader('Escribe y comparte tus reseñas: ')
        # Cargar las reseñas desde el archivo CSV
        reseñas_df = pd.read_csv('Archivos/reseñas.csv', encoding='utf') 
        # Limpiar los nombres de las columnas eliminando espacios extra
        reseñas_df.columns = reseñas_df.columns.str.strip() # str.strip() es un método de cadena de texto que se utiliza para eliminar los espacios en blanco al principio y al final de las cadenas
        random_reviews = reseñas_df.sample(n=3)  # sample() es un método de pandas que selecciona un subconjunto aleatorio de filas del DataFrame.
    
        # Mostrar las reseñas 
        for index, review in random_reviews.iterrows(): # iterrows() es un método de pandas que devuelve un iterador sobre las filas del DataFrame
            movie_id = review['id']  # Aquí tienes el ID de la película
            user_name = review['name']  # Nombre del usuario
            user_review = review['review']  # Contenido de la reseña
            movie_name = dm[dm['id'] == movie_id]['name'].values # Buscar el nombre de la película a partir del 'movie_id'
    
            if len(movie_name) > 0: # Si se encontró la película
                movie_name = movie_name[0]  # Obtener el nombre de la película (debe haber un único valor)

            else:
                movie_name = "Película no encontrada"  # En caso de que no se encuentre el ID de la película
    
            # Mostrar la información de la reseña
            st.write(f"### {movie_name}") # Título de la película
            st.write(f"**Reseña por:** {user_name}") # Nombre del usuario que escribió la reseña
            st.write(f"_{user_review}_") # Contenido de la reseña
            st.write("---") # Separador entre reseñas

    
    elif opcion == "Gráficos": # Si se selecciona la opción "Gráficos"

        # Combinar los DataFrames utilizando 'id' como clave, el how hace que solo esten presente los ids que coinciden
        df_merged = pd.merge(dm, dg_combined, on='id', how='inner') # 'inner' significa que solo se incluirán los datos que coincidan en ambas tablas
        
        # Convertir la columna 'date' a numérica (año)
        df_merged['Año'] = pd.to_numeric(df_merged['date'], errors='coerce') # convertir los valores de la columna 'date' a valores numéricos, almacenándolos en una nueva columna llamada 'Año', errors='coerce' se utiliza para manejar los errores que podrían ocurrir si algún valor no puede ser convertido a un número.
        
        # Crear un la casilla de seleccion de genersos, #sorted, es alfabeticamente
        generos_disponibles = ['Todos'] + sorted(df_merged['genre'].unique()) # Agrega la opcion todos y ordena los demas alfabeticamente
        genero_seleccionado = st.selectbox("Selecciona un género para verlo en el grafico", generos_disponibles) # Selecciona un género para verlo en el grafico
        
        # Filtrar el DataFrame según el género seleccionado
        if genero_seleccionado == 'Todos': # Si se selecciona la opción "Todos"
            df_filtrado = df_merged # Usara el por defecto
        else:
            df_filtrado = df_merged[df_merged['genre'] == genero_seleccionado] # Filtrar el DataFrame según el género seleccionado
        
        # Contar el número de películas por año
        movie_counts = df_filtrado.groupby('Año').size().reset_index(name='Cantidad de peliculas') # Agrupar por año y contar el número de películas por año
        
        # Crear el gráfico de líneas con Altair, mark_line() indica que el tipo de gráfico será una línea, encode() es donde se mapean las columnas del DataFrame a los ejes del gráfico, se configura la propiedad del gráfico.
        line_chart = alt.Chart(movie_counts).mark_line().encode(
            x='Año:O',  # El eje x es el año 
            y='Cantidad de peliculas:Q',  # El eje y es la cantidad de películas 
        ).properties(
            title=f'Número de películas por año ({genero_seleccionado})'
        ) 
        
        # Mostrar el gráfico en Streamlit
        st.altair_chart(line_chart, use_container_width=True) # Mostrar el gráfico en Streamlit, use_container_width=True hace que el gráfico se adapte al ancho de la ventana
        
        df_merged = pd.merge(dg_combined, dm, on='id') # Unir los df y que coincidan con id
        
        df_merged = df_merged.dropna(subset=['genre', 'rating']) # Eliminar los valores nulos de las columnas 'genre' y 'rating'
         
        df_merged['rating'] = pd.to_numeric(df_merged['rating'], errors='coerce') # Convertir la columna 'rating' a numérica 
        
        df_merged = df_merged.dropna(subset=['rating']) # Eliminar los valores nulos de la columna 'rating' 
        
        genre_ratings = df_merged.groupby('genre')['rating'].mean().reset_index() # Agrupar por género y calcular el promedio de rating, .reset_index() en pandas se utiliza para restablecer el índice de un DataFrame.
        
        top_genres = genre_ratings.sort_values(by='rating', ascending=False).head(10) # Ordenar por promedio de rating y seleccionar los 10 mejores géneros
        
        selected_genre = st.selectbox('Selecciona un género', ['Todos'] + list(top_genres['genre'].unique())) # Selectbox para seleccionar un genreo
        
        # Si se selecciona un género, mostrar las mejores películas de ese género
        if selected_genre == 'Todos': # Si se selecciona la opción "Todos"
            # Mostrar el gráfico de los géneros
            chart_data = top_genres 
            title = 'Top 10 Géneros con mayor calificación'
        else:
            df_genre = df_merged[df_merged['genre'] == selected_genre] # Filtrar las películas del género seleccionado
            
            top_movies = df_genre.sort_values(by='rating', ascending=False).head(10) # Ordenar por rating y seleccionar las 10 mejores películas
            
            # Crear el gráfico con las películas del género seleccionado
            chart_data = top_movies
            title = f'Top 10 Películas de {selected_genre} con mayor calificación'
        
        # Crear el gráfico con Altair, .mark_bar() en Altair se utiliza para crear un gráfico de barras, sort='-y': Esto ordena los valores en el eje X en función de los valores del eje Y, title='Géneros' if selected_genre == 'Todos' else 'Películas': El título del eje X cambia dependiendo de si se están mostrando géneros o películas, y='rating': El eje Y representa la columna 'rating',  Si selected_genre es 'Todos', el título será "Calificación Promedio". Si es un género específico o una película, el título será "Calificación".
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('genre' if selected_genre == 'Todos' else 'name', sort='-y', title='Géneros' if selected_genre == 'Todos' else 'Películas'),
            y=alt.Y('rating', title='Calificación Promedio' if selected_genre == 'Todos' else 'Calificación'),
            color='genre' if selected_genre == 'Todos' else 'name'
        ).properties(
            title=title
        )
        
        st.altair_chart(chart, use_container_width=True) # Mostrar el gráfico en Streamlit
                        
        #Generos mas repetidos en peliculas
        genre_counts = dg_combined['genre'].value_counts().reset_index() # Cantidad de veces que aprece cada genero
        genre_counts.columns = ['genre', 'count']  # Renombrar las columnas para orden
        
        # Calcular los porcentajes
        total_count = genre_counts['count'].sum() # Sumar todas las cantidades
        genre_counts['percentage'] = (genre_counts['count'] / total_count) * 100 # Calcular los porcentajes
    
        color_palette = alt.Scale(domain=genre_counts['genre'].tolist(), range=[
        '#FF6347', '#FF4500', '#FFD700', '#FF8C00', '#DC143C', '#C71585', '#F08080', 
        '#32CD32', '#8A2BE2', '#20B2AA', '#2E8B57', '#4682B4', '#D2691E', '#A52A2A', 
        '#C0C0C0', '#8A2BE2'
        ]) # Crear un color palette con 16 colores
    
        # Crear el gráfico de pie con porcentajes, .mark_arc() en Altair se utiliza para crear un gráfico de pie, theta es el ángulo de las "porciones" del pastel, y se basa en los valores de la columna percentage, type="quantitative" especifica que los datos de la columna percentage son cuantitativo, type="nominal" indica que genre es una variable categórica (nominal), scale=color_palette aplica una paleta de colores personalizada a los géneros, tooltip agrega información interactiva que aparece cuando el usuario pasa el mouse sobre una porción del gráfico.
        pie_chart = alt.Chart(genre_counts).mark_arc().encode(
            theta=alt.Theta(field="percentage", type="quantitative"),  # Tamaño de las porciones basado en porcentaje
            color=alt.Color(field="genre", type="nominal", scale=color_palette),
            tooltip=[alt.Tooltip("genre:N", title="Género"), #Mostrar datos al pasar el mouse
                     alt.Tooltip("percentage:Q", format=".1f", title="Porcentaje")]  # Mostrar porcentaje formateado
        ).properties(
            title="Generos mas repetidos en las peliculas" 
        )
        
        st.altair_chart(pie_chart, use_container_width=True) # Mostrar el gráfico en Streamlit

        # Duración y rating dispersion
        dm['rating'] = pd.to_numeric(dm['rating'], errors='coerce') # Convertir la columna rating a numérica
        dm['minute'] = pd.to_numeric(dm['minute'], errors='coerce') # Convertir la columna minute a numérica
        
        dm = dm.dropna(subset=['rating', 'minute']) # Eliminar filas con valores faltantes en rating o minute
        
        # Crear el gráfico de dispersión con mejoras visuales, .mark_point() indica que el gráfico será de dispersión, filled=True rellena los puntos, opacity=0.6 configura la opacidad de los puntos, 'minute:Q' el eje X está mapeado a la columna minute, 'rating:Q' el eje Y está mapeado a la columna rating, size=alt.Size('rating:Q') el tamaño de los puntos depende de los valores en la columna rating, scale=alt.Scale(domain=[0, 5], range=[50, 200]) se escala el tamaño de los puntos, width=700, height=400: Ajusta el tamaño del gráfico, .configure_legend(titleFontSize=14, labelFontSize=12): Configura la apariencia de la leyenda (14 titulo, 12 fuente etiqueta).
        scatter_plot = alt.Chart(dm).mark_point(filled=True, opacity=0.6).encode(
            x=alt.X('minute:Q', title='Duración (minutos)'),  # Título para el eje X
            y=alt.Y('rating:Q', title='Popularidad (rating)'),  # Título para el eje Y
            color=alt.Color('rating:Q', legend=alt.Legend(title='Rating')),
            size=alt.Size('rating:Q', scale=alt.Scale(domain=[0, 5], range=[50, 200])),  # Ajustar el tamaño de los puntos
            tooltip=['minute', 'rating']  # Mostrar detalles al pasar el cursor
        ).properties(
            title="Relación entre Duración y Popularidad de Películas",
            width=700,
            height=400
        ).configure_legend(
        titleFontSize=14,
        labelFontSize=12
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14 
        ).configure_title(
            fontSize=16, # Tamaño del título
            anchor='start' # Alinea el título al comienzo de la gráfica
        )

        st.altair_chart(scatter_plot, use_container_width=True) # Mostrar el gráfico en Streamlit
