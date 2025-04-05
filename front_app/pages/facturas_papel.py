# pages/facturas_papel.py

import streamlit as st
import pandas as pd
from components.boxes import info_box, warning_box, success_box
from components.downloads import download_excel
from components.charts import create_bar_chart
from datetime import datetime

def show_facturas_papel():
    st.markdown('<h1 class="main-header">Auditoría de Facturas en Papel</h1>', unsafe_allow_html=True)
    
    info_box("Información", "Verifica el cumplimiento de la obligatoriedad de factura electrónica.")
    
    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        st.selectbox("Seleccionar fecha", ["Fecha actual", "Datos históricos"], key="fecha_tipo_papel")
    with col2:
        if st.button("Actualizar datos", key="actualizar_papel"):
            st.session_state.datos_actualizados_papel = True
    with col3:
        st.markdown('<div style="text-align: right;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem;">Última actualización: 05/04/2025</span></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Facturas que incumplen", "Evolución mensual", "Proveedores destacados"])
    
    with tab1:
        df_papel = pd.DataFrame({
            "Número Factura": ["P2025-001", "P2025-002", "P2025-003"],
            "NIF Emisor": ["B12345678", "A87654321", "B11223344"],
            "Razón Social": ["Empresa A", "Empresa B", "Empresa C"],
            "Fecha Emisión": ["01/04/2025", "02/04/2025", "03/04/2025"],
            "Importe": [1000.00, 2500.50, 750.25],
            "Requisito Incumplido": ["Obligado", "Obligado", "Obligado"]
        })
        st.dataframe(df_papel)
        st.markdown(download_excel(df_papel, "facturas_papel_incumplen"), unsafe_allow_html=True)
    
    with tab2:
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril']
        cantidades = [10, 8, 5, 3]
        df_evolucion = pd.DataFrame({'Mes': meses, 'Cantidad': cantidades})
        st.plotly_chart(create_bar_chart(df_evolucion, 'Mes', 'Cantidad', 'Evolución mensual', 'Mes', 'Cantidad'), use_container_width=True)
        st.dataframe(df_evolucion)
        st.markdown(download_excel(df_evolucion, "evolucion_facturas_papel"), unsafe_allow_html=True)
    
    with tab3:
        df_proveedores = pd.DataFrame({
            "NIF Emisor": ["B12345678", "A87654321", "B11223344"],
            "Razón Social": ["Empresa A", "Empresa B", "Empresa C"],
            "Número de Facturas": [5, 3, 2],
            "Importe Total": [5000.00, 7500.50, 1500.25]
        })
        st.dataframe(df_proveedores)
        st.markdown(download_excel(df_proveedores, "proveedores_facturas_papel"), unsafe_allow_html=True)
