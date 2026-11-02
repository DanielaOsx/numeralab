"""Gráficas con Matplotlib (se dibujan sobre un Figure incrustado en Tkinter)."""
import numpy as np

ROJO = "#D90429"
NEGRO = "#111111"
GRIS = "#6B7280"
GRIS_CLARO = "#E5E7EB"
VERDE = "#16A34A"


def _muestrear(f, xmin, xmax, n=900):
    xs = np.linspace(xmin, xmax, n)
    ys = f.evaluar_array(xs)
    ys[np.abs(ys) > 1e8] = np.nan
    return xs, ys


def _limites_y(ys, extras=()):
    valores = [float(v) for v in extras] + [0.0]
    v = ys[np.isfinite(ys)]
    if v.size:
        lo, hi = np.percentile(v, [1, 99])
        valores += [float(lo), float(hi)]
    lo, hi = min(valores), max(valores)
    if hi - lo < 1e-12:
        lo, hi = lo - 1, hi + 1
    pad = 0.12 * (hi - lo)
    return lo - pad, hi + pad


def _estilo(ax, xmin, xmax):
    ax.set_facecolor("white")
    ax.grid(True, color=GRIS_CLARO, linewidth=0.9)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.axhline(0, color=NEGRO, linewidth=1.1, zorder=1)
    if xmin < 0 < xmax:
        ax.axvline(0, color=NEGRO, linewidth=1.1, zorder=1)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.set_xlim(xmin, xmax)


def mensaje_vacio(fig, texto):
    fig.clear()
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.5, 0.5, texto, ha="center", va="center", fontsize=13, color=GRIS, transform=ax.transAxes)


def vista_previa(fig, f, xmin, xmax, titulo="Vista previa de f(x)"):
    """Dibuja la función antes de calcular (o cuando se edita)."""
    if f is None or not xmin < xmax:
        mensaje_vacio(fig, "Escriba una función válida para ver su gráfica")
        return
    fig.clear()
    ax = fig.add_subplot(111)
    xs, ys = _muestrear(f, xmin, xmax)
    _estilo(ax, xmin, xmax)
    ax.plot(xs, ys, color=ROJO, linewidth=2.6, label="f(x)")
    ax.set_ylim(*_limites_y(ys))
    ax.set_title(titulo, fontsize=12, fontweight="bold", color=NEGRO)
    ax.legend(loc="best", frameon=False)


def graficar_secante(fig, f, res, compacto=False):
    """Función, secantes de las primeras iteraciones y aproximaciones sobre el eje x."""
    fig.clear()
    ax = fig.add_subplot(111)
    puntos = [res.x0] + [it.x_nuevo for it in res.iteraciones if it.x_nuevo is not None]
    lo, hi = min(puntos), max(puntos)
    span = (hi - lo) or max(1.0, abs(hi))
    xmin, xmax = lo - 0.35 * span, hi + 0.35 * span
    xs, ys = _muestrear(f, xmin, xmax)
    _estilo(ax, xmin, xmax)
    ax.plot(xs, ys, color=ROJO, linewidth=2.6, label="f(x)", zorder=3)

    primeras = [it for it in res.iteraciones[:6] if it.x_nuevo is not None]
    for k, it in enumerate(primeras):
        ax.plot([it.xi, it.x_nuevo], [it.fxi, 0], "--", color=GRIS, linewidth=1.3, zorder=2,
                label="Secante (cada iteración)" if k == 0 else None)
        ax.plot([it.xi], [it.fxi], "o", color=GRIS, markersize=4.5, zorder=4)

    ax.plot(puntos, [0] * len(puntos), "o", color=NEGRO, markersize=7, zorder=5, label="Aproximaciones $x_i$")
    grupos = []                                   # puntos casi iguales comparten una sola etiqueta
    for k, x in enumerate(puntos[:8]):
        if grupos and abs(x - grupos[-1][1]) < 0.045 * (xmax - xmin):
            grupos[-1][0].append(k)
        else:
            grupos.append([[k], x])
    for ks, x in grupos:
        texto = r"$\approx$".join(f"$x_{{{k}}}$" for k in (ks[0], ks[-1])) if len(ks) > 1 else f"$x_{{{ks[0]}}}$"
        ax.annotate(texto, (x, 0), textcoords="offset points", xytext=(0, 12), ha="center", fontsize=9,
                    color=NEGRO)
    ax.plot([res.raiz], [0], "*", color=VERDE, markersize=18, zorder=6,
            label=f"Raíz ≈ ({res.raiz:.6g}, 0)")
    dentro = (xs >= xmin) & (xs <= xmax)
    ax.set_ylim(*_limites_y(ys[dentro], [it.fxi for it in primeras]))
    ax.set_title("Secante modificada" if compacto else "Secante modificada: función y aproximaciones",
                 fontsize=10 if compacto else 12, fontweight="bold")
    leyenda = ax.legend(loc="lower left" if compacto else "best", frameon=True, framealpha=0.9,
                        fontsize=7.5 if compacto else 10)
    # Segunda leyenda: coordenadas (x, f(x)) de los puntos usados en cada iteración
    from matplotlib.lines import Line2D
    filas = [(f"$P_{{{k}}}$ = ({it.xi:.5g}, {it.fxi:.5g})") for k, it in enumerate(res.iteraciones[:4])]
    if filas:
        manijas = [Line2D([], [], marker="o", color=GRIS, linestyle="", markersize=4) for _ in filas]
        ax.add_artist(leyenda)
        ax.legend(manijas, filas, title="Puntos (x, y)", loc="upper right", frameon=True, framealpha=0.9,
                  fontsize=7 if compacto else 9, title_fontsize=7 if compacto else 9)
    if compacto:
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi + 0.55 * (hi - lo))      # espacio libre arriba para la leyenda de puntos
        ax.tick_params(labelsize=8)
        ax.set_xlabel("x", fontsize=8)
        ax.set_ylabel("f(x)", fontsize=8)


def graficar_dorada(fig, f, res, k=None, compacto=False, loc_leyenda=None):
    """Función con el intervalo de la iteración k, x1, x2 y el óptimo; abajo, cómo se reduce el intervalo."""
    fig.clear()
    its = res.iteraciones
    k = len(its) if k is None else max(1, min(k, len(its)))
    it = its[k - 1]
    gs = fig.add_gridspec(2, 1, height_ratios=[3.2, 1.2])
    ax = fig.add_subplot(gs[0])
    ab = fig.add_subplot(gs[1], sharex=ax)

    margen = 0.06 * (res.b - res.a)
    xmin, xmax = res.a - margen, res.b + margen
    xs, ys = _muestrear(f, xmin, xmax)
    _estilo(ax, xmin, xmax)
    ax.plot(xs, ys, color=ROJO, linewidth=2.6, label="f(x)", zorder=3)
    ax.axvspan(it.xl, it.xu, color=ROJO, alpha=0.09, zorder=1,
               label=f"Intervalo iter. {k}: [{it.xl:.4g}, {it.xu:.4g}]")
    ax.plot([it.x1], [it.f1], "o", color=NEGRO, markersize=9, zorder=5, label=f"$x_1$ = ({it.x1:.5g}, {it.f1:.5g})")
    ax.plot([it.x2], [it.f2], "o", markerfacecolor="white", markeredgecolor=NEGRO, markeredgewidth=2,
            markersize=9, zorder=5, label=f"$x_2$ = ({it.x2:.5g}, {it.f2:.5g})")
    for etiqueta, x, y in (("$x_1$", it.x1, it.f1), ("$x_2$", it.x2, it.f2)):
        ax.annotate(etiqueta, (x, y), textcoords="offset points", xytext=(0, 12), ha="center", fontsize=10)
    ax.plot([res.xopt], [res.fopt], "*", color=VERDE, markersize=19, zorder=6,
            label=f"{res.nombre_objetivo().capitalize()} ≈ ({res.xopt:.5g}, {res.fopt:.5g})")
    ax.set_ylim(*_limites_y(ys, [it.f1, it.f2, res.fopt]))
    ax.set_title("Sección dorada" if compacto else "Sección dorada: función, puntos interiores y óptimo",
                 fontsize=10 if compacto else 12, fontweight="bold")
    ax.legend(loc=loc_leyenda or ("lower left" if compacto else "best"), fontsize=7 if compacto else 8,
              frameon=True, framealpha=0.85)
    if compacto:
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, hi + 0.2 * (hi - lo))
    ax.tick_params(labelbottom=False)

    ab.set_facecolor("white")
    ab.grid(True, axis="x", color=GRIS_CLARO)
    for lado in ("top", "right"):
        ab.spines[lado].set_visible(False)
    for j, itj in enumerate(its, start=1):
        activo = j == k
        ab.hlines(j, itj.xl, itj.xu, color=ROJO if activo else "#D1D5DB", linewidth=5 if activo else 3)
    xl, xu = res.intervalo_final
    ab.hlines(len(its) + 1, xl, xu, color=VERDE, linewidth=4)
    ab.plot([res.xopt], [len(its) + 1], "*", color=VERDE, markersize=11)
    ab.set_ylim(len(its) + 1.8, 0.2)
    pasos = list(range(1, len(its) + 1, max(1, -(-len(its) // 5))))
    ab.set_yticks(pasos + [len(its) + 1])
    ab.set_yticklabels([str(p) for p in pasos] + ["final"], fontsize=8)
    ab.set_ylabel("Iteración", fontsize=9)
    ab.set_xlabel("x" if compacto else "x   (cada barra es el intervalo de búsqueda; se va reduciendo)",
                  fontsize=8 if compacto else 9)
    if compacto:
        ax.tick_params(labelsize=8)
        ab.tick_params(labelsize=7)
        ax.set_ylabel("f(x)", fontsize=8)


# ----------------------------------------------------------------------------------
# Gráficas de demostración para la pantalla de inicio (usan los métodos reales)
# ----------------------------------------------------------------------------------
def demo_secante(fig):
    from metodos.secante_modificada import secante_modificada
    from utilidades.evaluador_funciones import FuncionMatematica
    f = FuncionMatematica("exp(-x) - x")
    graficar_secante(fig, f, secante_modificada(f, 1.0, 0.01, 1), compacto=True)


def demo_dorada(fig):
    from metodos.seccion_dorada import seccion_dorada
    from utilidades.evaluador_funciones import FuncionMatematica
    f = FuncionMatematica("2 sin(x) - x^2/10")
    res = seccion_dorada(f, 0, 4, "maximizar", 1, 100, "relativo")
    graficar_dorada(fig, f, res, k=3, compacto=True)
