"""Método de la Sección Dorada (optimización de una variable, sin derivar).

IMPORTANTE: este método busca un MÁXIMO o un MÍNIMO local dentro de un
intervalo [a, b]. No sirve para encontrar raíces directamente.

    R = (√5 − 1)/2 = 0.618034...
    d = R·(x_U − x_L)        x1 = x_L + d        x2 = x_U − d

Este módulo no depende de la interfaz.
"""
import math
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from utilidades.evaluador_funciones import ErrorEvaluacion, ErrorParametro
from utilidades.ecuaciones import latex_de_texto, llenar, tx, tx_pct, txp
from utilidades.formato import fmt, fmt_pct, par

R = (math.sqrt(5) - 1) / 2
UNO_MENOS_R = 1 - R

FORMULA_D = "d = R·(x_U − x_L)      con R = (√5 − 1)/2 = 0.618034"
FORMULA_PUNTOS = "x1 = x_L + d        x2 = x_U − d"
FORMULA_ERROR = "ε_a = (1 − R)·| (x_U − x_L) / x_opt | × 100 %      con 1 − R = 0.381966"

TEX_R = r"R=\frac{\sqrt{5}-1}{2}=0.618034"
TEX_D = r"d=R\,(x_U-x_L)"
TEX_PUNTOS = r"x_1=x_L+d\qquad\qquad x_2=x_U-d"
TEX_ERROR = (r"\varepsilon_a=(1-R)\left|\frac{x_U-x_L}{x_{\mathrm{opt}}}\right|\times100\%"
             r"\qquad\left(1-R=0.381966\right)")


def _eq_funcion(texto):
    tex = latex_de_texto(texto)
    return ("eq", "f(x)=" + tex) if tex else ("calc", f"f(x) = {texto}")


def _condiciones(maxim):
    if maxim:
        return [("eq", r"\mathrm{Si}\ f(x_1)>f(x_2)\ \Rightarrow\ x_L=x_2"),
                ("p", "el máximo está entre x2 y x_U (se descarta el lado izquierdo)"),
                ("eq", r"\mathrm{Si}\ f(x_2)>f(x_1)\ \Rightarrow\ x_U=x_1"),
                ("p", "el máximo está entre x_L y x1 (se descarta el lado derecho)")]
    return [("eq", r"\mathrm{Si}\ f(x_1)<f(x_2)\ \Rightarrow\ x_L=x_2"),
            ("p", "el mínimo está entre x2 y x_U (se descarta el lado izquierdo)"),
            ("eq", r"\mathrm{Si}\ f(x_2)<f(x_1)\ \Rightarrow\ x_U=x_1"),
            ("p", "el mínimo está entre x_L y x1 (se descarta el lado derecho)")]


def bloques_ayuda():
    """Contenido inicial de la pestaña «Calculadora» (antes de calcular)."""
    return [("h2", "Fórmulas del método"), ("eqf", TEX_R), ("eqf", TEX_D), ("eqf", TEX_PUNTOS),
            ("eqf", TEX_ERROR),
            ("p", "Es un método de búsqueda por INTERVALOS: sirve para hallar un MÁXIMO o MÍNIMO de f(x) "
                  "dentro de [a, b]. No se usa para hallar raíces. Encuentra un óptimo local: el resultado "
                  "depende de la función y del intervalo.")]


@dataclass
class IteracionDorada:
    i: int
    xl: float
    xu: float
    d: float
    x1: float
    x2: float
    f1: float
    f2: float
    reutilizado: Optional[str]      # "x1", "x2" o None (qué punto viene de la iteración anterior)
    mejor_x1: bool                  # True si x1 es mejor que x2 para el objetivo
    empate: bool
    xopt: float
    fopt: float
    xl_nuevo: float
    xu_nuevo: float
    ea: float                       # error relativo aproximado (%)
    longitud: float                 # x_U - x_L antes de recortar
    longitud_nueva: float           # tamaño del intervalo ya recortado


@dataclass
class ResultadoDorada:
    funcion: str
    a: float
    b: float
    objetivo: str
    criterio: str
    tol: float
    max_iter: int
    iteraciones: List[IteracionDorada] = field(default_factory=list)
    xopt: Optional[float] = None
    fopt: Optional[float] = None
    intervalo_final: Tuple[float, float] = (0.0, 0.0)
    ea_final: Optional[float] = None
    evaluaciones: int = 0
    convergio: bool = False
    estado: str = "error"          # "convergio" | "max_iter"
    mensaje: str = ""
    advertencias: List[str] = field(default_factory=list)

    @property
    def n_iter(self):
        return len(self.iteraciones)

    @property
    def maximizar(self):
        return self.objetivo == "maximizar"

    def nombre_objetivo(self):
        return "máximo" if self.maximizar else "mínimo"

    def texto_criterio(self):
        if self.criterio == "relativo":
            return f"ε_a < {fmt(self.tol)} %"
        return f"longitud del intervalo < {fmt(self.tol)}"

    def bloques_resumen(self, dec=6):
        N = lambda v: tx(v, dec)
        tol_tex = (llenar(r"\varepsilon_a<@t@\%", t=N(self.tol)) if self.criterio == "relativo"
                   else llenar(r"x_U-x_L<@t@", t=N(self.tol)))
        b = [("h2", "Fórmulas utilizadas"), ("eqf", TEX_R), ("eqf", TEX_D), ("eqf", TEX_PUNTOS), ("eqf", TEX_ERROR),
             ("h2", "Datos"), _eq_funcion(self.funcion),
             ("eq", llenar(r"[a,\ b]=[@a@,\ @b@]", a=N(self.a), b=N(self.b))),
             ("p", f"Objetivo: {self.nombre_objetivo()}.  Condición de parada:"),
             ("eq", tol_tex),
             ("p", f"Máximo de iteraciones: {self.max_iter}"),
             ("h2", "Interpretación")]
        b.append(("ok" if self.convergio else "warn",
                  f"El {self.nombre_objetivo()} aproximado está en x ≈ {fmt(self.xopt, dec)}, "
                  f"donde f(x) ≈ {fmt(self.fopt, dec)}."))
        if self.iteraciones:
            u = self.iteraciones[-1]
            b.append(("h2", "Puntos de la gráfica (x, y)"))
            b.append(("eq", llenar(r"P_1=(x_1,\ f(x_1))=(@x@,\ @y@)", x=N(u.x1), y=N(u.f1))))
            b.append(("eq", llenar(r"P_2=(x_2,\ f(x_2))=(@x@,\ @y@)", x=N(u.x2), y=N(u.f2))))
            b.append(("eq", llenar(r"A=(x_L,\ 0)=(@x@,\ 0)\qquad B=(x_U,\ 0)=(@y@,\ 0)",
                                   x=N(self.intervalo_final[0]), y=N(self.intervalo_final[1]))))
            b.append(("eqr", llenar(r"\mathrm{\acute{O}ptimo}=(@x@,\ @y@)", x=N(self.xopt), y=N(self.fopt))))
        b.append(("p", "La sección dorada encuentra un óptimo LOCAL dentro del intervalo elegido. "
                       "El resultado depende de la función y del intervalo: si hay varios máximos o mínimos, "
                       "puede encontrar solo uno de ellos. No se usa para hallar raíces."))
        for a in self.advertencias:
            b.append(("warn", "⚠ " + a))
        return b


def _validar(a, b, objetivo, tol, max_iter, criterio):
    for nombre, v in (("a", a), ("b", b), ("la tolerancia", tol)):
        if v is None or not math.isfinite(v):
            raise ErrorParametro(f"El valor de {nombre} debe ser un número finito.")
    if not a < b:
        raise ErrorParametro("El límite inferior a debe ser menor que el límite superior b (a < b).")
    if objetivo not in ("minimizar", "maximizar"):
        raise ErrorParametro("El objetivo debe ser minimizar o maximizar.")
    if criterio not in ("relativo", "longitud"):
        raise ErrorParametro("Criterio de parada no válido.")
    if tol <= 0:
        raise ErrorParametro("La tolerancia debe ser mayor que cero.")
    if int(max_iter) != max_iter or max_iter < 1:
        raise ErrorParametro("El máximo de iteraciones debe ser un entero positivo.")


def _validar_dominio(f, a, b, puntos=41):
    """La función debe estar definida en todo [a, b] (se revisan los extremos y puntos intermedios)."""
    for k in range(puntos):
        x = a + (b - a) * k / (puntos - 1)
        try:
            f.evaluar(x)
        except ErrorEvaluacion:
            raise ErrorParametro(
                f"La función no está definida en todo el intervalo [{a:g}, {b:g}]: falla en x ≈ {x:g} "
                "(división entre cero, raíz de un negativo o logaritmo de un número ≤ 0). Elija otro intervalo.")


def seccion_dorada(f, a, b, objetivo="minimizar", tol=1.0, max_iter=100, criterio="relativo"):
    """Ejecuta el método.

    objetivo: "minimizar" | "maximizar"
    criterio: "relativo" (ε_a en %, el de clase) | "longitud" (longitud del intervalo, absoluta)
    """
    _validar(a, b, objetivo, tol, max_iter, criterio)
    _validar_dominio(f, a, b)
    max_iter = int(max_iter)
    res = ResultadoDorada(f.texto, float(a), float(b), objetivo, criterio, float(tol), max_iter)
    maxim = objetivo == "maximizar"

    xl, xu = float(a), float(b)
    d = R * (xu - xl)
    x1, x2 = xl + d, xu - d
    f1, f2 = f.evaluar(x1), f.evaluar(x2)
    res.evaluaciones = 2
    reutilizado = None
    xopt, fopt, ea = x1, f1, math.inf

    for i in range(1, max_iter + 1):
        d = R * (xu - xl)
        empate = f1 == f2
        mejor_x1 = (f1 > f2) if maxim else (f1 < f2)
        if mejor_x1:
            xopt, fopt = x1, f1
            xl_n, xu_n = x2, xu          # se descarta [x_L, x2)
        else:
            xopt, fopt = x2, f2
            xl_n, xu_n = xl, x1          # se descarta (x1, x_U]
        longitud = xu - xl
        ea = UNO_MENOS_R * abs(longitud / xopt) * 100 if xopt != 0 else math.inf
        res.iteraciones.append(IteracionDorada(
            i, xl, xu, d, x1, x2, f1, f2, reutilizado, mejor_x1, empate, xopt, fopt,
            xl_n, xu_n, ea, longitud, xu_n - xl_n))

        parar = ea < tol if criterio == "relativo" else (xu_n - xl_n) < tol
        if parar:
            res.convergio, res.estado = True, "convergio"
            xl, xu = xl_n, xu_n
            break
        # Se actualiza el intervalo REUTILIZANDO un punto y su evaluación.
        if mejor_x1:
            xl = xl_n
            x2, f2 = x1, f1                       # el viejo x1 es el nuevo x2
            x1 = xl + R * (xu - xl)
            f1 = f.evaluar(x1)
            reutilizado = "x2"
        else:
            xu = xu_n
            x1, f1 = x2, f2                       # el viejo x2 es el nuevo x1
            x2 = xu - R * (xu - xl)
            f2 = f.evaluar(x2)
            reutilizado = "x1"
        res.evaluaciones += 1
    else:
        res.estado = "max_iter"
        xl, xu = res.iteraciones[-1].xl_nuevo, res.iteraciones[-1].xu_nuevo

    res.xopt, res.fopt = xopt, fopt
    res.intervalo_final = (xl, xu)
    res.ea_final = ea

    tam = max(xu - xl, 1e-12)
    if abs(xl - res.a) <= 1e-12 * (1 + abs(res.a)):
        res.advertencias.append(
            "El óptimo quedó pegado al límite inferior a: la función puede ser monótona en [a, b]. "
            "Pruebe un intervalo más amplio.")
    elif abs(xu - res.b) <= 1e-12 * (1 + abs(res.b)):
        res.advertencias.append(
            "El óptimo quedó pegado al límite superior b: la función puede ser monótona en [a, b]. "
            "Pruebe un intervalo más amplio.")
    if criterio == "relativo" and xopt != 0 and abs(xopt) < tam:
        res.advertencias.append("El óptimo está muy cerca de 0, y el error relativo es poco confiable ahí. "
                                "Use el criterio «Longitud del intervalo».")

    if res.estado == "convergio":
        res.mensaje = (f"Convergió en {res.n_iter} iteración(es): {res.texto_criterio()} "
                       f"(ε_a = {fmt_pct(ea)}, longitud final = {fmt(xu - xl, 6)}).")
    else:
        res.mensaje = (f"Se alcanzó el máximo de iteraciones ({max_iter}) sin cumplir la tolerancia. "
                       "Aumente el máximo o la tolerancia.")
    return res


# ----------------------------------------------------------------------------------
# Procedimiento paso a paso (las ecuaciones se escriben en LaTeX para mostrarlas con formato)
# ----------------------------------------------------------------------------------
def generar_pasos(res, dec=6):
    N = lambda v: tx(v, dec)
    NP = lambda v: txp(v, dec)
    F = lambda v: fmt(v, dec)
    maxim = res.maximizar
    palabra = "máximo" if maxim else "mínimo"
    paginas = []

    tol_tex = (llenar(r"\varepsilon_a<@t@\%", t=N(res.tol)) if res.criterio == "relativo"
               else llenar(r"x_U-x_L<@t@", t=N(res.tol)))
    b = [("h1", "Planteamiento"),
         ("p", f"Buscamos el {palabra} de f(x) dentro del intervalo [a, b]. "
               "El método encierra el óptimo y reduce el intervalo en cada iteración usando la razón dorada, "
               "sin derivar. OJO: la sección dorada sirve para optimizar (máximos/mínimos), no para hallar raíces."),
         ("h2", "Datos del problema"),
         _eq_funcion(res.funcion),
         ("eq", llenar(r"x_L=a=@a@\qquad x_U=b=@b@", a=N(res.a), b=N(res.b))),
         ("p", f"Objetivo: {res.objetivo}.  Condición de parada:"),
         ("eq", tol_tex),
         ("p", f"Máximo de iteraciones: {res.max_iter}"),
         ("h2", "Fórmulas"),
         ("eqf", TEX_R), ("eqf", TEX_D), ("eqf", TEX_PUNTOS), ("eqf", TEX_ERROR),
         ("h2", f"Condiciones para {'MAXIMIZAR' if maxim else 'MINIMIZAR'} (se compara la altura de los dos puntos)")]
    b += _condiciones(maxim)
    b.append(("p", "Truco: en cada iteración solo hay UN punto nuevo; el otro se reutiliza con su f ya calculada."))
    paginas.append(("Planteamiento", b))

    for it in res.iteraciones:
        def origen(p):
            return ("↳ reutilizado de la iteración anterior (no se vuelve a calcular)"
                    if it.reutilizado == p else "↳ calculado en esta iteración")
        b = [("h1", f"Iteración {it.i}"),
             ("h2", "Paso 1 · Intervalo actual"),
             ("eq", llenar(r"x_L=@xl@\qquad x_U=@xu@", xl=N(it.xl), xu=N(it.xu))),
             ("h2", "Paso 2 · Distancia del corte d"),
             ("eq", llenar(r"d=R\,(x_U-x_L)=0.618034\times(@xu@-@xl@)=@d@", xu=N(it.xu), xl=NP(it.xl), d=N(it.d))),
             ("h2", "Paso 3 · Los dos puntos interiores"),
             ("eq", llenar(r"x_1=x_L+d=@xl@+@d@=@x1@", xl=N(it.xl), d=N(it.d), x1=N(it.x1))),
             ("eq", llenar(r"x_2=x_U-d=@xu@-@d@=@x2@", xu=N(it.xu), d=N(it.d), x2=N(it.x2))),
             ("h2", "Paso 4 · Evaluar f en x1 y x2 (se reemplaza cada x en la función)"),
             ("eq", llenar(r"f(x_1)=f(@x@)=@f@", x=N(it.x1), f=N(it.f1))),
             ("p", origen("x1")),
             ("eq", llenar(r"f(x_2)=f(@x@)=@f@", x=N(it.x2), f=N(it.f2))),
             ("p", origen("x2")),
             ("h2", "Paso 5 · Comparar y recortar el intervalo")]
        if it.mejor_x1:
            comp = ">" if maxim else "<"
            b.append(("p", f"Buscamos un {palabra.upper()}, así que nos quedamos con el punto "
                           f"{'más alto' if maxim else 'más bajo'}:"))
            b.append(("eq", llenar(r"f(x_1)=@a@\ @op@\ f(x_2)=@b@", a=N(it.f1), op=comp, b=N(it.f2))))
            b.append(("p", f"El {palabra} está entre x2 y x_U, se descarta el lado izquierdo:"))
            b.append(("eq", llenar(r"x_L=x_2=@v@", v=N(it.xl_nuevo))))
            b.append(("eq", llenar(r"x_{\mathrm{opt}}=x_1=@v@", v=N(it.xopt))))
        else:
            comp = ("=" if it.empate else (">" if maxim else "<"))
            b.append(("p", f"Buscamos un {palabra.upper()}: nos quedamos con "
                           f"{'el punto más alto' if maxim else 'el punto más bajo'}"
                           + (" (empate: se descarta el lado derecho):" if it.empate else ":")))
            b.append(("eq", llenar(r"f(x_2)=@a@\ @op@\ f(x_1)=@b@", a=N(it.f2), op=comp, b=N(it.f1))))
            b.append(("p", f"El {palabra} está entre x_L y x1, se descarta el lado derecho:"))
            b.append(("eq", llenar(r"x_U=x_1=@v@", v=N(it.xu_nuevo))))
            b.append(("eq", llenar(r"x_{\mathrm{opt}}=x_2=@v@", v=N(it.xopt))))
        b.append(("p", f"Intervalo nuevo: [{F(it.xl_nuevo)}, {F(it.xu_nuevo)}]   (longitud {F(it.longitud_nueva)})"))
        b.append(("h2", "Paso 6 · Error"))
        if it.xopt != 0:
            b.append(("eq", llenar(r"\varepsilon_a=0.381966\left|\frac{@xu@-@xl@}{@xo@}\right|\times100=@ea@",
                                   xu=N(it.xu), xl=NP(it.xl), xo=N(it.xopt), ea=tx_pct(it.ea))))
        else:
            b.append(("p", "x_opt = 0: el error relativo no está definido."))
        b.append(("h2", "Paso 7 · ¿Cumplimos la condición de parada?"))
        if res.criterio == "relativo":
            ok = it.ea < res.tol
            b.append(("eq", llenar(r"\varepsilon_a=@ea@\ @op@\ @t@\%", ea=tx_pct(it.ea),
                                   op="<" if ok else r"\geq", t=N(res.tol))))
        else:
            ok = it.longitud_nueva < res.tol
            b.append(("eq", llenar(r"x_U-x_L=@l@\ @op@\ @t@", l=N(it.longitud_nueva),
                                   op="<" if ok else r"\geq", t=N(res.tol))))
        b.append(("ok", "SÍ cumple. Terminamos.") if ok else ("warn", "NO cumple. Repetimos con el intervalo nuevo."))
        paginas.append((f"Iteración {it.i}", b))

    xl, xu = res.intervalo_final
    b = [("h1", "Resultado final"), ("p", res.mensaje),
         ("eqr", llenar(r"x_{\mathrm{opt}}\approx@x@", x=N(res.xopt))),
         ("eq", llenar(r"f(x_{\mathrm{opt}})=@f@", f=N(res.fopt))),
         ("eq", llenar(r"[x_L,\ x_U]=[@a@,\ @b@]", a=N(xl), b=N(xu))),
         ("p", f"Iteraciones: {res.n_iter}.  Evaluaciones de f: {res.evaluaciones}."),
         ("p", f"Recuerde: es un {palabra} local dentro del intervalo elegido.")]
    for a in res.advertencias:
        b.append(("warn", "⚠ " + a))
    paginas.append(("Resultado", b))
    return paginas
