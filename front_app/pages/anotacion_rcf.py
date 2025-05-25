import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
import plotly.express as px # For histogram
from ..ui_utils import info_box, warning_box, success_box, download_excel
from ..config import API_URL_ANOTACION

def show_anotacion_rcf():
    st.markdown('<h1 class="main-header">Auditoría de Anotación en RCF</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar la correcta anotación de las facturas electrónicas en el Registro Contable de Facturas (RCF) y analizar los tiempos de procesamiento."
    )

    # Initialize session state variables
    if 'anotacion_data' not in st.session_state:
        st.session_state.anotacion_data = {}
    if 'df_tiempos_detalle_api' not in st.session_state:
        st.session_state.df_tiempos_detalle_api = pd.DataFrame()
    if 'df_no_anotadas_api' not in st.session_state:
        st.session_state.df_no_anotadas_api = pd.DataFrame()
    if 'last_update_anotacion' not in st.session_state:
        st.session_state.last_update_anotacion = "N/A"

    # Date inputs and update button
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        fecha_inicio_input_rcf = st.date_input("Fecha Inicio", datetime.now() - timedelta(days=30), key="arcf_fecha_inicio")
    with col2:
        fecha_fin_input_rcf = st.date_input("Fecha Fin", datetime.now(), key="arcf_fecha_fin")
    with col3:
        if st.button("Actualizar datos", key="arcf_actualizar_rcf", use_container_width=True, type="primary"):
            fecha_inicio_str = fecha_inicio_input_rcf.strftime("%Y-%m-%d")
            fecha_fin_str = fecha_fin_input_rcf.strftime("%Y-%m-%d")
            
            payload = {"fecha_inicio": fecha_inicio_str, "fecha_fin": fecha_fin_str}
            
            try:
                response = requests.post(API_URL_ANOTACION, json=payload, timeout=20)
                response.raise_for_status()
                
                api_data = response.json()
                st.session_state.anotacion_data = api_data
                
                tiempos_anotacion_stats = api_data.get("tiempos_anotacion", {})
                detalle_tiempos = tiempos_anotacion_stats.get("detalle", [])
                if detalle_tiempos: # Ensure there's data before creating DataFrame
                    st.session_state.df_tiempos_detalle_api = pd.DataFrame(detalle_tiempos, columns=["Tiempo de Anotación (minutos)"])
                else:
                    st.session_state.df_tiempos_detalle_api = pd.DataFrame(columns=["Tiempo de Anotación (minutos)"]) # Empty DataFrame with column

                facturas_sin_fechas_ids = api_data.get("facturas_sin_fechas", [])
                if facturas_sin_fechas_ids: # Ensure there's data
                    st.session_state.df_no_anotadas_api = pd.DataFrame(facturas_sin_fechas_ids, columns=["ID Factura"])
                else:
                    st.session_state.df_no_anotadas_api = pd.DataFrame(columns=["ID Factura"]) # Empty DataFrame with column
                
                st.session_state.last_update_anotacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                success_box(f"Datos actualizados.", f"{api_data.get('total_facturas_electronicas_analizadas', 0)} facturas electrónicas analizadas.")

            except requests.exceptions.Timeout:
                st.error("Error: Timeout al contactar el backend. Intente nuevamente.")
            except requests.exceptions.HTTPError as e:
                st.error(f"Error al contactar el backend: {e.response.status_code} - {e.response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error de conexión: No se pudo conectar al backend. ({e})")
            except json.JSONDecodeError:
                st.error("Error: La respuesta del backend no es un JSON válido.")
            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {str(e)}")
                st.session_state.anotacion_data = {} 
                st.session_state.df_tiempos_detalle_api = pd.DataFrame()
                st.session_state.df_no_anotadas_api = pd.DataFrame()

    st.markdown(f'<div style="text-align: right; margin-bottom:1rem;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: {st.session_state.last_update_anotacion}</span></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        "Custodia de facturas", 
        "Tiempos medios de anotación", 
        "Facturas no anotadas en RCF"
    ])
    
    with tab1:
        st.markdown('<h2 class="subsection-header">Custodia de facturas</h2>', unsafe_allow_html=True)
        warning_box("Información no disponible", "Datos de custodia de facturas no disponibles desde este endpoint del backend.")
    
    with tab2:
        st.markdown('<h2 class="subsection-header">Tiempos medios de anotación</h2>', unsafe_allow_html=True)
        tiempos_data = st.session_state.anotacion_data.get("tiempos_anotacion", {})
        
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            promedio = tiempos_data.get('promedio_minutos')
            st.metric(label="Promedio (minutos)", value=f"{promedio:.2f}" if isinstance(promedio, (int, float)) else "N/A")
        with col_metric2:
            minimo = tiempos_data.get('minimo_minutos')
            st.metric(label="Mínimo (minutos)", value=f"{minimo:.2f}" if isinstance(minimo, (int, float)) else "N/A")
        with col_metric3:
            maximo = tiempos_data.get('maximo_minutos')
            st.metric(label="Máximo (minutos)", value=f"{maximo:.2f}" if isinstance(maximo, (int, float)) else "N/A")

        if not st.session_state.df_tiempos_detalle_api.empty:
            st.markdown("### Distribución de Tiempos de Anotación")
            fig_hist_tiempos = px.histogram(st.session_state.df_tiempos_detalle_api, x="Tiempo de Anotación (minutos)",
                                            title="Distribución de Tiempos de Anotación en RCF",
                                            labels={"Tiempo de Anotación (minutos)": "Tiempo (minutos)"})
            fig_hist_tiempos.update_layout(yaxis_title="Cantidad de Facturas")
            st.plotly_chart(fig_hist_tiempos, use_container_width=True)
            
            st.markdown("### Detalle de Tiempos de Anotación (minutos)")
            st.dataframe(st.session_state.df_tiempos_detalle_api)
            st.markdown(download_excel(st.session_state.df_tiempos_detalle_api, "detalle_tiempos_anotacion_rcf"), unsafe_allow_html=True)
        else:
            st.info("No hay datos detallados de tiempos de anotación disponibles para el periodo seleccionado.")

    with tab3:
        st.markdown('<h2 class="subsection-header">Facturas electrónicas con fechas faltantes para cálculo de tiempo de anotación</h2>', unsafe_allow_html=True)
        if not st.session_state.df_no_anotadas_api.empty:
            st.info("Se listan los IDs de las facturas para las cuales no se pudo calcular el tiempo de anotación por falta de fechas (presentación o registro RCF).")
            st.dataframe(st.session_state.df_no_anotadas_api)
            st.markdown(download_excel(st.session_state.df_no_anotadas_api, "facturas_sin_fechas_anotacion_rcf"), unsafe_allow_html=True)
        else:
            st.info("No se encontraron facturas con fechas faltantes para el periodo seleccionado, o no se han cargado datos.")
