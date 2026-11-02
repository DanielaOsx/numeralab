"""Teclado matemático en pantalla para la web: agrega símbolos al final de la función que se está escribiendo."""
import streamlit as st

from web.render import ancho

# (etiqueta, texto que se agrega). Las funciones se agregan con su paréntesis de apertura: sin(  exp(  ...
TECLAS = [
    [("7", "7"), ("8", "8"), ("9", "9"), ("(", "("), (")", ")"), ("⌫", "<borrar>")],
    [("4", "4"), ("5", "5"), ("6", "6"), ("×", "*"), ("÷", "/"), ("C", "<limpiar>")],
    [("1", "1"), ("2", "2"), ("3", "3"), ("−", "-"), ("+", "+"), ("x", "x")],
    [("0", "0"), (".", "."), ("x²", "^2"), ("xʸ", "^"), ("x³", "^3"), ("π", "pi")],
    [("eˣ", "exp("), ("√", "sqrt("), ("ln", "ln("), ("log", "log("), ("e", "e"), ("|x|", "abs(")],
    [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("asin", "asin("), ("acos", "acos("), ("atan", "atan(")],
]


def _pulsar(clave, token):
    actual = st.session_state.get(clave, "")
    if token == "<borrar>":
        st.session_state[clave] = actual[:-1]
    elif token == "<limpiar>":
        st.session_state[clave] = ""
    else:
        st.session_state[clave] = actual + token


def teclado(clave_funcion):
    """Dibuja el teclado. `clave_funcion` es la clave de session_state del campo de la función."""
    with st.container(key="teclado"):
        for r, fila in enumerate(TECLAS):
            cols = st.columns(6, gap="small")
            for c, (etiqueta, token) in enumerate(fila):
                cols[c].button(etiqueta, key=f"tk_{r}_{c}", on_click=_pulsar, args=(clave_funcion, token),
                               **ancho(st.button))
