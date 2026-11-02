"""Evaluador SEGURO de funciones matemáticas f(x).

No se usa eval() sobre el texto del usuario. La expresión se convierte a un
árbol sintáctico (ast) y solo se aceptan: números, la variable x, las
constantes pi y e, las operaciones + - * / ^ y una lista cerrada de funciones.
Cualquier otra cosa (nombres, atributos, llamadas, imports...) se rechaza.
"""
import ast
import math
import re

import numpy as np


class ErrorNumeraLab(ValueError):
    """Clase base de los errores propios del programa."""


class ErrorFuncion(ErrorNumeraLab):
    """La expresión escrita no es una función válida."""


class ErrorEvaluacion(ErrorNumeraLab):
    """La función no se pudo evaluar en un punto (división entre cero, dominio...)."""


class ErrorParametro(ErrorNumeraLab):
    """Un parámetro de entrada es inválido."""


FUNCIONES = {
    "sin": np.sin, "cos": np.cos, "tan": np.tan,
    "asin": np.arcsin, "acos": np.arccos, "atan": np.arctan,
    "sinh": np.sinh, "cosh": np.cosh, "tanh": np.tanh,
    "exp": np.exp, "sqrt": np.sqrt,
    "ln": np.log,       # logaritmo natural
    "log": np.log10,    # logaritmo en base 10
    "abs": np.abs,
}
CONSTANTES = {"pi": math.pi, "e": math.e}
MAX_LONGITUD = 300
MAX_NODOS = 250

_REEMPLAZOS = {
    "×": "*", "÷": "/", "−": "-", "–": "-", "·": "*",
    "π": "pi", "√": "sqrt", "²": "**2", "³": "**3",
}
_PATRON = re.compile(
    r"\s*(?:(\d+\.?\d*(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)"  # número
    r"|([A-Za-z_][A-Za-z_0-9]*)"                                   # nombre
    r"|(\*\*|[-+*/^()]))"                                          # operador
)


def _tokenizar(texto):
    tokens = []
    pos = 0
    while pos < len(texto):
        if texto[pos:].strip() == "":
            break
        m = _PATRON.match(texto, pos)
        if not m:
            cerca = texto[pos:pos + 8].strip()
            raise ErrorFuncion(f"Hay un carácter no permitido cerca de «{cerca}».")
        if m.group(1) is not None:
            tokens.append(("num", m.group(1)))
        elif m.group(2) is not None:
            nombre = m.group(2).lower()
            if nombre == "x" or nombre in CONSTANTES:
                tokens.append(("const", nombre))
            elif nombre in FUNCIONES:
                tokens.append(("func", nombre))
            else:
                pista = ""
                if re.fullmatch(r"x\d+", nombre):
                    pista = f" ¿Quiso escribir x^{nombre[1:]}?"
                raise ErrorFuncion(
                    f"No se reconoce «{m.group(2)}».{pista} Use solo x, pi, e y las funciones "
                    f"{', '.join(FUNCIONES)}."
                )
        else:
            tokens.append(("op", m.group(3)))
        pos = m.end()
    return tokens


def convertir_a_python(texto):
    """Convierte la notación del usuario (2x, ^, ln...) a una expresión tipo Python."""
    if not texto or not texto.strip():
        raise ErrorFuncion("La función está vacía. Escriba una expresión, por ejemplo: exp(-x) - x")
    if len(texto) > MAX_LONGITUD:
        raise ErrorFuncion("La expresión es demasiado larga.")
    for a, b in _REEMPLAZOS.items():
        texto = texto.replace(a, b)
    texto = re.sub(r"(?<=\d),(?=\d)", ".", texto)  # coma decimal -> punto
    tokens = _tokenizar(texto)
    salida = []
    for tipo, valor in tokens:
        if salida:
            pt, pv = salida[-1]
            previo_valor = pt in ("num", "const") or pv == ")"
            if previo_valor and (tipo in ("func", "const") or valor == "("):
                salida.append(("op", "*"))          # 2x -> 2*x ; 3(x+1) -> 3*(x+1)
            elif tipo == "num" and (pt == "const" or pv == ")"):
                salida.append(("op", "*"))          # x2 no existe, pero (x+1)2 -> (x+1)*2
        salida.append((tipo, valor))
    return " ".join("**" if v == "^" else v for _, v in salida)


def _validar(arbol):
    llamadas = {id(n.func) for n in ast.walk(arbol) if isinstance(n, ast.Call)}
    cuenta = 0
    for nodo in ast.walk(arbol):
        cuenta += 1
        if cuenta > MAX_NODOS:
            raise ErrorFuncion("La expresión es demasiado compleja.")
        if isinstance(nodo, (ast.Expression, ast.Load, ast.Add, ast.Sub, ast.Mult,
                             ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.BinOp, ast.UnaryOp)):
            continue
        if isinstance(nodo, ast.Constant):
            if isinstance(nodo.value, bool) or not isinstance(nodo.value, (int, float)):
                raise ErrorFuncion("Solo se permiten números.")
            continue
        if isinstance(nodo, ast.Name):
            if nodo.id == "x" or nodo.id in CONSTANTES:
                continue
            if nodo.id in FUNCIONES and id(nodo) in llamadas:
                continue
            raise ErrorFuncion(f"«{nodo.id}» debe escribirse con paréntesis, por ejemplo {nodo.id}(x).")
        if isinstance(nodo, ast.Call):
            if (not isinstance(nodo.func, ast.Name) or nodo.func.id not in FUNCIONES
                    or len(nodo.args) != 1 or nodo.keywords):
                raise ErrorFuncion("Cada función debe tener exactamente un argumento: sin(x), exp(-x)...")
            continue
        raise ErrorFuncion("La expresión contiene elementos no permitidos.")


def _calcular(n, x):
    if isinstance(n, ast.Constant):
        return float(n.value)
    if isinstance(n, ast.Name):
        return x if n.id == "x" else CONSTANTES[n.id]
    if isinstance(n, ast.UnaryOp):
        v = _calcular(n.operand, x)
        return -v if isinstance(n.op, ast.USub) else v
    if isinstance(n, ast.BinOp):
        a = _calcular(n.left, x)
        b = _calcular(n.right, x)
        if isinstance(n.op, ast.Add):
            return a + b
        if isinstance(n.op, ast.Sub):
            return a - b
        if isinstance(n.op, ast.Mult):
            return a * b
        if isinstance(n.op, ast.Div):
            return np.divide(a, b)
        return np.power(a, b)
    return FUNCIONES[n.func.id](_calcular(n.args[0], x))


class FuncionMatematica:
    """Función f(x) escrita por el usuario, lista para evaluarse de forma segura."""

    def __init__(self, texto):
        self.texto = (texto or "").strip()
        self.expresion = convertir_a_python(self.texto)
        try:
            self._arbol = ast.parse(self.expresion, mode="eval")
        except SyntaxError:
            raise ErrorFuncion("La expresión está mal escrita. Revise paréntesis, operadores y signos.")
        _validar(self._arbol)
        self._usa_x = any(isinstance(n, ast.Name) and n.id == "x" for n in ast.walk(self._arbol))

    def usa_x(self):
        return self._usa_x

    def __call__(self, x):
        with np.errstate(all="ignore"):
            try:
                return _calcular(self._arbol.body, x)
            except (ZeroDivisionError, OverflowError, FloatingPointError, ValueError):
                return np.nan

    def evaluar(self, x):
        """Evalúa f en un número y garantiza que el resultado sea finito."""
        r = self(np.float64(x))
        try:
            r = float(r)
        except (TypeError, ValueError):
            raise ErrorEvaluacion(f"No se pudo evaluar f({x}).")
        if not math.isfinite(r):
            raise ErrorEvaluacion(
                f"f({x:.6g}) no es un número finito (posible división entre cero o valor fuera del dominio, "
                f"como sqrt de un negativo o ln de un número ≤ 0)."
            )
        return r

    def evaluar_array(self, xs):
        """Evalúa f en un arreglo; los puntos no válidos quedan como NaN (para graficar)."""
        xs = np.asarray(xs, dtype=float)
        r = np.asarray(self(xs), dtype=float)
        r = np.broadcast_to(r, xs.shape).copy()
        r[~np.isfinite(r)] = np.nan
        return r

    def forma_simbolica(self):
        """Texto legible de la función interpretada por SymPy (solo para mostrar)."""
        try:
            import sympy as sp
            x = sp.Symbol("x")
            local = {
                "x": x, "pi": sp.pi, "e": sp.E, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
                "asin": sp.asin, "acos": sp.acos, "atan": sp.atan, "sinh": sp.sinh,
                "cosh": sp.cosh, "tanh": sp.tanh, "exp": sp.exp, "sqrt": sp.sqrt,
                "ln": sp.log, "log": lambda a: sp.log(a, 10), "abs": sp.Abs,
            }
            expr = sp.sympify(self.expresion, locals=local)  # ya validada: solo elementos permitidos
            return str(expr).replace("**", "^")
        except Exception:
            return self.texto


def valor_numerico(texto, nombre):
    """Convierte un campo de texto en número. Acepta 0.5, 0,5, 1e-3, pi/2, -2..."""
    t = (texto or "").strip()
    if not t:
        raise ErrorParametro(f"Falta el valor de «{nombre}».")
    try:
        g = FuncionMatematica(t)
    except ErrorFuncion:
        raise ErrorParametro(f"«{nombre}» debe ser un número (ejemplos: 0.5, -2, 1e-3, pi/2).")
    if g.usa_x():
        raise ErrorParametro(f"«{nombre}» debe ser un número, no puede contener x.")
    try:
        return g.evaluar(0.0)
    except ErrorEvaluacion:
        raise ErrorParametro(f"«{nombre}» no es un número válido.")
