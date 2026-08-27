import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from config import PALETA, COLOR_BG, COLOR_CARD, COLOR_TEXT, COLOR_SEC

def tema(fig):
    fig.update_layout(
        plot_bgcolor=COLOR_BG, paper_bgcolor=COLOR_CARD,
        font_color=COLOR_TEXT, legend_font_color=COLOR_SEC,
        title_font_color=COLOR_TEXT,
        xaxis=dict(gridcolor=COLOR_BG, tickfont_color=COLOR_SEC),
        yaxis=dict(gridcolor=COLOR_BG, tickfont_color=COLOR_SEC),
        margin=dict(t=60, b=40, l=40, r=20)
    )
    return fig

def grafico_dia_semana(df, col):
    if not col or col not in df.columns:
        return None
    orden = ["Lunes", "Martes", "Miércoles", "Miercoles", "Jueves", "Viernes", "Sábado", "Sabado", "Domingo"]
    conteo = df[col].value_counts()
    filtrados = {k: v for k, v in conteo.items() if k in orden}
    orden_f = [d for d in orden if d in filtrados]
    vals = [filtrados[d] for d in orden_f]
    fig = go.Figure(go.Bar(x=orden_f, y=vals, marker_color=PALETA[:len(orden_f)], text=vals, textposition="outside"))
    fig.update_layout(title="📅 Día de la Semana con Más Accidentes", xaxis_title="Día", yaxis_title="Cantidad")
    return tema(fig)

def grafico_servicio(df, col):
    if not col or col not in df.columns:
        return None
    conteo = df[col].value_counts().head(10)
    fig = go.Figure(go.Bar(
        y=conteo.index[::-1], x=conteo.values[::-1], orientation="h",
        marker_color=PALETA[:len(conteo)][::-1], text=conteo.values[::-1], textposition="outside"
    ))
    fig.update_layout(title="🏭 Servicios con Mayor Accidentalidad", xaxis_title="Cantidad", yaxis_title="Servicio")
    return tema(fig)

def grafico_top5_trabajadores(df, col_id, col_cie):
    if not col_id or col_id not in df.columns:
        return None
    top5 = df.groupby(col_id).size().nlargest(5).reset_index(name="Eventos")
    fig = go.Figure(go.Bar(
        x=[str(i) for i in top5[col_id]], y=top5["Eventos"],
        marker_color=PALETA[:5], text=top5["Eventos"], textposition="outside"
    ))
    fig.update_layout(title="👤 Top 5 Trabajadores con Más Eventos (CIE-10)", xaxis_title="Identificación", yaxis_title="N° Eventos")
    return tema(fig)

def grafico_cie10(df, col):
    if not col or col not in df.columns:
        return None
    conteo = df[col].value_counts().head(10)
    fig = go.Figure(go.Pie(labels=conteo.index, values=conteo.values, marker_colors=PALETA[:len(conteo)], textinfo="label+percent", hole=0.4))
    fig.update_layout(title="🏥 Patologías CIE-10 Más Presentadas")
    return tema(fig)

def grafico_tipo_anual(df, col_tipo, col_fecha):
    if not col_tipo or col_tipo not in df.columns:
        return None
    df = df.copy()
    anio = None
    if col_fecha and col_fecha in df.columns:
        df["_f"] = pd.to_datetime(df[col_fecha], errors="coerce")
        anio = df["_f"].dt.year.dropna().max()
        if anio:
            df = df[df["_f"].dt.year == anio]
    conteo = df[col_tipo].value_counts()
    titulo = "📊 Eventos del Año"
    if anio:
        titulo += f" {int(anio)}"
    fig = go.Figure(go.Pie(labels=conteo.index, values=conteo.values, marker_colors=PALETA[:len(conteo)], textinfo="label+value+percent", hole=0.35))
    fig.update_layout(title=titulo)
    return tema(fig)

def grafico_tendencia_mensual(df, col_fecha):
    if not col_fecha or col_fecha not in df.columns:
        return None
    df = df.copy()
    df["_f"] = pd.to_datetime(df[col_fecha], errors="coerce")
    df["_m"] = df["_f"].dt.to_period("M").astype(str)
    conteo = df.groupby("_m").size().reset_index(name="Eventos")
    fig = go.Figure(go.Scatter(
        x=conteo["_m"], y=conteo["Eventos"], mode="lines+markers+text",
        line=dict(color=PALETA[0], width=3), marker=dict(size=8, color=PALETA[0]),
        text=conteo["Eventos"], textposition="top center"
    ))
    fig.update_layout(title="📈 Tendencia Mensual de Eventos", xaxis_title="Mes", yaxis_title="Cantidad")
    return tema(fig)

def grafico_mecanismo(df, col):
    if not col or col not in df.columns:
        return None
    conteo = df[col].value_counts().head(8)
    fig = go.Figure(go.Bar(x=conteo.index, y=conteo.values, marker_color=PALETA[2], text=conteo.values, textposition="outside"))
    fig.update_layout(title="🔧 Mecanismos de Accidente", xaxis_title="Mecanismo", yaxis_title="Cantidad")
    fig.update_xaxes(tickangle=30)
    return tema(fig)

def grafico_parte_cuerpo(df, col):
    if not col or col not in df.columns:
        return None
    conteo = df[col].value_counts().head(8)
    fig = go.Figure(go.Pie(labels=conteo.index, values=conteo.values, marker_colors=PALETA[3:3+len(conteo)], textinfo="label+percent", hole=0.3))
    fig.update_layout(title="🦴 Parte del Cuerpo Afectada")
    return tema(fig)

def kpi_card(valor, titulo, color):
    return f"""<div style="background:{COLOR_CARD};border-radius:12px;padding:20px;
    border-left:4px solid {color};text-align:center;box-shadow:0 4px 15px rgba(0,0,0,0.3);">
    <div style="font-size:32px;font-weight:bold;color:{color};">{valor}</div>
    <div style="font-size:13px;color:{COLOR_SEC};margin-top:5px;">{titulo}</div></div>"""
