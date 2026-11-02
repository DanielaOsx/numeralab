"""Dibuja en Streamlit los bloques de texto y ecuaciones que generan los métodos (los mismos que usa el escritorio)."""
import html
import inspect

import streamlit as st


def ancho(funcion):
    """Argumento para que un elemento ocupe todo el ancho, según la versión de Streamlit instalada."""
    params = inspect.signature(funcion).parameters
    return {"width": "stretch"} if "width" in params else {"use_container_width": True}


# mathtext (escritorio) y KaTeX (web) casi coinciden; estas dos expresiones se escriben mejor así en KaTeX
_WEB = {r"\mathrm{Ra\acute{\imath}z}": r"\text{Raíz}", r"\mathrm{\acute{O}ptimo}": r"\text{Óptimo}"}


def latex_web(tex):
    for a, b in _WEB.items():
        tex = tex.replace(a, b)
    return tex


def _md(texto):
    """Escapa caracteres que Markdown interpretaría (x_i, x_L ... se verían en cursiva)."""
    return texto.replace("\\", "\\\\").replace("_", r"\_").replace("*", r"\*").replace("$", r"\$")


def mostrar_bloques(bloques):
    """bloques: lista de (estilo, contenido). Estilos: h1, h2, p, ok, warn, calc, eq, eqf, eqr."""
    for estilo, contenido in bloques:
        if estilo == "h1":
            st.markdown(f"<h3 class='h-rojo'>{html.escape(contenido)}</h3>", unsafe_allow_html=True)
        elif estilo == "h2":
            st.markdown(f"**{_md(contenido)}**")
        elif estilo == "p":
            if contenido.strip():
                st.markdown(_md(contenido))
        elif estilo == "ok":
            st.success(contenido)
        elif estilo == "warn":
            st.warning(contenido)
        elif estilo in ("eq", "eqf"):
            st.latex(latex_web(contenido))
        elif estilo == "eqr":
            st.latex(r"\color{#C8102E}{" + latex_web(contenido) + "}")
        else:                                  # calc / res: texto con formato de código
            st.markdown(f"`{contenido}`")
