# pages/tramitacion.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from components.boxes import info_box
from components.downloads import download_excel

def show_tramitacion():
    st.markdown('<h1 class="main-header">Auditoría de Tramitación</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar la correcta tramitación de las facturas y analizar los tiempos medios de tramitación."
    )
    
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        st.selectbox("Seleccionar fecha", ["Fecha actual", "Datos históricos"], key="fecha_tipo_tramitacion")
    with col2:
        if st.button("Actualizar datos", key="actualizar_tramitacion"):
            st.session_state.datos_actualizados_tramitacion = True
    with col3:
        st.markdown(
            '<div style="text-align: right;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem;">Última actualización: 05/04/2025</span></div>',
            unsafe_allow_html=True
        )
    
    st.markdown('<h2 class="section-header">Comparativa de solicitudes de anulación</h2>', unsafe_allow_html=True)
    
    df_solicitudes = pd.DataFrame({
        "Nº Factura": [],
        "NIF Emisor": [],
        "Fecha solicitud": [],
        "Estado en FACe": [],
        "Estado en RCF": []
    })
    if df_solicitudes.empty:
        st.write("No hay datos disponibles")
    else:
        st.dataframe(df_solicitudes)
        st.markdown(download_excel(df_solicitudes, "solicitudes_anulacion"), unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Tiempos medios de tramitación</h2>', unsafe_allow_html=True)
    
    df_tiempos_tramitacion = pd.DataFrame({
        "Estado": ["Registrada", "Contabilizada", "Conformada", "Pagada"],
        "Tiempo medio en FACe (días)": [1, 5, 10, 20],
        "Tiempo medio en RCF (días)": [1, 4, 8, 18],
        "Diferencia (días)": [0, 1, 2, 2]
    })
    st.dataframe(df_tiempos_tramitacion)
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_tiempos_tramitacion['Estado'],
        y=df_tiempos_tramitacion['Tiempo medio en FACe (días)'],
        name='FACe',
        marker_color='#3B82F6'
    ))
    fig.add_trace(go.Bar(
        x=df_tiempos_tramitacion['Estado'],
        y=df_tiempos_tramitacion['Tiempo medio en RCF (días)'],
        name='RCF',
        marker_color='#10B981'
    ))
    fig.update_layout(
        title='Comparativa de tiempos medios de tramitación',
        xaxis_title='Estado',
        yaxis_title='Tiempo medio (días)',
        barmode='group',
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(download_excel(df_tiempos_tramitacion, "tiempos_tramitacion"), unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Evolución mensual de tiempos de tramitación</h2>', unsafe_allow_html=True)
    
    df_evolucion_tiempos = pd.DataFrame({
        "Mes": ["Enero", "Febrero", "Marzo", "Abril"],
        "Tiempo medio hasta contabilización (días)": [4, 3, 3, 2],
        "Tiempo medio hasta conformidad (días)": [8, 7, 6, 5],
        "Tiempo medio hasta pago (días)": [20, 18, 16, 15]
    })
    st.dataframe(df_evolucion_tiempos)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_evolucion_tiempos['Mes'],
        y=df_evolucion_tiempos['Tiempo medio hasta contabilización (días)'],
        name='Contabilización',
        mode='lines+markers',
        marker_color='#3B82F6'
    ))
    fig2.add_trace(go.Scatter(
        x=df_evolucion_tiempos['Mes'],
        y=df_evolucion_tiempos['Tiempo medio hasta conformidad (días)'],
        name='Conformidad',
        mode='lines+markers',
        marker_color='#10B981'
    ))
    fig2.add_trace(go.Scatter(
        x=df_evolucion_tiempos['Mes'],
        y=df_evolucion_tiempos['Tiempo medio hasta pago (días)'],
        name='Pago',
        mode='lines+markers',
        marker_color='#F59E0B'
    ))
    fig2.update_layout(
        title='Evolución mensual de tiempos de tramitación',
        xaxis_title='Mes',
        yaxis_title='Tiempo medio (días)',
        height=500
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(download_excel(df_evolucion_tiempos, "evolucion_tiempos_tramitacion"), unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Facturas con mayor tiempo de tramitación</h2>', unsafe_allow_html=True)
    
    df_facturas_mayor_tiempo = pd.DataFrame({
        "Nº Factura": [],
        "NIF Emisor": [],
        "Razón Social": [],
        "Fecha Emisión": [],
        "Fecha Pago": [],
        "Tiempo total (días)": []
    })
    if df_facturas_mayor_tiempo.empty:
        st.write("No hay datos disponibles")
    else:
        st.dataframe(df_facturas_mayor_tiempo)
        st.markdown(download_excel(df_facturas_mayor_tiempo, "facturas_mayor_tiempo"), unsafe_allow_html=True)
