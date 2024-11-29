import streamlit as st 
from Paginas.Datos_principal import main 
from Paginas.Barra import principal
from Paginas.Cartelera import cartelera
from Paginas.Años import años


# Gestionar la navegación entre páginas
def app():

    st.set_page_config(layout="wide") #Esta función se utiliza para configurar el aspecto general de la página en Streamlit con un aspecto ancho como indica el wide

    if "page" not in st.session_state: #Si no hay una página guardada en la sesión, se crea una página principal
        st.session_state.page = "Main"  #Se crea una página principal

    if st.session_state.page == "Main": #Si la página actual es la principal
        main() #Se llama a la función main que contiene la página principal

    elif st.session_state.page == "DPeliculas": #Si la página actual es la de datos de películas
        principal() #Se llama a la función principal que contiene la página de datos de películas

    elif st.session_state.page == "Cartelera": #Si la página actual es la de cartelera
        cartelera() #Se llama a la función cartelera que contiene la página de cartelera
        
    elif st.session_state.page == "Años": #Si la página actual es la de años
        años() #Se llama a la función años que contiene la página de años

app() #Se llama a la función app que contiene la navegación entre páginas
