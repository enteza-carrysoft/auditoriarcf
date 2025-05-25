import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
from ..ui_utils import info_box, warning_box, success_box, download_excel
from ..config import API_URL_TRAMITACION

def show_tramitacion():
    st.markdown('<h1 class="main-header">Auditoría de Tramitación (Estados)</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar que el campo 'estado' de cada factura electrónica esté en un conjunto de valores válidos según la normativa."
    )

    # Initialize session state variables
    if 'tramitacion_data' not in st.session_state:
        st.session_state.tramitacion_data = {} 
    if 'df_estado_incorrecto_api' not in st.session_state:
        st.session_state.df_estado_incorrecto_api = pd.DataFrame()
    if 'last_update_tramitacion' not in st.session_state:
        st.session_state.last_update_tramitacion = "N/A"

    # Date inputs and update button
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        fecha_inicio_input_tramitacion = st.date_input("Fecha Inicio (Opcional)", value=None, key="tram_fecha_inicio")
    with col2:
        fecha_fin_input_tramitacion = st.date_input("Fecha Fin (Opcional)", value=None, key="tram_fecha_fin")
    with col3:
        if st.button("Actualizar datos", key="tram_actualizar_tramitacion", use_container_width=True, type="primary"):
            fecha_inicio_str = fecha_inicio_input_tramitacion.strftime("%Y-%m-%d") if fecha_inicio_input_tramitacion else None
            fecha_fin_str = fecha_fin_input_tramitacion.strftime("%Y-%m-%d") if fecha_fin_input_tramitacion else None
            
            payload = {}
            proceed_with_call = False
            if fecha_inicio_str and fecha_fin_str:
                payload = {"fecha_inicio": fecha_inicio_str, "fecha_fin": fecha_fin_str}
                proceed_with_call = True
            elif not fecha_inicio_str and not fecha_fin_str:
                proceed_with_call = True
            else: 
                 st.warning("Por favor, seleccione ambas fechas (Inicio y Fin) o ninguna para auditar todos los datos.")
                 proceed_with_call = False
            
            if proceed_with_call:
                try:
                    response = requests.post(API_URL_TRAMITACION, json=payload, timeout=20)
                    response.raise_for_status()
                    
                    api_data = response.json()
                    st.session_state.tramitacion_data = api_data
                    
                    facturas_estado_incorrecto = api_data.get("facturas_con_estado_incorrecto", [])
                    if facturas_estado_incorrecto:
                        st.session_state.df_estado_incorrecto_api = pd.DataFrame(facturas_estado_incorrecto)
                        st.session_state.df_estado_incorrecto_api = st.session_state.df_estado_incorrecto_api.rename(
                            columns={'id': 'ID Factura', 'numero_factura': 'Número Factura', 'estado': 'Estado Reportado'}
                        )
                    else:
                        st.session_state.df_estado_incorrecto_api = pd.DataFrame(columns=['ID Factura', 'Número Factura', 'Estado Reportado'])
                    
                    st.session_state.last_update_tramitacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    success_box(f"Datos actualizados.", f"{api_data.get('total_facturas_tramitacion', 0)} facturas analizadas para estado de tramitación.")

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
                    st.session_state.tramitacion_data = {}
                    st.session_state.df_estado_incorrecto_api = pd.DataFrame()

    st.markdown(f'<div style="text-align: right; margin-bottom:1rem;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: {st.session_state.last_update_tramitacion}</span></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Facturas con Estado de Tramitación Incorrecto</h2>', unsafe_allow_html=True)
    if not st.session_state.df_estado_incorrecto_api.empty:
        # Ensure the DataFrame has the expected columns before trying to select them
        df_display = st.session_state.df_estado_incorrecto_api
        if 'ID Factura' in df_display.columns and 'Número Factura' in df_display.columns and 'Estado Reportado' in df_display.columns:
             st.dataframe(df_display[['ID Factura', 'Número Factura', 'Estado Reportado']])
        else: # Fallback if columns are not as expected (e.g. after an error or if API changes)
             st.dataframe(df_display)
        st.markdown(download_excel(st.session_state.df_estado_incorrecto_api, "facturas_estado_incorrecto"), unsafe_allow_html=True)
    else:
        st.info("No se encontraron facturas con estado de tramitación incorrecto para el periodo seleccionado, o no se han cargado datos.")

    st.markdown('<h2 class="section-header">Comparativa de solicitudes de anulación</h2>', unsafe_allow_html=True)
    warning_box("Información no disponible", "Este análisis no está disponible desde el endpoint actual de tramitación de estados.")
    
    st.markdown('<h2 class="section-header">Tiempos medios de tramitación</h2>', unsafe_allow_html=True)
    warning_box("Información no disponible", "Este análisis no está disponible desde el endpoint actual de tramitación de estados.")
    
    st.markdown('<h2 class="section-header">Evolución mensual de tiempos de tramitación</h2>', unsafe_allow_html=True)
    warning_box("Información no disponible", "Este análisis no está disponible desde el endpoint actual de tramitación de estados.")
    
    st.markdown('<h2 class="section-header">Facturas con mayor tiempo de tramitación</h2>', unsafe_allow_html=True)
    warning_box("Información no disponible", "Este análisis no está disponible desde el endpoint actual de tramitación de estados.")
