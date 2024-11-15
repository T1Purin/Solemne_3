import streamlit as st
from Paginas.Main import main
from Paginas.Pagina_principal import Principal
from Paginas.Cartelera import Cartelera


# Función para gestionar la navegación entre páginas
def app():
    if "page" not in st.session_state:
        st.session_state.page = "Main"  # Página inicial por defecto

    if st.session_state.page == "Main":
        main()
    elif st.session_state.page == "Personal":
        Principal()
    elif st.session_state.page == "Cartelera":
        Cartelera()


# Ejecutar la aplicación
if __name__ == "__main__":
    app()
