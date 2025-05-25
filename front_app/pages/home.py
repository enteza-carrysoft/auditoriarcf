import streamlit as st
from ..ui_utils import info_box, create_bar_chart, create_line_chart # Adjusted path
import pandas as pd # For example data

def show_home():
    st.markdown('<h1 class="main-header">Auditoría del Registro Contable de Facturas</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta aplicación permite realizar la auditoría del Registro Contable de Facturas según lo establecido en el artículo 12.3 de la Ley 25/2013."
    )
    
    # Mostrar resumen de datos
    st.markdown('<h2 class="section-header">Resumen de Datos</h2>', unsafe_allow_html=True)
    
    # Crear columnas para mostrar estadísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Facturas", value="0") # Hardcoded
    
    with col2:
        st.metric(label="Facturas Electrónicas", value="0") # Hardcoded
    
    with col3:
        st.metric(label="Facturas en Papel", value="0") # Hardcoded
    
    with col4:
        st.metric(label="Tiempo Medio Tramitación", value="0 días") # Hardcoded
    
    # Mostrar gráficos de resumen
    st.markdown('<h2 class="section-header">Gráficos de Resumen</h2>', unsafe_allow_html=True)
    
    # Crear datos de ejemplo para los gráficos
    estados = ['Registrada', 'Contabilizada', 'Conformada', 'Pagada', 'Rechazada']
    cantidades = [50, 30, 20, 10, 5]
    df_estados = pd.DataFrame({'Estado': estados, 'Cantidad': cantidades})
    
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril']
    tiempos = [15, 14, 12, 10]
    df_tiempos = pd.DataFrame({'Mes': meses, 'Tiempo Medio (días)': tiempos})
    
    # Mostrar gráficos en dos columnas
    col1_charts, col2_charts = st.columns(2) # Renamed to avoid conflict with metric columns
    
    with col1_charts:
        st.plotly_chart(create_bar_chart(df_estados, 'Estado', 'Cantidad', 
                                         'Facturas por Estado', 'Estado', 'Cantidad'), use_container_width=True)
    
    with col2_charts:
        st.plotly_chart(create_line_chart(df_tiempos, 'Mes', 'Tiempo Medio (días)', 
                                          'Evolución de Tiempos de Tramitación', 'Mes', 'Tiempo Medio (días)'), use_container_width=True)
    
    # Mostrar accesos rápidos
    st.markdown('<h2 class="section-header">Accesos Rápidos</h2>', unsafe_allow_html=True)
    
    col1_buttons, col2_buttons, col3_buttons = st.columns(3) # Renamed to avoid conflict
        
    with col1_buttons:
        if st.button("📥 Importar Datos", use_container_width=True):
            st.session_state.selected_menu = "Importación de Datos"
            st.rerun() 
    
    with col2_buttons:
        if st.button("📊 Ver Informes", use_container_width=True):
            st.session_state.selected_menu = "Generación de Informes"
            st.rerun()
    
    with col3_buttons:
        if st.button("📝 Auditar Facturas en Papel", use_container_width=True):
            st.session_state.selected_menu = "Facturas en Papel"
            st.rerun()
