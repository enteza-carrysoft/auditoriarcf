# pages/home.py

import streamlit as st
import pandas as pd
from components.charts import create_bar_chart, create_line_chart
from components.boxes import info_box
from components.downloads import download_excel
from datetime import datetime
from PIL import Image

def show_home():
    st.markdown('<h1 class="main-header">Auditoría del Registro Contable de Facturas</h1>', unsafe_allow_html=True)
    
    info_box("Información",
             "Esta aplicación permite realizar la auditoría del Registro Contable de Facturas según el artículo 12.3 de la Ley 25/2013.")
    
    st.markdown('<h2 class="section-header">Resumen de Datos</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Facturas", value="0")
    with col2:
        st.metric(label="Facturas Electrónicas", value="0")
    with col3:
        st.metric(label="Facturas en Papel", value="0")
    with col4:
        st.metric(label="Tiempo Medio Tramitación", value="0 días")
    
    st.markdown('<h2 class="section-header">Gráficos de Resumen</h2>', unsafe_allow_html=True)
    
    estados = ['Registrada', 'Contabilizada', 'Conformada', 'Pagada', 'Rechazada']
    cantidades = [50, 30, 20, 10, 5]
    df_estados = pd.DataFrame({'Estado': estados, 'Cantidad': cantidades})
    
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    tiempos = [15, 14, 12, 10]
    df_tiempos = pd.DataFrame({'Mes': meses, 'Tiempo Medio (días)': tiempos})
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_bar_chart(df_estados, 'Estado', 'Cantidad', 'Facturas por Estado', 'Estado', 'Cantidad'), use_container_width=True)
    with col2:
        st.plotly_chart(create_line_chart(df_tiempos, 'Mes', 'Tiempo Medio (días)', 'Evolución de Tiempos de Tramitación', 'Mes', 'Tiempo Medio (días)'), use_container_width=True)
    
    st.markdown('<h2 class="section-header">Accesos Rápidos</h2>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Importar Datos", use_container_width=True):
            st.session_state.page = "Importación de Datos"
            st.experimental_rerun()
    with col2:
        if st.button("📊 Ver Informes", use_container_width=True):
            st.session_state.page = "Generación de Informes"
            st.experimental_rerun()
    with col3:
        if st.button("📝 Auditar Facturas en Papel", use_container_width=True):
            st.session_state.page = "Facturas en Papel"
            st.experimental_rerun()

def add_home_styles():
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; font-weight: bold; color: #1E3A8A; margin-bottom: 1rem; }
        .section-header { font-size: 1.8rem; font-weight: bold; color: #2563EB; margin-top: 2rem; margin-bottom: 1rem; }
        .subsection-header { font-size: 1.4rem; font-weight: bold; color: #3B82F6; margin-top: 1.5rem; margin-bottom: 0.8rem; }
        .info-box { background-color: #EFF6FF; border-left: 5px solid #3B82F6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; }
        .warning-box { background-color: #FEF3C7; border-left: 5px solid #F59E0B; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; }
        .success-box { background-color: #ECFDF5; border-left: 5px solid #10B981; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1.5rem; }
        .stTabs [data-baseweb="tab-list"] { gap: 2rem; }
        .stTabs [data-baseweb="tab"] { height: 4rem; white-space: pre-wrap; font-size: 1rem; font-weight: 500; color: #6B7280; }
        .stTabs [aria-selected="true"] { color: #2563EB; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
