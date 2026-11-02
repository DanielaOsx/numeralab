"""Método de la Secante Modificada (búsqueda de raíces, sin derivar).

    x_(i+1) = x_i - δ·x_i·f(x_i) / [ f(x_i + δ·x_i) - f(x_i) ]

Este módulo NO depende de la interfaz: devuelve un ResultadoSecante con todos
los datos de cada iteración y el texto del procedimiento paso a paso.
"""
import math
from dataclasses import dataclass, field
from typing import List, Optional

from utilidades.evaluador_funciones import ErrorEvaluacion, ErrorParametro
from utilidades.ecuaciones import latex_de_texto, llenar, tx, tx_pct, txp
from utilidades.formato import fmt, fmt_pct, par

FORMULA = "x_(i+1) = x_i − δ·x_i·f(x_i) / [ f(x_i + δ·x_i) − f(x_i) ]"
FORMULA_ERROR = "ε_a = | (x_nuevo − x_anterior) / x_nuevo | × 100 %"

TEX_FORMULA = r"x_{i+1}=x_i-\frac{\delta\,x_i\,f(x_i)}{f(x_i+\delta\,x_i)-f(x_i)}"
TEX_ERROR = (r"\varepsilon_a=\left|\frac{x_{\mathrm{nuevo}}-x_{\mathrm{anterior}}}"
             r"{x_{\mathrm{nuevo}}}\right|\times100\%")


def _eq_funcion(texto):
    tex = latex_de_texto(texto)
    return ("eq", "f(x)=" + tex) if tex else ("calc", f"f(x) = {texto}")


def bloques_ayuda():
    """Contenido inicial de la pestaña «Calculadora» (antes de calcular)."""
    return [("h2", "Fórmula del método"), ("eqf", TEX_FORMULA), ("eqf", TEX_ERROR),
            ("p", "Es un método ABIERTO: necesita UN valor inicial x₀ distinto de cero y una perturbación "
                  "relativa δ (por ejemplo 0.01). Se repite hasta que el error relativo aproximado sea menor "
                  "que la tolerancia.")]


@dataclass
class IteracionSecante:
    i: int
    xi: float
    fxi: float
    dx: float
    xi_pert: float
    f_pert: float
    numerador: float
    denominador: float
    x_nuevo: Optional[float]
    ea: Optional[float]
    nota: str = ""


@dataclass
class ResultadoSecante:
    funcion: str
    x0: float
    delta: float
    tol: float
    max_iter: int
    iteraciones: List[IteracionSecante] = field(default_factory=list)
    raiz: Optional[float] = None
    f_raiz: Optional[float] = None
    ea_final: Optional[float] = None
    convergio: bool = False
    estado: str = "error"          # "convergio" | "max_iter" | "error"
    mensaje: str = ""
    advertencias: List[str] = field(default_factory=list)

    @property
    def n_iter(self):
        return len(self.iteraciones)

    def bloques_resumen(self, dec=6):
        """Texto del resumen para la pestaña «Calculadora»: lista de (estilo, contenido)."""
        N = lambda v: tx(v, dec)
        b = [("h2", "Fórmula utilizada"), ("eqf", TEX_FORMULA), ("eqf", TEX_ERROR),
             ("h2", "Datos"), _eq_funcion(self.funcion),
             ("eq", llenar(r"x_0=@x0@\qquad\delta=@d@\qquad\mathrm{tol}=@t@\%", x0=N(self.x0), d=N(self.delta),
                           t=N(self.tol))),
             ("p", f"Máximo de iteraciones: {self.max_iter}"),
             ("h2", "Interpretación")]
        if self.convergio:
            b.append(("ok", f"La raíz aproximada es x ≈ {fmt(self.raiz, dec)}. "
                            f"En ese punto f(x) ≈ {fmt(self.f_raiz, dec)}, es decir, muy cerca de cero."))
        else:
            b.append(("warn", "El método no cumplió la tolerancia: la última aproximación "
                              f"(x ≈ {fmt(self.raiz, dec)}) puede no ser una raíz confiable."))
        b.append(("h2", "Puntos de la gráfica (x, y)"))
        for k, it in enumerate(self.iteraciones[:6]):
            b.append(("eq", llenar(r"P_@k@=(x_@k@,\ f(x_@k@))=(@x@,\ @y@)", k=k, x=N(it.xi), y=N(it.fxi))))
        if self.raiz is not None:
            b.append(("eqr", llenar(r"\mathrm{Ra\acute{\imath}z}=(@x@,\ 0)", x=N(self.raiz))))
        b.append(("p", "La raíz aproximada es el punto donde la curva cruza el eje x."))
        b.append(("p", "La secante modificada reemplaza la derivada de Newton-Raphson por una pendiente "
                       "estimada con un punto muy cercano (x + δ·x), por eso solo necesita un valor inicial."))
        for a in self.advertencias:
            b.append(("warn", "⚠ " + a))
        return b


def _validar(x0, delta, tol, max_iter):
    for nombre, v in (("x₀", x0), ("δ", delta), ("la tolerancia", tol)):
        if v is None or not math.isfinite(v):
            raise ErrorParametro(f"El valor de {nombre} debe ser un número finito.")
    if tol <= 0:
        raise ErrorParametro("La tolerancia debe ser mayor que cero.")
    if delta == 0:
        raise ErrorParametro("δ no puede ser cero: la perturbación δ·x sería nula y el denominador también.")
    if int(max_iter) != max_iter or max_iter < 1:
        raise ErrorParametro("El máximo de iteraciones debe ser un entero positivo.")
    if x0 == 0:
        raise ErrorParametro(
            "Con x₀ = 0 la perturbación δ·x₀ también vale 0 y habría una división entre cero. "
            "Elija un valor inicial distinto de cero (por ejemplo 0.5 o 1)."
        )


def secante_modificada(f, x0, delta, tol, max_iter=100):
    """Ejecuta el método. `f` es una FuncionMatematica; `tol` es un porcentaje."""
    _validar(x0, delta, tol, max_iter)
    max_iter = int(max_iter)
    res = ResultadoSecante(f.texto, float(x0), float(delta), float(tol), max_iter)
    if abs(delta) > 0.5:
        res.advertencias.append("δ es muy grande: la pendiente estimada puede ser mala. Valores típicos: 0.01 o 0.001.")
    if abs(delta) < 1e-9:
        res.advertencias.append("δ es extremadamente pequeño: puede haber errores de redondeo en el denominador.")

    x = float(x0)
    for i in range(1, max_iter + 1):
        if x == 0:
            res.estado, res.mensaje = "error", (
                f"En la iteración {i} se obtuvo x = 0, entonces δ·x = 0 y no se puede continuar. "
                "Pruebe con otro valor inicial.")
            break
        try:
            fx = f.evaluar(x)
            dx = delta * x
            xp = x + dx
            fp = f.evaluar(xp)
        except ErrorEvaluacion as e:
            if i == 1:
                raise
            res.estado, res.mensaje = "error", f"Iteración {i}: {e}"
            break
        num = dx * fx
        den = fp - fx
        if den == 0 or not math.isfinite(num / den if den != 0 else math.inf):
            res.iteraciones.append(IteracionSecante(i, x, fx, dx, xp, fp, num, den, None, None,
                                                    "El denominador f(x+δx) − f(x) vale 0."))
            res.estado, res.mensaje = "error", (
                f"Iteración {i}: el denominador f(x+δ·x) − f(x) es cero (la función es plana en ese punto). "
                "Cambie x₀ o δ.")
            break
        x_nuevo = x - num / den
        nota = ""
        if not math.isfinite(x_nuevo) or abs(x_nuevo) > 1e12:
            res.iteraciones.append(IteracionSecante(i, x, fx, dx, xp, fp, num, den, None, None,
                                                    "El valor creció sin control."))
            res.estado, res.mensaje = "error", f"Iteración {i}: el método diverge (x se hace enorme)."
            break
        if x_nuevo != 0:
            ea = abs((x_nuevo - x) / x_nuevo) * 100
        else:
            try:
                f0 = f.evaluar(0.0)
            except ErrorEvaluacion:
                f0 = math.inf
            if abs(f0) < 1e-12:
                ea, nota = 0.0, "x_nuevo = 0 y f(0) = 0: es una raíz exacta."
            else:
                ea, nota = math.inf, "x_nuevo = 0: el error relativo no está definido (división entre 0)."
        res.iteraciones.append(IteracionSecante(i, x, fx, dx, xp, fp, num, den, x_nuevo, ea, nota))
        x = x_nuevo
        if ea < tol:
            res.convergio, res.estado = True, "convergio"
            break
    else:
        res.estado = "max_iter"

    res.raiz = x
    try:
        res.f_raiz = f.evaluar(x)
    except ErrorEvaluacion:
        res.f_raiz = None
    ultimas = [it.ea for it in res.iteraciones if it.ea is not None]
    res.ea_final = ultimas[-1] if ultimas else None

    if res.estado == "convergio":
        res.mensaje = (f"Convergió en {res.n_iter} iteración(es): ε_a = {fmt_pct(res.ea_final)} "
                       f"< {fmt(res.tol)} %.")
        if res.f_raiz is not None and abs(res.f_raiz) > 1e-2:
            res.advertencias.append(
                f"|f(raíz)| = {fmt(abs(res.f_raiz), 4)} no es pequeño: revise que realmente haya una raíz cerca.")
    elif res.estado == "max_iter":
        res.mensaje = (f"Se alcanzó el máximo de iteraciones ({max_iter}) sin cumplir la tolerancia "
                       f"(último ε_a = {fmt_pct(res.ea_final)}). El método no convergió: pruebe otro x₀ o δ.")
    return res


# ----------------------------------------------------------------------------------
# Procedimiento paso a paso (las ecuaciones se escriben en LaTeX para mostrarlas con formato)
# ----------------------------------------------------------------------------------
def generar_pasos(res, dec=6):
    """Devuelve una lista de páginas: (título, [(estilo, contenido), ...]).

    Estilos de texto: h1, h2, p, ok, warn, calc.  Estilos de ecuación (LaTeX): eq, eqf (fórmula), eqr (resultado).
    """
    F = lambda v: fmt(v, dec)
    N = lambda v: tx(v, dec)
    NP = lambda v: txp(v, dec)
    paginas = []

    b = [("h1", "Planteamiento"),
         ("p", "Buscamos una raíz de f(x), es decir, un valor de x donde f(x) = 0. "
               "A diferencia de Newton-Raphson, aquí NO se deriva: la pendiente se estima moviendo x un poquito "
               "(δ·x) y viendo cuánto cambia f. Es un método ABIERTO: parte de un solo valor inicial."),
         ("h2", "Datos del problema"),
         _eq_funcion(res.funcion),
         ("eq", llenar(r"x_0=@x0@\qquad\delta=@d@", x0=N(res.x0), d=N(res.delta))),
         ("p", f"δ mueve x un {fmt(res.delta * 100, 4)} % de su valor.  Tolerancia: {F(res.tol)} %.  "
               f"Máximo de iteraciones: {res.max_iter}."),
         ("h2", "Fórmulas"),
         ("eqf", TEX_FORMULA), ("eqf", TEX_ERROR),
         ("h2", "Condición de parada"),
         ("eq", llenar(r"\varepsilon_a<@t@\%", t=N(res.tol))),
         ("p", f"Repetimos hasta cumplirla (o hasta llegar a {res.max_iter} iteraciones).")]
    paginas.append(("Planteamiento", b))

    for it in res.iteraciones:
        b = [("h1", f"Iteración {it.i}"),
             ("h2", "Paso 1 · Valor de partida"),
             ("p", "Partimos del valor inicial x₀." if it.i == 1 else "Partimos del valor que salió en la iteración anterior."),
             ("eq", llenar(r"x_i=@xi@", xi=N(it.xi))),
             ("h2", "Paso 2 · El «empujoncito» δ·x_i"),
             ("p", "Necesitamos un segundo punto muy cercano. Lo fabricamos moviendo x_i un poquito:"),
             ("eq", llenar(r"\delta\,x_i=@d@\times@xi@=@dx@", d=N(res.delta), xi=NP(it.xi), dx=N(it.dx))),
             ("eq", llenar(r"x_i+\delta\,x_i=@xi@+@dx@=@xp@", xi=N(it.xi), dx=NP(it.dx), xp=N(it.xi_pert))),
             ("h2", "Paso 3 · Evaluar la función en los dos puntos"),
             ("p", "Reemplazamos cada valor en f(x):"),
             ("eq", llenar(r"f(x_i)=f(@xi@)=@f@", xi=N(it.xi), f=N(it.fxi))),
             ("eq", llenar(r"f(x_i+\delta\,x_i)=f(@xp@)=@f@", xp=N(it.xi_pert), f=N(it.f_pert))),
             ("h2", "Paso 4 · Numerador y denominador"),
             ("p", "Numerador:"),
             ("eq", llenar(r"\delta\,x_i\,f(x_i)=@dx@\times@fx@=@n@", dx=NP(it.dx), fx=NP(it.fxi),
                           n=N(it.numerador))),
             ("p", "Denominador:"),
             ("eq", llenar(r"f(x_i+\delta\,x_i)-f(x_i)=@fp@-@fx@=@d@", fp=NP(it.f_pert), fx=NP(it.fxi),
                           d=N(it.denominador)))]
        if it.x_nuevo is None:
            b += [("warn", "✖ " + (it.nota or "No se pudo calcular el nuevo valor.")),
                  ("warn", "El método se detiene aquí. " + res.mensaje)]
            paginas.append((f"Iteración {it.i}", b))
            continue
        b += [("h2", "Paso 5 · Nuevo valor"),
              ("eq", r"x_{i+1}=x_i-\frac{\mathrm{Numerador}}{\mathrm{Denominador}}"),
              ("eq", llenar(r"x_{i+1}=@xi@-\frac{@n@}{@d@}", xi=N(it.xi), n=N(it.numerador), d=N(it.denominador))),
              ("eqr", llenar(r"x_{i+1}=@xn@", xn=N(it.x_nuevo))),
              ("h2", "Paso 6 · Error relativo aproximado")]
        if it.x_nuevo != 0:
            b.append(("eq", llenar(r"\varepsilon_a=\left|\frac{@xn@-@xi@}{@xn@}\right|\times100=@ea@",
                                   xn=N(it.x_nuevo), xi=NP(it.xi), ea=tx_pct(it.ea))))
        else:
            b.append(("eq", llenar(r"\varepsilon_a=@ea@", ea=tx_pct(it.ea))))
        if it.nota:
            b.append(("warn", it.nota))
        b.append(("h2", "Paso 7 · ¿Ya cumplimos la tolerancia?"))
        ok = it.ea < res.tol
        b.append(("eq", llenar(r"\varepsilon_a=@ea@\ @op@\ @t@\%", ea=tx_pct(it.ea),
                               op=r"<" if ok else r"\geq", t=N(res.tol))))
        if ok:
            b.append(("ok", "SÍ cumple la tolerancia. Terminamos."))
        else:
            b.append(("warn", f"NO cumple. Repetimos con x_i = {F(it.x_nuevo)}."))
        paginas.append((f"Iteración {it.i}", b))

    b = [("h1", "Resultado final"),
         ("p", res.mensaje),
         ("eqr", llenar(r"x\approx@x@", x=N(res.raiz)))]
    if res.f_raiz is not None:
        b.append(("eq", llenar(r"f(@x@)=@f@", x=N(res.raiz), f=N(res.f_raiz))))
    b.append(("eq", llenar(r"\varepsilon_a=@ea@", ea=tx_pct(res.ea_final) if res.ea_final is not None else "-")))
    b.append(("p", f"Iteraciones realizadas: {res.n_iter}"))
    for a in res.advertencias:
        b.append(("warn", "⚠ " + a))
    paginas.append(("Resultado", b))
    return paginas
