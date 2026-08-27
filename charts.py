import plotly.graph_objects as go
import pandas as pd
from config import PALETA, COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_SEC, COLOR_DANGER, COLOR_WARNING, COLOR_ACCENT

def tema(fig):
    fig.update_layout(
        plot_bgcolor=COLOR_BG, paper_bgcolor=COLOR_CARD,
        font_color=COLOR_TEXT, legend_font_color=COLOR_SEC,
        title_font_color=COLOR_TEXT,
        xaxis=dict(gridcolor=COLOR_BG, tickfont_color=COLOR_SEC),
        yaxis=dict(gridcolor=COLOR_BG, tickfont_color=COLOR_SEC),
        margin=dict(t=60, b=40, l=40, r=20))
    return fig

def g_dia_semana(df, col):
    if not col or col not in df.columns: return None
    orden = ["Lunes","Martes","Miércoles","Miercoles","Jueves","Viernes","Sábado","Sabado","Domingo"]
    ct = df[col].value_counts()
    fil = {k: v for k, v in ct.items() if k in orden}
    of = [d for d in orden if d in fil]
    vl = [fil[d] for d in of]
    fig = go.Figure(go.Bar(x=of, y=vl, marker_color=PALETA[:len(of)], text=vl, textposition="outside"))
    fig.update_layout(title="📅 Día con Más Accidentes", xaxis_title="Día", yaxis_title="Cantidad")
    return tema(fig)

def g_servicio(df, col):
    if not col or col not in df.columns: return None
    ct = df[col].value_counts().head(10)
    fig = go.Figure(go.Bar(y=ct.index[::-1], x=ct.values[::-1], orientation="h",
        marker_color=PALETA[:len(ct)][::-1], text=ct.values[::-1], textposition="outside"))
    fig.update_layout(title="🏭 Áreas/Procesos con Mayor Accidentalidad", xaxis_title="Cantidad", yaxis_title="")
    return tema(fig)

def g_top5(df, col_id):
    if not col_id or col_id not in df.columns: return None
    t5 = df.groupby(col_id).size().nlargest(5).reset_index(name="Eventos")
    fig = go.Figure(go.Bar(x=[str(i) for i in t5[col_id]], y=t5["Eventos"],
        marker_color=PALETA[:5], text=t5["Eventos"], textposition="outside"))
    fig.update_layout(title="👤 Top 5 Trabajadores con Más Eventos", xaxis_title="Identificación", yaxis_title="Eventos")
    return tema(fig)

def g_cie10(df, col):
    if not col or col not in df.columns: return None
    ct = df[col].value_counts().head(10)
    fig = go.Figure(go.Pie(labels=ct.index, values=ct.values, marker_colors=PALETA[:len(ct)], textinfo="label+percent", hole=0.4))
    fig.update_layout(title="🏥 CIE-10 Más Presentados")
    return tema(fig)

def g_tipo_anual(df, col_tipo, col_fecha):
    if not col_tipo or col_tipo not in df.columns: return None
    df = df.copy()
    anio = None
    if col_fecha and col_fecha in df.columns:
        df["_f"] = pd.to_datetime(df[col_fecha], errors="coerce")
        anio = df["_f"].dt.year.dropna().max()
        if anio: df = df[df["_f"].dt.year == anio]
    ct = df[col_tipo].value_counts()
    t = f"📊 Eventos del Año {int(anio)}" if anio else "📊 Eventos por Tipo"
    fig = go.Figure(go.Pie(labels=ct.index, values=ct.values, marker_colors=PALETA[:len(ct)], textinfo="label+value+percent", hole=0.35))
    fig.update_layout(title=t)
    return tema(fig)

def g_tendencia(df, col_fecha):
    if not col_fecha or col_fecha not in df.columns: return None
    df = df.copy()
    df["_f"] = pd.to_datetime(df[col_fecha], errors="coerce")
    df["_m"] = df["_f"].dt.to_period("M").astype(str)
    ct = df.groupby("_m").size().reset_index(name="Eventos")
    fig = go.Figure(go.Scatter(x=ct["_m"], y=ct["Eventos"], mode="lines+markers+text",
        line=dict(color=PALETA[0], width=3), marker=dict(size=8, color=PALETA[0]),
        text=ct["Eventos"], textposition="top center"))
    fig.update_layout(title="📈 Tendencia Mensual", xaxis_title="Mes", yaxis_title="Cantidad")
    return tema(fig)

def g_agente(df, col):
    if not col or col not in df.columns: return None
    ct = df[col].value_counts().head(8)
    fig = go.Figure(go.Bar(x=ct.index, y=ct.values, marker_color=PALETA[2], text=ct.values, textposition="outside"))
    fig.update_layout(title="⚡ Agente del Accidente", xaxis_title="Agente", yaxis_title="Cantidad")
    fig.update_xaxes(tickangle=30)
    return tema(fig)

def g_cuerpo(df, col):
    if not col or col not in df.columns: return None
    ct = df[col].value_counts().head(8)
    fig = go.Figure(go.Pie(labels=ct.index, values=ct.values, marker_colors=PALETA[3:3+len(ct)], textinfo="label+percent", hole=0.3))
    fig.update_layout(title="🦴 Parte del Cuerpo Afectada")
    return tema(fig)

def g_naturaleza(df, col):
    if not col or col not in df.columns: return None
    ct = df[col].value_counts().head(8)
    fig = go.Figure(go.Bar(y=ct.index[::-1], x=ct.values[::-1], orientation="h",
        marker_color=PALETA[4:4+len(ct)][::-1], text=ct.values[::-1], textposition="outside"))
    fig.update_layout(title="🔬 Naturaleza de la Lesión", xaxis_title="Cantidad", yaxis_title="")
    return tema(fig)

def g_estado(df, col):
    if not col or col not in df.columns: return None
    ct = df[col].value_counts()
    colores = {"ABIERTO": COLOR_DANGER, "CERRADO": COLOR_ACCENT, "EN PROCESO": COLOR_WARNING}
    mc = [colores.get(str(x).upper().strip(), "#70A1FF") for x in ct.index]
    fig = go.Figure(go.Pie(labels=ct.index, values=ct.values, marker_colors=mc, textinfo="label+value+percent", hole=0.35))
    fig.update_layout(title="📋 Estado de los Eventos")
    return tema(fig)

def kpi(v, t, c):
    return f"""<div style="background:{COLOR_CARD};border-radius:12px;padding:20px;
    border-left:4px solid {c};text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.3);">
    <div style="font-size:32px;font-weight:bold;color:{c};">{v}</div>
    <div style="font-size:13px;color:{COLOR_SEC};margin-top:5px;">{t}</div></div>"""
