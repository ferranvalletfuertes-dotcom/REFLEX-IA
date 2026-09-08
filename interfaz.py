import streamlit as st

def cargar_css(tema):
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@700&family=Inter:wght@400;500;600&display=swap');

    /* Fondo Vivo que Respira y Tipografía Global Segura */
    .stApp {
        background: linear-gradient(-45deg, #050505, #140808, #0a0a0c, #081014);
        background-size: 400% 400%;
        animation: respiracion 15s ease infinite;
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    @keyframes respiracion {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Contenedores de Cristal */
    div[data-testid="stContainer"] {
        background: rgba(20, 20, 25, 0.4) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
    }

    /* Títulos Premium */
    h1, h2, h3 { 
        font-family: 'Space Grotesk', sans-serif !important; 
        color: #ffffff !important; 
        letter-spacing: -0.5px; 
    }

    /* Inputs Elegantes */
    input, textarea, div[data-baseweb="select"] > div {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
    }
    input:focus, textarea:focus { 
        border-color: #ffffff !important; 
        background-color: rgba(255, 255, 255, 0.05) !important;
    }

    /* Botones de Acción (Sin alterar el interior del botón para salvar los iconos) */
    button[data-testid="baseButton-secondary"],
    button[data-testid="baseButton-primary"] {
        background-color: #f4f4f5 !important;
        color: #09090b !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
    }
    button[data-testid="baseButton-secondary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        transform: scale(1.02) !important;
        background-color: #ffffff !important;
    }

    /* Efecto de Luz Fluida en el Logo */
    .logo-animado {
        background: linear-gradient(90deg, #555 0%, #fff 50%, #555 100%);
        background-size: 200% auto;
        color: transparent;
        background-clip: text;
        -webkit-background-clip: text;
        animation: brillo_espejo 4s linear infinite;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.2rem;
        font-weight: 700;
        letter-spacing: -2px;
        display: inline-block;
    }
    
    @keyframes brillo_espejo {
        to { background-position: 200% center; }
    }
    </style>
    """, unsafe_allow_html=True)

def renderizar_logo(centrado=False):
    alineacion = "center" if centrado else "flex-start"
    tamaño_texto = "3.2rem" if centrado else "1.8rem"
    tamaño_logo = "55" if centrado else "38"
    
    html_blindado = f"<div style='display: flex; align-items: center; justify-content: {alineacion}; margin-bottom: 25px;'><svg width='{tamaño_logo}' height='{tamaño_logo}' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg' style='margin-right: 15px; flex-shrink: 0; filter: drop-shadow(0 8px 16px rgba(0,0,0,0.5));'><rect x='10' y='10' width='80' height='80' rx='24' fill='#0a0a0c' stroke='#25252b' stroke-width='4'/><path d='M25 50 H 75 M 50 25 V 75' stroke='#1f1f23' stroke-width='4' stroke-linecap='round'/><circle cx='50' cy='50' r='18' fill='#050505' stroke='#ffffff' stroke-width='6'/><circle cx='50' cy='50' r='6' fill='#ff2a2a' style='filter: drop-shadow(0 0 10px rgba(255,42,42,1));'/></svg><span class='logo-animado' style='font-size: {tamaño_texto}; line-height: 1;'>REFLEX</span></div>"
    
    st.markdown(html_blindado, unsafe_allow_html=True)