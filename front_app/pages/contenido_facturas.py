# pages/contenido_facturas.py

import streamlit as st
import pandas as pd
from components.boxes import info_box, warning_box
from components.downloads import download_excel
from components.charts import create_pie_chart

def show_contenido_facturas():
    st.markdown('<h1 class="main-header">Auditoría del Contenido de Facturas</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar el cumplimiento de las validaciones establecidas por la Orden HAP/1650/2015 y analizar los motivos de rechazo de facturas."
    )
    
    # Selector de fecha y botón de actualización
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        st.selectbox("Seleccionar fecha", ["Fecha actual", "Datos históricos"], key="fecha_tipo_contenido")
    with col2:
        if st.button("Actualizar datos", key="actualizar_contenido"):
            st.session_state.datos_actualizados_contenido = True
    with col3:
        st.markdown(
            '<div style="text-align: right;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem;">Última actualización: 05/04/2025</span></div>',
            unsafe_allow_html=True
        )
    
    st.markdown('<h2 class="section-header">Validaciones de la Orden HAP/1650/2015</h2>', unsafe_allow_html=True)
    
    df_validaciones = pd.DataFrame({
        "Validación": ["Formato Facturae", "Firma electrónica", "NIF emisor", "Códigos DIR3"],
        "Nº facturas": [0, 0, 0, 0],
        "Porcentaje": [0.0, 0.0, 0.0, 0.0]
    })
    st.dataframe(df_validaciones)
    st.markdown(download_excel(df_validaciones, "validaciones_facturas"), unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Facturas rechazadas por motivo</h2>', unsafe_allow_html=True)
    
    df_rechazos = pd.DataFrame({
        "Motivo": ["Duplicidad", "Órgano gestor incorrecto", "Datos incompletos", "Otros"],
        "Nº facturas": [0, 0, 0, 0],
        "Porcentaje": [0.0, 0.0, 0.0, 0.0]
    })
    st.dataframe(df_rechazos)
    st.plotly_chart(create_pie_chart(df_rechazos, 'Motivo', 'Nº facturas', 'Distribución de rechazos'), use_container_width=True)
    st.markdown(download_excel(df_rechazos, "rechazos_facturas"), unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Detalle de facturas rechazadas</h2>', unsafe_allow_html=True)
    
    df_detalle_rechazos = pd.DataFrame({
        "Nº Factura": [],
        "NIF Emisor": [],
        "Razón Social": [],
        "Fecha Rechazo": [],
        "Motivo": [],
        "Órgano Gestor": []
    })
    
    if df_detalle_rechazos.empty:
        st.write("No hay datos disponibles")
    else:
        st.dataframe(df_detalle_rechazos)
        st.markdown(download_excel(df_detalle_rechazos, "detalle_rechazos"), unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Proveedores con mayor número de rechazos</h2>', unsafe_allow_html=True)
    
    df_proveedores_rechazos = pd.DataFrame({
        "CIF Proveedor": [],
        "Razón Social": [],
        "Nº facturas rechazadas": [],
        "Porcentaje": []
    })
    
    if df_proveedores_rechazos.empty:
        st.write("No hay datos disponibles")
    else:
        st.dataframe(df_proveedores_rechazos)
        st.markdown(download_excel(df_proveedores_rechazos, "proveedores_rechazos"), unsafe_allow_html=True)
