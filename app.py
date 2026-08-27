import streamlit as st
import pandas as pd
from config import *
from auth import verificar_login, mostrar_login, es_admin, logout
from database import cargar_datos, guardar_datos
from charts import *
from ia_functions import analizar_datos_ia, generar_recomendaciones

st.set_page_config(page_title="Caracterización AT", page_icon="🛡️", layout="wide")

st.markdown(f"""<style>
:root{{--bg:{COLOR_BG};--card:{COLOR_CARD};--accent:{COLOR_ACCENT};}}
.stApp{{background:{COLOR_BG};}}
.stTabs [data-baseweb="tab-list"]{{gap:8px;background:{COLOR_CARD};border-radius:12px;padding:6px;}}
.stTabs [data-baseweb="tab"]{{border-radius:8px;color:{COLOR_SEC};font-weight:600;}}
.stTabs [aria-selected="true"]{{background:{COLOR_ACCENT}!important;color:{COLOR_BG}!important;}}
.stDataFrame{{background:{COLOR_CARD};border-radius:8px;}}
.stTextInput>div>div>input{{background:{COLOR_CARD};color:{COLOR_TEXT};border-color:{COLOR_SEC};}}
.sidebar .stButton>button{{background:{COLOR_ACCENT};color:{COLOR_BG};font-weight:bold;border-radius:8px;width:100%;}}
.block-container{{padding-top:2rem;}}
</style>""", unsafe_allow_html=True)

# ═══ LOGIN OBLIGATORIO ═══
if not verificar_login():
    mostrar_login()
    st.stop()

# ═══ SIDEBAR ═══
with st.sidebar:
    rol = st.session_state.get("rol", "consultor")
    icon = "👑" if rol == "admin" else "👁️"
    st.markdown(f"### {icon} {rol.upper()}")
    st.markdown("---")
    logout()
    if es_admin():
        st.markdown("---")
        st.markdown("#### 📁 Cargar Datos")
        archivo = st.file_uploader("Subir Excel", type=["xlsx"], key="up")
        if archivo:
            try:
                xl = pd.ExcelFile(archivo)
                nf = pd.read_excel(xl, "FORMATO") if "FORMATO" in xl.sheet_names else pd.DataFrame()
                nb = pd.read_excel(xl, "BASE DATOS") if "BASE DATOS" in xl.sheet_names else pd.DataFrame()
                if nf.empty and nb.empty:
                    st.error("❌ Hojas FORMATO o BASE DATOS no encontradas")
                else:
                    ok, msg = guardar_datos(nf, nb)
                    if ok:
                        st.success(msg)
                        st.session_state.df_f, st.session_state.df_b = cargar_datos()
                    else:
                        st.error(msg)
            except Exception as e:
                st.error(f"❌ {e}")
        if st.button("🔄 Recargar de Supabase"):
            st.session_state.df_f, st.session_state.df_b = cargar_datos()
            st.rerun()

# ═══ CARGAR DATOS ═══
if "df_f" not in st.session_state:
    st.session_state.df_f, st.session_state.df_b = cargar_datos()
df_f, df_b = st.session_state.df_f, st.session_state.df_b

# ═══ HEADER ═══
st.markdown(f"<h1 style='color:{COLOR_ACCENT};text-align:center;'>🛡️ CARACTERIZACIÓN DE ACCIDENTALIDAD LABORAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:{COLOR_SEC};text-align:center;'>Análisis integral de Seguridad y Salud en el Trabajo</p>", unsafe_allow_html=True)
st.markdown("---")

if df_f.empty:
    st.warning("⚠️ No hay datos cargados en el sistema.")
    if es_admin():
        st.info("📁 Sube el archivo CARACTERIZACION ACCIDENTALIDAD.xlsx desde el panel lateral izquierdo.")
    st.stop()

# ═══ COLUMNAS EXACTAS DEL EXCEL ═══
FF = "FECHA DEL EVENTO"
FD = "DÍA DE LA SEMANA (DEL EVENTO)"
FT = "TIPO DE EVENTO"
FA = "ÁREA/PROCESO"
FC = "CIE 10"
FI = "IDENTIFICACION"
FCU = "PARTE DEL CUERPO AFECTADA"
FAG = "AGENTE DEL ACCIDENTE"
FNA = "NATURALEZA DE LA LESIÓN"
FE = "ESTADO DEL EVENTO (ABIERTO, CERRADO, EN PROCESO)"

def cnt(b):
    if FT not in df_f.columns: return 0
    return df_f[FT].astype(str).str.contains(b, case=False, na=False).sum()

# ═══ TABS ═══
t1, t2, t3, t4 = st.tabs(["📊 Dashboard", "🔍 Consulta Trabajador", "🤖 Asistente IA", "⚙️ Administrador"])

# ═══════ DASHBOARD ═══════
with t1:
    total = len(df_f)
    kpis = [kpi(total, "Total Eventos", COLOR_ACCENT), kpi(cnt("accidente"), "Accidentes", COLOR_DANGER),
            kpi(cnt("enfermedad"), "Enf. Laborales", COLOR_WARNING), kpi(cnt("incidente"), "Incidentes", COLOR_INFO)]
    st.markdown(f"<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:16px;'>{''.join(kpis)}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        g = g_dia_semana(df_f, FD)
        if g: st.plotly_chart(g, use_container_width=True)
    with c2:
        g = g_tipo_anual(df_f, FT, FF)
        if g: st.plotly_chart(g, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        g = g_servicio(df_f, FA)
        if g: st.plotly_chart(g, use_container_width=True)
    with c4:
        g = g_cie10(df_f, FC)
        if g: st.plotly_chart(g, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        g = g_top5(df_f, FI)
        if g: st.plotly_chart(g, use_container_width=True)
    with c6:
        g = g_tendencia(df_f, FF)
        if g: st.plotly_chart(g, use_container_width=True)

    c7, c8 = st.columns(2)
    with c7:
        g = g_agente(df_f, FAG)
        if g: st.plotly_chart(g, use_container_width=True)
    with c8:
        g = g_cuerpo(df_f, FCU)
        if g: st.plotly_chart(g, use_container_width=True)

    c9, c10 = st.columns(2)
    with c9:
        g = g_naturaleza(df_f, FNA)
        if g: st.plotly_chart(g, use_container_width=True)
    with c10:
        g = g_estado(df_f, FE)
        if g: st.plotly_chart(g, use_container_width=True)

    st.markdown(f"<h3 style='color:{COLOR_ACCENT};'>💡 Recomendaciones IA</h3>", unsafe_allow_html=True)
    if st.button("🎯 Generar Recomendaciones", use_container_width=True):
        with st.spinner("Analizando con IA..."):
            r = generar_recomendaciones(df_f)
            st.markdown(f"<div style='background:{COLOR_CARD};padding:20px;border-radius:10px;color:{COLOR_SEC};line-height:1.8;'>{r}</div>", unsafe_allow_html=True)

# ═══════ CONSULTA TRABAJADOR ═══════
with t2:
    st.markdown(f"<h2 style='color:{COLOR_ACCENT};'>🔍 Consulta por Trabajador</h2>", unsafe_allow_html=True)
    cb, cbtn = st.columns([3, 1])
    with cb:
        bus = st.text_input("Identificación o cédula", placeholder="Ej: 1234567890")
    with cbtn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔎 Buscar", use_container_width=True):
            st.session_state["_bus"] = bus
    bus = st.session_state.get("_bus", "")
    if bus:
        dt = df_b[df_b[FI].astype(str).str.contains(bus, case=False, na=False)] if FI in df_b.columns else pd.DataFrame()
        et = df_f[df_f[FI].astype(str).str.contains(bus, case=False, na=False)] if FI in df_f.columns else pd.DataFrame()
        if dt.empty and et.empty:
            st.warning("⚠️ Sin resultados para esa identificación")
        else:
            if not dt.empty:
                st.markdown(f"<h3 style='color:{COLOR_ACCENT};'>👤 Datos del Trabajador</h3>", unsafe_allow_html=True)
                for _, row in dt.iterrows():
                    cols = st.columns(min(4, len(row)))
                    for i, (c, v) in enumerate(row.items()):
                        with cols[i % 4]:
                            st.markdown(f"<div style='background:{COLOR_CARD};padding:12px;border-radius:8px;margin:4px;border-left:3px solid {COLOR_ACCENT};'><small style='color:{COLOR_SEC};'>{c}</small><br><b style='color:{COLOR_TEXT};'>{v}</b></div>", unsafe_allow_html=True)
            if not et.empty:
                st.markdown(f"<h3 style='color:{COLOR_DANGER};'>📋 Historial de Eventos ({len(et)})</h3>", unsafe_allow_html=True)
                st.dataframe(et, use_container_width=True, hide_index=True)
                if FC in et.columns:
                    st.markdown(f"<h3 style='color:{COLOR_WARNING};'>🏥 CIE-10 Registrados</h3>", unsafe_allow_html=True)
                    for c, n in et[FC].value_counts().items():
                        st.markdown(f"<div style='background:{COLOR_CARD};padding:10px;border-radius:8px;margin:4px;display:flex;justify-content:space-between;'><span style='color:{COLOR_TEXT};'>{c}</span><span style='color:{COLOR_ACCENT};font-weight:bold;'>{n} vez(es)</span></div>", unsafe_allow_html=True)

# ═══════ ASISTENTE IA ═══════
with t3:
    st.markdown(f"<h2 style='color:{COLOR_ACCENT};'>🤖 Asistente de Análisis IA</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{COLOR_SEC};'>Pregúntame lo que quieras sobre tus datos</p>", unsafe_allow_html=True)
    sug = ["¿Principales riesgos?", "¿Medidas preventivas?", "¿Patrones estacionales?", "¿Servicios prioritarios?"]
    cs = st.columns(4)
    for i, s in enumerate(sug):
        with cs[i]:
            if st.button(s, key=f"s{i}", use_container_width=True):
                st.session_state["_pq"] = s
    pq = st.text_area("Escriba su pregunta:", value=st.session_state.get("_pq", ""), key="pqa")
    if st.button("🚀 Analizar con IA", use_container_width=True):
        if pq:
            with st.spinner("Pensando..."):
                r = analizar_datos_ia(df_f, df_b, pq)
                st.markdown(f"<div style='background:{COLOR_CARD};padding:20px;border-radius:12px;border-left:4px solid {COLOR_ACCENT};color:{COLOR_SEC};line-height:1.8;margin-top:16px;'>{r}</div>", unsafe_allow_html=True)
            st.session_state["_pq"] = ""

# ═══════ ADMINISTRADOR ═══════
with t4:
    if not es_admin():
        st.warning("🔒 Solo el administrador puede acceder a esta sección")
    else:
        st.markdown(f"<h2 style='color:{COLOR_ACCENT};'>⚙️ Administración de Datos</h2>", unsafe_allow_html=True)
        s1, s2 = st.tabs(["📝 Formato", "👥 Base Datos"])
        with s1:
            st.markdown(f"<h3>Hoja FORMATO — {len(df_f)} registros</h3>", unsafe_allow_html=True)
            ef = st.data_editor(df_f, num_rows="dynamic", use_container_width=True, hide_index=True, key="ef")
            if st.button("💾 Guardar Formato", use_container_width=True):
                st.session_state.df_f = ef
                ok, msg = guardar_datos(ef, st.session_state.df_b)
                st.success(msg) if ok else st.error(msg)
        with s2:
            st.markdown(f"<h3>Hoja BASE DATOS — {len(df_b)} registros</h3>", unsafe_allow_html=True)
            eb = st.data_editor(df_b, num_rows="dynamic", use_container_width=True, hide_index=True, key="eb")
            if st.button("💾 Guardar Base Datos", use_container_width=True):
                st.session_state.df_b = eb
                ok, msg = guardar_datos(st.session_state.df_f, eb)
                st.success(msg) if ok else st.error(msg)

st.markdown("---")
st.markdown(f"<p style='color:{COLOR_SEC};text-align:center;font-size:12px;'>🛡️ Caracterización AT v2.0 — Seguridad y Salud en el Trabajo</p>", unsafe_allow_html=True)
