import streamlit as st

def personal():
    st.title("Página Personal: Detalles de la Película Seleccionada")

    # Verificar si ya hay una película seleccionada en session_state
    if "selected_movie" in st.session_state:
        movie_data = st.session_state.selected_movie
        movie_id = movie_data['id']  # ID de la película

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

        # Mostrar las 3 películas similares (si existen)
        if not movie_data['genres_3'].empty:  # Si hay películas similares
            cols = st.columns(4)  # Crear tres columnas

            # Iterar sobre las películas similares y asignar cada una a una columna
            for idx, (index, row) in enumerate(movie_data['genres_3'].iterrows()):
                with cols[idx]:  # Usar la columna correspondiente
                    st.image(row['link'], caption=row['name'], width=160)
                    st.write(f"[Ver más detalles]({row['link']})")  # Link al póster de la película similar
        else:
            st.write("No hay películas similares disponibles.")

    else:
        st.write("No se ha seleccionado ninguna película aún.")

    # Crear un botón para regresar a la página principal
    st.write('Dale dos clicks al botón para regresar:')
    if st.button("Regresar a la Página Principal"):
        st.session_state.page = "Main"  # Cambiar a la página principal




