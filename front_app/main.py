# main.py

import streamlit as st
from PIL import Image
from config import get_supabase_client
from pages import home, import_data, facturas_papel, anotacion_rcf, contenido_facturas, tramitacion, informes

# Inicializamos la sesión para la navegación si aún no existe
if "page" not in st.session_state:
    st.session_state.page = "Inicio"

# Barra lateral para navegación
logo = Image.open("./images/logo.png")
st.sidebar.image(logo, use_container_width=True)
st.sidebar.markdown("# Auditoría de Facturas")
menu = st.sidebar.selectbox("Seleccione una sección", 
    ["Inicio", "Importación de Datos", "Facturas en Papel", "Anotación en RCF", 
     "Contenido de Facturas", "Tramitación", "Generación de Informes"])

st.session_state.page = menu

# Incluir estilos globales (puedes centralizarlos aquí o en cada página)
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1E3A8A; margin-bottom: 1rem; }
    .section-header { font-size: 1.8rem; font-weight: bold; color: #2563EB; margin-top: 2rem; margin-bottom: 1rem; }
    .subsection-header { font-size: 1.4rem; font-weight: bold; color: #3B82F6; margin-top: 1.5rem; margin-bottom: 0.8rem; }
    .info-box { background-color: #EFF6FF; border-left: 5px solid #3B82F6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; }
    .warning-box { background-color: #FEF3C7; border-left: 5px solid #F59E0B; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; }
    .success-box { background-color: #ECFDF5; border-left: 5px solid #10B981; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# Llamada a la función correspondiente según la sección seleccionada
if st.session_state.page == "Inicio":
    home.show_home()
elif st.session_state.page == "Importación de Datos":
    import_data.show_importacion_datos()
elif st.session_state.page == "Facturas en Papel":
    facturas_papel.show_facturas_papel()
elif st.session_state.page == "Anotación en RCF":
    anotacion_rcf.show_anotacion_rcf()  # Implementa show_anotacion_rcf en su módulo
elif st.session_state.page == "Contenido de Facturas":
    contenido_facturas.show_contenido_facturas()  # Implementa show_contenido_facturas
elif st.session_state.page == "Tramitación":
    tramitacion.show_tramitacion()  # Implementa show_tramitacion
elif st.session_state.page == "Generación de Informes":
    informes.show_generacion_informes()  # Implementa show_generacion_informes
