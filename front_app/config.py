# config.py

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuración de la página
# This is generally called only once, and usually in the main app script (main.py)
# st.set_page_config( # Commenting out as it should be in main.py
#     page_title="Auditoría de Facturas Electrónicas",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Función para obtener la conexión a Supabase (usando los secrets de streamlit)
# This might also be better suited for main.py or a dedicated supabase_client.py
# if it's used by multiple pages and needs to be initialized once.
def get_supabase_client():
    import supabase
    url = st.secrets.get("SUPABASE_URL", "https://your-project-url.supabase.co")
    key = st.secrets.get("SUPABASE_KEY", "your-anon-key")
    return supabase.create_client(url, key)

# API Endpoint URLs
# Fetch API_BASE_URL from environment variable or use default
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000/api")

# Construct specific API URLs using API_BASE_URL
API_URL_PAPEL = f"{API_BASE_URL}/auditar/v1/papel"
API_URL_ANOTACION = f"{API_BASE_URL}/auditar/v2/anotacion"
API_URL_CONTENIDO = f"{API_BASE_URL}/auditar/v3/validaciones" # Corrected typo
API_URL_TRAMITACION = f"{API_BASE_URL}/auditar/v4/tramitacion"
