import streamlit as st
import pandas as pd
import random
import altair as alt

def main():
    st.image("Archivos/logo.png")

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
    dm = next(dm_chunks).fillna('')  # Llenar los valores nulos de las películas con una cadena vacía
 
    def select_bar():
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
                    movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7)

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
                
        # Crear botones para cambiar a la página personal
        if st.button("Buscar"):
            st.session_state.page = "DPeliculas"  # Cambiar a la página personal
            st.rerun()

    def cartelera_bar():
        # Definir los géneros
        name_genre = dg_combined["genre"].unique()
        genre_selection = st.selectbox("Seleccione un género", ["Seleccione un género"] + list(name_genre))

        if genre_selection != "Seleccione un género":
            genero_movies = dg_combined[dg_combined["genre"] == genre_selection]["id"].unique()
            filtrar_movies = dm[dm["id"].isin(genero_movies)]
            top10 = filtrar_movies.head(12)

            st.write(f"Top 10 películas de {genre_selection}")

            # Inicializar el indice de pelicula en la sesión si no existe
            if "movie_index" not in st.session_state:
                st.session_state.movie_index = 0

            col1, col2 = st.columns([17, 1])

            # Botón anterior
            with col1:
                if st.session_state.movie_index > 0:
                    if st.button("←", use_container_width=False):
                        st.session_state.movie_index -= 6

            # Botón siguiente
            with col2:
                if st.session_state.movie_index < len(top10) - 6:
                    if st.button("→", use_container_width=False):
                        st.session_state.movie_index += 6

            selected_movies = top10.iloc[st.session_state.movie_index:st.session_state.movie_index + 6]
            columns = st.columns(6)

            for index, (col, row) in enumerate(zip(columns, selected_movies.iterrows())):
                movie_name = row[1]["name"]
                movie_poster_url = dp[dp["id"] == row[1]["id"]]["link"].values

                # Mostrar la imagen y el nombre de la película
                if len(movie_poster_url) > 0:
                    col.image(movie_poster_url[0], width=170)
                else:
                    col.write("Póster no disponible")

                # Botón para la película
                a = col.button(movie_name)

                if a:
                    # Obtener el id de la película
                    movie_gen = row[1]["id"]
                    
                    # Buscar los detalles de la película
                    movie_genres = dg_combined[dg_combined['id'] == movie_gen]['genre'].unique()
                    movie_actors = da_combined[da_combined['id'] == movie_gen]['name'].unique()[:5]
                    movie_tagline = dm[dm['id'] == movie_gen]['tagline'].unique()
                    movie_description = dm[dm['id'] == movie_gen]['description'].unique()
                    movie_rating = dm[dm['id'] == movie_gen]['rating'].unique()
                    movie_minute = dm[dm['id'] == movie_gen]['minute'].unique()
                    movie_poster_url = dp[dp['id'] == movie_gen]['link'].values[0]


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
                            movie_genres_3 = movie_genres_3.drop_duplicates(subset=['id']).head(7)
                            # Guardar los detalles de la película seleccionada en session_state
                    
                    st.session_state.selected_movie_genre = {
                        'name': movie_name,
                        'id': movie_gen,
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
                    st.session_state.page = "Cartelera"
                    st.rerun()

    def años_bar():
        años_names = pd.to_numeric(dm['date'], errors='coerce').dropna().astype(int).unique()
        años_names_sorted = sorted(años_names)  # Ordenar los años de menor a mayor
        años_selected = st.selectbox("Selecciona un año", ["Seleccione un año"] + list(años_names_sorted))

        if años_selected != "Seleccione un año":
            años_movies = dm[dm["date"] == años_selected]["id"].unique()
            filtrar_movies = dm[dm["id"].isin(años_movies)]
            top10 = filtrar_movies.head(12)

            st.write(f"Top 10 películas de {años_selected}")

            # Inicializar el indice de pelicula en la sesión si no existe
            if "movie_index" not in st.session_state:
                st.session_state.movie_index = 0

            col1, col2 = st.columns([17, 1])

            # Botón anterior
            with col1:
                if st.session_state.movie_index > 0:
                    if st.button("←", use_container_width=False):
                        st.session_state.movie_index -= 6

            # Botón siguiente
            with col2:
                if st.session_state.movie_index < len(top10) - 6:
                    if st.button("→", use_container_width=False):
                        st.session_state.movie_index += 6

            selected_movies = top10.iloc[st.session_state.movie_index:st.session_state.movie_index + 6]
            columns = st.columns(6)

            for index, (col, row) in enumerate(zip(columns, selected_movies.iterrows())):
                movie_name = row[1]["name"]
                movie_poster_url = dp[dp["id"] == row[1]["id"]]["link"].values

                # Mostrar la imagen y el nombre de la película
                # Verificar si la URL de la imagen está vacía
                if len(movie_poster_url) > 0 and movie_poster_url[0] != '':
                    # Mostrar la imagen y el nombre de la película
                    col.image(movie_poster_url[0], width=170)
                else:
                    # Si no hay imagen, mostrar un mensaje alternativo o una imagen por defecto
                    col.image("Archivos/404.png")

                # Botón para la película
                b = col.button(movie_name)

                if b:
                    # Buscar los datos relacionados con la película seleccionada
                    años_id = row[1]["id"]

                    # Buscar géneros, actores y la URL del póster para esta película
                    años_name = dm[dm["id"] == años_id]["name"].values[0]
                    años_genres = dg_combined[dg_combined['id'] == años_id]['genre'].unique()  # Usar los géneros combinados
                    años_actors = da_combined[da_combined['id'] == años_id]['name'].unique()[:5]  # Usar los actores combinados
                    años_tagline = dm[dm['id'] == años_id]['tagline'].unique()
                    años_description = dm[dm['id'] == años_id]['description'].unique()
                    años_rating = dm[dm['id'] == años_id]['rating'].unique()
                    años_minute = dm[dm['id'] == años_id]['minute'].unique()
                    años_poster_url = dp[dp['id'] == años_id]['link'].values[0]

                    # Verificar que movie_genres no esté vacío antes de intentar concatenar
                    if len(años_genres) > 0:
                        # Concatenar las películas de los géneros seleccionados
                        años_genres_3 = pd.concat([dg_combined[dg_combined['genre'] == genre] for genre in años_genres if not dg_combined[dg_combined['genre'] == genre].empty], ignore_index=True)
                        
                        if años_genres_3.empty:
                            st.write("No se encontraron películas similares para los géneros seleccionados.")
                        else:
                            # Unir los datos con el DataFrame de películas (dm) para obtener los nombres de las películas
                            años_genres_3 = años_genres_3.merge(dm[['id', 'name']], on='id', how='left')

                            # Unir los datos con el DataFrame de pósters (dp) para obtener las URLs de los pósters
                            años_genres_3 = años_genres_3.merge(dp[['id', 'link']], on='id', how='left')

                            # Obtener las tres primeras películas por género
                            años_genres_3 = años_genres_3.drop_duplicates(subset=['id']).head(7)

                            # Guardar todos los datos seleccionados en session_state para usarlos en la página personal
                    st.session_state.selected_movie_años = {
                        'name': años_name,
                        'id': años_id,
                        'genres': ', '.join(años_genres),
                        'actors': ', '.join(años_actors),
                        'tagline': años_tagline,
                        'description': años_description,
                        'rating': años_rating,
                        'minute': años_minute,
                        'poster_url': años_poster_url,
                        'genres_3': años_genres_3  # Aquí están las películas similares
                    }

                    st.session_state.page = "Años"  # Cambiar a la página personal
                    st.rerun()

    opcion = st.sidebar.selectbox(
    "Seleccione una sección:",
    ("Página principal", "Gráficos"))

    if opcion == "Página principal":
        
        # Verificar cuál opción fue elegida y mostrar el buscador correspondiente
        if 'search_type' not in st.session_state:
            st.session_state.search_type = 'movie'  # Valor por defecto (buscar por película)
    
        if st.session_state.search_type == 'movie':
            st.write("Buscador de Películas:")
            select_bar()  # Llamar al buscador de películas
        elif st.session_state.search_type == 'genre':
            st.write("Buscador de Géneros:")
            cartelera_bar()  # Llamar al buscador de géneros
        elif st.session_state.search_type == 'años':
            st.write("Buscador por años:")
            años_bar()
    
        # Mostrar la pregunta inicial para elegir entre los buscadores
        st.write("¿Qué tipo de buscador prefieres usar?")
    
        # Crear una fila de columnas para los botones (los botones estarán en una línea horizontal)
        col1, col2, col3 = st.columns([1, 1, 1])  # Crear 2 columnas con igual tamaño
    
        # Colocar un botón en cada columna
        with col1:
            if st.button('Buscar por película'):
                st.session_state.search_type = 'movie'  # Guardar la elección en session_state
                st.rerun()
    
        with col2:
            if st.button('Buscar por género'):
                st.session_state.search_type = 'genre'  # Guardar la elección en session_state
                st.rerun()
        
        with col3:
            if st.button('Buscar por años'):
                st.session_state.search_type = 'años'
                st.rerun()

        st.subheader('Tendencias del momento')
    
        # Seleccionar 4 películas aleatorias
        random_movies = dm.sample(n=6, random_state=62)  # Selecciona 4 películas aleatorias
    
        # Crear las columnas para mostrar las películas de manera lateral
        columns = st.columns(6)  # Crear 4 columnas
    
        # Mostrar las películas en las 4 columnas
        for i, (col, row) in enumerate(zip(columns, random_movies.iterrows())):
            movie_name = row[1]['name']
            movie_poster_url = dp[dp['id'] == row[1]['id']]['link'].values
            
            # Mostrar el nombre de la película y el póster en cada columna
            with col:
                if len(movie_poster_url) > 0:
                    st.image(movie_poster_url[0], width=170)
                    a = col.button(movie_name)
                    if a:
                        # Obtener el id de la película
                        movie_gen = row[1]["id"]
                        
                        # Buscar los detalles de la peli
                        movie_genres = dg_combined[dg_combined['id'] == movie_gen]['genre'].unique()
                        movie_actors = da_combined[da_combined['id'] == movie_gen]['name'].unique()[:5]
                        movie_tagline = dm[dm['id'] == movie_gen]['tagline'].unique()
                        movie_description = dm[dm['id'] == movie_gen]['description'].unique()
                        movie_rating = dm[dm['id'] == movie_gen]['rating'].unique()
                        movie_minute = dm[dm['id'] == movie_gen]['minute'].unique()
                        movie_poster_url = dp[dp['id'] == movie_gen]['link'].values[0]
    
    
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
                                # Guardar los detalles de la película seleccionada en session_state
                        
                        st.session_state.selected_movie_genre = {
                            'name': movie_name,
                            'id': movie_gen,
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
                        st.session_state.page = "Cartelera"
                        st.rerun()
    
                else:
                    st.write("Póster no disponible")
    
        st.subheader('Escribe y comparte tus reseñas: ')
    
        # Cargar las reseñas desde el archivo CSV (que contiene el 'movie_id' en lugar de 'movie_name')
        reseñas_df = pd.read_csv('Archivos/reseñas.csv', encoding='utf')
    
        # Limpiar los nombres de las columnas eliminando espacios extra
        reseñas_df.columns = reseñas_df.columns.str.strip()
    
        random_reviews = reseñas_df.sample(n=3)  # Selecciona 4 reseñas aleatorias
    
        # Mostrar las reseñas
        for index, review in random_reviews.iterrows():
            movie_id = review['id']  # Aquí tienes el ID de la película
            user_name = review['name']  # Nombre del usuario
            user_review = review['review']  # Contenido de la reseña
    
            # Buscar el nombre de la película a partir del 'movie_id'
            movie_name = dm[dm['id'] == movie_id]['name'].values
    
            if len(movie_name) > 0:
                movie_name = movie_name[0]  # Obtener el nombre de la película (debe haber un único valor)
            else:
                movie_name = "Película no encontrada"  # En caso de que no se encuentre el ID
    
            # Mostrar la información de la reseña
            st.write(f"### {movie_name}")
            st.write(f"**Reseña por:** {user_name}")
            st.write(f"_{user_review}_")
            st.write("---")

    
    elif opcion == "Gráficos":

        # Combinar los DataFrames utilizando 'id' como clave, el how hace que solo esten presente los ids que coinciden
        df_merged = pd.merge(dm, dg_combined, on='id', how='inner')
        
        # Convertir la columna 'date' a numérica (año)
        df_merged['Año'] = pd.to_numeric(df_merged['date'], errors='coerce')
        
        # Crear un la casilla de seleccion de genersos, #sorted, es alfabeticamente
        generos_disponibles = ['Todos'] + sorted(df_merged['genre'].unique())
        genero_seleccionado = st.selectbox("Selecciona un género para verlo en el grafico", generos_disponibles)
        
        # Filtrar el DataFrame según el género seleccionado
        if genero_seleccionado == 'Todos':
            df_filtrado = df_merged
        else:
            df_filtrado = df_merged[df_merged['genre'] == genero_seleccionado]
        
        # Contar el número de películas por año
        movie_counts = df_filtrado.groupby('Año').size().reset_index(name='Cantidad de peliculas')
        
        # Crear el gráfico de líneas con Altair
        line_chart = alt.Chart(movie_counts).mark_line().encode(
            x='Año:O',  # El eje x es el año 
            y='Cantidad de peliculas:Q',  # El eje y es la cantidad de películas 
        ).properties(
            title=f'Número de películas por año ({genero_seleccionado})'
        )
        
        # Mostrar el gráfico en Streamlit
        st.altair_chart(line_chart, use_container_width=True)
        
       # Unir los df y que coincidan con id
        df_merged = pd.merge(dg_combined, dm, on='id')
        
        # Eliminar valores nulos
        df_merged = df_merged.dropna(subset=['genre', 'rating'])
        
        # Convertir en valores numericos 
        df_merged['rating'] = pd.to_numeric(df_merged['rating'], errors='coerce')
        
        # Eliminar valores nulos  después de convertir
        df_merged = df_merged.dropna(subset=['rating'])
        
        # Calcular el promedio de rating por género
        genre_ratings = df_merged.groupby('genre')['rating'].mean().reset_index()
        
        # Ordenar por promedio de rating y seleccionar los 10 mejores géneros
        top_genres = genre_ratings.sort_values(by='rating', ascending=False).head(10)
        
        # Selectbox para seleccionar un genreo
        selected_genre = st.selectbox('Selecciona un género', ['Todos'] + list(top_genres['genre'].unique()))
        
        # Si se selecciona un género, mostrar las mejores películas de ese género
        if selected_genre == 'Todos':
            # Mostrar el gráfico de los géneros
            chart_data = top_genres
            title = 'Top 10 Géneros con mayor calificación'
        else:
            # Filtrar las películas del género seleccionado
            df_genre = df_merged[df_merged['genre'] == selected_genre]
            
            # Ordenar por rating y seleccionar las 10 mejores películas
            top_movies = df_genre.sort_values(by='rating', ascending=False).head(10)
            
            # Crear el gráfico con las películas del género seleccionado
            chart_data = top_movies
            title = f'Top 10 Películas de {selected_genre} con mayor calificación'
        
        # Crear el gráfico con Altair
        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('genre' if selected_genre == 'Todos' else 'name', sort='-y', title='Géneros' if selected_genre == 'Todos' else 'Películas'),
            y=alt.Y('rating', title='Calificación Promedio' if selected_genre == 'Todos' else 'Calificación'),
            color='genre' if selected_genre == 'Todos' else 'name'
        ).properties(
            title=title
        )
        
        st.altair_chart(chart, use_container_width=True)
                        
        #Generos mas repetidos en peliculas
        # cantidad de veces que aprece cada genero
        genre_counts = dg_combined['genre'].value_counts().reset_index()
        genre_counts.columns = ['genre', 'count']  # Renombrar las columnas para orden
        
        # Calcular los porcentajes
        total_count = genre_counts['count'].sum()
        genre_counts['percentage'] = (genre_counts['count'] / total_count) * 100
    
        color_palette = alt.Scale(domain=genre_counts['genre'].tolist(), range=[
        '#FF6347', '#FF4500', '#FFD700', '#FF8C00', '#DC143C', '#C71585', '#F08080', 
        '#32CD32', '#8A2BE2', '#20B2AA', '#2E8B57', '#4682B4', '#D2691E', '#A52A2A', 
        '#C0C0C0', '#8A2BE2'
        ])
    
        # Crear el gráfico de pie con porcentajes
        pie_chart = alt.Chart(genre_counts).mark_arc().encode(
            theta=alt.Theta(field="percentage", type="quantitative"),  # Tamaño de las porciones basado en porcentaje
            color=alt.Color(field="genre", type="nominal", scale=color_palette),
            tooltip=[alt.Tooltip("genre:N", title="Género"), #Mostrar datos al pasar el mouse
                     alt.Tooltip("percentage:Q", format=".1f", title="Porcentaje")]  # Mostrar porcentaje formateado
        ).properties(
            title="Generos mas repetidos en las peliculas"
        )
        
        # Mostrar el gráfico en Streamlit
        st.altair_chart(pie_chart, use_container_width=True)

        #duración y rating dispersion
        # Asegurarnos de que 'rating' y 'minute' son columnas numéricas
        dm['rating'] = pd.to_numeric(dm['rating'], errors='coerce')
        dm['minute'] = pd.to_numeric(dm['minute'], errors='coerce')
        
        # Eliminar filas con valores nulos
        dm = dm.dropna(subset=['rating', 'minute'])
        
        # Crear el gráfico de dispersión con mejoras visuales
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
            fontSize=16,
            anchor='start'
        )
        
        # Mostrar el gráfico en Streamlit
        st.altair_chart(scatter_plot, use_container_width=True)
