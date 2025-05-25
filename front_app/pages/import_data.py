import streamlit as st
import pandas as pd
from datetime import datetime
from ..ui_utils import info_box, success_box, warning_box, download_excel # download_excel might be used if any tab shows a df

def show_importacion_datos():
    st.markdown('<h1 class="main-header">Importación de Datos</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite importar datos desde diferentes plataformas de facturación electrónica como FACe, AOC o Biskaiticc."
    )
    
    # Crear pestañas para diferentes tipos de importación
    tab1, tab2, tab3, tab4 = st.tabs([
        "Facturas presentadas en plataforma", 
        "Facturas pendientes de descargar", 
        "Solicitudes de anulación",
        "Histórico de estados"
    ])
    
    with tab1:
        st.markdown('<h2 class="subsection-header">Importar facturas presentadas en plataforma</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            plataforma = st.selectbox(
                "Seleccione la plataforma",
                ["FACe", "AOC", "Biskaiticc", "Otra"],
                key="plataforma_facturas_import" # Unique key
            )
        
        with col2:
            fecha = st.date_input(
                "Fecha de importación",
                datetime.now(),
                key="fecha_facturas_import" # Unique key
            )
        
        uploaded_file = st.file_uploader("Seleccione el archivo de facturas (Excel o CSV)", type=["xlsx", "csv"], key="file_facturas_import") # Unique key
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("Vista previa de los datos:")
                st.dataframe(df.head())
                
                if st.button("Procesar facturas", key="procesar_facturas_import"): # Unique key
                    success_box(
                        "Procesamiento exitoso",
                        f"Se han procesado {len(df)} facturas correctamente."
                    )
            except Exception as e:
                warning_box(
                    "Error al procesar el archivo",
                    f"Se ha producido un error: {str(e)}"
                )
    
    with tab2:
        st.markdown('<h2 class="subsection-header">Facturas pendientes de descargar</h2>', unsafe_allow_html=True)
        
        col1_pend, col2_pend = st.columns(2) # Use different var names for columns in different scopes
        
        with col1_pend:
            plataforma_pend = st.selectbox( # Unique key for widget
                "Seleccione la plataforma",
                ["FACe", "AOC", "Biskaiticc", "Otra"],
                key="plataforma_pendientes_import"
            )
        
        with col2_pend:
            fecha_pend = st.date_input( # Unique key for widget
                "Fecha de consulta",
                datetime.now(),
                key="fecha_pendientes_import"
            )
        
        if st.button("Consultar facturas pendientes", key="consultar_pendientes_import"): # Unique key
            # Simulación de consulta
            df_pendientes = pd.DataFrame({
                "Número Factura": ["F2025-001", "F2025-002", "F2025-003"],
                "NIF Emisor": ["B12345678", "A87654321", "B11223344"],
                "Razón Social": ["Empresa A, S.L.", "Empresa B, S.A.", "Empresa C, S.L."],
                "Fecha Emisión": ["01/04/2025", "02/04/2025", "03/04/2025"],
                "Importe": [1000.00, 2500.50, 750.25],
                "Estado": ["Registrada", "Registrada", "Registrada"]
            })
            
            st.write("Facturas pendientes de descargar:")
            st.dataframe(df_pendientes)
            st.markdown(download_excel(df_pendientes, "facturas_pendientes"), unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<h2 class="subsection-header">Importar solicitudes de anulación</h2>', unsafe_allow_html=True)
        
        col1_anul, col2_anul = st.columns(2)
        
        with col1_anul:
            plataforma_anul = st.selectbox(
                "Seleccione la plataforma",
                ["FACe", "AOC", "Biskaiticc", "Otra"],
                key="plataforma_anulacion_import"
            )
        
        with col2_anul:
            fecha_anul = st.date_input(
                "Fecha de importación",
                datetime.now(),
                key="fecha_anulacion_import"
            )
        
        uploaded_file_anul = st.file_uploader("Seleccione el archivo de solicitudes (Excel o CSV)", type=["xlsx", "csv"], key="file_anulacion_import")
        
        if uploaded_file_anul is not None:
            try:
                if uploaded_file_anul.name.endswith('.csv'):
                    df_anul = pd.read_csv(uploaded_file_anul)
                else:
                    df_anul = pd.read_excel(uploaded_file_anul)
                
                st.write("Vista previa de los datos:")
                st.dataframe(df_anul.head())
                
                if st.button("Procesar solicitudes", key="procesar_anulacion_import"):
                    success_box(
                        "Procesamiento exitoso",
                        f"Se han procesado {len(df_anul)} solicitudes de anulación correctamente."
                    )
            except Exception as e:
                warning_box(
                    "Error al procesar el archivo",
                    f"Se ha producido un error: {str(e)}"
                )
    
    with tab4:
        st.markdown('<h2 class="subsection-header">Importar histórico de estados</h2>', unsafe_allow_html=True)
        
        col1_hist, col2_hist = st.columns(2)
        
        with col1_hist:
            plataforma_hist = st.selectbox(
                "Seleccione la plataforma",
                ["FACe", "AOC", "Biskaiticc", "Otra"],
                key="plataforma_historico_import"
            )
        
        with col2_hist:
            fecha_hist = st.date_input(
                "Fecha de importación",
                datetime.now(),
                key="fecha_historico_import"
            )
        
        uploaded_file_hist = st.file_uploader("Seleccione el archivo de histórico (Excel o CSV)", type=["xlsx", "csv"], key="file_historico_import")
        
        if uploaded_file_hist is not None:
            try:
                if uploaded_file_hist.name.endswith('.csv'):
                    df_hist = pd.read_csv(uploaded_file_hist)
                else:
                    df_hist = pd.read_excel(uploaded_file_hist)
                
                st.write("Vista previa de los datos:")
                st.dataframe(df_hist.head())
                
                if st.button("Procesar histórico", key="procesar_historico_import"):
                    success_box(
                        "Procesamiento exitoso",
                        f"Se han procesado {len(df_hist)} registros de histórico correctamente."
                    )
            except Exception as e:
                warning_box(
                    "Error al procesar el archivo",
                    f"Se ha producido un error: {str(e)}"
                )
