# pages/import_data.py

import streamlit as st
import pandas as pd
from datetime import datetime
from components.boxes import info_box, warning_box, success_box
from components.downloads import download_excel

def show_importacion_datos():
    st.markdown('<h1 class="main-header">Importación de Datos</h1>', unsafe_allow_html=True)
    
    info_box("Información",
             "Esta sección permite importar datos desde diferentes plataformas de facturación electrónica.")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Facturas presentadas en plataforma", 
        "Facturas pendientes de descargar", 
        "Solicitudes de anulación",
        "Histórico de estados"
    ])
    
    with tab1:
        st.markdown('<h2 class="subsection-header">Importar facturas presentadas</h2>', unsafe_allow_html=True)
        plataforma = st.selectbox("Seleccione la plataforma", ["FACe", "AOC", "Biskaiticc", "Otra"], key="plataforma_facturas")
        fecha = st.date_input("Fecha de importación", datetime.now(), key="fecha_facturas")
        uploaded_file = st.file_uploader("Seleccione el archivo de facturas (Excel o CSV)", type=["xlsx", "csv"], key="file_facturas")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                st.write("Vista previa:")
                st.dataframe(df.head())
                if st.button("Procesar facturas", key="procesar_facturas"):
                    success_box("Procesamiento exitoso", f"Se han procesado {len(df)} facturas correctamente.")
            except Exception as e:
                warning_box("Error", f"Se ha producido un error: {str(e)}")
    
    # Con tab2, tab3 y tab4 puedes replicar la lógica de importación para las otras secciones
    with tab2:
        st.markdown('<h2 class="subsection-header">Facturas pendientes de descargar</h2>', unsafe_allow_html=True)
        # Ejemplo de datos de consulta
        if st.button("Consultar facturas pendientes", key="consultar_pendientes"):
            df_pendientes = pd.DataFrame({
                "Número Factura": ["F2025-001", "F2025-002", "F2025-003"],
                "NIF Emisor": ["B12345678", "A87654321", "B11223344"],
                "Razón Social": ["Empresa A", "Empresa B", "Empresa C"],
                "Fecha Emisión": ["01/04/2025", "02/04/2025", "03/04/2025"],
                "Importe": [1000.00, 2500.50, 750.25],
                "Estado": ["Registrada", "Registrada", "Registrada"]
            })
            st.dataframe(df_pendientes)
            st.markdown(download_excel(df_pendientes, "facturas_pendientes"), unsafe_allow_html=True)
    
    # Los tabs 3 y 4 se estructuran de forma similar
