import streamlit as st
from config import ADMIN_USER, ADMIN_PASS

def login_admin():
    if "admin_logged" not in st.session_state:
        st.session_state.admin_logged = False
    if not st.session_state.admin_logged:
        with st.form("login_form"):
            c1, c2 = st.columns(2)
            with c1:
                user = st.text_input("👤 Usuario", placeholder="Usuario")
            with c2:
                pwd = st.text_input("🔑 Contraseña", type="password", placeholder="Contraseña")
            if st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True):
                if user == ADMIN_USER and pwd == ADMIN_PASS:
                    st.session_state.admin_logged = True
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        return False
    return True

def logout_admin():
    if st.sidebar.button("🚪 Cerrar Sesión"):
        st.session_state.admin_logged = False
        st.rerun()
