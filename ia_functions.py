from openai import OpenAI
from config import OPENAI_API_KEY

def analizar_datos_ia(df_formato, df_base, pregunta):
    if not OPENAI_API_KEY:
        return "⚠️ Configure su clave API de OpenAI en el archivo .env"
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        rf = df_formato.head(30).to_string() if not df_formato.empty else "Sin datos de eventos"
        rb = df_base.head(15).to_string() if not df_base.empty else "Sin datos de trabajadores"
        prompt = f"""Eres un experto en Seguridad y Salud en el Trabajo (SST) en Colombia.
Analiza estos datos de accidentalidad laboral y responde en español:

EVENTOS:
{rf}

TRABAJADORES:
{rb}

Pregunta: {pregunta}

Responde de forma concisa, profesional y con datos concretos si es posible."""
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}],
            max_tokens=500, temperature=0.3
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generar_recomendaciones(df_formato):
    if not OPENAI_API_KEY:
        return "⚠️ Configure su clave API de OpenAI en el archivo .env"
    if df_formato.empty:
        return "No hay datos para analizar"
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        resumen = df_formato.to_string()
        prompt = f"""Eres un experto en SST colombiano. Con base en estos datos de accidentalidad:
{resumen}

Genera 5 recomendaciones prácticas y específicas para reducir la accidentalidad.
Sé conciso, usa viñetas (•) y lenguaje profesional."""
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}],
            max_tokens=600, temperature=0.4
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"
