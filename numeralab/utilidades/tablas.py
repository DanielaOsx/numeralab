"""Tabla de iteraciones (encabezados y filas ya formateadas), compartida por escritorio y web."""
from utilidades.formato import fmt, fmt_pct


def tabla_iteraciones(metodo, res, dec=6):
    """Devuelve (encabezados, filas) con textos listos para mostrar."""
    if metodo == "secante":
        cols = ["i", "x_i", "f(x_i)", "x_i + δ·x_i", "f(x_i + δ·x_i)", "x_(i+1)", "ε_a (%)"]
        filas = [[it.i, fmt(it.xi, dec, True), fmt(it.fxi, dec, True), fmt(it.xi_pert, dec, True),
                  fmt(it.f_pert, dec, True), fmt(it.x_nuevo, dec, True) if it.x_nuevo is not None else "—",
                  fmt_pct(it.ea, dec) if it.ea is not None else "—"] for it in res.iteraciones]
    else:
        cols = ["i", "a (x_L)", "b (x_U)", "x1", "x2", "f(x1)", "f(x2)", "Intervalo actualizado", "ε_a (%)", "Longitud"]
        F = lambda v: fmt(v, dec, True)
        filas = [[it.i, F(it.xl), F(it.xu), F(it.x1), F(it.x2), F(it.f1), F(it.f2),
                  f"[{fmt(it.xl_nuevo, 4, True)}, {fmt(it.xu_nuevo, 4, True)}]", fmt_pct(it.ea),
                  fmt(it.longitud_nueva, 5, True)] for it in res.iteraciones]
    return cols, filas
