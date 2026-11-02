"""Ventana principal de NumeraLab: menú lateral, inicio, historial y configuración."""
import math
import time
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from interfaz.componentes import (BLANCO, BORDE, FONDO, GRIS, NEGRO, NEGRO_2, ROJO, ROJO_SUAVE, TEXTO,
                                  BotonModerno, ROJO_OSC, configurar_estilos_ttk, fuente, _rect_redondo)
from interfaz.pagina_metodo import PaginaMetodo
from metodos.ejemplos import NOMBRES
from utilidades import graficas
from utilidades.formato import fmt, fmt_pct



class ItemNavegacion(tk.Frame):
    """Opción del menú lateral con efecto al pasar el cursor y marca de la opción activa."""

    def __init__(self, master, texto, comando, simbolo="●"):
        super().__init__(master, bg=NEGRO, cursor="hand2")
        self.comando, self.activo = comando, False
        self.barra = tk.Frame(self, bg=NEGRO, width=5)
        self.barra.pack(side="left", fill="y")
        self.lbl = tk.Label(self, text=f"  {simbolo}   {texto}", font=fuente(11, "bold"), bg=NEGRO, fg="#D1D5DB",
                            anchor="w", pady=13, padx=6, cursor="hand2")
        self.lbl.pack(side="left", fill="x", expand=True)
        for w in (self, self.lbl, self.barra):
            w.bind("<Enter>", lambda e: self._pintar(True))
            w.bind("<Leave>", lambda e: self._pintar(False))
            w.bind("<Button-1>", lambda e: self.comando())

    def _pintar(self, hover):
        if self.activo:
            bg, fg, barra = ROJO, BLANCO, BLANCO
        elif hover:
            bg, fg, barra = NEGRO_2, BLANCO, ROJO
        else:
            bg, fg, barra = NEGRO, "#D1D5DB", NEGRO
        for w in (self, self.lbl):
            w.configure(bg=bg)
        self.lbl.configure(fg=fg)
        self.barra.configure(bg=barra)

    def activar(self, valor):
        self.activo = valor
        self._pintar(False)


class VentanaPrincipal(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NumeraLab — Calculadora de Métodos Numéricos")
        self.escala = max(1.0, self.winfo_fpixels("1i") / 96.0)
        ancho = min(int(1400 * self.escala), self.winfo_screenwidth() - 40)
        alto = min(int(850 * self.escala), self.winfo_screenheight() - 90)
        x, y = (self.winfo_screenwidth() - ancho) // 2, max(0, (self.winfo_screenheight() - alto) // 2 - 20)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.minsize(min(1100, ancho), min(680, alto))
        self.configure(bg=FONDO)
        self.decimales = 6
        self.historial = []
        self._aviso_id = None
        configurar_estilos_ttk(self)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._construir_menu()
        self.contenedor = tk.Frame(self, bg=FONDO)
        self.contenedor.grid(row=0, column=1, sticky="nsew")
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.paginas = {
            "inicio": self._pagina_inicio(),
            "secante": PaginaMetodo(self.contenedor, self, "secante"),
            "dorada": PaginaMetodo(self.contenedor, self, "dorada"),
            "historial": self._pagina_historial(),
            "config": self._pagina_config(),
        }
        for p in self.paginas.values():
            p.grid(row=0, column=0, sticky="nsew")
        self.aviso = tk.Label(self.contenedor, text="", font=fuente(11, "bold"), bg=NEGRO, fg=BLANCO, padx=18, pady=10)
        self.mostrar_pagina("inicio")
        self.protocol("WM_DELETE_WINDOW", self.cerrar)

    # ------------------------------------------------------------------ menú lateral
    def _construir_menu(self):
        menu = tk.Frame(self, bg=NEGRO, width=int(240 * self.escala))
        menu.grid(row=0, column=0, sticky="ns")
        menu.grid_propagate(False)
        menu.pack_propagate(False)
        logo = tk.Frame(menu, bg=NEGRO)
        logo.pack(fill="x", padx=18, pady=(26, 6))
        icono = tk.Canvas(logo, width=46, height=46, bg=NEGRO, highlightthickness=0)
        _rect_redondo(icono, 2, 2, 44, 44, 12, fill=ROJO, outline=ROJO)
        icono.create_text(23, 23, text="∑", fill=BLANCO, font=fuente(22, "bold"))
        icono.pack(side="left")
        tk.Label(logo, text="NumeraLab", font=fuente(16, "bold"), bg=NEGRO, fg=BLANCO).pack(side="left", padx=8)
        tk.Label(menu, text="Métodos Numéricos", font=fuente(10), bg=NEGRO, fg="#9CA3AF", anchor="w").pack(
            fill="x", padx=20, pady=(0, 22))
        self.items = {}
        for clave, texto, simbolo in (("inicio", "Inicio", "⌂"), ("secante", "Secante Modificada", "ƒ"),
                                      ("dorada", "Sección Dorada", "φ"), ("historial", "Historial", "☰"),
                                      ("config", "Configuración", "⚙")):
            it = ItemNavegacion(menu, texto, lambda c=clave: self.mostrar_pagina(c), simbolo)
            it.pack(fill="x", pady=1)
            self.items[clave] = it
        pie = tk.Frame(menu, bg=NEGRO)
        pie.pack(side="bottom", fill="x", padx=20, pady=(0, 22))
        tk.Frame(pie, bg=ROJO, height=3, width=46).pack(anchor="w", pady=(0, 10))
        tk.Label(pie, text="UNIVERSIDAD PILOTO\nDE COLOMBIA", font=fuente(11, "bold"), bg=NEGRO, fg=BLANCO,
                 justify="left", anchor="w").pack(fill="x")
        tk.Label(pie, text="MÉTODOS NUMÉRICOS · 2026", font=fuente(9, "bold"), bg=NEGRO, fg=ROJO,
                 anchor="w").pack(fill="x", pady=(4, 8))
        tk.Label(pie, text="Nikole Daniela Ospina Mayorga\nIsabela Ortega Torrado", font=fuente(9),
                 bg=NEGRO, fg="#9CA3AF", justify="left", anchor="w").pack(fill="x")

    def mostrar_pagina(self, nombre):
        self.paginas[nombre].tkraise()
        for k, it in self.items.items():
            it.activar(k == nombre)
        if nombre == "historial":
            self._llenar_historial()

    def ocultar_aviso(self):
        self.aviso.place_forget()

    def mostrar_aviso(self, texto, ms=3500):
        self.aviso.configure(text=texto)
        self.aviso.place(relx=0.5, rely=1.0, anchor="s", y=-18)
        self.aviso.lift()
        if self._aviso_id:
            self.after_cancel(self._aviso_id)
        self._aviso_id = self.after(ms, self.aviso.place_forget)

    # ------------------------------------------------------------------ inicio
    def _pagina_inicio(self):
        p = tk.Frame(self.contenedor, bg=FONDO)
        p.grid_columnconfigure(0, weight=1, uniform="m")
        p.grid_columnconfigure(1, weight=1, uniform="m")
        p.grid_rowconfigure(1, weight=1)
        banda = tk.Frame(p, bg=ROJO_SUAVE, highlightbackground=BORDE, highlightthickness=1)
        banda.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(20, 10))
        banda.grid_columnconfigure(0, weight=1)
        izq = tk.Frame(banda, bg=ROJO_SUAVE)
        izq.grid(row=0, column=0, sticky="w", padx=32, pady=16)
        tk.Label(izq, text="Bienvenido a", font=fuente(13), bg=ROJO_SUAVE, fg=GRIS).pack(anchor="w")
        tk.Label(izq, text="NumeraLab", font=fuente(34, "bold"), bg=ROJO_SUAVE, fg=ROJO).pack(anchor="w")
        tk.Label(izq, text="Calculadora interactiva de Métodos Numéricos", font=fuente(16, "bold"),
                 bg=ROJO_SUAVE, fg=NEGRO).pack(anchor="w")
        tk.Label(izq, text="Elija un método, complete los datos y obtenga el resultado con su procedimiento "
                           "paso a paso, la tabla de iteraciones y la gráfica.",
                 font=fuente(11), bg=ROJO_SUAVE, fg=TEXTO, justify="left", wraplength=int(560 * self.escala)
                 ).pack(anchor="w", pady=(8, 0))
        deco = tk.Canvas(banda, width=330, height=150, bg=ROJO_SUAVE, highlightthickness=0)
        deco.grid(row=0, column=1, padx=30)
        deco.create_line(15, 120, 315, 120, fill=NEGRO, width=2)
        deco.create_line(50, 12, 50, 135, fill=NEGRO, width=2)
        pts = []
        for k in range(0, 281, 8):
            pts += [35 + k, 120 - 85 * math.sin(k / 280 * math.pi * 1.35) * math.exp(-k / 520) - 6]
        deco.create_line(*pts, fill=ROJO, width=4, smooth=True)
        for xx in (90, 160, 215):
            deco.create_oval(xx - 5, 115, xx + 5, 125, fill=NEGRO, outline=NEGRO)
        deco.create_oval(249, 111, 265, 127, fill="#16A34A", outline="#16A34A")

        self._tarjeta_metodo(
            p, 0, "ƒ", "Método de la Secante Modificada",
            ("MÉTODO ABIERTO", "1 valor inicial", "Sin derivadas", "Busca raíces"),
            "Parte de un solo valor x₀ y lo mejora en cada iteración hasta que f(x) = 0. La pendiente se estima "
            "con un punto cercano, x + δ·x, por eso no necesita derivar. Es rápido, pero puede fallar si x₀ "
            "está lejos de la raíz.", "secante", graficas.demo_secante)
        self._tarjeta_metodo(
            p, 1, "φ", "Método de la Sección Dorada",
            ("POR INTERVALOS", "Intervalo [a, b]", "Sin derivadas", "Máximos y mínimos"),
            "Encierra el máximo o mínimo de f(x) entre a y b y reduce el intervalo con la razón dorada (0.618) "
            "en cada paso, reutilizando una evaluación. Siempre avanza, pero encuentra un óptimo local y no "
            "sirve para hallar raíces.", "dorada", graficas.demo_dorada)
        return p

    def _tarjeta_metodo(self, p, col, simbolo, titulo, etiquetas, texto, clave, demo):
        t = tk.Frame(p, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        t.grid(row=1, column=col, sticky="nsew", padx=(24, 10) if col == 0 else (10, 24), pady=(4, 20))
        t.grid_columnconfigure(1, weight=1)
        t.grid_rowconfigure(4, weight=1)
        c = tk.Canvas(t, width=64, height=64, bg=BLANCO, highlightthickness=0)
        c.create_oval(4, 4, 60, 60, fill=ROJO, outline=ROJO)
        c.create_text(32, 32, text=simbolo, fill=BLANCO, font=fuente(24, "bold"))
        c.grid(row=0, column=0, padx=(20, 12), pady=(18, 6))
        tk.Label(t, text=titulo, font=fuente(15, "bold"), bg=BLANCO, fg=NEGRO, anchor="w", justify="left",
                 wraplength=int(330 * self.escala)).grid(row=0, column=1, sticky="w", pady=(18, 6), padx=(0, 16))
        fila = tk.Frame(t, bg=BLANCO)
        fila.grid(row=1, column=0, columnspan=2, sticky="w", padx=20)
        for k, e in enumerate(etiquetas):
            tk.Label(fila, text=f" {e} ", font=fuente(8, "bold"), bg=ROJO if k == 0 else ROJO_SUAVE,
                     fg=BLANCO if k == 0 else ROJO_OSC, pady=3).pack(side="left", padx=(0, 5))
        tk.Label(t, text=texto, font=fuente(10), bg=BLANCO, fg=GRIS, anchor="nw", justify="left",
                 wraplength=int(430 * self.escala)).grid(row=2, column=0, columnspan=2, sticky="w", padx=20,
                                                         pady=(8, 8))
        BotonModerno(t, "Seleccionar  →", lambda: self.mostrar_pagina(clave), ancho=190, alto=42,
                     bg=BLANCO).grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 8))
        fig = Figure(figsize=(4.6, 2.5), dpi=100, facecolor="white", layout="constrained")
        demo(fig)
        marco_fig = tk.Frame(t, bg=BLANCO, width=240, height=160)
        marco_fig.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=12, pady=(0, 12))
        lienzo = FigureCanvasTkAgg(fig, master=marco_fig)
        lienzo.get_tk_widget().place(x=0, y=0, relwidth=1, relheight=1)

    # ------------------------------------------------------------------ historial
    def _pagina_historial(self):
        p = tk.Frame(self.contenedor, bg=FONDO)
        p.grid_rowconfigure(2, weight=1)
        p.grid_columnconfigure(0, weight=1)
        tk.Label(p, text="Historial de cálculos", font=fuente(22, "bold"), bg=FONDO, fg=NEGRO, anchor="w").grid(
            row=0, column=0, sticky="w", padx=24, pady=(24, 0))
        tk.Label(p, text="Cada cálculo queda guardado mientras el programa esté abierto. "
                         "Haga doble clic en uno para volver a cargarlo.", font=fuente(11), bg=FONDO, fg=GRIS,
                 anchor="w").grid(row=1, column=0, sticky="w", padx=24, pady=(0, 10))
        marco = tk.Frame(p, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        marco.grid(row=2, column=0, sticky="nsew", padx=24)
        marco.grid_rowconfigure(0, weight=1)
        marco.grid_columnconfigure(0, weight=1)
        self.tabla_hist = ttk.Treeview(marco, columns=("hora", "metodo", "funcion", "resultado"),
                                       show="headings", selectmode="browse")
        for c, t, w in (("hora", "Hora", 90), ("metodo", "Método", 170), ("funcion", "Función", 300),
                        ("resultado", "Resultado", 420)):
            self.tabla_hist.heading(c, text=t)
            self.tabla_hist.column(c, width=w, anchor="w", stretch=True)
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.tabla_hist.yview)
        self.tabla_hist.configure(yscrollcommand=sy.set)
        self.tabla_hist.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        self.tabla_hist.bind("<Double-1>", lambda e: self._cargar_historial())
        botones = tk.Frame(p, bg=FONDO)
        botones.grid(row=3, column=0, sticky="w", padx=24, pady=14)
        BotonModerno(botones, "Cargar seleccionado", self._cargar_historial, ancho=210, alto=44, bg=FONDO).pack(side="left")
        BotonModerno(botones, "Borrar historial", self._borrar_historial, ancho=180, alto=44, estilo="contorno",
                     bg=FONDO).pack(side="left", padx=10)
        return p

    def registrar_historial(self, metodo, res, entrada):
        dec = self.decimales
        if metodo == "secante":
            resumen = f"x ≈ {fmt(res.raiz, dec)}   (ε_a = {fmt_pct(res.ea_final)}, {res.n_iter} iter.)"
        else:
            resumen = f"x* ≈ {fmt(res.xopt, dec)},  f(x*) ≈ {fmt(res.fopt, dec)}   ({res.n_iter} iter.)"
        if res.estado != "convergio":
            resumen += "   [no convergió]"
        self.historial.insert(0, dict(hora=time.strftime("%H:%M:%S"), metodo=metodo, funcion=entrada["funcion"],
                                      resumen=resumen, entrada=entrada))
        del self.historial[100:]

    def _llenar_historial(self):
        self.tabla_hist.delete(*self.tabla_hist.get_children())
        for k, h in enumerate(self.historial):
            self.tabla_hist.insert("", "end", iid=str(k),
                                   values=(h["hora"], NOMBRES[h["metodo"]], h["funcion"], h["resumen"]))

    def _cargar_historial(self):
        sel = self.tabla_hist.selection()
        if not sel:
            messagebox.showinfo("Historial", "Seleccione primero un cálculo de la lista.", parent=self)
            return
        h = self.historial[int(sel[0])]
        self.mostrar_pagina(h["metodo"])
        self.paginas[h["metodo"]].restaurar(h["entrada"])

    def _borrar_historial(self):
        if self.historial and messagebox.askyesno("Borrar historial", "¿Desea borrar todo el historial?", parent=self):
            self.historial.clear()
            self._llenar_historial()

    # ------------------------------------------------------------------ configuración
    def _pagina_config(self):
        p = tk.Frame(self.contenedor, bg=FONDO)
        p.grid_columnconfigure(0, weight=1)
        tk.Label(p, text="Configuración", font=fuente(22, "bold"), bg=FONDO, fg=NEGRO, anchor="w").grid(
            row=0, column=0, sticky="w", padx=24, pady=(24, 10))
        t1 = tk.Frame(p, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        t1.grid(row=1, column=0, sticky="ew", padx=24, pady=6)
        tk.Label(t1, text="Decimales mostrados en resultados, tablas y procedimiento", font=fuente(12, "bold"),
                 bg=BLANCO, fg=NEGRO).pack(anchor="w", padx=20, pady=(16, 4))
        fila = tk.Frame(t1, bg=BLANCO)
        fila.pack(anchor="w", padx=20, pady=(0, 16))
        self.var_dec = tk.IntVar(value=self.decimales)
        tk.Spinbox(fila, from_=2, to=12, textvariable=self.var_dec, width=5, font=fuente(14), justify="center",
                   relief="flat", highlightthickness=2, highlightbackground=BORDE, highlightcolor=ROJO).pack(side="left")
        BotonModerno(fila, "Aplicar", self._aplicar_decimales, ancho=130, alto=40, bg=BLANCO).pack(side="left", padx=12)
        t2 = tk.Frame(p, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        t2.grid(row=2, column=0, sticky="ew", padx=24, pady=6)
        ayuda = ("Cómo escribir funciones\n\n"
                 "•  Variable: x        Constantes: pi, e\n"
                 "•  Operaciones: +  -  *  /  ^ (potencia).  También vale 2x, 3(x+1), (x+1)(x-1)\n"
                 "•  Funciones: sin, cos, tan, asin, acos, atan, sinh, cosh, tanh, exp, sqrt, ln, log, abs\n"
                 "•  ln(x) es el logaritmo natural y log(x) el de base 10\n"
                 "•  Los números aceptan coma o punto decimal, y expresiones como pi/2 o 1e-3\n\n"
                 "Seguridad: el texto se interpreta con un analizador matemático propio; no se ejecuta código.")
        tk.Label(t2, text=ayuda, font=fuente(11), bg=BLANCO, fg=TEXTO, justify="left", anchor="w").pack(
            anchor="w", padx=20, pady=16)
        t3 = tk.Frame(p, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        t3.grid(row=3, column=0, sticky="ew", padx=24, pady=6)
        tk.Label(t3, text="NumeraLab · Calculadora de Métodos Numéricos\nSecante Modificada y Sección Dorada · "
                          "Python, Tkinter, NumPy, SymPy y Matplotlib", font=fuente(11), bg=BLANCO, fg=GRIS,
                 justify="left").pack(anchor="w", padx=20, pady=16)
        return p

    def _aplicar_decimales(self):
        try:
            d = int(self.var_dec.get())
            if not 2 <= d <= 12:
                raise ValueError
        except (tk.TclError, ValueError):
            messagebox.showerror("Decimales", "Escriba un número entero entre 2 y 12.", parent=self)
            return
        self.decimales = d
        for k in ("secante", "dorada"):
            self.paginas[k].refrescar()
        self.mostrar_aviso(f"Ahora se muestran {d} decimales.")

    def cerrar(self):
        self.quit()
        self.destroy()
