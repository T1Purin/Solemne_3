import streamlit as st
import pandas as pd
import random
from pyecharts import options as opts
from pyecharts.charts import Bar
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
            st.session_state.page = "DPeliculas"  # Cambiar a la página personal


    def cartelera_bar():
        # Definir los géneros
        name_genre = dg_combined["genre"].unique()
        genre_selection = st.selectbox("Seleccione un género", ["Seleccione un género"] + list(name_genre))

        if genre_selection != "Seleccione un género":
            genero_movies = dg_combined[dg_combined["genre"] == genre_selection]["id"].unique()
            filtrar_movies = dm[dm["id"].isin(genero_movies)]
            top10 = filtrar_movies.head(10)

            st.write(f"Top 10 películas de {genre_selection}")

            # Inicializar el índice de películas en la sesión si no existe
            if "movie_index" not in st.session_state:
                st.session_state.movie_index = 0

            col1, col2 = st.columns([17, 1])

            # Botón anterior
            with col1:
                if st.session_state.movie_index > 0:
                    if st.button("←", use_container_width=False):
                        st.session_state.movie_index -= 5

            # Botón siguiente
            with col2:
                if st.session_state.movie_index < len(top10) - 5:
                    if st.button("→", use_container_width=False):
                        st.session_state.movie_index += 5

            selected_movies = top10.iloc[st.session_state.movie_index:st.session_state.movie_index + 5]
            columns = st.columns(5)

            for index, (col, row) in enumerate(zip(columns, selected_movies.iterrows())):
                movie_name = row[1]["name"]
                movie_poster_url = dp[dp["id"] == row[1]["id"]]["link"].values

                # Mostrar la imagen y el nombre de la película
                if len(movie_poster_url) > 0:
                    col.image(movie_poster_url[0], width=140)
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

    # Verificar cuál opción fue elegida y mostrar el buscador correspondiente
    if 'search_type' not in st.session_state:
        st.session_state.search_type = 'movie'  # Valor por defecto (buscar por película)

    if st.session_state.search_type == 'movie':
        st.write("Buscador de Películas:")
        select_bar()  # Llamar al buscador de películas
    else:
        st.write("Buscador de Géneros:")
        cartelera_bar()  # Llamar al buscador de géneros

    # Mostrar la pregunta inicial para elegir entre los buscadores
    st.write("¿Qué tipo de buscador prefieres usar?")

    # Crear una fila de columnas para los botones (los botones estarán en una línea horizontal)
    col1, col2 = st.columns([1, 1])  # Crear 2 columnas con igual tamaño

    # Colocar un botón en cada columna
    with col1:
        if st.button('Buscar por película'):
            st.session_state.search_type = 'movie'  # Guardar la elección en session_state

    with col2:
        if st.button('Buscar por género'):
            st.session_state.search_type = 'genre'  # Guardar la elección en session_state

    st.subheader('Tendencias del momento')

    # Seleccionar 4 películas aleatorias
    random_movies = dm.sample(n=4, random_state=42)  # Selecciona 4 películas aleatorias

    # Crear las columnas para mostrar las películas de manera lateral
    columns = st.columns(4)  # Crear 4 columnas

    # Mostrar las películas en las 4 columnas
    for i, (col, row) in enumerate(zip(columns, random_movies.iterrows())):
        movie_name = row[1]['name']
        movie_poster_url = dp[dp['id'] == row[1]['id']]['link'].values
        
        # Mostrar el nombre de la película y el póster en cada columna
        with col:
            if len(movie_poster_url) > 0:
                st.image(movie_poster_url[0], width=140)
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

    st.subheader('Estadisticas:')
    
   # Título de la página
    st.title("Top 10 Géneros por Rating")
    
    # Unir los DataFrames
    df_merged = pd.merge(dg_combined, dm, on='id')
    
    # Expandir los géneros
    df_merged['genre'] = df_merged['genre'].str.split(',')
    df_exploded = df_merged.explode('genre')
    
    # Eliminar filas con valores nulos en 'genre' o 'rating'
    df_exploded = df_exploded.dropna(subset=['genre', 'rating'])
    
    # Asegurarse de que 'rating' sea numérico
    df_exploded['rating'] = pd.to_numeric(df_exploded['rating'], errors='coerce')
    
    # Eliminar filas con valores no numéricos en 'rating'
    df_exploded = df_exploded.dropna(subset=['rating'])
    
    # Calcular el promedio de rating por género
    genre_ratings = df_exploded.groupby('genre')['rating'].mean().reset_index()
    
    # Ordenar por promedio de rating y seleccionar los 10 mejores géneros
    top_genres = genre_ratings.sort_values(by='rating', ascending=False).head(10)
    # Preparar los datos para el gráfico ECharts
    x_data = top_genres['genre'].tolist()  # Los géneros
    y_data = top_genres['rating'].tolist()  # Los ratings promedio
    
    # Crear el gráfico con Altair
    chart = alt.Chart(top_genres).mark_bar().encode(
        x=alt.X('genre', sort='-y'),
        y='rating',
        color='genre'
    ).properties(
        title='Top 10 Géneros por Promedio de Rating'
    )
    
    # Mostrar el gráfico en Streamlit
    st.altair_chart(chart, use_container_width=True)
#----------------------------------------------------------------------------------

    #Generos mas repetidos en peliculas
    genre_counts = dg_combined['genre'].value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']  # Renombrar las columnas para claridad
    
    # Calcular los porcentajes
    total_count = genre_counts['count'].sum()
    genre_counts['percentage'] = (genre_counts['count'] / total_count) * 100

    color_palette = alt.Scale(domain=genre_counts['genre'].tolist(), range=[
    '#FF6347', '#4682B4', '#32CD32', '#FFD700', '#8A2BE2', '#DC143C', '#FF8C00', 
    '#20B2AA', '#C71585', '#F08080', '#8A2BE2', '#A52A2A', '#FF4500', '#2E8B57', 
    '#D2691E', '#C0C0C0'
    ])
    # Crear el gráfico de pie con porcentajes
    pie_chart = alt.Chart(genre_counts).mark_arc().encode(
        theta=alt.Theta(field="percentage", type="quantitative"),  # Tamaño de las porciones basado en porcentaje
        color=alt.Color(field="genre", type="nominal", scale=color_palette),
        tooltip=[alt.Tooltip("genre:N", title="Género"),
                 alt.Tooltip("percentage:Q", format=".1f", title="Porcentaje")]  # Mostrar porcentaje formateado
    ).properties(
        title="Generos mas usados para las peliculas"
    )
    
    # Mostrar el gráfico en Streamlit
    st.altair_chart(pie_chart, use_container_width=True)
            
