import streamlit as st
from ..ui_utils import info_box, warning_box, success_box # Only these are used from ui_utils

def show_generacion_informes():
    st.markdown('<h1 class="main-header">Generación de Informes</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite generar los informes de auditoría requeridos por el artículo 12.3 de la Ley 25/2013 y consultar los informes generados anteriormente."
    )
    
    # Selección de modelo de informe
    st.markdown('<h2 class="section-header">Seleccione el modelo de informe</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # For buttons inside markdown, direct action like st.button is not possible.
        # These are decorative for now or would need complex JS injection.
        # For actual functionality, use st.button outside markdown.
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 1</h3>
            <p style="text-align: center; color: #6B7280;">Informe básico</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Incluye información básica sobre la auditoría de facturas electrónicas.</p>
            <div style="text-align: center; margin-top: 1rem;">
                 <!-- Placeholder for buttons -->
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Generar Modelo 1", key="gen_modelo1", use_container_width=True):
            st.info("Funcionalidad 'Generar Modelo 1' no implementada.")


    with col2:
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 2</h3>
            <p style="text-align: center; color: #6B7280;">Informe detallado</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Incluye información detallada sobre la auditoría con análisis estadísticos.</p>
            <div style="text-align: center; margin-top: 1rem;">
                 <!-- Placeholder for buttons -->
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Generar Modelo 2", key="gen_modelo2", use_container_width=True):
            st.info("Funcionalidad 'Generar Modelo 2' no implementada.")

    with col3:
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 3</h3>
            <p style="text-align: center; color: #6B7280;">Informe completo</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Incluye información exhaustiva con anexos y documentación adicional.</p>
            <div style="text-align: center; margin-top: 1rem;">
                 <!-- Placeholder for buttons -->
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Generar Modelo 3", key="gen_modelo3", use_container_width=True):
            st.info("Funcionalidad 'Generar Modelo 3' no implementada.")
            
    # Generar nuevo informe
    st.markdown('<h2 class="section-header">Generar nuevo informe</h2>', unsafe_allow_html=True)
    
    col_form1, col_form2 = st.columns(2) # Unique column variable names
    
    with col_form1:
        entidad = st.text_input("Entidad", "", key="informe_entidad")
    
    with col_form2:
        periodo = st.selectbox(
            "Período auditado",
            ["Año actual", "Año anterior", "Personalizado"],
            key="informe_periodo"
        )
    
    col_form_b1, col_form_b2 = st.columns(2) # Unique column variable names
    
    with col_form_b1:
        nombre_informe = st.text_input("Nombre del informe", "", key="informe_nombre")
    
    with col_form_b2:
        modelo_informe = st.selectbox(
            "Modelo de informe",
            ["Modelo 1 - Básico", "Modelo 2 - Detallado", "Modelo 3 - Completo"],
            key="informe_modelo"
        )
    
    notas = st.text_area("Notas adicionales", "", key="informe_notas") # Changed to text_area for more space
    
    if st.button("Generar informe", key="generar_informe_main_button"):
        if not entidad or not nombre_informe:
            warning_box(
                "Campos incompletos",
                "Por favor, complete los campos obligatorios: Entidad y Nombre del informe."
            )
        else:
            success_box(
                "Informe generado correctamente",
                f"Se ha generado el informe '{nombre_informe}' con el modelo {modelo_informe} para la entidad '{entidad}' correspondiente al periodo '{periodo}'. Notas: {notas if notas else 'N/A'}"
            )
    
    # Consulta de documentos almacenados
    st.markdown('<h2 class="section-header">Consulta de documentos de auditoría almacenados</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para informes almacenados
    # This would typically come from a database or file system, not hardcoded
    df_informes = pd.DataFrame({
        "Fecha": [],
        "Modelo": [],
        "Nombre": [],
        "Notas": [],
        # "Acciones": [] # Actions would require more complex Streamlit logic (e.g. buttons in cells)
    })
    
    if df_informes.empty:
        st.info("No hay documentos de auditoría almacenados disponibles para consulta.") # Changed from st.write
    else:
        st.dataframe(df_informes)
