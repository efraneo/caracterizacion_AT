import streamlit as st
import pandas as pd
from config import *
from auth import login_admin, logout_admin
from database import guardar_datos_supabase
from charts import *
from ia_functions import analizar_datos_ia, generar_recomendaciones

st.set_page_config(page_title="Caracterización AT", page_icon="🛡️", layout="wide")

# === CSS ===
st.markdown(f"""<style>
:root{{--bg:{COLOR_BG};--card:{COLOR_CARD};--accent:{COLOR_ACCENT};--text:{COLOR_TEXT};--sec:{COLOR_SEC};}}
.stApp{{background:{COLOR_BG};}}
.stTabs [data-baseweb="tab-list"]{{gap:8px;background:{COLOR_CARD};border-radius:12px;padding:6px;}}
.stTabs [data-baseweb="tab"]{{border-radius:8px;color:{COLOR_SEC};font-weight:600;}}
.stTabs [aria-selected="true"]{{background:{COLOR_ACCENT}!important;color:{COLOR_BG}!important;}}
.stDataFrame{{background:{COLOR_CARD};border-radius:8px;}}
.stTextInput>div>div>input{{background:{COLOR_CARD};color:{COLOR_TEXT};border-color:{COLOR_SEC};}}
.sidebar .stButton>button{{background:{COLOR_ACCENT};color:{COLOR_BG};font-weight:bold;border-radius:8px;width:100%;}}
.block-container{{padding-top:2rem;}}
</style>""", unsafe_allow_html=True)

# === Session State ===
for k, v in [("df_formato", pd.DataFrame()), ("df_base", pd.DataFrame()), ("pregunta_ia", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# === Sidebar ===
with st.sidebar:
    st.image("https://img.icons8.com/3d-fluency/94/shield.png", width=80)
    st.title("🛡️ Caracterización AT")
    st.markdown("---")
    archivo = st.file_uploader("📁 Cargar Excel", type=["xlsx"], key="upload")
    if archivo:
        try:
            xl = pd.ExcelFile(archivo)
            if "FORMATO" in xl.sheet_names:
                st.session_state.df_formato = pd.read_excel(xl, "FORMATO")
            if "BASE DATOS" in xl.sheet_names:
                st.session_state.df_base = pd.read_excel(xl, "BASE DATOS")
            n1, n2 = len(st.session_state.df_formato), len(st.session_state.df_base)
            st.success(f"✅ {n1} eventos, {n2} trabajadores")
        except Exception as e:
            st.error(f"❌ {e}")
    st.markdown("---")
    if not st.session_state.df_formato.empty:
        if st.button("💾 Guardar en Supabase"):
            ok, msg = guardar_datos_supabase(st.session_state.df_formato, st.session_state.df_base)
            st.success(msg) if ok else st.error(msg)
    st.markdown("---")
    logout_admin()

# === Header ===
st.markdown(f"<h1 style='color:{COLOR_ACCENT};text-align:center;'>🛡️ CARACTERIZACIÓN DE ACCIDENTALIDAD LABORAL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color:{COLOR_SEC};text-align:center;'>Análisis integral de eventos de Seguridad y Salud en el Trabajo</p>", unsafe_allow_html=True)
st.markdown("---")

df_f, df_b = st.session_state.df_formato, st.session_state.df_base
if df_f.empty:
    st.warning("⚠️ Cargue el archivo CARACTERIZACION ACCIDENTALIDAD.xlsx para comenzar")
    st.stop()

# === Detección automática de columnas ===
def detectar(df, opciones):
    for op in opciones:
        for c in df.columns:
            if op.upper() in str(c).upper():
                return c
    return None

col_dia = detectar(df_f, ["DIA", "SEMANA"])
col_serv = detectar(df_f, ["SERVICIO", "PROCESO", "AREA", "ÁREA"])
col_id = detectar(df_b, ["IDENTIFICACION", "IDENTIFICACIÓN", "CEDULA", "CÉDULA", "DOCUMENTO", "ID"])
col_cie = detectar(df_f, ["CIE", "DIAGNOSTICO", "DIAGNÓSTICO", "PATOL"])
col_tipo = detectar(df_f, ["TIPO", "CLASE"])
col_fecha = detectar(df_f, ["FECHA", "DATE"])
col_mec = detectar(df_f, ["MECANISMO", "MECA", "FORMA"])
col_cuerpo = detectar(df_f, ["CUERPO", "PARTE", "UBICACION", "UBICACIÓN"])

def conteo_tipo(df, col, busqueda):
    if not col or col not in df.columns:
        return 0
    return df[col].astype(str).str.contains(busqueda, case=False, na=False).sum()

# === TABS ===
t1, t2, t3, t4 = st.tabs(["📊 Dashboard", "🔍 Consulta Trabajador", "🤖 Asistente IA", "⚙️ Administrador"])

# ===================== DASHBOARD =====================
with t1:
    total = len(df_f)
    acc = conteo_tipo(df_f, col_tipo, "accidente")
    enf = conteo_tipo(df_f, col_tipo, "enfermedad")
    inc = conteo_tipo(df_f, col_tipo, "incidente")
    kpis = [
        kpi_card(total, "Total Eventos", COLOR_ACCENT),
        kpi_card(acc, "Accidentes", COLOR_DANGER),
        kpi_card(enf, "Enf. Laborales", COLOR_WARNING),
        kpi_card(inc, "Incidentes", COLOR_INFO)
    ]
    st.markdown(f"<div style='display:grid;grid-template-columns:repeat(4,1fr);gap:16px;'>{''.join(kpis)}</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        g = grafico_dia_semana(df_f, col_dia)
        if g: st.plotly_chart(g, use_container_width=True)
    with c2:
        g = grafico_tipo_anual(df_f, col_tipo, col_fecha)
        if g: st.plotly_chart(g, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        g = grafico_servicio(df_f, col_serv)
        if g: st.plotly_chart(g, use_container_width=True)
    with c4:
        g = grafico_cie10(df_f, col_cie)
        if g: st.plotly_chart(g, use_container_width=True)

    c5, c6 = st.columns(2)
    with c5:
        g = grafico_top5_trabajadores(df_f, col_id, col_cie)
        if g: st.plotly_chart(g, use_container_width=True)
    with c6:
        g = grafico_tendencia_mensual(df_f, col_fecha)
        if g: st.plotly_chart(g, use_container_width=True)

    c7, c8 = st.columns(2)
    with c7:
        g = grafico_mecanismo(df_f, col_mec)
        if g: st.plotly_chart(g, use_container_width=True)
    with c8:
        g = grafico_parte_cuerpo(df_f, col_cuerpo)
        if g: st.plotly_chart(g, use_container_width=True)

    st.markdown(f"<h3 style='color:{COLOR_ACCENT};'>💡 Recomendaciones IA</h3>", unsafe_allow_html=True)
    if st.button("🎯 Generar Recomendaciones", use_container_width=True):
        with st.spinner("Analizando con IA..."):
            rec = generar_recomendaciones(df_f)
            st.markdown(f"<div style='background:{COLOR_CARD};padding:20px;border-radius:10px;color:{COLOR_SEC};line-height:1.8;'>{rec}</div>", unsafe_allow_html=True)

# ===================== CONSULTA TRABAJADOR =====================
with t2:
    st.markdown(f"<h2 style='color:{COLOR_ACCENT};'>🔍 Consulta por Trabajador</h2>", unsafe_allow_html=True)
    cb, cbtn = st.columns([3, 1])
    with cb:
        busqueda = st.text_input("Identificación o cédula", placeholder="Ej: 1234567890")
    with cbtn:
        st.markdown("<br>", unsafe_allow_html=True)
        buscar = st.button("🔎 Buscar", use_container_width=True)

    if busqueda and buscar:
        datos_t = pd.DataFrame()
        eventos_t = pd.DataFrame()
        if col_id and col_id in df_b.columns:
            m = df_b[col_id].astype(str).str.contains(str(busqueda), case=False, na=False)
            datos_t = df_b[m]
        if col_id and col_id in df_f.columns:
            m2 = df_f[col_id].astype(str).str.contains(str(busqueda), case=False, na=False)
            eventos_t = df_f[m2]
        elif not col_id and len(df_f.columns) > 0:
            m2 = df_f.iloc[:, 0].astype(str).str.contains(str(busqueda), case=False, na=False)
            eventos_t = df_f[m2]

        if datos_t.empty and eventos_t.empty:
            st.warning("⚠️ No se encontraron registros")
        else:
            if not datos_t.empty:
                st.markdown(f"<h3 style='color:{COLOR_ACCENT};'>👤 Datos del Trabajador</h3>", unsafe_allow_html=True)
                for _, row in datos_t.iterrows():
                    cols = st.columns(min(4, len(row)))
                    for i, (c, v) in enumerate(row.items()):
                        with cols[i % 4]:
                            st.markdown(f"<div style='background:{COLOR_CARD};padding:12px;border-radius:8px;margin:4px;border-left:3px solid {COLOR_ACCENT};'><small style='color:{COLOR_SEC};'>{c}</small><br><b style='color:{COLOR_TEXT};'>{v}</b></div>", unsafe_allow_html=True)
            if not eventos_t.empty:
                st.markdown(f"<h3 style='color:{COLOR_DANGER};'>📋 Historial de Eventos ({len(eventos_t)})</h3>", unsafe_allow_html=True)
                st.dataframe(eventos_t, use_container_width=True, hide_index=True)
                if col_cie and col_cie in eventos_t.columns:
                    st.markdown(f"<h3 style='color:{COLOR_WARNING};'>🏥 CIE-10 Registrados</h3>", unsafe_allow_html=True)
                    for cie, cnt in eventos_t[col_cie].value_counts().items():
                        st.markdown(f"<div style='background:{COLOR_CARD};padding:10px;border-radius:8px;margin:4px;display:flex;justify-content:space-between;'><span style='color:{COLOR_TEXT};'>{cie}</span><span style='color:{COLOR_ACCENT};font-weight:bold;'>{cnt} vez(es)</span></div>", unsafe_allow_html=True)

# ===================== ASISTENTE IA =====================
with t3:
    st.markdown(f"<h2 style='color:{COLOR_ACCENT};'>🤖 Asistente de Análisis IA</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{COLOR_SEC};'>Pregúntame sobre tus datos de accidentalidad</p>", unsafe_allow_html=True)
    sugerencias = [
        "¿Cuáles son los principales riesgos?",
        "¿Qué medidas preventivas sugieres?",
        "¿Hay patrones estacionales?",
        "¿Qué servicios necesitan intervención?"
    ]
    cs = st.columns(4)
    for i, s in enumerate(sugerencias):
        with cs[i]:
            if st.button(s, key=f"s{i}", use_container_width=True):
                st.session_state.pregunta_ia = s
    pregunta = st.text_area("Escriba su pregunta:", value=st.session_state.pregunta_ia, key="pq")
    if st.button("🚀 Analizar con IA", use_container_width=True):
        if pregunta:
            with st.spinner("Pensando..."):
                resp = analizar_datos_ia(df_f, df_b, pregunta)
                st.markdown(f"<div style='background:{COLOR_CARD};padding:20px;border-radius:12px;border-left:4px solid {COLOR_ACCENT};color:{COLOR_SEC};line-height:1.8;margin-top:16px;'>{resp}</div>", unsafe_allow_html=True)
            st.session_state.pregunta_ia = ""

# ===================== ADMINISTRADOR =====================
with t4:
    if not login_admin():
        st.info("🔒 Inicie sesión como administrador")
    else:
        st.markdown(f"<h2 style='color:{COLOR_ACCENT};'>⚙️ Panel de Administración</h2>", unsafe_allow_html=True)
        st1, st2 = st.tabs(["📝 Formato", "👥 Base Datos"])
        with st1:
            st.markdown(f"<h3>Hoja FORMATO ({len(df_f)} registros)</h3>", unsafe_allow_html=True)
            ed_f = st.data_editor(df_f, num_rows="dynamic", use_container_width=True, hide_index=True, key="ef")
            if st.button("💾 Guardar Formato", use_container_width=True):
                st.session_state.df_formato = ed_f
                ok, msg = guardar_datos_supabase(ed_f, st.session_state.df_base)
                st.success("✅ Guardado" + (" + Supabase" if ok else ""))
        with st2:
            st.markdown(f"<h3>Hoja BASE DATOS ({len(df_b)} registros)</h3>", unsafe_allow_html=True)
            ed_b = st.data_editor(df_b, num_rows="dynamic", use_container_width=True, hide_index=True, key="eb")
            if st.button("💾 Guardar Base Datos", use_container_width=True):
                st.session_state.df_base = ed_b
                ok, msg = guardar_datos_supabase(st.session_state.df_formato, ed_b)
                st.success("✅ Guardado" + (" + Supabase" if ok else ""))

st.markdown("---")
st.markdown(f"<p style='color:{COLOR_SEC};text-align:center;font-size:12px;'>🛡️ Caracterización AT v1.0 — Seguridad y Salud en el Trabajo</p>", unsafe_allow_html=True)
