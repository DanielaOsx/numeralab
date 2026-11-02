"""Funciones para mostrar números de forma clara en tablas y explicaciones."""
import math


def fmt(x, dec=6, fijo=False):
    """Formatea un número.

    Con fijo=False quita los ceros sobrantes (0.5 en lugar de 0.500000).
    Con fijo=True mantiene siempre `dec` decimales (útil en tablas).
    """
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    if isinstance(x, int) and not isinstance(x, bool):
        return str(x)
    if math.isnan(x):
        return "no definido"
    if math.isinf(x):
        return "∞" if x > 0 else "-∞"
    if x == 0:
        return f"{0:.{dec}f}" if fijo else "0"
    if abs(x) < 10 ** (-dec) or abs(x) >= 1e10:
        return f"{x:.4e}"
    s = f"{x:.{dec}f}"
    if not fijo:
        s = s.rstrip("0").rstrip(".")
        if s in ("-0", ""):
            s = "0"
    return s


def fmt_pct(x, dec=4):
    """Formatea un porcentaje (error relativo)."""
    if x is None:
        return "—"
    if math.isinf(x):
        return "∞ %"
    return f"{x:.{min(dec, 4)}f} %"


def par(x, dec=6):
    """Número entre paréntesis si es negativo, para sustituciones como (-0.5)."""
    s = fmt(x, dec)
    return f"({s})" if s.startswith("-") else s
