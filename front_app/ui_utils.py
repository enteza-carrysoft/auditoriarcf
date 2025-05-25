import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import base64

# Función para descargar datos como Excel
def download_excel(df, filename):
    output = io.BytesIO()
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
