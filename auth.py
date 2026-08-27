import streamlit as st

def verificar_login():
    if "logged" not in st.session_state:
        st.session_state.logged = False
        st.session_state.rol = None
    return st.session_state.logged

def es_admin():
    return st.session_state.get("rol") == "admin"

def mostrar_login():
    st.markdown(f"""<style>
    .login-box{{max-width:420px;margin:80px auto;padding:40px;background:{COLOR_CARD};
    border-radius:16px;border:1px solid #2a3a4a;text-align:center;box-shadow:0 8px 32px rgba(0,0,0,0.5);}}
    .login-box h1{{color:{COLOR_ACCENT};font-size:26px;margin-bottom:6px;}}
    .login-box p{{color:{COLOR_SEC};margin-bottom:20px;font-size:14px;}}
    </style>""", unsafe_allow_html=True)
    st.markdown("""<div class="login-box">
    <h1>🛡️ Caracterización AT</h1>
    <p>Sistema de Accidentalidad Laboral</p></div>""", unsafe_allow_html=True)
    with st.form("login_form"):
        user = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
        pwd = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese su contraseña")
        if st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True):
            au = st.secrets.get("ADMIN_USER", "admin")
            ap = st.secrets.get("ADMIN_PASS", "admin123")
            cu = st.secrets.get("CONSULTOR_USER", "consultor")
            cp = st.secrets.get("CONSULTOR_PASS", "consultor123")
            if user == au and pwd == ap:
                st.session_state.logged, st.session_state.rol = True, "admin"
                st.rerun()
            elif user == cu and pwd == cp:
                st.session_state.logged, st.session_state.rol = True, "consultor"
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")

def logout():
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.logged, st.session_state.rol = False, None
        st.rerun()
