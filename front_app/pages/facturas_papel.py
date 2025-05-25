import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import requests
import json
from ..ui_utils import info_box, warning_box, success_box, download_excel
from ..config import API_URL_PAPEL

def show_facturas_papel():
    st.markdown('<h1 class="main-header">Auditoría de Facturas en Papel</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar el cumplimiento de la obligatoriedad de factura electrónica establecida en el artículo 4 de la Ley 25/2013, analizando las facturas en papel registradas en un periodo."
    )
    
    # Initialize session state for data if it doesn't exist
    if 'df_papel_api' not in st.session_state:
        st.session_state.df_papel_api = pd.DataFrame() # Ensure it's an empty DataFrame
    if 'last_update_papel' not in st.session_state:
        st.session_state.last_update_papel = "N/A"

    # Date inputs and update button
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        fecha_inicio_input = st.date_input("Fecha Inicio", datetime.now() - timedelta(days=30), key="fp_fecha_inicio")
    with col2:
        fecha_fin_input = st.date_input("Fecha Fin", datetime.now(), key="fp_fecha_fin")
    with col3:
        if st.button("Actualizar datos", key="fp_actualizar_papel", use_container_width=True, type="primary"):
            fecha_inicio_str = fecha_inicio_input.strftime("%Y-%m-%d")
            fecha_fin_str = fecha_fin_input.strftime("%Y-%m-%d")
            
            payload = {"fecha_inicio": fecha_inicio_str, "fecha_fin": fecha_fin_str}
            
            try:
                response = requests.post(API_URL_PAPEL, json=payload, timeout=20) 
                response.raise_for_status()  
                
                api_data = response.json()
                
                fuera_plazo_data = []
                for item in api_data.get("v1_2_fuera_plazo_30_dias", []):
                    fuera_plazo_data.append({
                        "ID Factura": item.get("id"),
                        "Número Factura": item.get("numero_factura"),
                        "NIF Emisor": item.get("proveedor_nif"),
                        "Fecha Presentación": item.get("fecha_presentacion"),
                        "Fecha Registro RCF": item.get("fecha_registro_rcf"),
                        "Días Transcurridos": item.get("dias_transcurridos"),
                        "Detalle Incumplimiento": "Fuera de plazo (>30 días)"
                    })
                
                sin_fecha_presentacion_data = []
                for factura_id in api_data.get("v1_2_sin_fecha_presentacion", []):
                    sin_fecha_presentacion_data.append({
                        "ID Factura": factura_id,
                        "Número Factura": "N/A (Solo ID)",
                        "NIF Emisor": "N/A (Solo ID)",
                        "Detalle Incumplimiento": "Sin fecha de presentación"
                    })

                sin_fecha_registro_data = []
                for factura_id in api_data.get("v1_2_sin_fecha_registro_rcf", []):
                    sin_fecha_registro_data.append({
                        "ID Factura": factura_id,
                        "Número Factura": "N/A (Solo ID)",
                        "NIF Emisor": "N/A (Solo ID)",
                        "Detalle Incumplimiento": "Sin fecha de registro RCF"
                    })
                
                duplicadas_data = []
                for item in api_data.get("v1_4_duplicadas_potenciales", []):
                    duplicadas_data.append({
                        "ID Factura": item.get("id"),
                        "Número Factura": item.get("numero_factura"),
                        "NIF Emisor": item.get("proveedor_nif"),
                        "Fecha Factura": item.get("fecha_factura"),
                        "Fecha Registro RCF": item.get("fecha_registro_rcf"),
                        "IDs Duplicados Asociados": ", ".join(map(str, item.get("ids_duplicados_asociados", []))),
                        "Detalle Incumplimiento": "Potencial duplicidad"
                    })

                all_incidents = fuera_plazo_data + sin_fecha_presentacion_data + sin_fecha_registro_data + duplicadas_data
                
                if all_incidents:
                    st.session_state.df_papel_api = pd.DataFrame(all_incidents)
                    st.session_state.df_papel_api = st.session_state.df_papel_api.fillna({
                        "Número Factura": "N/A", "NIF Emisor": "N/A", 
                        "Fecha Presentación": "N/A", "Fecha Registro RCF": "N/A",
                        "Días Transcurridos": "N/A", "Fecha Factura": "N/A",
                        "IDs Duplicados Asociados": "N/A"
                    })
                    cols_order = ["ID Factura", "Número Factura", "NIF Emisor", "Fecha Factura", 
                                  "Fecha Presentación", "Fecha Registro RCF", "Días Transcurridos", 
                                  "IDs Duplicados Asociados", "Detalle Incumplimiento"]
                    actual_cols = [col for col in cols_order if col in st.session_state.df_papel_api.columns]
                    st.session_state.df_papel_api = st.session_state.df_papel_api[actual_cols]
                else:
                    st.session_state.df_papel_api = pd.DataFrame(columns=[
                        "ID Factura", "Número Factura", "NIF Emisor", "Fecha Factura", 
                        "Fecha Presentación", "Fecha Registro RCF", "Días Transcurridos", 
                        "IDs Duplicados Asociados", "Detalle Incumplimiento"
                    ])

                st.session_state.last_update_papel = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                success_box(f"Datos actualizados correctamente.", f"{api_data.get('total_facturas_papel_analizadas', 0)} facturas de papel analizadas en el periodo.")
            
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
                st.session_state.df_papel_api = pd.DataFrame() # Reset on error


    st.markdown(f'<div style="text-align: right; margin-bottom:1rem;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: {st.session_state.last_update_papel}</span></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs([
        "Incumplimientos detectados en facturas de papel", 
        "Evolución mensual de facturas en papel", 
        "Proveedores con mayor número de facturas en papel"
    ])
    
    with tab1:
        st.markdown('<h2 class="subsection-header">Facturas en papel con posibles incumplimientos</h2>', unsafe_allow_html=True)
        if not st.session_state.df_papel_api.empty:
            st.dataframe(st.session_state.df_papel_api)
            st.markdown(download_excel(st.session_state.df_papel_api, "facturas_papel_incumplimientos"), unsafe_allow_html=True)
        else:
            st.info("No se encontraron incumplimientos para el periodo seleccionado o no se han cargado datos.")
    
    with tab2:
        st.markdown('<h2 class="subsection-header">Evolución mensual de facturas en papel</h2>', unsafe_allow_html=True)
        warning_box("Información no disponible", "Evolución mensual y datos de proveedores no disponibles actualmente desde este endpoint del backend para facturas de papel.")
    
    with tab3:
        st.markdown('<h2 class="subsection-header">Proveedores con mayor número de facturas en papel</h2>', unsafe_allow_html=True)
        warning_box("Información no disponible", "Evolución mensual y datos de proveedores no disponibles actualmente desde este endpoint del backend para facturas de papel.")
