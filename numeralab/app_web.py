"""NumeraLab — versión web (Streamlit).

Ejecutar:   streamlit run app_web.py        (se abre en http://localhost:8501)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st  # noqa: E402

st.set_page_config(page_title="NumeraLab · Métodos Numéricos", page_icon="∑", layout="wide")

from web import paginas as P  # noqa: E402

P.inyectar_css()
P.iniciar_estado()

P.PAGINAS = {
    "inicio": st.Page(P.pagina_inicio, title="Inicio", icon=":material/home:", default=True),
    "secante": st.Page(P.pagina_secante, title="Secante Modificada", icon=":material/functions:", url_path="secante"),
    "dorada": st.Page(P.pagina_dorada, title="Sección Dorada", icon=":material/trending_up:", url_path="dorada"),
    "historial": st.Page(P.pagina_historial, title="Historial", icon=":material/history:", url_path="historial"),
    "config": st.Page(P.pagina_config, title="Configuración", icon=":material/settings:", url_path="configuracion"),
}
pagina = st.navigation(list(P.PAGINAS.values()))
P.pie_sidebar()
pagina.run()
