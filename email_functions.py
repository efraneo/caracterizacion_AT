import requests
from config import EMAIL_API_KEY, EMAIL_FROM

def enviar_correo(destinatario, asunto, cuerpo):
    if not EMAIL_API_KEY or not EMAIL_FROM:
        return False, "Sin credenciales de correo configuradas"
    try:
        dominio = EMAIL_FROM.split("@")[1]
        resp = requests.post(
            f"https://api.mailgun.net/v3/{dominio}/messages",
            auth=("api", EMAIL_API_KEY),
            data={"from": EMAIL_FROM, "to": destinatario, "subject": asunto, "text": cuerpo}
        )
        if resp.status_code == 200:
            return True, "Correo enviado"
        return False, f"Error {resp.status_code}"
    except Exception as e:
        return False, str(e)

def notificar_evento(trabajador, tipo, fecha, cie10):
    asunto = f"🔔 Nuevo {tipo} registrado - {trabajador}"
    cuerpo = f"""Se registró un nuevo evento:
- Trabajador: {trabajador}
- Tipo: {tipo}
- Fecha: {fecha}
- CIE-10: {cie10}
Revise el sistema para más detalles."""
    return enviar_correo(EMAIL_FROM, asunto, cuerpo)
