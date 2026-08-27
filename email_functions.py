import requests
import streamlit as st

def enviar_correo(destino, asunto, cuerpo):
    if not st.secrets.get("EMAIL_API_KEY"):
        return False, "Sin credenciales de correo"
    try:
        dom = st.secrets["EMAIL_FROM"].split("@")[1]
        r = requests.post(f"https://api.mailgun.net/v3/{dom}/messages",
            auth=("api", st.secrets["EMAIL_API_KEY"]),
            data={"from": st.secrets["EMAIL_FROM"], "to": destino, "subject": asunto, "text": cuerpo})
        return (True, "Correo enviado") if r.status_code == 200 else (False, f"Error {r.status_code}")
    except Exception as e:
        return False, str(e)

def notificar_evento(trabajador, tipo, fecha, cie10):
    asunto = f"🔔 Nuevo {tipo} - {trabajador}"
    cuerpo = f"Trabajador: {trabajador}\nTipo: {tipo}\nFecha: {fecha}\nCIE-10: {cie10}\nRevise el sistema."
    return enviar_correo(st.secrets.get("EMAIL_FROM", ""), asunto, cuerpo)
