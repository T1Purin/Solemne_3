import streamlit as st
from Paginas.Datos_principal import main
from Paginas.Barra import principal
from Paginas.Cartelera import cartelera
from Paginas.Años import años


#Gestionar la navegación entre páginas
def app():

    st.set_page_config(layout="wide")

    if "page" not in st.session_state:
        st.session_state.page = "Main"

    if st.session_state.page == "Main":
        main()
    elif st.session_state.page == "DPeliculas":
        principal()
    elif st.session_state.page == "Cartelera":
        cartelera()
    elif st.session_state.page == "Años":
        años()

app()
