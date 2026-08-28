import streamlit as st
import pandas as pd
from datetime import date, time, datetime
from supabase import create_client

MAP_F = {
    "no_registro": "No.", "fecha_evento": "FECHA DEL EVENTO", "hora": "HORA",
    "identificacion": "IDENTIFICACION", "nombre_apellido": "NOMBRE Y APELLIDO",
    "fecha_nacimiento": "FECHA NACIMIENTO", "edad": "EDAD", "sexo": "SEXO",
    "fecha_ingreso": "FECHA DE INGRESO",
    "antiguedad": "ANTIGÜEDAD EN LA EMPRESA (MESES Y DIAS)",
    "cargo": "CARGO", "area_proceso": "ÁREA/PROCESO",
    "fecha_radicado_arl": "FECHA RADICADO EN ARL",
    "dia_semana": "DÍA DE LA SEMANA (DEL EVENTO)", "tipo_evento": "TIPO DE EVENTO",
    "sede_empresa": "SEDE DE LA EMPRESA", "sitio_ocurrencia": "SITIO OCURRENCIA",
    "descripcion_evento": "DESCRIPCIÓN DEL EVENTO", "cie10": "CIE 10",
    "dias_incapacidad": "DÍAS INCAPACIDAD",
    "naturaleza_lesion": "NATURALEZA DE LA LESIÓN",
    "parte_cuerpo": "PARTE DEL CUERPO AFECTADA",
    "agente_lesion": "AGENTE DE LA LESIÓN", "tipo_accidente": "TIPO DE ACCIDENTE",
    "condicion_ambiental": "CONDICIÓN AMBIENTAL PELIGROSA",
    "agente_accidente": "AGENTE DEL ACCIDENTE",
    "acto_subestandar": "ACTO SUBESTANDAR",
    "factores_personales": "FACTORES PERSONALES",
    "factores_trabajo": "FACTORES DE TRABAJO",
    "medidas_control": "MEDIDAS DE CONTROL",
    "fecha_cierre_medidas": "FECHA CIERRE DE MEDIDAS DE CONTROL",
    "estado_evento": "ESTADO DEL EVENTO (ABIERTO, CERRADO, EN PROCESO)"
}
MAP_F_INV = {v: k for k, v in MAP_F.items()}
MAP_B = {
    "no_registro": "No.", "identificacion": "IDENTIFICACION",
    "apellidos_nombres": "APELLIDOS Y NOMBRES", "cargo": "CARGO",
    "area_proceso": "AREA/PROCESO", "salario": "SALARIO",
    "fecha_inicio": "F. INICIO", "eps": "EPS", "afp": "AFP",
    "sexo": "SEXO", "fecha_nacimiento": "F. NACIMIENTO", "edad": "EDAD",
    "direccion": "DIRECCION", "contacto": "CONTACTO",
    "correo_personal": "CORREO PERSONAL", "tel_familiar": "TEL. FAMILIAR",
    "hipertension": "HIPERTENSION ARTERIAL", "obesidad": "OBESIDAD",
    "diabetes": "DIABETES", "cardiopatia": "CARDIOPATIA",
    "hipotiroidismo": "HIPOTIROIDISMO", "dislipidemia": "DISLIPIDEMIA",
    "enfermedad_renal": "ENFERMEDAD RENAL", "fumador": "FUMADOR",
    "enfermedad_pulmonar": "ENFERMEDAD PULMONAR"
}
MAP_B_INV = {v: k for k, v in MAP_B.items()}
SQL_F = set(MAP_F.keys())
SQL_B = set(MAP_B.keys())

def get_supa():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key: return None
    return create_client(url, key)

def safe_val(v):
    if pd.isna(v): return None
    if isinstance(v, (date, datetime)): return str(v)
    if isinstance(v, time): return str(v)
    if hasattr(v, 'item'): v = v.item()
    if isinstance(v, str) and v.strip().lower() in ("none", "nan", "", "nat", "na", "sin dato"): return None
    if isinstance(v, float) and v == int(v): return int(v)
    if isinstance(v, str) and ":" in v:
        v = v.lower().replace(" a.m.", "").replace(" p.m.", "").replace(" am", "").replace(" pm", "").strip()
    return v

def limpiar_filas(df, col_id, col_fecha=None):
    if col_id and col_id in df.columns:
        s = df[col_id].astype(str).str.strip().str.lower()
        df = df[s.notna() & (s != "none") & (s != "nan") & (s != "nat") & (s != "") & (s != "na") & (s != "sin dato")]
    if col_fecha and col_fecha in df.columns:
        df = df[df[col_fecha].notna()]
    return df

def preparar_lote(df, cols_validas):
    cols = [c for c in df.columns if c in cols_validas]
    if not cols: return []
    lote = []
    for _, row in df[cols].iterrows():
        d = {k: safe_val(v) for k, v in row.items()}
        if any(v is not None for v in d.values()):
            lote.append(d)
    return lote

def cargar_datos():
    supa = get_supa()
    if not supa: return pd.DataFrame(), pd.DataFrame()
    try:
        rf = supa.table("formato").select("*").execute()
        rb = supa.table("base_datos").select("*").execute()
        df_f = pd.DataFrame(rf.data) if rf.data else pd.DataFrame()
        df_b = pd.DataFrame(rb.data) if rb.data else pd.DataFrame()
        for c in ["id", "created_at", "updated_at"]:
            df_f = df_f.drop(columns=[c], errors="ignore")
            df_b = df_b.drop(columns=[c], errors="ignore")
        return df_f.rename(columns=MAP_F), df_b.rename(columns=MAP_B)
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def guardar_datos(df_f, df_b):
    supa = get_supa()
    if not supa: return False, "Sin credenciales Supabase"
    try:
        df_f = df_f.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)
        df_b = df_b.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)

        # Debug: ver qué columnas trae el Excel
        cols_excel_f = list(df_f.columns)
        cols_excel_b = list(df_b.columns)

        df_fs = df_f.rename(columns=MAP_F_INV)
        df_bs = df_b.rename(columns=MAP_B_INV)

        df_fs = limpiar_filas(df_fs, "identificacion", "fecha_evento")
        df_bs = limpiar_filas(df_bs, "identificacion")

        dup_f = 0
        if "fecha_evento" in df_fs.columns and "identificacion" in df_fs.columns:
            antes = len(df_fs)
            df_fs = df_fs.drop_duplicates(subset=["fecha_evento", "identificacion"], keep="last")
            dup_f = antes - len(df_fs)
        dup_b = 0
        if "identificacion" in df_bs.columns:
            antes = len(df_bs)
            df_bs = df_bs.drop_duplicates(subset=["identificacion"], keep="last")
            dup_b = antes - len(df_bs)

        lote_f = preparar_lote(df_fs, SQL_F)
        lote_b = preparar_lote(df_bs, SQL_B)

        # Si no hay nada válido, decir qué pasó
        if not lote_f and not lote_b:
            return False, f"❌ No hay datos válidos. Columnas Excel FORMATO: {cols_excel_f[:5]}... Columnas SQL esperadas: {list(MAP_F_INV.keys())[:5]}..."

        CHUNK = 500
        if lote_f:
            for i in range(0, len(lote_f), CHUNK):
                supa.table("formato").upsert(lote_f[i:i+CHUNK], on_conflict="fecha_evento,identificacion").execute()
        if lote_b:
            for i in range(0, len(lote_b), CHUNK):
                supa.table("base_datos").upsert(lote_b[i:i+CHUNK]).execute()

        msg = f"✅ {len(lote_f)} eventos + {len(lote_b)} trabajadores"
        extras = []
        if dup_f > 0: extras.append(f"{dup_f} dup. formato")
        if dup_b > 0: extras.append(f"{dup_b} dup. base datos")
        if extras: msg += f" ({', '.join(extras)} omitidos)"
        return True, msg
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
