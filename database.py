from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
import pandas as pd

def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def guardar_datos_supabase(df_formato, df_base):
    supa = get_supabase()
    if not supa:
        return False, "Sin credenciales Supabase"
    try:
        for _, row in df_formato.iterrows():
            supa.table("formato").upsert(row.to_dict()).execute()
        for _, row in df_base.iterrows():
            supa.table("base_datos").upsert(row.to_dict()).execute()
        return True, "Datos guardados en Supabase"
    except Exception as e:
        return False, str(e)

def cargar_datos_supabase():
    supa = get_supabase()
    if not supa:
        return None, None
    try:
        rf = supa.table("formato").select("*").execute()
        rb = supa.table("base_datos").select("*").execute()
        df_f = pd.DataFrame(rf.data) if rf.data else pd.DataFrame()
        df_b = pd.DataFrame(rb.data) if rb.data else pd.DataFrame()
        return df_f, df_b
    except Exception:
        return None, None

def actualizar_registro(tabla, id_reg, datos):
    supa = get_supabase()
    if not supa:
        return False
    try:
        supa.table(tabla).update(datos).eq("id", id_reg).execute()
        return True
    except Exception:
        return False

def eliminar_registro(tabla, id_reg):
    supa = get_supabase()
    if not supa:
        return False
    try:
        supa.table(tabla).delete().eq("id", id_reg).execute()
        return True
    except Exception:
        return False
