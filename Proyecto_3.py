import streamlit as st
from Paginas.Main import main
from Paginas.Pagina_principal import principal
from Paginas.Cartelera import cartelera

st.session_state.page = "Main"

#Gestionar la navegación entre páginas
def app():

    if st.session_state.page == "Main":
        st.set_page_config(layout="wide")
        main()
    elif st.session_state.page == "DPeliculas":
        st.set_page_config(layout="wide")
        principal()
    elif st.session_state.page == "Cartelera":
        st.set_page_config(layout="wide")
        cartelera()

app()
