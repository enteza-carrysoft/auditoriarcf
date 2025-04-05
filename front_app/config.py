# config.py

import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Auditoría de Facturas Electrónicas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para obtener la conexión a Supabase (usando los secrets de streamlit)
def get_supabase_client():
    import supabase
    url = st.secrets.get("SUPABASE_URL", "https://your-project-url.supabase.co")
    key = st.secrets.get("SUPABASE_KEY", "your-anon-key")
    return supabase.create_client(url, key)
