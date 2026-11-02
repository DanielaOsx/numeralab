"""Componentes visuales reutilizables: colores, botones redondeados, tarjetas, campos."""
import base64
import tkinter as tk
from tkinter import ttk

from utilidades.ecuaciones import png_ecuacion

NEGRO = "#0F0F10"
NEGRO_2 = "#1C1C1F"
ROJO = "#D90429"
ROJO_HOVER = "#EF233C"
ROJO_OSC = "#9D0208"
ROJO_SUAVE = "#FDECEF"
BLANCO = "#FFFFFF"
FONDO = "#F3F4F6"
TEXTO = "#111827"
GRIS = "#6B7280"
BORDE = "#E5E7EB"
VERDE = "#16A34A"
VERDE_SUAVE = "#E8F7EE"
AMBAR = "#B45309"
AMBAR_SUAVE = "#FEF3C7"

FUENTE = "Segoe UI"
MONO = "Consolas"


def fuente(tam=11, peso="normal"):
    return (FUENTE, tam, peso)


ESTILOS_BOTON = {
    # estilo: (fondo, fondo_hover, texto, borde)
    "rojo": (ROJO, ROJO_HOVER, BLANCO, ROJO),
    "negro": (NEGRO, "#2E2E33", BLANCO, NEGRO),
    "contorno": (BLANCO, ROJO_SUAVE, ROJO, ROJO),
    "gris": ("#EEF0F3", "#DFE3E8", TEXTO, "#EEF0F3"),
    "fun": (ROJO_SUAVE, "#FAD0D8", ROJO_OSC, ROJO_SUAVE),
    "oscuro": ("#2A2A2E", "#3A3A40", BLANCO, "#2A2A2E"),
}


def _rect_redondo(canvas, x1, y1, x2, y2, r, **kw):
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class BotonModerno(tk.Canvas):
    """Botón con bordes redondeados y efecto al pasar el cursor. Se estira con su contenedor."""

    def __init__(self, master, texto, comando=None, ancho=160, alto=44, estilo="rojo",
                 tam=11, peso="bold", radio=12, bg=None):
        try:
            fondo_padre = bg or master.cget("bg")
        except tk.TclError:
            fondo_padre = FONDO
        esc = max(1.0, master.winfo_fpixels("1i") / 96.0)      # crece junto con la fuente (pantallas HiDPI)
        super().__init__(master, width=int(ancho * esc), height=int(alto * esc), bg=fondo_padre,
                         highlightthickness=0, bd=0, cursor="hand2")
        self.texto, self.comando, self.estilo = texto, comando, estilo
        self.radio, self.tam, self.peso = radio, tam, peso
        self.hover = False
        self.activo = True
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._soltar)
        self.bind("<Configure>", lambda e: self._dibujar())
        self._dibujar()

    def _set_hover(self, v):
        self.hover = v
        self._dibujar()

    def _soltar(self, e):
        if self.activo and self.comando and 0 <= e.x <= self.winfo_width() and 0 <= e.y <= self.winfo_height():
            self.comando()

    def configurar(self, texto=None, estilo=None, activo=None):
        if texto is not None:
            self.texto = texto
        if estilo is not None:
            self.estilo = estilo
        if activo is not None:
            self.activo = activo
            self.configure(cursor="hand2" if activo else "arrow")
        self._dibujar()

    def _dibujar(self):
        self.delete("all")
        w = max(self.winfo_width(), int(self["width"]))
        h = max(self.winfo_height(), int(self["height"]))
        fondo, hover, txt, borde = ESTILOS_BOTON[self.estilo]
        if not self.activo:
            fondo, txt, borde = "#E5E7EB", "#9CA3AF", "#E5E7EB"
        elif self.hover:
            fondo = hover
        _rect_redondo(self, 2, 2, w - 2, h - 2, self.radio, fill=fondo, outline=borde, width=2)
        self.create_text(w / 2, h / 2, text=self.texto, fill=txt, font=fuente(self.tam, self.peso))


class TarjetaResultado(tk.Frame):
    """Tarjeta con título pequeño y un valor grande destacado."""

    def __init__(self, master, titulo, color=ROJO):
        super().__init__(master, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        tk.Frame(self, bg=color, height=4).pack(fill="x")
        self.lbl_titulo = tk.Label(self, text=titulo, font=fuente(9, "bold"), bg=BLANCO, fg=GRIS, anchor="w")
        self.lbl_titulo.pack(fill="x", padx=12, pady=(8, 0))
        self.lbl_valor = tk.Label(self, text="—", font=fuente(17, "bold"), bg=BLANCO, fg=TEXTO, anchor="w")
        self.lbl_valor.pack(fill="x", padx=12)
        self.lbl_detalle = tk.Label(self, text=" ", font=fuente(9), bg=BLANCO, fg=GRIS, anchor="w")
        self.lbl_detalle.pack(fill="x", padx=12, pady=(0, 8))

    def actualizar(self, valor, detalle=" ", titulo=None):
        self.lbl_valor.configure(text=valor)
        self.lbl_detalle.configure(text=detalle)
        if titulo:
            self.lbl_titulo.configure(text=titulo)


class CampoEtiquetado(tk.Frame):
    """Etiqueta + campo de texto con borde que se enciende en rojo al seleccionarlo."""

    def __init__(self, master, etiqueta, valor="", bg=BLANCO, tam=12):
        super().__init__(master, bg=bg)
        self.lbl = tk.Label(self, text=etiqueta, font=fuente(9, "bold"), bg=bg, fg=GRIS, anchor="w")
        self.lbl.pack(fill="x")
        self.var = tk.StringVar(value=valor)
        self.entry = tk.Entry(self, textvariable=self.var, font=fuente(tam), relief="flat", bg="#F9FAFB",
                              fg=TEXTO, insertbackground=ROJO, highlightthickness=2,
                              highlightbackground=BORDE, highlightcolor=ROJO, bd=4)
        self.entry.pack(fill="x", ipady=5)

    def get(self):
        return self.var.get()

    def set(self, valor):
        self.var.set(valor)

    def set_etiqueta(self, texto):
        self.lbl.configure(text=texto)


class CampoCombo(tk.Frame):
    """Etiqueta + lista desplegable de solo lectura."""

    def __init__(self, master, etiqueta, valores, bg=BLANCO):
        super().__init__(master, bg=bg)
        tk.Label(self, text=etiqueta, font=fuente(9, "bold"), bg=bg, fg=GRIS, anchor="w").pack(fill="x")
        self.var = tk.StringVar(value=valores[0])
        self.combo = ttk.Combobox(self, textvariable=self.var, values=valores, state="readonly",
                                  font=fuente(11), style="Moderno.TCombobox")
        self.combo.pack(fill="x", ipady=4)

    def get(self):
        return self.var.get()

    def set(self, valor):
        self.var.set(valor)


class MarcoDesplazable(tk.Frame):
    """Contenedor con barra de desplazamiento vertical (para ventanas pequeñas)."""

    def __init__(self, master, bg=FONDO):
        super().__init__(master, bg=bg)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.barra = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.barra.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.barra.grid(row=0, column=1, sticky="ns")
        self.interior = tk.Frame(self.canvas, bg=bg)
        self._id = self.canvas.create_window((0, 0), window=self.interior, anchor="nw")
        self.interior.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._id, width=e.width))
        for ev in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.bind_all(ev, self._rueda, add="+")

    def _rueda(self, e):
        try:
            w = self.winfo_containing(e.x_root, e.y_root)
        except (KeyError, tk.TclError):
            return
        while w is not None and w is not self:
            w = w.master
        if w is None:
            return
        if self.interior.winfo_height() <= self.canvas.winfo_height():
            return
        paso = -1 if (e.num == 4 or getattr(e, "delta", 0) > 0) else 1
        self.canvas.yview_scroll(paso * 2, "units")


def configurar_etiquetas_texto(txt):
    """Estilos de texto compartidos por las pestañas Calculadora y Procedimiento."""
    txt.tag_configure("h1", font=fuente(18, "bold"), foreground=ROJO, spacing1=4, spacing3=8)
    txt.tag_configure("h2", font=fuente(12, "bold"), foreground=NEGRO, spacing1=12, spacing3=4)
    txt.tag_configure("p", font=fuente(12), foreground=TEXTO, spacing3=4, lmargin1=2, lmargin2=2)
    txt.tag_configure("formula", font=(MONO, 13), foreground=NEGRO, background="#F3F4F6",
                      lmargin1=14, lmargin2=14, spacing1=3, spacing3=3)
    txt.tag_configure("calc", font=(MONO, 12), foreground="#1F2937", lmargin1=18, lmargin2=18,
                      spacing1=2, spacing3=2)
    txt.tag_configure("ok", font=fuente(12, "bold"), foreground=VERDE, spacing1=4, spacing3=4)
    txt.tag_configure("warn", font=fuente(12, "bold"), foreground=AMBAR, spacing1=4, spacing3=4)
    txt.tag_configure("eqlinea", lmargin1=14, lmargin2=14, spacing1=2, spacing3=2)
    txt.tag_configure("res", font=fuente(15, "bold"), foreground=ROJO, spacing1=8, spacing3=6, lmargin1=18)


# Estilos de ecuación: (tamaño de letra, color, color de fondo)
ESTILOS_EQ = {
    "eq": (15, TEXTO, BLANCO),
    "eqf": (16, NEGRO, "#F3F4F6"),       # fórmula del método (con fondo gris)
    "eqr": (19, ROJO, BLANCO),           # resultado destacado
    "eqprev": (21, NEGRO, "#F9FAFB"),    # vista previa de la función que escribe el usuario
}


def imagen_ecuacion(latex, estilo="eq", escala=1.0, max_ancho=0):
    """PhotoImage con la ecuación en formato matemático (o None si el LaTeX no es válido)."""
    tam, color, fondo = ESTILOS_EQ[estilo]
    png = png_ecuacion(latex, tam, color, fondo, int(110 * escala), max_ancho=max_ancho)
    if png is None:
        return None
    return tk.PhotoImage(data=base64.b64encode(png))


def pintar_bloques(txt, bloques, escala=1.0):
    """Escribe bloques (estilo, contenido). Los estilos eq/eqf/eqr se dibujan como ecuaciones."""
    txt.configure(state="normal")
    txt.delete("1.0", "end")
    txt._imagenes = []                                   # evita que Tk descarte las imágenes
    ancho = max(300, (txt.winfo_width() if txt.winfo_width() > 50 else 640) - 90)
    for estilo, contenido in bloques:
        if estilo in ESTILOS_EQ:
            img = imagen_ecuacion(contenido, estilo, escala, ancho)
            if img is not None:
                txt._imagenes.append(img)
                inicio = txt.index("end-1c")
                txt.insert("end", " ")
                txt.image_create("end", image=img, padx=8, pady=3)
                txt.insert("end", "\n")
                txt.tag_add("eqlinea", inicio, "end-1c")
                continue
            estilo = "calc"
        txt.insert("end", contenido + "\n", estilo)
    txt.configure(state="disabled")
    txt.yview_moveto(0)


def crear_texto(master, **kw):
    """Widget Text de solo lectura con su barra de desplazamiento; devuelve (frame, text)."""
    marco = tk.Frame(master, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
    marco.grid_rowconfigure(0, weight=1)
    marco.grid_columnconfigure(0, weight=1)
    txt = tk.Text(marco, wrap="word", bd=0, padx=16, pady=12, bg=BLANCO, relief="flat",
                  highlightthickness=0, state="disabled", cursor="arrow", **kw)
    barra = ttk.Scrollbar(marco, orient="vertical", command=txt.yview)
    txt.configure(yscrollcommand=barra.set)
    txt.grid(row=0, column=0, sticky="nsew")
    barra.grid(row=0, column=1, sticky="ns")
    configurar_etiquetas_texto(txt)
    return marco, txt


def configurar_estilos_ttk(root):
    estilo = ttk.Style(root)
    estilo.theme_use("clam")
    estilo.configure("TNotebook", background=FONDO, borderwidth=0, tabmargins=(0, 0, 0, 0))
    estilo.configure("TNotebook.Tab", padding=(20, 11), font=fuente(11, "bold"), background="#E5E7EB",
                     foreground=TEXTO, borderwidth=0)
    estilo.map("TNotebook.Tab", background=[("selected", NEGRO), ("active", "#D1D5DB")],
               foreground=[("selected", BLANCO)])
    estilo.configure("Treeview", rowheight=32, font=fuente(11), background=BLANCO, fieldbackground=BLANCO,
                     foreground=TEXTO, borderwidth=0)
    estilo.configure("Treeview.Heading", background=NEGRO, foreground=BLANCO, font=fuente(10, "bold"),
                     relief="flat", padding=(6, 9))
    estilo.map("Treeview.Heading", background=[("active", ROJO)])
    estilo.map("Treeview", background=[("selected", ROJO)], foreground=[("selected", BLANCO)])
    estilo.configure("Moderno.TCombobox", padding=6, fieldbackground="#F9FAFB", background=BLANCO,
                     arrowcolor=ROJO, bordercolor=BORDE, lightcolor=BORDE, darkcolor=BORDE)
    estilo.map("Moderno.TCombobox", fieldbackground=[("readonly", "#F9FAFB")],
               background=[("readonly", BLANCO)], selectbackground=[("readonly", "#F9FAFB")],
               selectforeground=[("readonly", TEXTO)])
    estilo.configure("Vertical.TScrollbar", background="#D1D5DB", troughcolor=FONDO, bordercolor=FONDO,
                     arrowcolor=NEGRO, relief="flat")
    estilo.configure("Horizontal.TScrollbar", background="#D1D5DB", troughcolor=FONDO, bordercolor=FONDO,
                     arrowcolor=NEGRO, relief="flat")
    root.option_add("*TCombobox*Listbox.font", fuente(11))
