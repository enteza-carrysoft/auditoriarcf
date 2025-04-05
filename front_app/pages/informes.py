# pages/informes.py

import streamlit as st
import pandas as pd
from components.boxes import info_box, warning_box, success_box
from components.downloads import download_excel

def show_generacion_informes():
    st.markdown('<h1 class="main-header">Generación de Informes</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite generar los informes de auditoría requeridos por el artículo 12.3 de la Ley 25/2013 y consultar los informes generados anteriormente."
    )
    
    st.markdown('<h2 class="section-header">Seleccione el modelo de informe</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 1</h3>
            <p style="text-align: center; color: #6B7280;">Informe básico</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Información básica sobre la auditoría.</p>
            <div style="display: flex; justify-content: center; gap: 0.5rem;">
                <button style="background-color: #F3F4F6; padding: 0.5rem 1rem;">Ver plantilla</button>
                <button style="background-color: #2563EB; color: white; padding: 0.5rem 1rem;">Generar</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 2</h3>
            <p style="text-align: center; color: #6B7280;">Informe detallado</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Análisis estadístico detallado.</p>
            <div style="display: flex; justify-content: center; gap: 0.5rem;">
                <button style="background-color: #F3F4F6; padding: 0.5rem 1rem;">Ver plantilla</button>
                <button style="background-color: #2563EB; color: white; padding: 0.5rem 1rem;">Generar</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 3</h3>
            <p style="text-align: center; color: #6B7280;">Informe completo</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Con anexos y documentación adicional.</p>
            <div style="display: flex; justify-content: center; gap: 0.5rem;">
                <button style="background-color: #F3F4F6; padding: 0.5rem 1rem;">Ver plantilla</button>
                <button style="background-color: #2563EB; color: white; padding: 0.5rem 1rem;">Generar</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Generar nuevo informe</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        entidad = st.text_input("Entidad", "")
    with col2:
        periodo = st.selectbox("Período auditado", ["Año actual", "Año anterior", "Personalizado"])
    
    col1, col2 = st.columns(2)
    with col1:
        nombre_informe = st.text_input("Nombre del informe", "")
    with col2:
        modelo_informe = st.selectbox("Modelo de informe", ["Modelo 1 - Básico", "Modelo 2 - Detallado", "Modelo 3 - Completo"])
    
    notas = st.text_input("Notas adicionales", "")
    
    if st.button("Generar informe", key="generar_informe"):
        if not entidad or not nombre_informe:
            warning_box("Campos incompletos", "Complete los campos obligatorios: Entidad y Nombre del informe.")
        else:
            success_box("Informe generado correctamente", f"Se ha generado el informe '{nombre_informe}' con el modelo {modelo_informe}.")
    
    st.markdown('<h2 class="section-header">Consulta de documentos almacenados</h2>', unsafe_allow_html=True)
    
    df_informes = pd.DataFrame({
        "Fecha": [],
        "Modelo": [],
        "Nombre": [],
        "Notas": [],
        "Acciones": []
    })
    if df_informes.empty:
        st.write("No hay documentos almacenados")
    else:
        st.dataframe(df_informes)
        st.markdown(download_excel(df_informes, "informes_almacenados"), unsafe_allow_html=True)
