import streamlit as st
import pandas as pd
from config import *
from auth import verificar_login, mostrar_login, es_admin, logout
from database import cargar_datos, guardar_datos, get_supa
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

# ═══ FUNCIÓN: Detectar encabezados automáticamente ═══
def leer_hoja(xl, hoja, columnas_clave):
    df_raw = pd.read_excel(xl, hoja, header=None)
    fila_h = 0
    for i in range(min(15, len(df_raw))):
        valores = [str(v).strip().upper() for v in df_raw.iloc[i].values]
        coincidencias = sum(1 for c in columnas_clave if any(c in v for v in valores))
        if coincidencias >= 3:
            fila_h = i
            break
    df = pd.read_excel(xl, hoja, header=fila_h)
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]
    df = df.dropna(how='all')
    df.columns = [str(c).strip() for c in df.columns]
    return df

if not verificar_login():
    mostrar_login()
    st.stop()

with st.sidebar:
    rol = st.session_state.get("rol", "consultor")
    icon = "👑" if rol == "admin" else "👁️"
    st.markdown(f"### {icon} Rol: **{rol.upper()}**")
    st.markdown("---")
    logout()

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
COL_KPI = [COLOR_ACCENT, COLOR_DANGER, COLOR_WARNING, COLOR_INFO, PALETA[4], PALETA[5]]

def filtrar_validos(df):
    if FI not in df.columns: return df
    s = df[FI].astype(str).str.strip().str.lower()
    return df[s.notna() & (s != "none") & (s != "nan") & (s != "")]

if "df_f" not in st.session_state:
    st.session_state.df_f, st.session_state.df_b = cargar_datos()
df_f, df_b = st.session_state.df_f, st.session_state.df_b

st.markdown("<h1 style='color:#0D6EFD;text-align:center;'>🛡️ CARACTERIZACIÓN DE ACCIDENTALIDAD LABORAL</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#6C757D;text-align:center;'>Análisis integral de Seguridad y Salud en el Trabajo</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:#DEE2E6;'>", unsafe_allow_html=True)

if df_f.empty and not es_admin():
    st.warning("⚠️ No hay datos cargados. Contacte al administrador.")
    st.stop()

if es_admin():
    t1, t2, t3, t4 = st.tabs(["📊 Dashboard", "🔍 Consulta Trabajador", "🤖 Asistente IA", "⚙️ Administrador"])
else:
    t1, t2, t3 = st.tabs(["📊 Dashboard", "🔍 Consulta Trabajador", "🤖 Asistente IA"])

with t1:
    if df_f.empty:
        st.info("📁 No hay datos. Carga el archivo Excel desde ⚙️ Administrador.")
    else:
        df_v = filtrar_validos(df_f)
        total = len(df_v)
        kpis = [kpi(total, "Total Eventos", COLOR_ACCENT)]
        if FT in df_v.columns:
            tipos = df_v[FT].dropna().astype(str).str.strip()
            tipos = tipos[(tipos != "None") & (tipos != "nan") & (tipos != "")]
            for i, (tipo, cant) in enumerate(tipos.value_counts().items()):
                kpis.append(kpi(cant, tipo, COL_KPI[(i+1) % len(COL_KPI)]))
        n = len(kpis)
        cols_grid = f"repeat({n},1fr)" if n <= 6 else "repeat(3,1fr)"
        st.markdown(f"<div style='display:grid;grid-template-columns:{cols_grid};gap:16px;'>{''.join(kpis)}</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            g = g_dia_semana(df_v, FD)
            if g: st.plotly_chart(g, use_container_width=True)
        with c2:
            g = g_tipo_anual(df_v, FT, FF)
            if g: st.plotly_chart(g, use_container_width=True)
        c3, c4 = st.columns(2)
        with c3:
            g = g_servicio(df_v, FA)
            if g: st.plotly_chart(g, use_container_width=True)
        with c4:
            g = g_cie10(df_v, FC)
            if g: st.plotly_chart(g, use_container_width=True)
        c5, c6 = st.columns(2)
        with c5:
            g = g_top5(df_v, FI)
            if g: st.plotly_chart(g, use_container_width=True)
        with c6:
            g = g_tendencia(df_v, FF)
            if g: st.plotly_chart(g, use_container_width=True)
        c7, c8 = st.columns(2)
        with c7:
            g = g_agente(df_v, FAG)
            if g: st.plotly_chart(g, use_container_width=True)
        with c8:
            g = g_cuerpo(df_v, FCU)
            if g: st.plotly_chart(g, use_container_width=True)
        c9, c10 = st.columns(2)
        with c9:
            g = g_naturaleza(df_v, FNA)
            if g: st.plotly_chart(g, use_container_width=True)
        with c10:
            g = g_estado(df_v, FE)
            if g: st.plotly_chart(g, use_container_width=True)
        st.markdown(f"<h3 style='color:#0D6EFD;'>💡 Recomendaciones IA</h3>", unsafe_allow_html=True)
        if st.button("🎯 Generar Recomendaciones", use_container_width=True):
            with st.spinner("Analizando..."):
                r = generar_recomendaciones(df_v)
                st.markdown(f"<div style='background:#F8F9FA;padding:20px;border-radius:10px;color:#1A1A2E;line-height:1.8;border-left:4px solid #0D6EFD;'>{r}</div>", unsafe_allow_html=True)

with t2:
    if df_f.empty:
        st.info("📁 No hay datos. Carga el archivo Excel desde ⚙️ Administrador.")
    else:
        df_v2 = filtrar_validos(df_f)
        st.markdown("<h2 style='color:#0D6EFD;'>🔍 Consulta por Trabajador</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### ⚡ ¿Sufrió Accidente de Trabajo?")
        cid = st.text_input("Identificación del trabajador", placeholder="Ej: 1234567890", key="qr")
        if cid:
            mask = df_v2[FI].astype(str).str.contains(cid, case=False, na=False) if FI in df_v2.columns else pd.Series([False]*len(df_v2))
            eventos = df_v2[mask]
            ats = eventos[eventos[FT].astype(str).str.contains("accidente", case=False, na=False)] if FT in eventos.columns and not eventos.empty else pd.DataFrame()
            if ats.empty:
                st.markdown("<div style='background:#D1E7DD;color:#0F5132;padding:16px;border-radius:10px;font-size:16px;font-weight:bold;text-align:center;'>✅ Este trabajador NO tiene accidentes de trabajo registrados</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='background:#F8D7DA;color:#842029;padding:16px;border-radius:10px;font-size:16px;font-weight:bold;text-align:center;'>❌ Este trabajador tiene {len(ats)} accidente(s) de trabajo</div>", unsafe_allow_html=True)
                for _, r in ats.iterrows():
                    st.markdown(f"<div style='background:#FFF3CD;color:#664D03;padding:12px;border-radius:8px;margin:4px 0;border-left:3px solid #FD7E14;'><b>📅 {r.get(FF,'')}</b> — CIE-10: <b>{r.get(FC,'')}</b> — Estado: <b>{r.get(FE,'')}</b></div>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### 📋 Consulta Completa")
        cb, cbtn = st.columns([3, 1])
        with cb:
            bus = st.text_input("Búsqueda completa", placeholder="Ej: 1234567890", key="bc")
        with cbtn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔎 Buscar", use_container_width=True):
                st.session_state["_bus"] = bus
        bus = st.session_state.get("_bus", "")
        if bus:
            dt = df_b[df_b[FI].astype(str).str.contains(bus, case=False, na=False)] if FI in df_b.columns else pd.DataFrame()
            et = df_v2[df_v2[FI].astype(str).str.contains(bus, case=False, na=False)] if FI in df_v2.columns else pd.DataFrame()
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
                    st.markdown(f"<h3 style='color:#DC3545;'>📋 Historial ({len(et)})</h3>", unsafe_allow_html=True)
                    st.dataframe(et, use_container_width=True, hide_index=True)
                    if FC in et.columns:
                        st.markdown("<h3 style='color:#FD7E14;'>🏥 CIE-10</h3>", unsafe_allow_html=True)
                        for c, n in et[FC].value_counts().items():
                            st.markdown(f"<div style='background:#F8F9FA;padding:10px;border-radius:8px;margin:4px;display:flex;justify-content:space-between;border:1px solid #DEE2E6;'><span>{c}</span><span style='color:#0D6EFD;font-weight:bold;'>{n} vez(es)</span></div>", unsafe_allow_html=True)

with t3:
    if df_f.empty:
        st.info("📁 No hay datos. Carga el archivo Excel desde ⚙️ Administrador.")
    else:
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

if es_admin():
    with t4:
        st.markdown("<h2 style='color:#0D6EFD;'>⚙️ Panel de Administración</h2>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### 📁 Cargar Archivo Excel")
        st.markdown("<p style='color:#6C757D;'>La app detecta automáticamente los encabezados, sin importar en qué fila estén.</p>", unsafe_allow_html=True)
        archivo = st.file_uploader("Seleccionar archivo Excel", type=["xlsx"], key="up_admin", label_visibility="collapsed")
        if archivo:
            try:
                xl = pd.ExcelFile(archivo)
                # Detectar encabezados automáticamente
                nf = leer_hoja(xl, "FORMATO", ["FECHA DEL EVENTO", "IDENTIFICACION", "TIPO DE EVENTO", "CIE 10", "CARGO"]) if "FORMATO" in xl.sheet_names else pd.DataFrame()
                nb = leer_hoja(xl, "BASE DATOS", ["IDENTIFICACION", "CARGO", "EPS", "AFP", "APELLIDOS"]) if "BASE DATOS" in xl.sheet_names else pd.DataFrame()

                # Mostrar qué encontró
                st.markdown(f"<div style='background:#F8F9FA;padding:12px;border-radius:8px;border:1px solid #DEE2E6;font-size:13px;color:#6C757D;'>📋 FORMATO: <b>{len(nf)}</b> filas, <b>{len(nf.columns)}</b> columnas encontradas<br>📋 BASE DATOS: <b>{len(nb)}</b> filas, <b>{len(nb.columns)}</b> columnas encontradas</div>", unsafe_allow_html=True)

                if nf.empty and nb.empty:
                    st.error("❌ No se encontraron las hojas o los encabezados no coinciden")
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
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 Recargar Datos", use_container_width=True):
                st.session_state.df_f, st.session_state.df_b = cargar_datos()
                st.rerun()
        with col_r2:
            if st.button("🗑️ Limpiar Base de Datos", type="secondary", use_container_width=True):
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
        st.markdown("#### 📊 Resumen")
        rc1, rc2 = st.columns(2)
        with rc1:
            df_v_r = filtrar_validos(df_f)
            st.markdown(f"<div style='background:#F8F9FA;padding:20px;border-radius:10px;border:1px solid #DEE2E6;text-align:center;'><div style='font-size:28px;font-weight:bold;color:#0D6EFD;'>{len(df_v_r)}</div><div style='color:#6C757D;'>Eventos válidos</div></div>", unsafe_allow_html=True)
        with rc2:
            st.markdown(f"<div style='background:#F8F9FA;padding:20px;border-radius:10px;border:1px solid #DEE2E6;text-align:center;'><div style='font-size:28px;font-weight:bold;color:#198754;'>{len(df_b)}</div><div style='color:#6C757D;'>Trabajadores</div></div>", unsafe_allow_html=True)
        st.markdown("---")
        if not df_f.empty:
            s1, s2 = st.tabs(["📝 Formato", "👥 Base Datos"])
            with s1:
                df_v_e = filtrar_validos(df_f)
                st.markdown(f"<h3>FORMATO — {len(df_v_e)} registros válidos</h3>", unsafe_allow_html=True)
                st.dataframe(df_v_e, use_container_width=True, hide_index=True)
            with s2:
                st.markdown(f"<h3>BASE DATOS — {len(df_b)} registros</h3>", unsafe_allow_html=True)
                st.dataframe(df_b, use_container_width=True, hide_index=True)
        else:
            st.info("📁 Carga el archivo Excel para ver los datos.")

st.markdown("<hr style='border-color:#DEE2E6;'>", unsafe_allow_html=True)
st.markdown("<p style='color:#6C757D;text-align:center;font-size:12px;'>🛡️ Caracterización AT v2.0</p>", unsafe_allow_html=True)
