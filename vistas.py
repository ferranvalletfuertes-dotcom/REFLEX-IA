import os
import streamlit as st
from PIL import Image
import io
import base64
import uuid
import json
import re
import requests
import time
from gtts import gTTS

# ==========================================
# 1. LANDING PAGE Y ACCESO (EMAIL / CONTRASEÑA)
# ==========================================
def render_login():
    st.markdown("""
    <style>
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    .landing-container { max-width: 800px; margin: 0 auto; padding: 2rem 1rem; font-family: 'Inter', sans-serif; }
    .hero-section { text-align: center; padding: 4rem 1rem; animation: fadeInUp 1s ease-out; }
    .hero-title { font-size: 3.5rem; font-weight: 800; background: linear-gradient(135deg, #ffffff 0%, #ff2a2a 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; }
    .hero-subtitle { color: #888; font-size: 1.2rem; margin-bottom: 2rem; }
    .scroll-card { background: linear-gradient(135deg, #0a0a0c 0%, #16161d 100%); border: 1px solid rgba(255, 42, 42, 0.2); border-radius: 16px; padding: 2.5rem; margin: 3rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.8); animation: fadeInUp 0.8s ease-out; transition: transform 0.3s ease; }
    .scroll-card:hover { border-color: rgba(255, 42, 42, 0.6); transform: translateY(-5px); }
    .card-title { color: #ff2a2a; font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 1px; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="landing-container">
        <div class="hero-section">
            <h1 class="hero-title">REFLEX AI</h1>
            <p class="hero-subtitle">El sistema definitivo de diagnóstico psicológico, conductual y de optimización implacable.</p>
        </div>
        <div class="scroll-card">
            <div class="card-title">⚡ ¿Qué es este sistema?</div>
            <p style="color: #ddd; line-height: 1.6;">REFLEX AI no es un chatbot de autoayuda común. Es una herramienta de ingeniería de conducta diseñada para erradicar bloqueos mentales y destrozar excusas.</p>
        </div>
        <div style="background: rgba(255, 42, 42, 0.05); border: 1px solid rgba(255, 42, 42, 0.3); border-radius: 8px; padding: 15px; text-align: justify; font-size: 0.75rem; color: #888; font-family: 'Inter', sans-serif; margin-bottom: 2rem;">
            <strong style="color: #ff2a2a;">TÉRMINOS DE USO Y EXENCIÓN DE RESPONSABILIDAD:</strong> REFLEX AI es una herramienta diseñada exclusivamente con fines de entretenimiento y auto-reflexión. NO constituye asesoramiento médico, psicológico, financiero ni profesional.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    with col_centro:
        with st.container(border=True):
            tab1, tab2 = st.tabs(["Iniciar Sesión", "Crear Cuenta"])
            with tab1:
                email = st.text_input("Email", key="log_email")
                pwd = st.text_input("Contraseña", type="password", key="log_pwd")
                if st.button("ENTRAR AL ESCÁNER", use_container_width=True):
                    try:
                        resp = st.session_state.supabase.auth.sign_in_with_password({"email": email, "password": pwd})
                        if resp.user:
                            st.session_state.usuario_id = resp.user.id
                            st.rerun()
                    except Exception as e:
                        st.error(f"Fallo: {e}")
            with tab2:
                reg_email = st.text_input("Email", key="reg_email")
                reg_pwd = st.text_input("Contraseña (Min 6)", type="password", key="reg_pwd")
                if st.button("FORJAR IDENTIDAD", use_container_width=True):
                    try:
                        resp = st.session_state.supabase.auth.sign_up({"email": reg_email, "password": reg_pwd})
                        if resp.user:
                            st.session_state.usuario_id = resp.user.id
                            st.rerun()
                    except Exception as e:
                        st.error(f"Fallo: {e}")

# ==========================================
# 2. PERSISTENCIA Y PROTOCOLO ANTI-BASURA
# ==========================================
def cargar_db():
    if "db_cargada" not in st.session_state:
        try:
            resp = st.session_state.supabase.table("chats_memoria").select("*").eq("usuario_id", st.session_state.usuario_id).execute()
            chats_utiles = []
            for fila in resp.data:
                if fila.get('mensajes') and len(fila['mensajes']) > 0:
                    chats_utiles.append(fila)
                else:
                    try: st.session_state.supabase.table("chats_memoria").delete().eq("id", fila['id']).execute()
                    except: pass
            
            st.session_state.chats_guardados = {fila['id']: fila['mensajes'] for fila in chats_utiles}
            st.session_state.chat_meta = {fila['id']: fila['meta'] for fila in chats_utiles}
            st.session_state.evidencias_guardadas = {fila['id']: None for fila in chats_utiles}
            st.session_state.chat_actual = chats_utiles[0]['id'] if chats_utiles else "default"
            
            if not chats_utiles:
                st.session_state.chats_guardados["default"] = []
                st.session_state.chat_meta["default"] = {"rol": "un juez implacable", "brutalidad": 7, "privacidad": False, "tono": "Intermedio (Claro)"}
                st.session_state.evidencias_guardadas["default"] = None
        except Exception as e:
            st.error(f"Fallo al conectar con la bóveda de datos: {e}")
        st.session_state.db_cargada = True

    if "compartir_datos" not in st.session_state:
        try:
            usuario = st.session_state.supabase.auth.get_user().user
            st.session_state.compartir_datos = usuario.user_metadata.get("compartir_datos", False)
        except:
            st.session_state.compartir_datos = False

def sincronizar_db(chat_id):
    if chat_id != "default":
        mensajes_actuales = st.session_state.chats_guardados.get(chat_id, [])
        if len(mensajes_actuales) > 0:
            meta_actualizada = st.session_state.chat_meta[chat_id].copy()
            meta_actualizada["privacidad_compartida"] = st.session_state.compartir_datos
            datos = {"id": chat_id, "usuario_id": st.session_state.usuario_id, "meta": meta_actualizada, "mensajes": mensajes_actuales}
            try: st.session_state.supabase.table("chats_memoria").upsert(datos).execute()
            except Exception as e: st.error(f"Error de sincronización: {e}")

def borrar_chat(chat_id):
    try: st.session_state.supabase.table("chats_memoria").delete().eq("id", chat_id).eq("usuario_id", st.session_state.usuario_id).execute()
    except Exception as e: st.error(f"Fallo de Supabase: {e}")
    if chat_id in st.session_state.chats_guardados: del st.session_state.chats_guardados[chat_id]
    if chat_id in st.session_state.chat_meta: del st.session_state.chat_meta[chat_id]
    if chat_id in st.session_state.evidencias_guardadas: del st.session_state.evidencias_guardadas[chat_id]
    
    chats_restantes = list(st.session_state.chats_guardados.keys())
    st.session_state.chat_actual = chats_restantes[0] if chats_restantes else "default"
    if not chats_restantes:
        st.session_state.chats_guardados["default"] = []
        st.session_state.chat_meta["default"] = {"rol": "un juez implacable", "brutalidad": 7, "privacidad": False, "tono": "Intermedio (Claro)"}
        st.session_state.evidencias_guardadas["default"] = None
    st.rerun()

# ==========================================
# 3. ESCÁNER NEURONAL Y GRÁFICOS
# ==========================================
def render_escaner():
    def guardar_privacidad():
        valor = st.session_state.checkbox_privacidad
        st.session_state.compartir_datos = valor
        try:
            st.session_state.supabase.auth.update_user({"data": {"compartir_datos": valor}})
            st.toast("Preferencia blindada.", icon="🔒")
        except: pass

    cargar_db()
    if not st.session_state.chats_guardados or st.session_state.chat_actual not in st.session_state.chats_guardados:
        chat_por_defecto = "Análisis Inicial"
        st.session_state.chats_guardados[chat_por_defecto] = []
        st.session_state.chat_meta[chat_por_defecto] = {"rol": "un juez implacable", "brutalidad": 7, "privacidad": False, "tono": "Intermedio (Claro)"}
        st.session_state.evidencias_guardadas[chat_por_defecto] = None
        st.session_state.chat_actual = chat_por_defecto

    svg_core = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect x="10" y="10" width="80" height="80" rx="24" fill="#0a0a0c" stroke="#25252b" stroke-width="4"/><path d="M25 50 H 75 M 50 25 V 75" stroke="#1f1f23" stroke-width="4" stroke-linecap="round"/><circle cx="50" cy="50" r="18" fill="#050505" stroke="#ffffff" stroke-width="6"/><circle cx="50" cy="50" r="6" fill="#ff2a2a"/></svg>"""
    avatar_ia = f"data:image/svg+xml;base64,{base64.b64encode(svg_core.encode('utf-8')).decode('utf-8')}"

    st.markdown("""
    <style>
    .stChatInputContainer textarea { background-color: transparent !important; border: none !important; color: white !important; padding-top: 15px !important; min-height: 120px !important; }
    .stChatInputContainer { border-radius: 12px !important; background-color: #1a1a21 !important; border: 1px solid #333 !important; padding: 5px !important; }
    .stChatInputContainer:focus-within { border-color: #ffffff !important; }
    [data-testid="stChatMessage"]:has(div:contains("👤")) { flex-direction: row-reverse; text-align: right; background-color: #16161d; border-radius: 15px 0px 15px 15px; padding: 1rem; }
    [data-testid="stChatMessage"]:has(img) { background-color: transparent; border-left: 2px solid #ffffff; padding: 1rem; }
    [data-testid="stChatMessage"] { animation: fadeIn 0.4s ease-out forwards; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
    [data-testid="stStatusWidget"] { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("<div style='text-align: center; margin-bottom: 25px; border-bottom: 1px solid rgba(255, 42, 42, 0.2);'><h2 style='color:#ff2a2a; margin:0;'>REFLEX</h2><h3 style='color:#666; font-size:0.9rem;'>A.I. SYSTEM</h3></div>", unsafe_allow_html=True)
        with st.expander("⚙️ Ajustes"):
            st.checkbox("Compartir datos", value=st.session_state.compartir_datos, key="checkbox_privacidad", on_change=guardar_privacidad)
        
        tono_actual = st.session_state.chat_meta[st.session_state.chat_actual].get("tono", "Intermedio (Claro)")
        nuevo_tono = st.select_slider("🎙️ Registro Lingüístico", options=["Colega (Directo)", "Intermedio (Claro)", "Implacable (Técnico)"], value=tono_actual)
        if nuevo_tono != tono_actual:
            st.session_state.chat_meta[st.session_state.chat_actual]["tono"] = nuevo_tono
            st.markdown("---")
            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.supabase.auth.sign_out()
                st.session_state.clear()
                st.rerun()

        st.markdown("### Memoria de Sesiones")
        if st.button("➕ Nuevo Análisis", use_container_width=True):
            nuevo_id = str(uuid.uuid4())[:8]
            st.session_state.chats_guardados[nuevo_id] = []
            st.session_state.evidencias_guardadas[nuevo_id] = None
            st.session_state.chat_meta[nuevo_id] = {"rol": "un juez implacable", "brutalidad": 7, "tono": "Intermedio (Claro)"}
            st.session_state.chat_actual = nuevo_id
            st.rerun()
            
        for chat_id in list(reversed(list(st.session_state.chats_guardados.keys()))):
            if chat_id != "default" and len(st.session_state.chats_guardados[chat_id]) > 0:
                rol_hist = st.session_state.chat_meta[chat_id].get("rol", "Análisis")[:12]
                col_btn, col_menu = st.columns([4, 1])
                with col_btn:
                    if st.button(f"▪️ {rol_hist}", key=f"btn_{chat_id}", use_container_width=True):
                        st.session_state.chat_actual = chat_id
                        st.rerun()
                with col_menu:
                    with st.popover("⋮"):
                        if st.button("🗑️ Borrar", key=f"del_{chat_id}"): borrar_chat(chat_id)

    mensajes_actuales = st.session_state.chats_guardados[st.session_state.chat_actual]
    evidencia_actual = st.session_state.evidencias_guardadas.get(st.session_state.chat_actual)

    if not mensajes_actuales:
        with st.container(border=True):
            diccionario_roles = {
                "Estilo & Outfits": "un juez de moda y proporciones físicas",
                "Conversión & Negocios": "un auditor técnico de CRO y copywriting",
                "Perfiles de Citas": "un analista de comportamiento social",
                "Físico & Postura": "un evaluador implacable de biomecánica",
                "Miedos & Inseguridades": "un analista psicológico letal"
            }
            rol_seleccionado = st.selectbox("Disciplina:", list(diccionario_roles.keys()))
            nivel_brutalidad = st.slider("Brutalidad", 1, 10, 7)
            archivo = st.file_uploader("Adjuntar archivo (Opcional)", type=["jpg", "png", "jpeg"])
            contexto = st.text_area("Contexto", placeholder="Ej: Me bloqueo en público...")
            
            if st.button("Ejecutar Diagnóstico", type="primary", use_container_width=True):
                if st.session_state.chat_actual == "default": st.warning("Crea una Nueva Sesión.")
                elif archivo is not None or contexto.strip() != "":
                    st.session_state.evidencias_guardadas[st.session_state.chat_actual] = archivo.getvalue() if archivo else None
                    st.session_state.chat_meta[st.session_state.chat_actual] = {"rol": diccionario_roles[rol_seleccionado], "brutalidad": nivel_brutalidad, "tono": "Intermedio (Claro)"}
                    st.session_state.chats_guardados[st.session_state.chat_actual].append({"role": "user", "content": contexto, "mostrar": contexto if contexto else "Análisis iniciado.", "avatar": "👤"})
                    sincronizar_db(st.session_state.chat_actual)
                    st.rerun()
                else: st.warning("Proporciona contexto o sube un archivo.")
    else:
        for i, msg in enumerate(mensajes_actuales):
            with st.chat_message(msg["role"], avatar=msg.get("avatar", avatar_ia)):
                texto_crudo = msg.get("mostrar", msg["content"])
                match_elo = re.search(r'\[ELO:\s*([0-9]+(?:\.[0-9]+)?)/10\]', texto_crudo, re.IGNORECASE)
                match_metricas = re.search(r'\[METRICAS:\s*(.+?)\]', texto_crudo, re.IGNORECASE)
                texto_limpio = re.sub(r'\[ELO:\s*[0-9]+(?:\.[0-9]+)?/10\]', '', texto_crudo, flags=re.IGNORECASE)
                texto_limpio = re.sub(r'\[METRICAS:\s*.+?\]', '', texto_limpio, flags=re.IGNORECASE).strip()
                
                st.markdown(texto_limpio)
                if i == 0 and evidencia_actual: st.image(evidencia_actual, width=200)
                
                if match_elo and msg["role"] == "assistant":
                    nota = match_elo.group(1)
                    html_barras = ""
                    if match_metricas:
                        for dato in match_metricas.group(1).split(','):
                            if '=' in dato:
                                nombre, valor = dato.split('=')
                                html_barras += f"<div style='margin-top: 12px; text-align: left;'><div style='display: flex; justify-content: space-between; font-size: 0.75rem; color: #aaa; font-family: \"Space Grotesk\", sans-serif;'><span>{nombre.strip().upper()}</span><span>{float(valor.strip())}/10</span></div><div style='width: 100%; background: rgba(255,255,255,0.05); height: 6px; border-radius: 3px;'><div style='width: {(float(valor.strip()) / 10) * 100}%; background: {'#ff2a2a' if float(valor.strip()) < 5 else '#ffdb58' if float(valor.strip()) < 8 else '#00ff88'}; height: 100%; border-radius: 3px;'></div></div></div>"
                    st.markdown(f"<div style='background: linear-gradient(135deg, #0a0a0c 0%, #16161d 100%); padding: 30px; border: 1px solid rgba(255,42,42,0.3); border-radius: 16px; text-align: center; margin-top: 20px;'><p style='color: #ff2a2a; font-weight: 700; margin: 0;'>DIAGNÓSTICO REFLEX</p><h1 style='font-size: 5rem; margin: 5px 0; color: white;'>{nota}<span style='font-size: 2rem; color: #555;'>/10</span></h1><div>{html_barras}</div></div>", unsafe_allow_html=True)

        if mensajes_actuales[-1]["role"] == "user":
            with st.chat_message("assistant", avatar=avatar_ia):
                with st.spinner("Calculando métricas REFLEX..."):
                    contents = []
                    meta = st.session_state.chat_meta.get(st.session_state.chat_actual, {})
                    instruccion_sistema = f"Eres REFLEX AI. Rol: {meta.get('rol', 'juez')}. Brutalidad: {meta.get('brutalidad', 7)}/10. Tono: {meta.get('tono', 'Directo')}. OBLIGATORIO: Termina SIEMPRE con [ELO: X/10] y [METRICAS: Estructura=X, Detalles=X, Contexto=X, Impacto=X]."
                    
                    contents.append({"role": "user", "parts": [{"text": instruccion_sistema}]})
                    contents.append({"role": "model", "parts": [{"text": "Entendido. Operaré estrictamente bajo estos parámetros exactos."}]})

                    for m in mensajes_actuales[:-1]:
                        contents.append({"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]})
                    
                    partes_finales = [{"text": mensajes_actuales[-1]["content"]}]
                    if evidencia_actual is not None:
                        partes_finales.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(evidencia_actual).decode('utf-8')}})
                    contents.append({"role": "user", "parts": partes_finales})

                    try:
                        GEMINI_KEY = os.environ.get("GEMINI_KEY") or st.secrets["GEMINI_KEY"]
                        payload = {"contents": contents, "safetySettings": [{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"}, {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}]}
                        
                        url_flash = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
                        respuesta = requests.post(url_flash, headers={"Content-Type": "application/json"}, data=json.dumps(payload))
                        
                        if respuesta.status_code == 404:
                            for c in contents: c["parts"] = [p for p in c["parts"] if "inline_data" not in p]
                            url_pro = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_KEY}"
                            respuesta = requests.post(url_pro, headers={"Content-Type": "application/json"}, data=json.dumps(payload))

                        if respuesta.status_code == 200:
                            texto_bruto = respuesta.json()['candidates'][0]['content']['parts'][0]['text']
                            def generador(t):
                                for p in t.split(" "): yield p + " "; time.sleep(0.01)
                            texto_final = st.write_stream(generador(texto_bruto))
                            st.session_state.chats_guardados[st.session_state.chat_actual].append({"role": "assistant", "content": texto_final, "avatar": avatar_ia})
                            sincronizar_db(st.session_state.chat_actual)
                        else:
                            st.error(f"Fallo del servidor de IA. Código: {respuesta.status_code}")
                    except Exception as e:
                        st.error(f"Error crítico: {e}")

        with st.popover("➕ Añadir imagen"):
            nueva_foto = st.file_uploader("Adjuntar archivo extra", type=["jpg", "png", "jpeg"], key="foto_extra")
            if nueva_foto:
                st.session_state.evidencias_guardadas[st.session_state.chat_actual] = nueva_foto.getvalue()
                st.success("Enviado.")

        if nuevo_mensaje := st.chat_input("Exige la solución exacta..."):
            st.session_state.chats_guardados[st.session_state.chat_actual].append({"role": "user", "content": nuevo_mensaje, "mostrar": nuevo_mensaje, "avatar": "👤"})
            sincronizar_db(st.session_state.chat_actual)
            st.rerun()
