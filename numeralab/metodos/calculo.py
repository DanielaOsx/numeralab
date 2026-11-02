"""Punto único de entrada para calcular: convierte los textos de los campos en números, valida y ejecuta el método.

Lo usan tanto la interfaz de escritorio como la web, de modo que ambas validan y calculan exactamente igual.
"""
from metodos.ejemplos import CRITERIOS
from metodos.secante_modificada import secante_modificada
from metodos.seccion_dorada import seccion_dorada
from utilidades.evaluador_funciones import ErrorFuncion, ErrorParametro, FuncionMatematica, valor_numerico


def calcular(metodo, texto_funcion, campos):
    """Devuelve (f, resultado). `campos` es un dict con los textos de los campos de entrada.

    Lanza ErrorFuncion / ErrorParametro / ErrorEvaluacion (todos subclases de ErrorNumeraLab) si algo es inválido.
    """
    f = FuncionMatematica(texto_funcion)
    if not f.usa_x():
        raise ErrorFuncion("La función debe contener la variable x. Ejemplo: x^2 - 4")
    tol = valor_numerico(campos["tol"], "Error tolerado")
    mi = valor_numerico(campos["max_iter"], "Máximo de iteraciones")
    if mi != int(mi) or mi < 1:
        raise ErrorParametro("El máximo de iteraciones debe ser un número entero positivo.")
    if metodo == "secante":
        res = secante_modificada(f, valor_numerico(campos["x0"], "Valor inicial x₀"),
                                 valor_numerico(campos["delta"], "Perturbación δ"), tol, int(mi))
    else:
        res = seccion_dorada(f, valor_numerico(campos["a"], "Límite inferior a"),
                             valor_numerico(campos["b"], "Límite superior b"),
                             "maximizar" if campos["objetivo"] == "Maximizar" else "minimizar", tol, int(mi),
                             "relativo" if campos["criterio"] == CRITERIOS[0] else "longitud")
    return f, res
