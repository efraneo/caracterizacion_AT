import streamlit as st
import pandas as pd
from config import *
from auth import verificar_login, mostrar_login, es_admin, logout
from database import cargar_datos, guardar_datos
from charts import *
from ia_functions import analizar_datos_ia, generar_recomendaciones

st.set_page_config(page_title="Caracterización AT", page_icon="🛡️", layout="wide")

st.markdown("""<style>
.stApp{background:#FFFFFF;}
.stTabs [data-baseweb="tab-list"]{gap:6px;background:#F8F9FA;border-radius:10px;padding:4px;border:1px solid #DEE2E6;}
.stTabs [data-baseweb="tab"]{border-radius:8px;color:#6C757D;font-weight:600;font-size:14px;}
.stTabs [aria-selected="true"]{background:#0D6EFD!important;color:white!important;}
.stDataFrame{border:1px solid #DEE2E6;border-radius:8px;}
.stTextInput>div>div>input{background:white;color:#1A1A2E;border:1px solid #DEE2E6;border-radius:8px;}
.stTextArea>div>div>textarea{background:white;color:#1A1A2E;border:1px solid #DEE2E6;border-radius:8px;}
.sidebar{background:#F8F9FA;border-right:1px solid #DEE2E6;}
.sidebar .stButton>button{background:#0D6EFD;color:white;font-weight:bold;border-radius:8px;width:100%;border:none;}
.sidebar .stButton>button:hover{background:#0B5ED7;}
.block-container{padding-top:2rem;max-width:1400px;}
</style>""", unsafe_allow_html=True)

if not verificar_login():
    mostrar_login()
    st.stop()

# Sidebar limpio: solo rol y logout
with st.sidebar:
    rol = st.session_state.get("rol", "consultor")
    icon = "👑" if rol == "admin" else "👁️"
    st.markdown(f"### {icon} Rol: **{rol.upper()}**")
    st.markdown("---")
    logout()

# Cargar datos desde Supabase
if "df_f" not in st.session_state:
    st.session_state.df_f, st.session_state.df_b = cargar_datos()
df_f, df_b = st.session_state.df_f, st.session_state.df_b

st.markdown("<h1 style='color:#0D6EFD;text-align:center;'>🛡️ CARACTERIZACIÓN DE ACCIDENTALIDAD LABORAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6C757D;text-align:center;'>Análisis integral de Seguridad y Salud en el Trabajo</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:#DEE2E6;'>", unsafe_allow_html=True)

if df_f.empty:
    if es_admin():
        st.warning("⚠️ No hay datos. Ve a ⚙️ Administrador para cargar el archivo Excel.")
    else:
        st.warning("⚠️ No hay datos cargados en el sistema. Contacte al administrador.")
    st.stop()

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

t1, t2, t3, t4 = st.tabs(["📊 Dashboard", "🔍 Consulta Trabajador", "🤖 Asistente IA", "⚙️ Administrador"])

with t1:
    total = len(df_f)
    kpis = [kpi(total,"Total Eventos",COLOR_ACCENT), kpi(cnt("accidente"),"Accidentes",COLOR_DANGER),
            kpi(cnt("enfermedad"),"Enf. Laborales",COLOR_WARNING), kpi(cnt("incidente"),"Incidentes",COLOR_INFO)]
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

    st.markdown(f"<h3 style='color:#0D6EFD;'>💡 Recomendaciones IA</h3>", unsafe_allow_html=True)
    if st.button("🎯 Generar Recomendaciones", use_container_width=True):
        with st.spinner("Analizando..."):
            r = generar_recomendaciones(df_f)
            st.markdown(f"<div style='background:#F8F9FA;padding:20px;border-radius:10px;color:#1A1A2E;line-height:1.8;border-left:4px solid #0D6EFD;'>{r}</div>", unsafe_allow_html=True)

with t2:
    st.markdown("<h2 style='color:#0D6EFD;'>🔍 Consulta por Trabajador</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### ⚡ Consulta Rápida — ¿Sufrió Accidente de Trabajo?")
    cid = st.text_input("Identificación del trabajador", placeholder="Ej: 1234567890", key="qr")
    if cid:
        mask = df_f[FI].astype(str).str.contains(cid, case=False, na=False) if FI in df_f.columns else pd.Series([False]*len(df_f))
        eventos = df_f[mask]
        ats = eventos[eventos[FT].astype(str).str.contains("accidente", case=False, na=False)] if FT in eventos.columns and not eventos.empty else pd.DataFrame()
        if ats.empty:
            st.markdown("<div style='background:#D1E7DD;color:#0F5132;padding:16px;border-radius:10px;font-size:16px;font-weight:bold;text-align:center;'>✅ Este trabajador NO tiene accidentes de trabajo registrados</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background:#F8D7DA;color:#842029;padding:16px;border-radius:10px;font-size:16px;font-weight:bold;text-align:center;'>❌ Este trabajador tiene {len(ats)} accidente(s) de trabajo registrado(s)</div>", unsafe_allow_html=True)
            for _, r in ats.iterrows():
                fec = r.get(FF, "Sin fecha")
                cie = r.get(FC, "Sin CIE-10")
                est = r.get(FE, "Sin estado")
                st.markdown(f"<div style='background:#FFF3CD;color:#664D03;padding:12px;border-radius:8px;margin:4px 0;border-left:3px solid #FD7E14;'><b>📅 {fec}</b> — CIE-10: <b>{cie}</b> — Estado: <b>{est}</b></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 📋 Consulta Completa")
    cb, cbtn = st.columns([3, 1])
    with cb:
        bus = st.text_input("Búsqueda completa por identificación", placeholder="Ej: 1234567890", key="bc")
    with cbtn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔎 Buscar", use_container_width=True):
            st.session_state["_bus"] = bus
    bus = st.session_state.get("_bus", "")
    if bus:
        dt = df_b[df_b[FI].astype(str).str.contains(bus, case=False, na=False)] if FI in df_b.columns else pd.DataFrame()
        et = df_f[df_f[FI].astype(str).str.contains(bus, case=False, na=False)] if FI in df_f.columns else pd.DataFrame()
        if dt.empty and et.empty:
            st.warning("⚠️ Sin resultados")
        else:
            if not dt.empty:
                st.markdown("<h3 style='color:#0D6EFD;'>👤 Datos del Trabajador</h3>", unsafe_allow_html=True)
                for _, row in dt.iterrows():
                    cols = st.columns(min(4, len(row)))
                    for i, (c, v) in enumerate(row.items()):
                        with cols[i % 4]:
                            st.markdown(f"<div style='background:#F8F9FA;padding:12px;border-radius:8px;margin:4px;border-left:3px solid #0D6EFD;border:1px solid #DEE2E6;'><small style='color:#6C757D;'>{c}</small><br><b style='color:#1A1A2E;'>{v}</b></div>", unsafe_allow_html=True)
            if not et.empty:
                st.markdown(f"<h3 style='color:#DC3545;'>📋 Historial de Eventos ({len(et)})</h3>", unsafe_allow_html=True)
                st.dataframe(et, use_container_width=True, hide_index=True)
                if FC in et.columns:
                    st.markdown("<h3 style='color:#FD7E14;'>🏥 CIE-10 Registrados</h3>", unsafe_allow_html=True)
                    for c, n in et[FC].value_counts().items():
                        st.markdown(f"<div style='background:#F8F9FA;padding:10px;border-radius:8px;margin:4px;display:flex;justify-content:space-between;border:1px solid #DEE2E6;'><span style='color:#1A1A2E;'>{c}</span><span style='color:#0D6EFD;font-weight:bold;'>{n} vez(es)</span></div>", unsafe_allow_html=True)

with t3:
    st.markdown("<h2 style='color:#0D6EFD;'>🤖 Asistente de Análisis IA</h2>", unsafe_allow_html=True)
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
                st.markdown(f"<div style='background:#F8F9FA;padding:20px;border-radius:12px;border-left:4px solid #0D6EFD;color:#1A1A2E;line-height:1.8;margin-top:16px;'>{r}</div>", unsafe_allow_html=True)
            st.session_state["_pq"] = ""

# ═══════ TAB ADMINISTRADOR — SOLO ADMIN ═══════
with t4:
    if not es_admin():
        st.warning("🔒 Solo el administrador puede acceder aquí")
    else:
        st.markdown("<h2 style='color:#0D6EFD;'>⚙️ Panel de Administración</h2>", unsafe_allow_html=True)
        st.markdown("---")

        # SECCIÓN DE CARGA DE ARCHIVO
        st.markdown("#### 📁 Cargar Archivo Excel")
        st.markdown("<p style='color:#6C757D;'>Sube el archivo CARACTERIZACION ACCIDENTALIDAD.xlsx con las hojas FORMATO y BASE DATOS.</p>", unsafe_allow_html=True)
        archivo = st.file_uploader("Seleccionar archivo Excel", type=["xlsx"], key="up_admin", label_visibility="collapsed")
        if archivo:
            try:
                xl = pd.ExcelFile(archivo)
                nf = pd.read_excel(xl, "FORMATO") if "FORMATO" in xl.sheet_names else pd.DataFrame()
                nb = pd.read_excel(xl, "BASE DATOS") if "BASE DATOS" in xl.sheet_names else pd.DataFrame()
                if nf.empty and nb.empty:
                    st.error("❌ No se encontraron las hojas FORMATO ni BASE DATOS en el archivo")
                else:
                    with st.spinner("Guardando en base de datos..."):
                        ok, msg = guardar_datos(nf, nb)
                    if ok:
                        st.success(msg)
                        st.session_state.df_f, st.session_state.df_b = cargar_datos()
                        st.rerun()
                    else:
                        st.error(msg)
            except Exception as e:
                st.error(f"❌ Error al leer el archivo: {e}")

        st.markdown("---")

        # BOTÓN RECARGAR
        col_r1, col_r2 = st.columns([1, 3])
        with col_r1:
            if st.button("🔄 Recargar Datos", use_container_width=True):
                st.session_state.df_f, st.session_state.df_b = cargar_datos()
                st.rerun()
        with col_r2:
            if st.button("🗑️ Limpiar Base de Datos", type="secondary", use_container_width=True):
                from database import get_supa
                supa = get_supa()
                if supa:
                    try:
                        supa.table("formato").delete().neq("id", 0).execute()
                        supa.table("base_datos").delete().neq("id", 0).execute()
                        st.session_state.df_f, st.session_state.df_b = pd.DataFrame(), pd.DataFrame()
                        st.success("✅ Base de datos limpiada")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ {e}")

        st.markdown("---")

        # RESUMEN DE LO CARGADO
        st.markdown("#### 📊 Resumen de Datos Cargados")
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown(f"<div style='background:#F8F9FA;padding:20px;border-radius:10px;border:1px solid #DEE2E6;text-align:center;'><div style='font-size:28px;font-weight:bold;color:#0D6EFD;'>{len(df_f)}</div><div style='color:#6C757D;'>Eventos en FORMATO</div></div>", unsafe_allow_html=True)
        with rc2:
            st.markdown(f"<div style='background:#F8F9FA;padding:20px;border-radius:10px;border:1px solid #DEE2E6;text-align:center;'><div style='font-size:28px;font-weight:bold;color:#198754;'>{len(df_b)}</div><div style='color:#6C757D;'>Trabajadores en BASE DATOS</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        # EDITORES DE DATOS
        s1, s2 = st.tabs(["📝 Formato", "👥 Base Datos"])
        with s1:
            st.markdown(f"<h3>Hoja FORMATO — {len(df_f)} registros</h3>", unsafe_allow_html=True)
            ef = st.data_editor(df_f, num_rows="dynamic", use_container_width=True, hide_index=True, key="ef")
            if st.button("💾 Guardar Cambios Formato", use_container_width=True):
                st.session_state.df_f = ef
                ok, msg = guardar_datos(ef, st.session_state.df_b)
                st.success(msg) if ok else st.error(msg)
        with s2:
            st.markdown(f"<h3>Hoja BASE DATOS — {len(df_b)} registros</h3>", unsafe_allow_html=True)
            eb = st.data_editor(df_b, num_rows="dynamic", use_container_width=True, hide_index=True, key="eb")
            if st.button("💾 Guardar Cambios Base Datos", use_container_width=True):
                st.session_state.df_b = eb
                ok, msg = guardar_datos(st.session_state.df_f, eb)
                st.success(msg) if ok else st.error(msg)

st.markdown("<hr style='border-color:#DEE2E6;'>", unsafe_allow_html=True)
st.markdown("<p style='color:#6C757D;text-align:center;font-size:12px;'>🛡️ Caracterización AT v2.0</p>", unsafe_allow_html=True)
