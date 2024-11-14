import streamlit as st
from Paginas.Main import main
from Paginas.Personal import personal

def app():
    # Asegúrate de que 'page' esté en session_state
    if "page" not in st.session_state:
        st.session_state.page = "Main"  # Página inicial predeterminada

    # Mostrar el contenido según la página seleccionada
    if st.session_state.page == "Main":
        main()  # Mostrar la página principal
    elif st.session_state.page == "Personal":
        personal()  # Mostrar la página personal

# Ejecutamos la aplicación
if __name__ == "__main__":
    app()
