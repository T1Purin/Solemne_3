import streamlit as st
from Paginas.Main import main
from Paginas.Pagina_principal import principal
from Paginas.Cartelera import cartelera

st.session_state.page = "Main"

#Gestionar la navegación entre páginas
def app():

    if st.session_state.page == "Main":
        main()
    elif st.session_state.page == "DPeliculas":
        principal()
    elif st.session_state.page == "Cartelera":
        cartelera()

app()
