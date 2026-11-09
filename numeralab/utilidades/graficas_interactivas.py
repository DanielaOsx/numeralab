"""Gráficas interactivas (Plotly) para la web: zoom con la rueda, arrastrar para mover, caja de zoom, reinicio...

La función se muestrea en un rango MUCHO más ancho que la vista inicial, así al alejar o mover la gráfica
la curva sigue ahí (como en GeoGebra). Doble clic = volver a la vista inicial.
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utilidades.graficas import GRIS, NEGRO, ROJO, VERDE, _limites_y, _muestrear

GRIS_CLARO = "#E5E7EB"
CONFIG = {"scrollZoom": True, "displaylogo": False, "doubleClick": "reset",
          "modeBarButtonsToRemove": ["lasso2d", "select2d"],
          "toImageButtonOptions": {"format": "png", "filename": "grafica_numeralab", "scale": 2}}
AMPLIAR = 6          # el muestreo cubre AMPLIAR veces el ancho de la vista inicial (a cada lado)


def _curva(f, xmin, xmax):
    ancho = xmax - xmin
    return _muestrear(f, xmin - AMPLIAR * ancho, xmax + AMPLIAR * ancho, 6000)


def _ejes(fig, xmin, xmax, ymin, ymax, **kw):
    ejes = dict(showgrid=True, gridcolor=GRIS_CLARO, zeroline=True, zerolinecolor=NEGRO, zerolinewidth=1.6,
                showline=False, ticks="outside")
    fig.update_xaxes(range=[xmin, xmax], **ejes, **kw.get("x", {}))
    fig.update_yaxes(range=[ymin, ymax], **ejes, **kw.get("y", {}))


def _base(fig, titulo, revision):
    fig.update_layout(title=dict(text=f"<b>{titulo}</b>", x=0.02, font=dict(size=16)), plot_bgcolor="white",
                      paper_bgcolor="white", dragmode="pan", hovermode="closest", uirevision=revision,
                      margin=dict(l=55, r=20, t=55, b=45),
                      legend=dict(bgcolor="rgba(255,255,255,0.88)", bordercolor=GRIS_CLARO, borderwidth=1,
                                  font=dict(size=11)))


def _traza_f(xs, ys):
    return go.Scatter(x=xs, y=ys, mode="lines", name="f(x)", line=dict(color=ROJO, width=3), connectgaps=False,
                      hovertemplate="x = %{x:.6g}<br>f(x) = %{y:.6g}<extra>f(x)</extra>")


def plotly_secante(f, res, revision="secante"):
    puntos = [res.x0] + [it.x_nuevo for it in res.iteraciones if it.x_nuevo is not None]
    lo, hi = min(puntos), max(puntos)
    span = (hi - lo) or max(1.0, abs(hi))
    xmin, xmax = lo - 0.35 * span, hi + 0.35 * span
    xs, ys = _curva(f, xmin, xmax)
    dentro = (xs >= xmin) & (xs <= xmax)
    primeras = [it for it in res.iteraciones[:6] if it.x_nuevo is not None]
    ymin, ymax = _limites_y(ys[dentro], [it.fxi for it in primeras])

    fig = go.Figure()
    fig.add_trace(_traza_f(xs, ys))
    for k, it in enumerate(primeras):
        fig.add_trace(go.Scatter(
            x=[it.xi, it.x_nuevo], y=[it.fxi, 0], mode="lines", line=dict(color=GRIS, width=1.6, dash="dash"),
            name="Secante (cada iteración)", legendgroup="sec", showlegend=k == 0, hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=[it.xi for it in primeras], y=[it.fxi for it in primeras], mode="markers+text", name="Puntos (x_i, f(x_i))",
        marker=dict(color=GRIS, size=8), text=[f"P{k}" for k in range(len(primeras))], textposition="top center",
        hovertemplate="P%{pointNumber}<br>x = %{x:.6g}<br>f(x) = %{y:.6g}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=puntos, y=[0] * len(puntos), mode="markers+text", name="Aproximaciones x_i",
        marker=dict(color=NEGRO, size=10), text=[f"x{k}" if k < 8 else "" for k in range(len(puntos))],
        textposition="top center", hovertemplate="x%{pointNumber} = %{x:.8g}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=[res.raiz], y=[0], mode="markers", name=f"Raíz ≈ ({res.raiz:.6g}, 0)",
        marker=dict(color=VERDE, size=18, symbol="star", line=dict(color="white", width=1)),
        hovertemplate="Raíz ≈ %{x:.8g}<extra></extra>"))
    _base(fig, "Secante modificada: función y aproximaciones", revision)
    _ejes(fig, xmin, xmax, ymin, ymax, x=dict(title="x"), y=dict(title="f(x)"))
    return fig


def plotly_dorada(f, res, k=None, revision="dorada"):
    its = res.iteraciones
    k = len(its) if k is None else max(1, min(k, len(its)))
    it = its[k - 1]
    margen = 0.06 * (res.b - res.a)
    xmin, xmax = res.a - margen, res.b + margen
    xs, ys = _curva(f, xmin, xmax)
    dentro = (xs >= xmin) & (xs <= xmax)
    ymin, ymax = _limites_y(ys[dentro], [it.f1, it.f2, res.fopt])

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.76, 0.24], vertical_spacing=0.05)
    fig.add_trace(_traza_f(xs, ys), row=1, col=1)
    fig.add_vrect(x0=it.xl, x1=it.xu, fillcolor=ROJO, opacity=0.09, line_width=0, layer="below", row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers", marker=dict(color="rgba(217,4,41,0.25)", size=12, symbol="square"),
        name=f"Intervalo iter. {k}: [{it.xl:.4g}, {it.xu:.4g}]"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[it.x1], y=[it.f1], mode="markers+text", text=["x1"], textposition="top center",
        marker=dict(color=NEGRO, size=12), name=f"x1 = ({it.x1:.5g}, {it.f1:.5g})",
        hovertemplate="x1<br>x = %{x:.8g}<br>f = %{y:.8g}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[it.x2], y=[it.f2], mode="markers+text", text=["x2"], textposition="top center",
        marker=dict(color="white", size=12, line=dict(color=NEGRO, width=2.5)),
        name=f"x2 = ({it.x2:.5g}, {it.f2:.5g})",
        hovertemplate="x2<br>x = %{x:.8g}<br>f = %{y:.8g}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=[res.xopt], y=[res.fopt], mode="markers",
        marker=dict(color=VERDE, size=19, symbol="star", line=dict(color="white", width=1)),
        name=f"{res.nombre_objetivo().capitalize()} ≈ ({res.xopt:.5g}, {res.fopt:.5g})",
        hovertemplate="Óptimo<br>x = %{x:.8g}<br>f = %{y:.8g}<extra></extra>"), row=1, col=1)

    # Abajo: cómo se reduce el intervalo (una barra por iteración)
    gx, gy = [], []
    for j, itj in enumerate(its, start=1):
        if j != k:
            gx += [itj.xl, itj.xu, None]
            gy += [j, j, None]
    fig.add_trace(go.Scatter(x=gx, y=gy, mode="lines", line=dict(color="#D1D5DB", width=5), showlegend=False,
                             hoverinfo="skip"), row=2, col=1)
    fig.add_trace(go.Scatter(x=[it.xl, it.xu], y=[k, k], mode="lines", line=dict(color=ROJO, width=8),
                             showlegend=False, hovertemplate=f"Iteración {k}<br>x = %{{x:.6g}}<extra></extra>"),
                  row=2, col=1)
    xl, xu = res.intervalo_final
    fig.add_trace(go.Scatter(x=[xl, xu], y=[len(its) + 1] * 2, mode="lines", line=dict(color=VERDE, width=7),
                             showlegend=False, hovertemplate="Intervalo final<br>x = %{x:.8g}<extra></extra>"),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=[res.xopt], y=[len(its) + 1], mode="markers", showlegend=False,
                             marker=dict(color=VERDE, size=11, symbol="star"), hoverinfo="skip"), row=2, col=1)

    _base(fig, "Sección dorada: función, puntos interiores y óptimo", revision)
    fig.update_layout(height=640)
    _ejes(fig, xmin, xmax, ymin, ymax, y=dict(title="f(x)"))
    fig.update_yaxes(range=[len(its) + 1.8, 0.2], fixedrange=True, zeroline=False, title="Iteración", row=2, col=1,
                     tickmode="array", tickvals=list(range(1, len(its) + 1, max(1, -(-len(its) // 5)))) + [len(its) + 1],
                     ticktext=[str(v) for v in range(1, len(its) + 1, max(1, -(-len(its) // 5)))] + ["final"])
    fig.update_xaxes(title="x   (cada barra es el intervalo de búsqueda; se va reduciendo)", row=2, col=1)
    return fig
