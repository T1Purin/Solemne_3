import streamlit as st
import pandas as pd

def Cartelera():
    st.title("Cartelera de Películas por Género")

    # Verificar si ya hay películas seleccionadas por género
    if "selected_genre_movies_genre" in st.session_state:
        genre_movies = st.session_state.selected_genre_movies_genre

        # Mostrar las películas por género
        for idx, row in genre_movies.iterrows():
            st.image(row['link'], caption=row['name'], width=220)
            st.write(row['description'])

        # Aquí puedes agregar la funcionalidad para navegar entre películas, agregar más detalles, etc.
    else:
        st.write("No se ha seleccionado un género.")

    # Crear un botón para regresar a la página principal
    st.write('Dale dos clics al botón para regresar:')
    if st.button("Regresar a la Página Principal"):
        st.session_state.page = "Main"  # Cambiar a la página principal

