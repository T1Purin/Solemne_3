import streamlit as st
from Paginas.Main import main
from Paginas.Pagina_principal import principal
from Paginas.Cartelera import cartelera

#Gestionar la navegación entre páginas
def app():
    if 'page' not session_state:
    st.session_state.page = "Main"

    if st.session_state.page == "Main":
        main()
    elif st.session_state.page == "DPeliculas":
        principal()
    elif st.session_state.page == "Cartelera":
        cartelera()

app()
