import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
from ..ui_utils import info_box, warning_box, success_box, download_excel
from ..config import API_URL_CONTENIDO

def show_contenido_facturas():
    st.markdown('<h1 class="main-header">Auditoría del Contenido de Facturas</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar el cumplimiento de las validaciones de contenido de las facturas (ej. errores de cálculo) y, en futuras versiones, analizar motivos de rechazo."
    )

    # Initialize session state variables
    if 'contenido_data' not in st.session_state:
        st.session_state.contenido_data = {} 
    if 'df_facturas_con_errores_api' not in st.session_state:
        st.session_state.df_facturas_con_errores_api = pd.DataFrame()
    if 'last_update_contenido' not in st.session_state:
        st.session_state.last_update_contenido = "N/A"

    # Date inputs and update button
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        fecha_inicio_input_contenido = st.date_input("Fecha Inicio (Opcional)", value=None, key="cf_fecha_inicio")
    with col2:
        fecha_fin_input_contenido = st.date_input("Fecha Fin (Opcional)", value=None, key="cf_fecha_fin")
    with col3:
        if st.button("Actualizar datos", key="cf_actualizar_contenido", use_container_width=True, type="primary"):
            fecha_inicio_str = fecha_inicio_input_contenido.strftime("%Y-%m-%d") if fecha_inicio_input_contenido else None
            fecha_fin_str = fecha_fin_input_contenido.strftime("%Y-%m-%d") if fecha_fin_input_contenido else None
            
            payload = {}
            proceed_with_call = False
            if fecha_inicio_str and fecha_fin_str:
                payload = {"fecha_inicio": fecha_inicio_str, "fecha_fin": fecha_fin_str}
                proceed_with_call = True
            elif not fecha_inicio_str and not fecha_fin_str: # Both are None, proceed
                proceed_with_call = True
            else: # Only one is None
                 st.warning("Por favor, seleccione ambas fechas (Inicio y Fin) o ninguna para auditar todos los datos.")
                 proceed_with_call = False
            
            if proceed_with_call:
                try:
                    response = requests.post(API_URL_CONTENIDO, json=payload, timeout=20)
                    response.raise_for_status()
                    
                    api_data = response.json()
                    st.session_state.contenido_data = api_data
                    
                    facturas_con_errores = api_data.get("facturas_con_errores", [])
                    if facturas_con_errores:
                        for f in facturas_con_errores:
                            f['errores'] = ', '.join(f.get('errores', []))
                        st.session_state.df_facturas_con_errores_api = pd.DataFrame(facturas_con_errores)
                        st.session_state.df_facturas_con_errores_api = st.session_state.df_facturas_con_errores_api.rename(
                            columns={'id': 'ID Factura', 'numero_factura': 'Número Factura', 'errores': 'Errores Detectados'}
                        )
                    else:
                        st.session_state.df_facturas_con_errores_api = pd.DataFrame(columns=['ID Factura', 'Número Factura', 'Errores Detectados'])
                    
                    st.session_state.last_update_contenido = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    success_box(f"Datos actualizados.", f"{api_data.get('total_facturas_validadas', 0)} facturas validadas para errores de cálculo.")

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
                    st.session_state.contenido_data = {}
                    st.session_state.df_facturas_con_errores_api = pd.DataFrame()

    st.markdown(f'<div style="text-align: right; margin-bottom:1rem;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: {st.session_state.last_update_contenido}</span></div>', unsafe_allow_html=True)
    
    st.markdown('<h2 class="section-header">Validaciones de Contenido (Errores de Cálculo)</h2>', unsafe_allow_html=True)
    
    if not st.session_state.df_facturas_con_errores_api.empty:
        display_df = st.session_state.df_facturas_con_errores_api
        if 'ID Factura' in display_df.columns and 'Número Factura' in display_df.columns and 'Errores Detectados' in display_df.columns:
             st.dataframe(display_df[['ID Factura', 'Número Factura', 'Errores Detectados']])
        else: # Fallback in case columns were not renamed or are missing
             st.dataframe(display_df)
        st.markdown(download_excel(st.session_state.df_facturas_con_errores_api, "facturas_con_errores_calculo"), unsafe_allow_html=True)
    else:
        st.info("No se encontraron facturas con errores de cálculo para el periodo seleccionado, o no se han cargado datos.")
    
    info_box("Nota sobre Validaciones", 
             "Este endpoint actualmente detalla errores de cálculo en los importes de las facturas. Otras validaciones (formato Facturae, firma, NIF, códigos DIR3) no son detalladas por esta consulta específica.")

    st.markdown('<h2 class="section-header">Facturas rechazadas por motivo</h2>', unsafe_allow_html=True)
    warning_box("Información no disponible", "Análisis de facturas rechazadas y desglose por proveedores no disponible desde este endpoint del backend.")
    
    st.markdown('<h2 class="section-header">Detalle de facturas rechazadas</h2>', unsafe_allow_html=True)
    warning_box("Información no disponible", "Análisis de facturas rechazadas y desglose por proveedores no disponible desde este endpoint del backend.")
    
    st.markdown('<h2 class="section-header">Proveedores con mayor número de rechazos</h2>', unsafe_allow_html=True)
    warning_box("Información no disponible", "Análisis de facturas rechazadas y desglose por proveedores no disponible desde este endpoint del backend.")
