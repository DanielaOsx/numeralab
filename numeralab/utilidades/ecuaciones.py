"""Ecuaciones con formato matemático (fracciones, exponentes, subíndices).

Convierte LaTeX simple en imágenes PNG usando el motor «mathtext» de Matplotlib
(no necesita instalar LaTeX). También convierte la función escrita por el usuario
(x^2 + x^4, (x^5-12)/sin(x^2)...) a LaTeX con SymPy para mostrarla «bonita».
"""
import io
import re
from functools import lru_cache

import matplotlib

matplotlib.rcParams["mathtext.fontset"] = "cm"
from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from utilidades.formato import fmt  # noqa: E402


# ----------------------------------------------------------------------------------
# Números en formato LaTeX (para armar las sustituciones del procedimiento)
# ----------------------------------------------------------------------------------
def tx(x, dec=6):
    """Número como texto LaTeX: 1.2e-05 -> 1.2\\times10^{-5}, inf -> \\infty."""
    s = fmt(x, dec)
    if s == "∞":
        return r"\infty"
    if s == "-∞":
        return r"-\infty"
    if s in ("no definido", "—"):
        return r"\mathrm{indefinido}"
    m = re.fullmatch(r"(-?[\d.]+)e([+-]\d+)", s)
    if m:
        return f"{m.group(1)}\\times10^{{{int(m.group(2))}}}"
    return s


def txp(x, dec=6):
    """Igual que tx, pero entre paréntesis si es negativo: (-0.5)."""
    s = tx(x, dec)
    return f"({s})" if s.startswith("-") else s


def tx_pct(x, dec=4):
    return tx(x, dec) + r"\%"


def llenar(plantilla, **valores):
    """Reemplaza @nombre@ en una plantilla LaTeX (evita el lío de llaves de las f-strings)."""
    return re.sub(r"@(\w+)@", lambda m: str(valores[m.group(1)]), plantilla)


# ----------------------------------------------------------------------------------
# Función del usuario -> LaTeX
# ----------------------------------------------------------------------------------
def latex_de_funcion(f):
    """LaTeX de una FuncionMatematica (o None si no se puede). Se usa solo para mostrar."""
    try:
        import sympy as sp
        x = sp.Symbol("x")
        local = {
            "x": x, "pi": sp.pi, "e": sp.E, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
            "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "sinh": sp.sinh, "cosh": sp.cosh,
            "tanh": sp.tanh, "exp": sp.exp, "sqrt": sp.sqrt, "abs": sp.Abs,
            "ln": sp.Function("ln"), "log": sp.Function("log"),
        }
        expr = sp.sympify(f.expresion, locals=local, evaluate=False)   # ya validada por el evaluador seguro
        tex = sp.latex(expr, order="none", inv_trig_style="full", mul_symbol=None)
        tex = re.sub(r"\\operatorname\{(\w+)\}", r"\\\1", tex)
        tex = re.sub(r"(?<![\d.])1 (?:\\cdot )?(?=\\frac)", "", tex)     # «1 \frac{1}{x}» -> «\frac{1}{x}»
        return tex
    except Exception:
        return None


# ----------------------------------------------------------------------------------
# Renderizado
# ----------------------------------------------------------------------------------
@lru_cache(maxsize=4096)
def _render(latex, tam, color, fondo, dpi, pad, max_ancho):
    fig = Figure(dpi=dpi)
    fig.patch.set_facecolor(fondo)
    t = fig.text(0, 0, f"${latex}$", fontsize=tam, color=color, va="bottom", ha="left")
    canvas = FigureCanvasAgg(fig)
    bb = t.get_window_extent(canvas.get_renderer())      # aquí se detectan errores de sintaxis LaTeX
    w, h = bb.width + 2 * pad, bb.height + 2 * pad
    if max_ancho and w > max_ancho and tam > 8:
        return _render(latex, max(8.0, tam * max_ancho / w), color, fondo, dpi, pad, 0)
    fig.set_size_inches(w / dpi, h / dpi)
    t.set_position((pad / w, pad / h))
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=fondo)
    return buf.getvalue()


def png_ecuacion(latex, tam=16.0, color="#111827", fondo="#FFFFFF", dpi=110, pad=5, max_ancho=0):
    """PNG (bytes) de una ecuación LaTeX, o None si la sintaxis no es válida."""
    try:
        return _render(latex, float(tam), color, fondo, int(dpi), int(pad), int(max_ancho))
    except Exception:
        return None


def latex_de_texto(texto):
    """LaTeX de la función escrita como texto (o None si no es válida)."""
    from utilidades.evaluador_funciones import ErrorFuncion, FuncionMatematica
    try:
        return latex_de_funcion(FuncionMatematica(texto))
    except ErrorFuncion:
        return None
