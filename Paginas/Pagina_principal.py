import streamlit as st
import pandas as pd

def principal():
    st.title("Detalles de la Película Seleccionada")

    # Verificar si ya hay una película seleccionada en session_state
    if "selected_movie" in st.session_state:
        movie_data = st.session_state.selected_movie
        movie_id = movie_data['id']  # ID de la película actual

        # Mostrar la información de la película seleccionada (columna 1)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(movie_data['poster_url'], caption=movie_data['name'], width=230)

        with col2:
            st.title(movie_data['name'])
            st.write(f'Calificación: {movie_data["rating"][0]}')
            st.progress(float(movie_data["rating"][0]) / 5)  # Asegúrate de que rating esté en el formato adecuado (0-5)
            st.caption(f"Géneros: {movie_data['genres']}, Duración: {int(movie_data['minute'][0])} minutos.")
            st.write(movie_data['tagline'][0])
            st.write(f"Actores: {movie_data['actors']}")
            st.write(movie_data['description'][0])

        # Crear la caja para ingresar el nombre y la reseña
        name = st.text_input("Ingresa tu nombre:")
        review = st.text_area("Escribe tu reseña:")

        # Crear un espacio para mostrar las reseñas anteriores
        if "reviews" not in st.session_state:
            st.session_state.reviews = {}  # Inicializar un diccionario para almacenar reseñas por película

        # Mostrar reseñas ya existentes para esta película
        if movie_id in st.session_state.reviews:
            st.subheader("Reseñas Anteriores:")
            for review_entry in st.session_state.reviews[movie_id]:
                st.write(f"{review_entry['name']}: {review_entry['review']}")

        # Botón para enviar la reseña
        if st.button("Enviar reseña"):
            if name and review:
                # Guardar la reseña en el diccionario de reseñas
                if movie_id not in st.session_state.reviews:
                    st.session_state.reviews[movie_id] = []  # Inicializa la lista si es la primera reseña

                st.session_state.reviews[movie_id].append({'name': name, 'review': review})

                st.write(f"Gracias {name} por tu reseña:")
                st.write(review)
            elif not name:
                st.write("Por favor, ingresa tu nombre.")
            elif not review:
                st.write("Por favor, escribe una reseña.")

        # Mostrar las 4 películas similares (si existen)
        if 'genres_3' in movie_data and not movie_data['genres_3'].empty:  # Asegúrate de que 'genres_3' existe y no está vacío
            cols = st.columns(3)  # Cambiar a 3 columnas para las películas similares

            # Filtrar las películas similares para excluir la película actual
            filtered_similar_movies = movie_data['genres_3'][movie_data['genres_3']['id'] != movie_id]

            # Asegurarse de que no haya duplicados de las películas ya mostradas
            displayed_movie_ids = [movie_id]  # Inicializar con la película seleccionada

            # Iteramos sobre las columnas para obtener los IDs de las películas que ya están en la barra
            for col in cols:
                displayed_movie_ids += [movie['id'] for movie in st.session_state.get('displayed_movies', [])]

            # Excluir cualquier película que ya se haya mostrado previamente
            filtered_similar_movies = filtered_similar_movies[~filtered_similar_movies['id'].isin(displayed_movie_ids)]

            # Si hay menos de 4 películas similares, reemplazamos las faltantes con otras películas
            if len(filtered_similar_movies) < 3:
                # Filtramos nuevamente las películas similares para tomar solo las que no sean la película actual
                other_movies = movie_data['genres_3'][movie_data['genres_3']['id'] != movie_id]
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
                    # Crear un enlace a la página de detalles de la película seleccionada
                    movie_link = f"/detalles_pelicula/{row['id']}"  # Asumiendo que 'id' es el identificador único de la película
                    st.markdown(f"[Ver detalles]({movie_link})")

            if len(filtered_similar_movies) == 0:
                st.write("No hay películas similares disponibles.")
        else:
            st.write("No hay películas similares disponibles.")

    else:
        st.write("No se ha seleccionado ninguna película aún.")

    # Crear un botón para regresar a la página principal
    st.write('Dale dos clics al botón para regresar:')
    if st.button("Regresar a la Página Principal"):
        st.session_state.page = "Main"  # Cambiar a la página principal
        st.session_state.selected_movie = None  # Limpiar la película seleccionada
