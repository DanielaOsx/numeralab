"""Páginas de la versión web de NumeraLab (Streamlit).

Usa los MISMOS módulos de cálculo que la versión de escritorio (metodos/, utilidades/), de modo que ambas versiones
validan, calculan y explican exactamente igual.
"""
import time

import pandas as pd
import streamlit as st
from matplotlib.figure import Figure

from metodos import secante_modificada as m_sec
from metodos import seccion_dorada as m_dor
from metodos.calculo import calcular
from metodos.ejemplos import CRITERIOS, EJEMPLOS, INFO, NOMBRES, OBJETIVOS, PREDETERMINADOS
from utilidades import graficas
from utilidades.ecuaciones import latex_de_funcion
from utilidades.evaluador_funciones import ErrorFuncion, ErrorNumeraLab, FuncionMatematica
from utilidades.formato import fmt, fmt_pct
from utilidades.pdf import procedimiento_pdf
from utilidades.tablas import tabla_iteraciones
from web.render import ancho, latex_web, mostrar_bloques
from web.teclado import teclado

PAGINAS = {}       # lo llena app_web.py en cada ejecución (para poder cambiar de página con st.switch_page)

CAMPOS = {"secante": ["funcion", "x0", "delta", "tol", "max_iter"],
          "dorada": ["funcion", "a", "b", "objetivo", "criterio", "tol", "max_iter"]}

CSS = """
<style>
.block-container {padding-top: 3.6rem; max-width: 1500px;}
h3.h-rojo {color:#D90429; margin: .6rem 0 .2rem 0;}
.enc {background:#fff; border:1px solid #E5E7EB; border-left:8px solid #D90429; border-radius:12px;
      padding:14px 22px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; gap:12px;}
.enc h1 {font-size:1.9rem; margin:0; padding:0; color:#0F0F10;}
.enc p {margin:2px 0 0 0; color:#6B7280;}
.chip {background:#D90429; color:#fff; font-weight:700; font-size:.8rem; padding:6px 14px; border-radius:6px; white-space:nowrap;}
.chip2 {background:#FDECEF; color:#9D0208; font-weight:700; font-size:.72rem; padding:4px 10px; border-radius:6px;
        margin-right:6px; display:inline-block; margin-bottom:4px;}
.hero {background:#FDECEF; border:1px solid #E5E7EB; border-radius:14px; padding:26px 34px; margin-bottom:14px;}
.hero .a {color:#6B7280; font-size:1.1rem;} .hero .b {color:#D90429; font-size:2.8rem; font-weight:800; line-height:1.1;}
.hero .c {color:#0F0F10; font-size:1.35rem; font-weight:700;} .hero .d {color:#111827; margin-top:8px; max-width:720px;}
.tit {display:flex; align-items:center; gap:14px; font-size:1.3rem; font-weight:700; margin-bottom:8px;}
.ico {background:#D90429; color:#fff; width:46px; height:46px; border-radius:50%; display:inline-flex;
      align-items:center; justify-content:center; font-size:1.5rem; font-weight:700;}
div[data-testid="stMetric"] {background:#fff; border:1px solid #E5E7EB; border-top:4px solid #D90429; border-radius:12px;
      padding:10px 16px;}
section[data-testid="stSidebar"] {background:#0F0F10;}
section[data-testid="stSidebar"] * {color:#E5E7EB;}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {border-radius:10px;}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] {background:#D90429;}
section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"][aria-current="page"] * {color:#fff; font-weight:700;}
.pie {border-top:3px solid #D90429; margin-top:14px; padding-top:12px; font-size:.82rem;}
.pie b {color:#fff; font-size:.95rem;} .pie .r {color:#D90429; font-weight:700;} .pie .g {color:#9CA3AF;}
.st-key-teclado div[data-testid="stHorizontalBlock"] {flex-wrap:nowrap !important; gap:4px !important;}
.st-key-teclado div[data-testid="stColumn"] {min-width:0 !important; flex:1 1 0 !important; width:auto !important;}
.st-key-teclado button {padding:0.15rem 0; min-height:2.3rem; font-weight:700;}
.st-key-teclado div[data-testid="stVerticalBlock"] {gap:4px;}
</style>
"""


def inyectar_css():
    st.markdown(CSS, unsafe_allow_html=True)


def K(m, campo):
    return f"{m}:{campo}"


def iniciar_estado():
    """Crea los valores iniciales y los mantiene vivos al cambiar de página (Streamlit borra los campos que no se dibujan)."""
    for m, campos in CAMPOS.items():
        defaults = {"funcion": "", **PREDETERMINADOS[m]}
        for c in campos:
            st.session_state[K(m, c)] = st.session_state.get(K(m, c), defaults[c])
        st.session_state.setdefault(K(m, "ej"), 0)
        st.session_state.setdefault(K(m, "pag"), 0)
        st.session_state.setdefault(K(m, "res"), None)
        st.session_state.setdefault(K(m, "f"), None)
        st.session_state.setdefault(K(m, "firma"), None)
        if K(m, "iter") in st.session_state:
            st.session_state[K(m, "iter")] = st.session_state[K(m, "iter")]
        if K(m, "todo") in st.session_state:
            st.session_state[K(m, "todo")] = st.session_state[K(m, "todo")]
    st.session_state["decimales"] = st.session_state.get("decimales", 6)
    st.session_state.setdefault("historial", [])


def pie_sidebar():
    st.sidebar.markdown(
        "<div class='pie'><b>UNIVERSIDAD PILOTO<br>DE COLOMBIA</b><br><span class='r'>MÉTODOS NUMÉRICOS · 2026</span>"
        "<br><br><span class='g'>Nikole Daniela Ospina Mayorga<br>Isabela Ortega Torrado</span></div>",
        unsafe_allow_html=True)


# ------------------------------------------------------------------------------------------------ inicio
@st.cache_resource(show_spinner=False)
def _figura_demo(metodo):
    fig = Figure(figsize=(5.2, 3.3), dpi=110, facecolor="white", layout="constrained")
    (graficas.demo_secante if metodo == "secante" else graficas.demo_dorada)(fig)
    return fig


def pagina_inicio():
    st.markdown(
        "<div class='hero'><div class='a'>Bienvenido a</div><div class='b'>NumeraLab</div>"
        "<div class='c'>Calculadora interactiva de Métodos Numéricos</div>"
        "<div class='d'>Elija un método, complete los datos y obtenga el resultado con su procedimiento paso a paso, "
        "la tabla de iteraciones y la gráfica.</div></div>", unsafe_allow_html=True)
    tarjetas = [
        ("secante", "ƒ", ("MÉTODO ABIERTO", "1 valor inicial", "Sin derivadas", "Busca raíces"),
         "Parte de un solo valor x₀ y lo mejora en cada iteración hasta que f(x) = 0. La pendiente se estima con un "
         "punto cercano, x + δ·x, por eso no necesita derivar. Es rápido, pero puede fallar si x₀ está lejos de la raíz."),
        ("dorada", "φ", ("POR INTERVALOS", "Intervalo [a, b]", "Sin derivadas", "Máximos y mínimos"),
         "Encierra el máximo o mínimo de f(x) entre a y b y reduce el intervalo con la razón dorada (0.618) en cada "
         "paso, reutilizando una evaluación. Siempre avanza, pero encuentra un óptimo local y no sirve para hallar raíces."),
    ]
    for col, (m, simbolo, chips, texto) in zip(st.columns(2, gap="large"), tarjetas):
        with col, st.container(border=True):
            st.markdown(f"<div class='tit'><span class='ico'>{simbolo}</span>{INFO[m]['titulo']}</div>"
                        + "".join(f"<span class='chip2'>{c}</span>" for c in chips), unsafe_allow_html=True)
            st.write(texto)
            if st.button("Seleccionar  →", key=f"sel_{m}", type="primary"):
                st.switch_page(PAGINAS[m])
            st.pyplot(_figura_demo(m), **ancho(st.pyplot))


# ------------------------------------------------------------------------------------------------ método
def _encabezado(m):
    info = INFO[m]
    st.markdown(f"<div class='enc'><div><h1>{info['titulo']}</h1><p>NumeraLab · Calculadora interactiva de Métodos "
                f"Numéricos — {info['subtitulo']}</p></div><span class='chip'>{info['etiqueta']}</span></div>",
                unsafe_allow_html=True)


def _cargar_ejemplo(m):
    lista = EJEMPLOS[m]
    ej = lista[st.session_state[K(m, "ej")] % len(lista)]
    for c, v in ej.items():
        st.session_state[K(m, c)] = v
    st.session_state[K(m, "ej")] += 1


def _limpiar(m):
    st.session_state[K(m, "funcion")] = ""
    for c, v in PREDETERMINADOS[m].items():
        st.session_state[K(m, c)] = v
    for c in ("res", "f", "firma"):
        st.session_state[K(m, c)] = None


def _firma(m):
    return tuple(st.session_state[K(m, c)] for c in CAMPOS[m])


def _vista_previa(texto):
    """Muestra la función escrita como ecuación (fracciones, exponentes...) o el error si no es válida."""
    with st.container(border=True):
        if not texto.strip():
            st.caption("Escriba una función o presione EJEMPLO. Aquí verá la ecuación con formato matemático.")
            return
        try:
            f = FuncionMatematica(texto)
        except ErrorFuncion as e:
            st.error(str(e), icon="✖")
            return
        if not f.usa_x():
            st.error("La función debe contener la variable x.", icon="✖")
            return
        tex = latex_de_funcion(f)
        if tex:
            st.latex("f(x)=" + latex_web(tex))
        else:
            st.code("f(x) = " + f.texto)


def _entradas(m):
    st.markdown("##### DATOS DE ENTRADA")
    st.text_input("Función f(x)", key=K(m, "funcion"), placeholder="Ej.: exp(-x) - x   ·   x^3 - 2x - 5")
    _vista_previa(st.session_state[K(m, "funcion")])
    if m == "secante":
        c1, c2 = st.columns(2)
        c1.text_input("Valor inicial x₀", key=K(m, "x0"))
        c2.text_input("Perturbación relativa δ", key=K(m, "delta"))
        c1.text_input("Error tolerado (%)", key=K(m, "tol"))
        c2.text_input("Máx. iteraciones", key=K(m, "max_iter"))
    else:
        c1, c2 = st.columns(2)
        c1.text_input("Límite inferior a", key=K(m, "a"))
        c2.text_input("Límite superior b", key=K(m, "b"))
        c1.selectbox("Objetivo", OBJETIVOS, key=K(m, "objetivo"))
        c2.text_input("Máx. iteraciones", key=K(m, "max_iter"))
        c1.selectbox("Criterio de parada", CRITERIOS, key=K(m, "criterio"))
        etiqueta = ("Error tolerado (%)" if st.session_state[K(m, "criterio")] == CRITERIOS[0]
                    else "Error tolerado (longitud)")
        c2.text_input(etiqueta, key=K(m, "tol"))
    calcular_pulsado = st.button("CALCULAR", type="primary", **ancho(st.button), key=K(m, "btn"))
    b1, b2 = st.columns(2)
    b1.button("EJEMPLO", on_click=_cargar_ejemplo, args=(m,), **ancho(st.button), key=K(m, "bej"))
    b2.button("LIMPIAR", on_click=_limpiar, args=(m,), **ancho(st.button), key=K(m, "blim"))
    st.markdown("##### TECLADO MATEMÁTICO")
    teclado(K(m, "funcion"))
    with st.expander("Ayuda de sintaxis"):
        st.markdown(
            "Use **x** como variable, **^** para potencias, ***** para multiplicar (también vale `2x`), "
            "`ln(x)` logaritmo natural, `log(x)` base 10, `exp(x)` = eˣ, `sqrt(x)` raíz cuadrada. "
            "Funciones: sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, exp, sqrt, ln, log, abs. "
            "Los números aceptan coma o punto decimal y expresiones como `pi/2` o `1e-3`.")
    return calcular_pulsado


def _registrar_historial(m, res, f_texto):
    dec = st.session_state["decimales"]
    if m == "secante":
        resumen = f"x ≈ {fmt(res.raiz, dec)}   (ε_a = {fmt_pct(res.ea_final)}, {res.n_iter} iter.)"
    else:
        resumen = f"x* ≈ {fmt(res.xopt, dec)},  f(x*) ≈ {fmt(res.fopt, dec)}   ({res.n_iter} iter.)"
    if res.estado != "convergio":
        resumen += "   [no convergió]"
    entrada = {c: st.session_state[K(m, c)] for c in CAMPOS[m]}
    hist = st.session_state["historial"]
    hist.insert(0, dict(hora=time.strftime("%H:%M:%S"), metodo=m, funcion=f_texto, resumen=resumen, entrada=entrada))
    del hist[100:]


def _ejecutar(m):
    campos = {c: st.session_state[K(m, c)] for c in CAMPOS[m] if c != "funcion"}
    try:
        f, res = calcular(m, st.session_state[K(m, "funcion")], campos)
    except ErrorNumeraLab as e:
        st.error(f"**Revise los datos.** {e}")
        return
    st.session_state[K(m, "f")], st.session_state[K(m, "res")] = f, res
    st.session_state[K(m, "firma")] = _firma(m)
    st.session_state[K(m, "pag")] = 0
    st.session_state[K(m, "iter")] = max(1, res.n_iter)
    _registrar_historial(m, res, st.session_state[K(m, "funcion")])


def _tarjetas(m, res, dec):
    a, b = st.columns(2)
    if m == "secante":
        a.metric("RAÍZ APROXIMADA", fmt(res.raiz, dec), help="x donde f(x) ≈ 0")
        b.metric("VALOR f(raíz)", fmt(res.f_raiz, dec), help="debe ser cercano a 0")
        a.metric("ERROR APROXIMADO ε_a", fmt_pct(res.ea_final, dec), help=f"tolerancia: {fmt(res.tol)} %")
        b.metric("ITERACIONES", str(res.n_iter), help=f"máximo permitido: {res.max_iter}")
    else:
        xl, xu = res.intervalo_final
        a.metric("ÓPTIMO x*", fmt(res.xopt, dec), help=f"{res.nombre_objetivo()} aproximado")
        b.metric("VALOR f(x*)", fmt(res.fopt, dec))
        a.metric("INTERVALO FINAL", f"[{fmt(xl, 4)}, {fmt(xu, 4)}]", help=f"longitud {fmt(xu - xl, 6)}")
        b.metric("ITERACIONES", str(res.n_iter), help=f"{res.evaluaciones} evaluaciones de f")


def _mover_pagina(m, delta, n):
    st.session_state[K(m, "pag")] = min(max(st.session_state[K(m, "pag")] + delta, 0), n - 1)


def _boton_pdf(m, res, dec, paginas):
    """Genera el PDF una sola vez por cálculo (es lento) y ofrece su descarga."""
    clave = (st.session_state[K(m, "firma")], dec)
    if st.session_state.get(K(m, "pdf_clave")) != clave:
        st.session_state[K(m, "pdf_clave")], st.session_state[K(m, "pdf")] = clave, None
    if st.session_state.get(K(m, "pdf")) is None:
        if st.button("Preparar PDF del procedimiento", key=K(m, "bpdf")):
            with st.spinner("Generando PDF..."):
                st.session_state[K(m, "pdf")] = procedimiento_pdf(
                    NOMBRES[m], res.funcion, res.mensaje,
                    res.bloques_resumen(dec), paginas)
            st.rerun()
    else:
        st.download_button("Descargar PDF del procedimiento", st.session_state[K(m, "pdf")],
                           file_name=f"procedimiento_{m}.pdf", mime="application/pdf", type="primary",
                           key=K(m, "dpdf"))


def _tab_procedimiento(m, res, dec):
    gen = m_sec.generar_pasos if m == "secante" else m_dor.generar_pasos
    paginas = gen(res, dec)
    n = len(paginas)
    _boton_pdf(m, res, dec, paginas)
    st.session_state[K(m, "pag")] = min(st.session_state[K(m, "pag")], n - 1)
    c1, c2, c3, c4 = st.columns([1.25, 2, 1.25, 1.5], vertical_alignment="center")
    idx = st.session_state[K(m, "pag")]
    c1.button("◀ Anterior", disabled=idx == 0, on_click=_mover_pagina, args=(m, -1, n), key=K(m, "ant"),
              **ancho(st.button))
    c3.button("Siguiente ▶", disabled=idx >= n - 1, on_click=_mover_pagina, args=(m, 1, n), key=K(m, "sig"),
              type="primary", **ancho(st.button))
    todo = c4.toggle("Ver todo", key=K(m, "todo"))
    if todo:
        c2.markdown(f"**Procedimiento completo** ({n} secciones)")
        for _, bloques in paginas:
            mostrar_bloques(bloques)
            st.divider()
    else:
        titulo, bloques = paginas[idx]
        c2.markdown(f"**{titulo}** · paso {idx + 1} de {n}")
        mostrar_bloques(bloques)


def _tab_tabla(m, res, dec):
    cols, filas = tabla_iteraciones(m, res, dec)
    df = pd.DataFrame(filas, columns=cols)
    st.dataframe(df, hide_index=True, **ancho(st.dataframe))
    st.download_button("Descargar tabla (CSV)", df.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"iteraciones_{m}.csv", mime="text/csv")


def _tab_grafica(m, res, f):
    fig = Figure(figsize=(9, 6 if m == "dorada" else 5.4), dpi=110, facecolor="white", layout="constrained")
    if m == "secante":
        graficas.graficar_secante(fig, f, res)
    else:
        k = st.slider("Iteración mostrada", 1, max(1, res.n_iter), key=K(m, "iter"))
        graficas.graficar_dorada(fig, f, res, k)
    st.pyplot(fig, **ancho(st.pyplot))


def _salidas(m, dec):
    res, f = st.session_state[K(m, "res")], st.session_state[K(m, "f")]
    if res is None:
        st.info("Escriba una función, ajuste los datos y presione **CALCULAR** (o pruebe con **EJEMPLO**).")
        mostrar_bloques(m_sec.bloques_ayuda() if m == "secante" else m_dor.bloques_ayuda())
        return
    if st.session_state[K(m, "firma")] != _firma(m):
        st.warning("⚠ Los datos cambiaron. Presione CALCULAR para actualizar los resultados.")
    banner = {"convergio": st.success, "max_iter": st.warning}.get(res.estado, st.error)
    banner(res.mensaje)
    _tarjetas(m, res, dec)
    t1, t2, t3, t4 = st.tabs(["Calculadora", "Procedimiento", "Tabla de iteraciones", "Gráfica"])
    with t1:
        mostrar_bloques(res.bloques_resumen(dec))
    with t2:
        _tab_procedimiento(m, res, dec)
    with t3:
        _tab_tabla(m, res, dec)
    with t4:
        _tab_grafica(m, res, f)


def _pagina_metodo(m):
    _encabezado(m)
    dec = st.session_state["decimales"]
    izq, der = st.columns([1, 1.6], gap="large")
    with izq:
        pulsado = _entradas(m)
    with der:
        if pulsado or st.session_state.pop("_auto", None) == m:
            _ejecutar(m)
        _salidas(m, dec)


def pagina_secante():
    _pagina_metodo("secante")


def pagina_dorada():
    _pagina_metodo("dorada")


# ------------------------------------------------------------------------------------------------ historial y configuración
def _cargar_historial(h):
    m = h["metodo"]
    for c, v in h["entrada"].items():
        st.session_state[K(m, c)] = v
    st.session_state["_auto"] = m


def pagina_historial():
    st.markdown("## Historial de cálculos")
    st.caption("Los cálculos quedan guardados mientras dure su sesión en el navegador. Use «Cargar» para repetirlos.")
    hist = st.session_state["historial"]
    if not hist:
        st.info("Todavía no hay cálculos. Haga uno en «Secante Modificada» o «Sección Dorada».")
        return
    if st.button("Borrar historial"):
        hist.clear()
        st.rerun()
    for k, h in enumerate(hist):
        with st.container(border=True):
            c = st.columns([1, 2, 3, 5, 1.4], vertical_alignment="center")
            c[0].write(h["hora"])
            c[1].write(NOMBRES[h["metodo"]])
            c[2].code(h["funcion"], language=None)
            c[3].write(h["resumen"])
            if c[4].button("Cargar", key=f"cargar_{k}"):
                _cargar_historial(h)
                st.switch_page(PAGINAS[h["metodo"]])


def pagina_config():
    st.markdown("## Configuración")
    st.slider("Decimales mostrados en resultados, tablas y procedimiento", 2, 12, key="decimales")
    st.markdown("""
**Cómo escribir funciones**

- Variable: `x`   ·   Constantes: `pi`, `e`
- Operaciones: `+  -  *  /  ^` (potencia). También vale `2x`, `3(x+1)`, `(x+1)(x-1)`
- Funciones: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `exp`, `sqrt`, `ln`, `log`, `abs`
- `ln(x)` es el logaritmo natural y `log(x)` el de base 10
- Los números aceptan coma o punto decimal, y expresiones como `pi/2` o `1e-3`

**Seguridad:** el texto se interpreta con un analizador matemático propio; no se ejecuta código.
""")
    st.caption("NumeraLab · Secante Modificada y Sección Dorada · Python, Streamlit, NumPy, SymPy, Pandas y Matplotlib.")
