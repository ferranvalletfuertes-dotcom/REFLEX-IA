import streamlit as st
from interfaz import cargar_css, renderizar_logo
from motor import inicializar_estados
from vistas import render_login, render_escaner

st.set_page_config(page_title="REFLEX AI", layout="wide", initial_sidebar_state="collapsed")

inicializar_estados()
cargar_css(st.session_state.tema)

# 1. BARRERA DE SEGURIDAD
if not st.session_state.usuario_id:
    renderizar_logo(centrado=True)
    render_login()

# 2. LA MATRIZ AISLADA (Un solo jugador)
else:
    nav1, nav2, nav3 = st.columns([8, 1, 1])
    with nav1: renderizar_logo(centrado=False)
    with nav2:
        if st.button("Cerrar Sesión", use_container_width=True): 
            st.session_state.usuario_id = None
            st.rerun()
    with nav3:
        modo = st.toggle("🌙", value=(st.session_state.tema == "oscuro"), label_visibility="collapsed")
        if modo and st.session_state.tema == "blanco": st.session_state.tema = "oscuro"; st.rerun()
        elif not modo and st.session_state.tema == "oscuro": st.session_state.tema = "blanco"; st.rerun()
    
    st.markdown("<hr style='margin-top: 0; border-color: #333;'>", unsafe_allow_html=True)
    
    render_escaner()