import streamlit as st
import pandas as pd
from PIL import Image

# Import utilities and config (config not directly used in main.py but good for context)
from .ui_utils import info_box 
# from .config import API_BASE_URL # Not directly used here

# Import page functions
from .pages.home import show_home
from .pages.import_data import show_importacion_datos
from .pages.facturas_papel import show_facturas_papel
from .pages.anotacion_rcf import show_anotacion_rcf
from .pages.contenido_facturas import show_contenido_facturas
from .pages.tramitacion import show_tramitacion
from .pages.informes import show_generacion_informes

# Configuración de la página
st.set_page_config(
    page_title="Auditoría de Facturas Electrónicas",
    page_icon="images/ControlFace.png", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .subsection-header {
        font-size: 1.4rem;
        font-weight: bold;
        color: #3B82F6;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .info-box {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .warning-box {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .success-box {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        font-size: 1rem;
        font-weight: 500;
        color: #6B7280;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main_app():
    # Sidebar with navigation
    try:
        logo = Image.open("images/logo.png") 
        st.sidebar.image(logo, use_container_width=True)
    except FileNotFoundError:
        st.sidebar.error("Logo no encontrado en front_app/images/logo.png")

    st.sidebar.markdown("# Auditoría de Facturas")
    
    menu_options = ["Inicio", "Importación de Datos", "Facturas en Papel", 
                    "Anotación en RCF", "Contenido de Facturas", 
                    "Tramitación", "Generación de Informes"]
    
    if 'selected_menu' not in st.session_state:
        st.session_state.selected_menu = "Inicio"

    selected_menu_item = st.sidebar.selectbox(
        "Seleccione una sección",
        menu_options,
        index=menu_options.index(st.session_state.selected_menu), 
        key="main_menu_selector" 
    )
    
    if selected_menu_item != st.session_state.selected_menu:
        st.session_state.selected_menu = selected_menu_item
        st.rerun() 

    # Routing logic
    if st.session_state.selected_menu == "Inicio":
        show_home()
    elif st.session_state.selected_menu == "Importación de Datos":
        show_importacion_datos()
    elif st.session_state.selected_menu == "Facturas en Papel":
        show_facturas_papel()
    elif st.session_state.selected_menu == "Anotación en RCF":
        show_anotacion_rcf()
    elif st.session_state.selected_menu == "Contenido de Facturas":
        show_contenido_facturas()
    elif st.session_state.selected_menu == "Tramitación":
        show_tramitacion()
    elif st.session_state.selected_menu == "Generación de Informes":
        show_generacion_informes()
    else:
        st.error(f"Página no encontrada: {st.session_state.selected_menu}")
        show_home() # Default to home

if __name__ == "__main__":
    main_app()
