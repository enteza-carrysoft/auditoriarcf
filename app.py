import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import io
import base64
import supabase
from PIL import Image
import xlsxwriter

# Configuración de la página
st.set_page_config(
    page_title="Auditoría de Facturas Electrónicas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2563EB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .subsection-header {
        font-size: 1.4rem;
        font-weight: bold;
        color: #3B82F6;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
    }
    .info-box {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .warning-box {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .success-box {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        font-size: 1rem;
        font-weight: 500;
        color: #6B7280;
    }
    .stTabs [aria-selected="true"] {
        color: #2563EB;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Función para conectar con Supabase
def get_supabase_client():
    url = st.secrets.get("SUPABASE_URL", "https://your-project-url.supabase.co")
    key = st.secrets.get("SUPABASE_KEY", "your-anon-key")
    return supabase.create_client(url, key)

# Función para descargar datos como Excel
def download_excel(df, filename):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False)
    processed_data = output.getvalue()
    b64 = base64.b64encode(processed_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">Descargar Excel</a>'
    return href

# Función para crear un gráfico de barras
def create_bar_chart(df, x_col, y_col, title, x_label, y_label):
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=500
    )
    return fig

# Función para crear un gráfico de líneas
def create_line_chart(df, x_col, y_col, title, x_label, y_label):
    fig = px.line(df, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=500
    )
    return fig

# Función para crear un gráfico circular
def create_pie_chart(df, names_col, values_col, title):
    fig = px.pie(df, names=names_col, values=values_col, title=title)
    fig.update_layout(height=500)
    return fig

# Función para mostrar información en un cuadro
def info_box(title, content):
    st.markdown(f"""
    <div class="info-box">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

# Función para mostrar advertencia en un cuadro
def warning_box(title, content):
    st.markdown(f"""
    <div class="warning-box">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

# Función para mostrar éxito en un cuadro
def success_box(title, content):
    st.markdown(f"""
    <div class="success-box">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

# Función principal para la aplicación
def main():
    # Barra lateral con navegación
    st.sidebar.markdown("# Auditoría de Facturas")
    menu = st.sidebar.selectbox(
        "Seleccione una sección",
        ["Inicio", "Importación de Datos", "Facturas en Papel", "Anotación en RCF", 
         "Contenido de Facturas", "Tramitación", "Generación de Informes"]
    )
    
    # Mostrar la sección seleccionada
    if menu == "Inicio":
        show_home()
    elif menu == "Importación de Datos":
        show_importacion_datos()
    elif menu == "Facturas en Papel":
        show_facturas_papel()
    elif menu == "Anotación en RCF":
        show_anotacion_rcf()
    elif menu == "Contenido de Facturas":
        show_contenido_facturas()
    elif menu == "Tramitación":
        show_tramitacion()
    elif menu == "Generación de Informes":
        show_generacion_informes()

# Función para mostrar la página de inicio
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
        st.metric(label="Total Facturas", value="0")
    
    with col2:
        st.metric(label="Facturas Electrónicas", value="0")
    
    with col3:
        st.metric(label="Facturas en Papel", value="0")
    
    with col4:
        st.metric(label="Tiempo Medio Tramitación", value="0 días")
    
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
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_bar_chart(df_estados, 'Estado', 'Cantidad', 
                                         'Facturas por Estado', 'Estado', 'Cantidad'), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_line_chart(df_tiempos, 'Mes', 'Tiempo Medio (días)', 
                                          'Evolución de Tiempos de Tramitación', 'Mes', 'Tiempo Medio (días)'), use_container_width=True)
    
    # Mostrar accesos rápidos
    st.markdown('<h2 class="section-header">Accesos Rápidos</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Importar Datos", use_container_width=True):
            st.session_state.menu = "Importación de Datos"
            st.rerun()

    
    with col2:
        if st.button("📊 Ver Informes", use_container_width=True):
            st.session_state.menu = "Generación de Informes"
            st.rerun()

    
    with col3:
        if st.button("📝 Auditar Facturas en Papel", use_container_width=True):
            st.session_state.menu = "Facturas en Papel"
            st.rerun()


# Función para mostrar la página de importación de datos
def show_importacion_datos():
    st.markdown('<h1 class="main-header">Importación de Datos</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite importar datos desde diferentes plataformas de facturación electrónica como FACe, AOC o Biskaiticc."
    )
    
    # Crear pestañas para diferentes tipos de importación
    tab1, tab2, tab3, tab4 = st.tabs([
        "Facturas presentadas en plataforma", 
        "Facturas pendientes de descargar", 
        "Solicitudes de anulación",
        "Histórico de estados"
    ])
    
    with tab1:
        st.markdown('<h2 class="subsection-header">Importar facturas presentadas en plataforma</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            plataforma = st.selectbox(
                "Seleccione la plataforma",
                ["FACe", "AOC", "Biskaiticc", "Otra"],
                key="plataforma_facturas"
            )
        
        with col2:
            fecha = st.date_input(
                "Fecha de importación",
                datetime.now(),
                key="fecha_facturas"
            )
        
        uploaded_file = st.file_uploader("Seleccione el archivo de facturas (Excel o CSV)", type=["xlsx", "csv"], key="file_facturas")
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("Vista previa de los datos:")
                st.dataframe(df.head())
                
                if st.button("Procesar facturas", key="procesar_facturas"):
                    success_box(
                        "Procesamiento exitoso",
                        f"Se han procesado {len(df)} facturas correctamente."
                    )
            except Exception as e:
                warning_box(
                    "Error al procesar el archivo",
                    f"Se ha producido un error: {str(e)}"
                )
    
    with tab2:
        st.markdown('<h2 class="subsection-header">Facturas pendientes de descargar</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            plataforma = st.selectbox(
                "Seleccione la plataforma",
                ["FACe", "AOC", "Biskaiticc", "Otra"],
                key="plataforma_pendientes"
            )
        
        with col2:
            fecha = st.date_input(
                "Fecha de consulta",
                datetime.now(),
                key="fecha_pendientes"
            )
        
        if st.button("Consultar facturas pendientes", key="consultar_pendientes"):
            # Aquí se simularía la consulta a la plataforma
            # Mostramos datos de ejemplo
            df_pendientes = pd.DataFrame({
                "Número Factura": ["F2025-001", "F2025-002", "F2025-003"],
                "NIF Emisor": ["B12345678", "A87654321", "B11223344"],
                "Razón Social": ["Empresa A, S.L.", "Empresa B, S.A.", "Empresa C, S.L."],
                "Fecha Emisión": ["01/04/2025", "02/04/2025", "03/04/2025"],
                "Importe": [1000.00, 2500.50, 750.25],
                "Estado": ["Registrada", "Registrada", "Registrada"]
            })
            
            st.write("Facturas pendientes de descargar:")
            st.dataframe(df_pendientes)
            
            st.markdown(download_excel(df_pendientes, "facturas_pendientes"), unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<h2 class="subsection-header">Importar solicitudes de anulación</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            plataforma = st.selectbox(
                "Seleccione la plataforma",
                ["FACe", "AOC", "Biskaiticc", "Otra"],
                key="plataforma_anulacion"
            )
        
        with col2:
            fecha = st.date_input(
                "Fecha de importación",
                datetime.now(),
                key="fecha_anulacion"
            )
        
        uploaded_file = st.file_uploader("Seleccione el archivo de solicitudes (Excel o CSV)", type=["xlsx", "csv"], key="file_anulacion")
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("Vista previa de los datos:")
                st.dataframe(df.head())
                
                if st.button("Procesar solicitudes", key="procesar_anulacion"):
                    success_box(
                        "Procesamiento exitoso",
                        f"Se han procesado {len(df)} solicitudes de anulación correctamente."
                    )
            except Exception as e:
                warning_box(
                    "Error al procesar el archivo",
                    f"Se ha producido un error: {str(e)}"
                )
    
    with tab4:
        st.markdown('<h2 class="subsection-header">Importar histórico de estados</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            plataforma = st.selectbox(
                "Seleccione la plataforma",
                ["FACe", "AOC", "Biskaiticc", "Otra"],
                key="plataforma_historico"
            )
        
        with col2:
            fecha = st.date_input(
                "Fecha de importación",
                datetime.now(),
                key="fecha_historico"
            )
        
        uploaded_file = st.file_uploader("Seleccione el archivo de histórico (Excel o CSV)", type=["xlsx", "csv"], key="file_historico")
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("Vista previa de los datos:")
                st.dataframe(df.head())
                
                if st.button("Procesar histórico", key="procesar_historico"):
                    success_box(
                        "Procesamiento exitoso",
                        f"Se han procesado {len(df)} registros de histórico correctamente."
                    )
            except Exception as e:
                warning_box(
                    "Error al procesar el archivo",
                    f"Se ha producido un error: {str(e)}"
                )

# Función para mostrar la página de facturas en papel
def show_facturas_papel():
    st.markdown('<h1 class="main-header">Auditoría de Facturas en Papel</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar el cumplimiento de la obligatoriedad de factura electrónica establecida en el artículo 4 de la Ley 25/2013."
    )
    
    # Selector de fecha y botón de actualización
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        fecha_tipo = st.selectbox(
            "Seleccionar fecha",
            ["Fecha actual", "Datos históricos"],
            key="fecha_tipo_papel"
        )
    
    with col2:
        if st.button("Actualizar datos", key="actualizar_papel"):
            st.session_state.datos_actualizados_papel = True
    
    with col3:
        st.markdown('<div style="text-align: right;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: 05/04/2025</span></div>', unsafe_allow_html=True)
    
    # Crear pestañas para diferentes análisis
    tab1, tab2, tab3 = st.tabs([
        "Facturas en papel que incumplen la normativa", 
        "Evolución mensual de facturas en papel", 
        "Proveedores con mayor número de facturas en papel"
    ])
    
    with tab1:
        # Datos de ejemplo para facturas en papel
        df_papel = pd.DataFrame({
            "Número Factura": ["P2025-001", "P2025-002", "P2025-003"],
            "NIF Emisor": ["B12345678", "A87654321", "B11223344"],
            "Razón Social": ["Empresa A, S.L.", "Empresa B, S.A.", "Empresa C, S.L."],
            "Fecha Emisión": ["01/04/2025", "02/04/2025", "03/04/2025"],
            "Importe": [1000.00, 2500.50, 750.25],
            "Requisito Incumplido": ["Obligado a facturación electrónica", "Obligado a facturación electrónica", "Obligado a facturación electrónica"]
        })
        
        st.write("Facturas en papel que incumplen la normativa:")
        st.dataframe(df_papel)
        
        st.markdown(download_excel(df_papel, "facturas_papel_incumplen"), unsafe_allow_html=True)
    
    with tab2:
        # Datos de ejemplo para evolución mensual
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril']
        cantidades = [10, 8, 5, 3]
        porcentajes = [5.0, 4.0, 2.5, 1.5]
        df_evolucion = pd.DataFrame({
            'Mes': meses, 
            'Cantidad': cantidades,
            'Porcentaje': porcentajes
        })
        
        st.plotly_chart(create_bar_chart(df_evolucion, 'Mes', 'Cantidad', 
                                         'Evolución mensual de facturas en papel', 'Mes', 'Cantidad'), use_container_width=True)
        
        st.dataframe(df_evolucion)
        
        st.markdown(download_excel(df_evolucion, "evolucion_facturas_papel"), unsafe_allow_html=True)
    
    with tab3:
        # Datos de ejemplo para proveedores
        df_proveedores = pd.DataFrame({
            "NIF Emisor": ["B12345678", "A87654321", "B11223344"],
            "Razón Social": ["Empresa A, S.L.", "Empresa B, S.A.", "Empresa C, S.L."],
            "Número de Facturas": [5, 3, 2],
            "Importe Total": [5000.00, 7500.50, 1500.25],
            "Porcentaje": [50.0, 30.0, 20.0]
        })
        
        st.write("Proveedores con mayor número de facturas en papel:")
        st.dataframe(df_proveedores)
        
        st.plotly_chart(create_pie_chart(df_proveedores, 'Razón Social', 'Número de Facturas', 
                                         'Distribución de facturas en papel por proveedor'), use_container_width=True)
        
        st.markdown(download_excel(df_proveedores, "proveedores_facturas_papel"), unsafe_allow_html=True)

# Función para mostrar la página de anotación en RCF
def show_anotacion_rcf():
    st.markdown('<h1 class="main-header">Auditoría de Anotación en RCF</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar la correcta anotación de las facturas en el Registro Contable de Facturas."
    )
    
    # Selector de fecha y botón de actualización
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        fecha_tipo = st.selectbox(
            "Seleccionar fecha",
            ["Fecha actual", "Datos históricos"],
            key="fecha_tipo_rcf"
        )
    
    with col2:
        if st.button("Actualizar datos", key="actualizar_rcf"):
            st.session_state.datos_actualizados_rcf = True
    
    with col3:
        st.markdown('<div style="text-align: right;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: 05/04/2025</span></div>', unsafe_allow_html=True)
    
    # Crear pestañas para diferentes análisis
    tab1, tab2, tab3 = st.tabs([
        "Custodia de facturas", 
        "Tiempos medios de anotación", 
        "Facturas no anotadas en RCF"
    ])
    
    with tab1:
        # Datos de ejemplo para custodia
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(label="Total facturas", value="100")
            st.metric(label="Facturas comprobadas", value="20")
        
        with col2:
            st.metric(label="Facturas con errores", value="0")
            st.metric(label="Porcentaje de errores", value="0%")
        
        success_box(
            "Resultado de la auditoría de custodia",
            "No se han detectado errores en la custodia de facturas. Se cumple correctamente con la normativa."
        )
    
    with tab2:
        # Datos de ejemplo para tiempos medios
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril']
        tiempos_medios = [120, 100, 90, 80]
        tiempos_minimos = [30, 25, 20, 15]
        tiempos_maximos = [240, 210, 180, 150]
        df_tiempos = pd.DataFrame({
            'Mes': meses, 
            'Tiempo Medio (minutos)': tiempos_medios,
            'Tiempo Mínimo (minutos)': tiempos_minimos,
            'Tiempo Máximo (minutos)': tiempos_maximos
        })
        
        st.plotly_chart(create_line_chart(df_tiempos, 'Mes', 'Tiempo Medio (minutos)', 
                                          'Evolución de tiempos medios de anotación', 'Mes', 'Tiempo Medio (minutos)'), use_container_width=True)
        
        st.dataframe(df_tiempos)
        
        st.markdown(download_excel(df_tiempos, "tiempos_anotacion"), unsafe_allow_html=True)
    
    with tab3:
        # Datos de ejemplo para facturas no anotadas
        df_no_anotadas = pd.DataFrame({
            "Número Factura": ["F2025-004", "F2025-005"],
            "NIF Emisor": ["B12345678", "A87654321"],
            "Razón Social": ["Empresa A, S.L.", "Empresa B, S.A."],
            "Fecha Emisión": ["04/04/2025", "05/04/2025"],
            "Importe": [1200.00, 3500.50],
            "Fecha Registro FACe": ["04/04/2025", "05/04/2025"],
            "Días Pendientes": [1, 0]
        })
        
        st.write("Facturas registradas en FACe pero no anotadas en RCF:")
        st.dataframe(df_no_anotadas)
        
        st.markdown(download_excel(df_no_anotadas, "facturas_no_anotadas"), unsafe_allow_html=True)

# Función para mostrar la página de contenido de facturas
def show_contenido_facturas():
    st.markdown('<h1 class="main-header">Auditoría del Contenido de Facturas</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar el cumplimiento de las validaciones establecidas por la Orden HAP/1650/2015 y analizar los motivos de rechazo de facturas."
    )
    
    # Selector de fecha y botón de actualización
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        fecha_tipo = st.selectbox(
            "Seleccionar fecha",
            ["Fecha actual", "Datos históricos"],
            key="fecha_tipo_contenido"
        )
    
    with col2:
        if st.button("Actualizar datos", key="actualizar_contenido"):
            st.session_state.datos_actualizados_contenido = True
    
    with col3:
        st.markdown('<div style="text-align: right;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: 05/04/2025</span></div>', unsafe_allow_html=True)
    
    # Validaciones de la Orden HAP/1650/2015
    st.markdown('<h2 class="section-header">Validaciones de la Orden HAP/1650/2015</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para validaciones
    df_validaciones = pd.DataFrame({
        "Validación": ["Validación de formato Facturae", "Validación de firma electrónica", "Validación de NIF emisor", "Validación de códigos DIR3"],
        "Nº facturas": [0, 0, 0, 0],
        "Porcentaje": [0.0, 0.0, 0.0, 0.0]
    })
    
    st.dataframe(df_validaciones)
    
    st.markdown(download_excel(df_validaciones, "validaciones_facturas"), unsafe_allow_html=True)
    
    # Facturas rechazadas por motivo
    st.markdown('<h2 class="section-header">Facturas rechazadas por motivo</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para rechazos
    df_rechazos = pd.DataFrame({
        "Motivo": ["Duplicidad", "Órgano gestor incorrecto", "Datos incompletos", "Otros motivos"],
        "Nº facturas": [0, 0, 0, 0],
        "Porcentaje": [0.0, 0.0, 0.0, 0.0]
    })
    
    st.dataframe(df_rechazos)
    
    st.plotly_chart(create_pie_chart(df_rechazos, 'Motivo', 'Nº facturas', 
                                     'Distribución de facturas rechazadas por motivo'), use_container_width=True)
    
    st.markdown(download_excel(df_rechazos, "rechazos_facturas"), unsafe_allow_html=True)
    
    # Detalle de facturas rechazadas
    st.markdown('<h2 class="section-header">Detalle de facturas rechazadas</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para detalle de rechazos
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
    
    # Proveedores con mayor número de rechazos
    st.markdown('<h2 class="section-header">Proveedores con mayor número de rechazos</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para proveedores con rechazos
    df_proveedores_rechazos = pd.DataFrame({
        "CIF Proveedor": [],
        "Razón Social": [],
        "Nº facturas rechazadas": [],
        "Porcentaje sobre total rechazos": []
    })
    
    if df_proveedores_rechazos.empty:
        st.write("No hay datos disponibles")
    else:
        st.dataframe(df_proveedores_rechazos)
        st.markdown(download_excel(df_proveedores_rechazos, "proveedores_rechazos"), unsafe_allow_html=True)

# Función para mostrar la página de tramitación
def show_tramitacion():
    st.markdown('<h1 class="main-header">Auditoría de Tramitación</h1>', unsafe_allow_html=True)
    
    info_box(
        "Información",
        "Esta sección permite verificar la correcta tramitación de las facturas y analizar los tiempos medios de tramitación."
    )
    
    # Selector de fecha y botón de actualización
    col1, col2, col3 = st.columns([2, 2, 3])
    
    with col1:
        fecha_tipo = st.selectbox(
            "Seleccionar fecha",
            ["Fecha actual", "Datos históricos"],
            key="fecha_tipo_tramitacion"
        )
    
    with col2:
        if st.button("Actualizar datos", key="actualizar_tramitacion"):
            st.session_state.datos_actualizados_tramitacion = True
    
    with col3:
        st.markdown('<div style="text-align: right;"><span style="background-color: #E5E7EB; padding: 0.5rem; border-radius: 0.5rem; font-size: 0.9rem;">Última actualización: 05/04/2025</span></div>', unsafe_allow_html=True)
    
    # Comparativa de solicitudes de anulación
    st.markdown('<h2 class="section-header">Comparativa de solicitudes de anulación</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para solicitudes de anulación
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
    
    # Tiempos medios de tramitación
    st.markdown('<h2 class="section-header">Tiempos medios de tramitación</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para tiempos de tramitación
    df_tiempos_tramitacion = pd.DataFrame({
        "Estado": ["Registrada", "Contabilizada", "Conformada", "Pagada"],
        "Tiempo medio en FACe (días)": [1, 5, 10, 20],
        "Tiempo medio en RCF (días)": [1, 4, 8, 18],
        "Diferencia (días)": [0, 1, 2, 2]
    })
    
    st.dataframe(df_tiempos_tramitacion)
    
    # Crear gráfico de barras agrupadas
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
    
    # Evolución mensual de tiempos de tramitación
    st.markdown('<h2 class="section-header">Evolución mensual de tiempos de tramitación</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para evolución mensual
    df_evolucion_tiempos = pd.DataFrame({
        "Mes": ["Enero", "Febrero", "Marzo", "Abril"],
        "Tiempo medio hasta contabilización (días)": [4, 3, 3, 2],
        "Tiempo medio hasta conformidad (días)": [8, 7, 6, 5],
        "Tiempo medio hasta pago (días)": [20, 18, 16, 15]
    })
    
    st.dataframe(df_evolucion_tiempos)
    
    # Crear gráfico de líneas múltiples
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_evolucion_tiempos['Mes'],
        y=df_evolucion_tiempos['Tiempo medio hasta contabilización (días)'],
        name='Contabilización',
        mode='lines+markers',
        marker_color='#3B82F6'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_evolucion_tiempos['Mes'],
        y=df_evolucion_tiempos['Tiempo medio hasta conformidad (días)'],
        name='Conformidad',
        mode='lines+markers',
        marker_color='#10B981'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_evolucion_tiempos['Mes'],
        y=df_evolucion_tiempos['Tiempo medio hasta pago (días)'],
        name='Pago',
        mode='lines+markers',
        marker_color='#F59E0B'
    ))
    
    fig.update_layout(
        title='Evolución mensual de tiempos de tramitación',
        xaxis_title='Mes',
        yaxis_title='Tiempo medio (días)',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(download_excel(df_evolucion_tiempos, "evolucion_tiempos_tramitacion"), unsafe_allow_html=True)
    
    # Facturas con mayor tiempo de tramitación
    st.markdown('<h2 class="section-header">Facturas con mayor tiempo de tramitación</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para facturas con mayor tiempo
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

# Función para mostrar la página de generación de informes
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
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 1</h3>
            <p style="text-align: center; color: #6B7280;">Informe básico</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Incluye información básica sobre la auditoría de facturas electrónicas.</p>
            <div style="display: flex; justify-content: center; gap: 0.5rem; margin-top: 1rem;">
                <button style="background-color: #F3F4F6; border: 1px solid #D1D5DB; border-radius: 0.25rem; padding: 0.5rem 1rem; cursor: pointer;">Ver plantilla</button>
                <button style="background-color: #2563EB; color: white; border: none; border-radius: 0.25rem; padding: 0.5rem 1rem; cursor: pointer;">Generar</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 2</h3>
            <p style="text-align: center; color: #6B7280;">Informe detallado</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Incluye información detallada sobre la auditoría con análisis estadísticos.</p>
            <div style="display: flex; justify-content: center; gap: 0.5rem; margin-top: 1rem;">
                <button style="background-color: #F3F4F6; border: 1px solid #D1D5DB; border-radius: 0.25rem; padding: 0.5rem 1rem; cursor: pointer;">Ver plantilla</button>
                <button style="background-color: #2563EB; color: white; border: none; border-radius: 0.25rem; padding: 0.5rem 1rem; cursor: pointer;">Generar</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="border: 1px solid #E5E7EB; border-radius: 0.5rem; padding: 1rem; height: 100%;">
            <h3 style="text-align: center;">Modelo 3</h3>
            <p style="text-align: center; color: #6B7280;">Informe completo</p>
            <p style="text-align: center; font-size: 0.8rem; color: #6B7280;">Incluye información exhaustiva con anexos y documentación adicional.</p>
            <div style="display: flex; justify-content: center; gap: 0.5rem; margin-top: 1rem;">
                <button style="background-color: #F3F4F6; border: 1px solid #D1D5DB; border-radius: 0.25rem; padding: 0.5rem 1rem; cursor: pointer;">Ver plantilla</button>
                <button style="background-color: #2563EB; color: white; border: none; border-radius: 0.25rem; padding: 0.5rem 1rem; cursor: pointer;">Generar</button>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Generar nuevo informe
    st.markdown('<h2 class="section-header">Generar nuevo informe</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        entidad = st.text_input("Entidad", "")
    
    with col2:
        periodo = st.selectbox(
            "Período auditado",
            ["Año actual", "Año anterior", "Personalizado"]
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        nombre_informe = st.text_input("Nombre del informe", "")
    
    with col2:
        modelo_informe = st.selectbox(
            "Modelo de informe",
            ["Modelo 1 - Básico", "Modelo 2 - Detallado", "Modelo 3 - Completo"]
        )
    
    notas = st.text_input("Notas adicionales", "")
    
    if st.button("Generar informe", key="generar_informe"):
        if not entidad or not nombre_informe:
            warning_box(
                "Campos incompletos",
                "Por favor, complete los campos obligatorios: Entidad y Nombre del informe."
            )
        else:
            success_box(
                "Informe generado correctamente",
                f"Se ha generado el informe '{nombre_informe}' con el modelo {modelo_informe}."
            )
    
    # Consulta de documentos almacenados
    st.markdown('<h2 class="section-header">Consulta de documentos de auditoría almacenados</h2>', unsafe_allow_html=True)
    
    # Datos de ejemplo para informes almacenados
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

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
