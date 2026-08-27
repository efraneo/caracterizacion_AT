from openai import OpenAI
import streamlit as st

def analizar_datos_ia(df_f, df_b, pregunta):
    if not st.secrets.get("OPENAI_API_KEY"):
        return "⚠️ Configure OPENAI_API_KEY en secrets de Streamlit"
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        rf = df_f.head(30).to_string() if not df_f.empty else "Sin datos"
        rb = df_b.head(15).to_string() if not df_b.empty else "Sin datos"
        prompt = f"""Eres experto en SST colombiano. Analiza estos datos y responde en español:
EVENTOS:\n{rf}\n\nTRABAJADORES:\n{rb}\n\nPregunta: {pregunta}
Responde de forma concisa y profesional."""
        r = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}],
            max_tokens=500, temperature=0.3)
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"

def generar_recomendaciones(df_f):
    if not st.secrets.get("OPENAI_API_KEY"):
        return "⚠️ Configure OPENAI_API_KEY en secrets de Streamlit"
    if df_f.empty:
        return "Sin datos para analizar"
    try:
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        prompt = f"""Eres experto en SST colombiano. Datos de accidentalidad:
{df_f.to_string()}
Genera 5 recomendaciones prácticas para reducir la accidentalidad. Usa viñetas (•)."""
        r = client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}],
            max_tokens=600, temperature=0.4)
        return r.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {str(e)}"
