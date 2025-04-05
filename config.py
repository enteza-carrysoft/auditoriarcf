# config.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR CRÍTICO: Las variables de entorno SUPABASE_URL y SUPABASE_SERVICE_KEY deben estar definidas.")
    supabase = None
else:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Conexión con Supabase establecida correctamente.")
    except Exception as e:
        print(f"Error CRÍTICO al inicializar el cliente de Supabase: {e}")
        supabase = None
