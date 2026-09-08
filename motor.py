import os
import streamlit as st
from supabase import create_client
import google.generativeai as genai

def inicializar_estados():
    if 'supabase' not in st.session_state:
        url = os.environ.get("SUPABASE_URL") or st.secrets["SUPABASE_URL"]
        key = os.environ.get("SUPABASE_KEY") or st.secrets["SUPABASE_KEY"]
        st.session_state.supabase = create_client(url, key)

    if 'gemini_configurado' not in st.session_state:
        GEMINI_KEY = os.environ.get("GEMINI_KEY") or st.secrets["GEMINI_KEY"]
        genai.configure(api_key=GEMINI_KEY)
        st.session_state.gemini_configurado = True

    if 'usuario_id' not in st.session_state: 
        st.session_state.usuario_id = None
        
    if 'tema' not in st.session_state: 
        st.session_state.tema = "oscuro"
