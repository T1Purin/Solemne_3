import streamlit as st
import pandas as pd

def Cartelera():
    st.title("Cartelera de Películas por Género")

    # Verificar si ya hay películas seleccionadas por género
    if "selected_genre_movies" in st.session_state:
        genre_movies = st.session_state.selected_genre_movies

        # Mostrar las películas por género
        for idx, row in genre_movies.iterrows():
            st.image(row['poster_url'], caption=row['name'], width=220)
            st.write(row['description'])

        # Aquí puedes agregar la funcionalidad para navegar entre películas, agregar más detalles, etc.
    else:
        st.write("No se ha seleccionado un género.")
