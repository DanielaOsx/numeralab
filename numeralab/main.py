"""NumeraLab — Calculadora de Métodos Numéricos.

Ejecutar:   python main.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _verificar_dependencias():
    faltan = []
    for modulo, paquete in (("numpy", "numpy"), ("matplotlib", "matplotlib"), ("sympy", "sympy")):
        try:
            __import__(modulo)
        except ImportError:
            faltan.append(paquete)
    try:
        import tkinter  # noqa: F401
    except ImportError:
        print("Tkinter no está instalado. En Windows viene con Python: reinstale Python marcando «tcl/tk and IDLE».")
        sys.exit(1)
    if faltan:
        print("Faltan paquetes:", ", ".join(faltan))
        print("Instálelos con:   pip install -r requirements.txt")
        sys.exit(1)


def main():
    _verificar_dependencias()
    try:  # nitidez en pantallas de alta resolución (Windows)
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    import matplotlib
    matplotlib.use("TkAgg")
    from interfaz.ventana_principal import VentanaPrincipal
    VentanaPrincipal().mainloop()


if __name__ == "__main__":
    main()
