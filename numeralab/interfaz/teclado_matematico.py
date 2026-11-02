"""Teclado matemático visual que escribe en el campo de texto que esté seleccionado."""
import tkinter as tk

from interfaz.componentes import BLANCO, GRIS, BotonModerno, fuente

# (etiqueta que se ve, texto que se inserta, cuántos caracteres retroceder el cursor, estilo)
TECLAS = [
    [("7", "7", 0, "gris"), ("8", "8", 0, "gris"), ("9", "9", 0, "gris"),
     ("(", "(", 0, "negro"), (")", ")", 0, "negro"), ("⌫", "<borrar>", 0, "oscuro")],
    [("4", "4", 0, "gris"), ("5", "5", 0, "gris"), ("6", "6", 0, "gris"),
     ("×", "*", 0, "negro"), ("÷", "/", 0, "negro"), ("C", "<limpiar>", 0, "contorno")],
    [("1", "1", 0, "gris"), ("2", "2", 0, "gris"), ("3", "3", 0, "gris"),
     ("−", "-", 0, "negro"), ("+", "+", 0, "negro"), ("x", "x", 0, "oscuro")],
    [("0", "0", 0, "gris"), (".", ".", 0, "gris"), ("x²", "^2", 0, "fun"),
     ("xʸ", "^", 0, "fun"), ("a⁄b", "()/()", 4, "fun"), ("π", "pi", 0, "fun")],
    [("eˣ", "exp()", 1, "fun"), ("√", "sqrt()", 1, "fun"), ("ln", "ln()", 1, "fun"),
     ("log", "log()", 1, "fun"), ("e", "e", 0, "fun"), ("|x|", "abs()", 1, "fun")],
    [("sin", "sin()", 1, "fun"), ("cos", "cos()", 1, "fun"), ("tan", "tan()", 1, "fun"),
     ("asin", "asin()", 1, "fun"), ("acos", "acos()", 1, "fun"), ("atan", "atan()", 1, "fun")],
]


class TecladoMatematico(tk.Frame):
    """Inserta símbolos en el último campo registrado que recibió el foco."""

    def __init__(self, master, bg=BLANCO):
        super().__init__(master, bg=bg)
        self.destino = None
        for c in range(6):
            self.grid_columnconfigure(c, weight=1, uniform="teclas")
        for r, fila in enumerate(TECLAS):
            for c, (etq, texto, retro, estilo) in enumerate(fila):
                b = BotonModerno(self, etq, lambda t=texto, k=retro: self._pulsar(t, k), ancho=60, alto=36,
                                 estilo=estilo, tam=11, radio=9, bg=bg)
                b.grid(row=r, column=c, padx=2, pady=2, sticky="ew")
        pista = tk.Label(self, text="Escriba aquí o con su teclado: arriba verá la función con formato matemático.",
                         font=fuente(9), bg=bg, fg=GRIS, anchor="w", justify="left")
        pista.grid(row=len(TECLAS), column=0, columnspan=6, sticky="w", pady=(4, 0))
        pista.bind("<Configure>", lambda e: pista.configure(wraplength=max(120, e.width - 4)))

    def registrar(self, entry):
        """Hace que el teclado escriba en este campo cuando esté seleccionado."""
        entry.bind("<FocusIn>", lambda e, w=entry: setattr(self, "destino", w), add="+")
        if self.destino is None:
            self.destino = entry

    def _pulsar(self, texto, retroceso):
        e = self.destino
        if e is None:
            return
        e.focus_set()
        if texto == "<borrar>":
            self.borrar_ultimo(e)
        elif texto == "<limpiar>":
            e.delete(0, "end")
        else:
            if e.selection_present():
                e.delete("sel.first", "sel.last")
            pos = e.index("insert")
            e.insert(pos, texto)
            e.icursor(pos + len(texto) - retroceso)

    @staticmethod
    def borrar_ultimo(e):
        if e.selection_present():
            e.delete("sel.first", "sel.last")
            return
        pos = e.index("insert")
        if pos > 0:
            e.delete(pos - 1)
