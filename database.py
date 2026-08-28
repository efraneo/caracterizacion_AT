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
SQL_F = set(MAP_F.keys())
SQL_B = set(MAP_B.keys())

def _n(s):
    return str(s).upper().replace("Á","A").replace("É","E").replace("Í","I").replace("Ó","O").replace("Ú","U").replace("Ñ","N")

def buscar_mapeo(col_excel, mapeo):
    cn = _n(col_excel)
    for k, v in mapeo.items():
        if _n(k) == cn or cn in _n(k) or _n(k) in cn:
            return v
    return cn.lower().replace(" ","_").replace("/","_").replace("(","").replace(")","")

def renombrar_inv(df, mapeo):
    return df.rename(columns=lambda c: buscar_mapeo(c, mapeo))

def renombrar_directo(df, mapeo):
    nuevo = {}
    for c in df.columns:
        cn = _n(c)
        for k, v in mapeo.items():
            if _n(k) == cn:
                nuevo[c] = v
                break
        if c not in nuevo:
            nuevo[c] = c
    return df.rename(columns=nuevo)

def get_supa():
    url = st.secrets.get("SUPABASE_URL", "")
    key = st.secrets.get("SUPABASE_KEY", "")
    if not url or not key: return None
    return create_client(url, key)

def safe_val(v):
    if pd.isna(v): return None
    if isinstance(v, (date, datetime)): return str(v)
    if isinstance(v, time) and not isinstance(v, datetime):
        s = str(v)
        return None if s == "00:00:00" else s
    if hasattr(v, 'item'): v = v.item()
    if isinstance(v, str) and v.strip().lower() in ("none","nan","","nat","na","sin dato"): return None
    if isinstance(v, float) and v == int(v): return int(v)
    if isinstance(v, str) and ":" in v:
        v = v.lower().replace(" a.m.","").replace(" p.m.","").replace(" am","").replace(" pm","").strip()
    return v

def limpiar_filas(df, col_id, col_fecha=None):
    if col_id and col_id in df.columns:
        s = df[col_id].astype(str).str.strip().str.lower()
        df = df[s.notna() & (s != "none") & (s != "nan") & (s != "nat") & (s != "") & (s != "na") & (s != "sin dato")]
    if col_fecha and col_fecha in df.columns:
        df = df[df[col_fecha].notna()]
    return df

def purgar_silent(supa):
    try:
        for tabla, cols in [("formato", ["fecha_evento","identificacion"]), ("base_datos", ["identificacion"])]:
            resp = supa.table(tabla).select("id", *cols).order("id").execute()
            if resp.data:
                vistos = {}
                elim = []
                for r in resp.data:
                    vals = [str(r.get(c,"")).strip() for c in cols]
                    if all(v and v != "None" for v in vals):
                        clave = tuple(vals)
                        if clave in vistos:
                            elim.append(r["id"])
                        else:
                            vistos[clave] = r["id"]
                for j in range(0, len(elim), 100):
                    supa.table(tabla).delete().in_("id", elim[j:j+100]).execute()
    except Exception:
        pass

def purgar_duplicados():
    supa = get_supa()
    if not supa: return False, "Sin credenciales"
    try:
        total = 0
        for tabla, cols in [("formato", ["fecha_evento","identificacion"]), ("base_datos", ["identificacion"])]:
            resp = supa.table(tabla).select("id", *cols).order("id").execute()
            if resp.data:
                vistos = {}
                elim = []
                for r in resp.data:
                    vals = [str(r.get(c,"")).strip() for c in cols]
                    if all(v and v != "None" for v in vals):
                        clave = tuple(vals)
                        if clave in vistos:
                            elim.append(r["id"])
                        else:
                            vistos[clave] = r["id"]
                for j in range(0, len(elim), 100):
                    supa.table(tabla).delete().in_("id", elim[j:j+100]).execute()
                total += len(elim)
        return True, f"✅ {total} duplicados eliminados"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def cargar_datos():
    supa = get_supa()
    if not supa: return pd.DataFrame(), pd.DataFrame()
    try:
        rf = supa.table("formato").select("*").execute()
        rb = supa.table("base_datos").select("*").execute()
        df_f = pd.DataFrame(rf.data) if rf.data else pd.DataFrame()
        df_b = pd.DataFrame(rb.data) if rb.data else pd.DataFrame()
        for c in ["id","created_at","updated_at"]:
            df_f = df_f.drop(columns=[c], errors="ignore")
            df_b = df_b.drop(columns=[c], errors="ignore")
        return renombrar_directo(df_f, MAP_F), renombrar_directo(df_b, MAP_B)
    except Exception:
        return pd.DataFrame(), pd.DataFrame()

def guardar_datos(df_f, df_b):
    supa = get_supa()
    if not supa: return False, "Sin credenciales Supabase"
    try:
        # PURGA AUTOMÁTICA antes de cargar
        purgar_silent(supa)
        # Limpiar y mapear
        df_f = df_f.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)
        df_b = df_b.rename(columns=lambda x: x.strip() if isinstance(x, str) else x)
        df_fs = renombrar_inv(df_f, MAP_F)
        df_bs = renombrar_inv(df_b, MAP_B)
        # Limpiar filas inválidas
        df_fs = limpiar_filas(df_fs, "identificacion", "fecha_evento")
        df_bs = limpiar_filas(df_bs, "identificacion")
        # Preparar lotes
        lote_f, lote_b = [], []
        for _, row in df_fs.iterrows():
            d = {k: safe_val(v) for k, v in row.items() if k in SQL_F}
            if any(v is not None for v in d.values()): lote_f.append(d)
        for _, row in df_bs.iterrows():
            d = {k: safe_val(v) for k, v in row.items() if k in SQL_B}
            if any(v is not None for v in d.values()): lote_b.append(d)
        # Insertar por lotes
        CHUNK = 500
        if lote_f:
            for i in range(0, len(lote_f), CHUNK):
                supa.table("formato").upsert(lote_f[i:i+CHUNK], on_conflict="fecha_evento,identificacion").execute()
        if lote_b:
            for i in range(0, len(lote_b), CHUNK):
                supa.table("base_datos").upsert(lote_b[i:i+CHUNK]).execute()
        msg = f"✅ {len(lote_f)} eventos + {len(lote_b)} trabajadores guardados"
        return True, msg
    except Exception as e:
        return False, f"❌ Error: {str(e)}"
