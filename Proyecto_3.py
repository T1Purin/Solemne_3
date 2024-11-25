import streamlit as st
from Paginas.Main import main
from Paginas.Pagina_principal import principal
from Paginas.Cartelera import cartelera


#Gestionar la navegación entre páginas
def app():

    st.set_page_config(layout="wide")

    if "page" not in st.session_state:
        st.session_state.page = "Main"

    if st.session_state.page == "Main":
        pass
    elif st.session_state.page == "DPeliculas":
        pass
    elif st.session_state.page == "Cartelera":
        pass

app()
