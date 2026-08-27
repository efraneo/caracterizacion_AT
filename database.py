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

# Columnas válidas que existen en la tabla SQL
SQL_COLS_F = set(MAP_F.keys())
SQL_COLS_B = set(MAP_B.keys())

def get_supa():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key:
        return None
    return create_client(url, key)

def safe_val(v):
    if pd.isna(v):
        return None
    if isinstance(v, (date, datetime)):
        return str(v)
    if isinstance(v, time):
        return str(v)
    if hasattr(v, 'item'):
        return v.item()
    return v

def cargar_datos():
    supa = get_supa()
    if not supa:
        return pd.DataFrame(), pd.DataFrame()
    try:
        rf = supa.table("formato").select("*").execute()
        rb = supa.table("base_datos").select("*").execute()
        df_f = pd.DataFrame(rf.data) if rf.data else pd.DataFrame()
        df_b = pd.DataFrame(rb.data) if rb.data else pd.DataFrame()
        for c in ["id", "created_at", "updated_at"]:
            df_f = df_f.drop(columns=[c], errors="ignore")
            df_b = df_b.drop(columns=[c], errors="ignore")
        df_f = df_f.rename(columns=MAP_F)
        df_b = df_b.rename(columns=MAP_B)
        return df_f, df_b
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def guardar_datos(df_f, df_b):
    supa = get_supa()
    if not supa:
        return False, "Sin credenciales Supabase"
    try:
        # Limpiar espacios en nombres de columna del Excel
        df_f = df_f.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)
        df_b = df_b.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)
        # Renombrar Excel → SQL
        df_fs = df_f.rename(columns=MAP_F_INV)
        df_bs = df_b.rename(columns=MAP_B_INV)
        # SOLO columnas que existen en la tabla SQL
        cols_f = [c for c in df_fs.columns if c in SQL_COLS_F]
        cols_b = [c for c in df_bs.columns if c in SQL_COLS_B]
        for _, row in df_fs[cols_f].iterrows():
            d = {k: safe_val(v) for k, v in row.items()}
            supa.table("formato").upsert(d).execute()
        for _, row in df_bs[cols_b].iterrows():
            d = {k: safe_val(v) for k, v in row.items()}
            supa.table("base_datos").upsert(d).execute()
        return True, f"✅ {len(df_f)} eventos + {len(df_b)} trabajadores guardados"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
