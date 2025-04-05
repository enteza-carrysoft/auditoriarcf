# pages/anotacion_rcf.py

import streamlit as st
import pandas as pd
from datetime import datetime
from components.boxes import info_box, success_box
from components.downloads import download_excel
from components.charts import create_line_chart
import plotly.express as px

def show_anotacion_rcf():
    st.markdown('<h1 class="main-header">Auditoría de Anotación en RCF</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar la correcta anotación de las facturas en el Registro Contable de Facturas."
    )
    
    # Selector de fecha y botón de actualización
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        st.selectbox("Seleccionar fecha", ["Fecha actual", "Datos históricos"], key="fecha_tipo_rcf")
    with col2:
        if st.button("Actualizar datos", key="actualizar_rcf"):
            st.session_state.datos_actualizados_rcf = True
    with col3:
        st.markdown(
            '<div style="text-align: right;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: 05/04/2025</span></div>',
            unsafe_allow_html=True
        )
    
    # Pestañas para análisis
    tab1, tab2, tab3 = st.tabs(["Custodia de facturas", "Tiempos medios de anotación", "Facturas no anotadas en RCF"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Total facturas", value="100")
            st.metric(label="Facturas comprobadas", value="20")
        with col2:
            st.metric(label="Facturas con errores", value="0")
            st.metric(label="Porcentaje de errores", value="0%")
        success_box(
            "Resultado de la auditoría de custodia",
            "No se han detectado errores en la custodia de facturas. Se cumple correctamente con la normativa."
        )
    
    with tab2:
        # Datos de ejemplo para tiempos de anotación
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril']
        tiempos_medios = [120, 100, 90, 80]
        tiempos_minimos = [30, 25, 20, 15]
        tiempos_maximos = [240, 210, 180, 150]
        df_tiempos = pd.DataFrame({
            'Mes': meses, 
            'Tiempo Medio (minutos)': tiempos_medios,
            'Tiempo Mínimo (minutos)': tiempos_minimos,
            'Tiempo Máximo (minutos)': tiempos_maximos
        })
        
        st.plotly_chart(
            create_line_chart(df_tiempos, 'Mes', 'Tiempo Medio (minutos)', 
                              'Evolución de tiempos medios de anotación', 'Mes', 'Tiempo Medio (minutos)'),
            use_container_width=True
        )
        st.dataframe(df_tiempos)
        st.markdown(download_excel(df_tiempos, "tiempos_anotacion"), unsafe_allow_html=True)
    
    with tab3:
        # Datos de ejemplo para facturas no anotadas
        df_no_anotadas = pd.DataFrame({
            "Número Factura": ["F2025-004", "F2025-005"],
            "NIF Emisor": ["B12345678", "A87654321"],
            "Razón Social": ["Empresa A", "Empresa B"],
            "Fecha Emisión": ["04/04/2025", "05/04/2025"],
            "Importe": [1200.00, 3500.50],
            "Fecha Registro FACe": ["04/04/2025", "05/04/2025"],
            "Días Pendientes": [1, 0]
        })
        st.write("Facturas registradas en FACe pero no anotadas en RCF:")
        st.dataframe(df_no_anotadas)
        st.markdown(download_excel(df_no_anotadas, "facturas_no_anotadas"), unsafe_allow_html=True)
