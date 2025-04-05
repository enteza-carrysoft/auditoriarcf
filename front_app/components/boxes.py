# components/boxes.py

import streamlit as st

def info_box(title, content):
    st.markdown(f"""
    <div class="info-box">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def warning_box(title, content):
    st.markdown(f"""
    <div class="warning-box">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)

def success_box(title, content):
    st.markdown(f"""
    <div class="success-box">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)
