"""Datos compartidos por la interfaz de escritorio (Tkinter) y la web (Streamlit): sin dependencias gráficas."""

INFO = {
    "secante": dict(titulo="Método de la Secante Modificada",
                    subtitulo="Encuentra raíces de f(x) sin calcular derivadas",
                    etiqueta="RAÍCES"),
    "dorada": dict(titulo="Método de la Sección Dorada",
                   subtitulo="Encuentra el máximo o mínimo de f(x) dentro de un intervalo",
                   etiqueta="OPTIMIZACIÓN"),
}
NOMBRES = {"secante": "Secante Modificada", "dorada": "Sección Dorada"}
CRITERIOS = ("Error relativo (%)", "Longitud del intervalo")
OBJETIVOS = ("Minimizar", "Maximizar")

PREDETERMINADOS = {
    "secante": dict(x0="0.5", delta="0.01", tol="1", max_iter="100"),
    "dorada": dict(a="0", b="5", objetivo="Minimizar", criterio=CRITERIOS[1], tol="0.01", max_iter="100"),
}
EJEMPLOS = {
    "secante": [
        dict(funcion="exp(-x) - x", x0="0.5", delta="0.01", tol="1", max_iter="100"),
        dict(funcion="exp(-x) - x", x0="1", delta="0.01", tol="1", max_iter="100"),     # ejemplo 6.8 de Chapra
    ],
    "dorada": [
        dict(funcion="(x - 2)^2 + 1", a="0", b="5", objetivo="Minimizar", criterio=CRITERIOS[1],
             tol="0.01", max_iter="100"),
        dict(funcion="4x - 1.8x^2 + 1.2x^3 - 0.3x^4", a="-2", b="4", objetivo="Maximizar",
             criterio=CRITERIOS[0], tol="1", max_iter="100"),
    ],
}
