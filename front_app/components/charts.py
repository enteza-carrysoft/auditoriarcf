# components/charts.py

import plotly.express as px
import plotly.graph_objects as go

def create_bar_chart(df, x_col, y_col, title, x_label, y_label):
    fig = px.bar(df, x=x_col, y=y_col, title=title)
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, height=500)
    return fig

def create_line_chart(df, x_col, y_col, title, x_label, y_label):
    fig = px.line(df, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, height=500)
    return fig

def create_pie_chart(df, names_col, values_col, title):
    fig = px.pie(df, names=names_col, values=values_col, title=title)
    fig.update_layout(height=500)
    return fig
