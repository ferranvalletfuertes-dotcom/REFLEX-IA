import streamlit as st
from motor import inicializar_estados
from vistas import render_login, render_escaner

st.set_page_config(page_title="REFLEX AI", page_icon="🔴", layout="wide")

inicializar_estados()

if st.session_state.usuario_id is None:
    render_login()
else:
    render_escaner()
