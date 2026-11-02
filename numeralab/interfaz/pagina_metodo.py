"""Página completa de un método: panel de entrada con teclado y pestañas de resultados."""
import tkinter as tk
from tkinter import messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from interfaz.componentes import (AMBAR, AMBAR_SUAVE, BLANCO, BORDE, FONDO, GRIS, NEGRO, ROJO, ROJO_OSC,
                                  ROJO_SUAVE, TEXTO, VERDE, VERDE_SUAVE, BotonModerno, CampoCombo,
                                  CampoEtiquetado, MarcoDesplazable, TarjetaResultado, crear_texto, fuente,
                                  imagen_ecuacion, pintar_bloques)
from interfaz.teclado_matematico import TecladoMatematico
from metodos import secante_modificada as m_sec
from metodos.calculo import calcular as calcular_metodo
from metodos.ejemplos import CRITERIOS, EJEMPLOS, INFO, OBJETIVOS, PREDETERMINADOS
from metodos import seccion_dorada as m_dor
from utilidades import graficas
from utilidades.evaluador_funciones import (ErrorFuncion, ErrorNumeraLab, FuncionMatematica, valor_numerico)
from utilidades.ecuaciones import latex_de_funcion
from utilidades.tablas import tabla_iteraciones
from utilidades.formato import fmt, fmt_pct



class PaginaMetodo(tk.Frame):
    def __init__(self, master, ventana, metodo):
        super().__init__(master, bg=FONDO)
        self.ventana, self.metodo, self.info = ventana, metodo, INFO[metodo]
        self.resultado = None
        self.f_actual = None
        self.f_edicion = None
        self.obsoleto = False
        self.paginas, self.pagina_idx, self.ver_todo = [], 0, False
        self.iter_graf = 1
        self.ejemplo_idx = 0
        self._after_preview = None
        self.campos = {}

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_encabezado()
        cuerpo = tk.Frame(self, bg=FONDO)
        cuerpo.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))
        cuerpo.grid_columnconfigure(0, weight=0, minsize=int(480 * self.ventana.escala))
        cuerpo.grid_columnconfigure(1, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)
        self._construir_entrada(cuerpo)
        self._construir_resultados(cuerpo)
        self._poner_datos(PREDETERMINADOS[metodo], vaciar_funcion=True)
        self._al_cambiar_funcion()
        self._reiniciar_resultados()

    # ------------------------------------------------------------------ encabezado
    def _construir_encabezado(self):
        enc = tk.Frame(self, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        enc.grid(row=0, column=0, sticky="ew", padx=18, pady=(14, 12))
        enc.grid_columnconfigure(1, weight=1)
        tk.Frame(enc, bg=ROJO, width=8).grid(row=0, column=0, rowspan=2, sticky="ns")
        tk.Label(enc, text=self.info["titulo"], font=fuente(22, "bold"), bg=BLANCO, fg=NEGRO,
                 anchor="w").grid(row=0, column=1, sticky="w", padx=18, pady=(10, 0))
        tk.Label(enc, text="NumeraLab · Calculadora interactiva de Métodos Numéricos — " + self.info["subtitulo"],
                 font=fuente(11), bg=BLANCO, fg=GRIS, anchor="w").grid(row=1, column=1, sticky="w", padx=18,
                                                                       pady=(0, 10))
        tk.Label(enc, text=f"  {self.info['etiqueta']}  ", font=fuente(10, "bold"), bg=ROJO, fg=BLANCO,
                 pady=5).grid(row=0, column=2, rowspan=2, padx=18)

    # ------------------------------------------------------------------ panel de entrada
    def _construir_entrada(self, parent):
        marco = MarcoDesplazable(parent, FONDO)
        marco.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        tarjeta = tk.Frame(marco.interior, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        tarjeta.pack(fill="both", expand=True, padx=(0, 6), pady=2)
        cont = tk.Frame(tarjeta, bg=BLANCO)
        cont.pack(fill="both", expand=True, padx=16, pady=14)

        tk.Label(cont, text="DATOS DE ENTRADA", font=fuente(10, "bold"), bg=BLANCO, fg=ROJO,
                 anchor="w").pack(fill="x")
        tk.Label(cont, text="Función f(x)", font=fuente(9, "bold"), bg=BLANCO, fg=GRIS,
                 anchor="w").pack(fill="x", pady=(8, 0))
        fila = tk.Frame(cont, bg=BLANCO)
        fila.pack(fill="x")
        tk.Label(fila, text="f(x) =", font=fuente(14, "bold"), bg=BLANCO, fg=ROJO).pack(side="left", padx=(0, 8))
        self.var_funcion = tk.StringVar()
        self.entry_funcion = tk.Entry(fila, textvariable=self.var_funcion, font=fuente(15), relief="flat",
                                      bg="#F9FAFB", fg=TEXTO, insertbackground=ROJO, highlightthickness=2,
                                      highlightbackground=BORDE, highlightcolor=ROJO, bd=4)
        self.entry_funcion.pack(side="left", fill="x", expand=True, ipady=6)
        self.lbl_validacion = tk.Label(cont, text="", font=fuente(9), bg=BLANCO, anchor="w", justify="left",
                                       wraplength=430)
        self.lbl_validacion.pack(fill="x", pady=(4, 2))
        self.caja_eq = tk.Frame(cont, bg="#F9FAFB", highlightbackground=BORDE, highlightthickness=1,
                                height=int(88 * self.ventana.escala))
        self.caja_eq.pack(fill="x", pady=(0, 4))
        self.caja_eq.pack_propagate(False)
        self.lbl_eq = tk.Label(self.caja_eq, bg="#F9FAFB", fg=GRIS, font=fuente(10),
                               text="Aquí verá su función escrita como ecuación")
        self.lbl_eq.pack(expand=True)
        self._img_funcion = None

        rejilla = tk.Frame(cont, bg=BLANCO)
        rejilla.pack(fill="x", pady=(6, 0))
        rejilla.grid_columnconfigure(0, weight=1, uniform="p")
        rejilla.grid_columnconfigure(1, weight=1, uniform="p")
        if self.metodo == "secante":
            self._campo(rejilla, "x0", "Valor inicial x₀", 0, 0)
            self._campo(rejilla, "delta", "Perturbación relativa δ", 0, 1)
            self._campo(rejilla, "tol", "Error tolerado (%)", 1, 0)
            self._campo(rejilla, "max_iter", "Máx. iteraciones", 1, 1)
        else:
            self._campo(rejilla, "a", "Límite inferior a", 0, 0)
            self._campo(rejilla, "b", "Límite superior b", 0, 1)
            self.campos["objetivo"] = CampoCombo(rejilla, "Objetivo", OBJETIVOS)
            self.campos["objetivo"].grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=5)
            self._campo(rejilla, "max_iter", "Máx. iteraciones", 1, 1)
            self.campos["criterio"] = CampoCombo(rejilla, "Criterio de parada", CRITERIOS)
            self.campos["criterio"].grid(row=2, column=0, sticky="ew", padx=(0, 6), pady=5)
            self._campo(rejilla, "tol", "Error tolerado (%)", 2, 1)
            self.campos["criterio"].var.trace_add("write", lambda *a: self._etiqueta_tolerancia())
        for c in self.campos.values():
            if hasattr(c, "var"):
                c.var.trace_add("write", lambda *a: self._programar_preview())

        botones = tk.Frame(cont, bg=BLANCO)
        botones.pack(fill="x", pady=(12, 6))
        botones.grid_columnconfigure(0, weight=1, uniform="b")
        botones.grid_columnconfigure(1, weight=1, uniform="b")
        BotonModerno(botones, "CALCULAR", self.calcular, alto=48, estilo="rojo", tam=14, bg=BLANCO).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=3)
        BotonModerno(botones, "EJEMPLO", self.cargar_ejemplo, alto=40, estilo="negro", bg=BLANCO).grid(
            row=1, column=0, sticky="ew", padx=(0, 3), pady=3)
        BotonModerno(botones, "LIMPIAR", self.limpiar, alto=40, estilo="contorno", bg=BLANCO).grid(
            row=1, column=1, sticky="ew", padx=(3, 0), pady=3)
        BotonModerno(botones, "VER PROCEDIMIENTO", self.ver_procedimiento, alto=40, estilo="gris", bg=BLANCO).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=3)

        tk.Label(cont, text="TECLADO MATEMÁTICO", font=fuente(10, "bold"), bg=BLANCO, fg=ROJO,
                 anchor="w").pack(fill="x", pady=(8, 2))
        self.teclado = TecladoMatematico(cont, BLANCO)
        self.teclado.pack(fill="x")
        self.teclado.registrar(self.entry_funcion)
        for c in self.campos.values():
            if hasattr(c, "entry"):
                self.teclado.registrar(c.entry)

        ayuda = ("Ayuda de sintaxis: use x como variable, ^ para potencias, * para multiplicar (2x también "
                 "vale), ln(x) logaritmo natural, log(x) base 10, exp(x) = eˣ, sqrt(x) raíz cuadrada. "
                 "Ejemplos: exp(-x) - x   ·   x^3 - 2x - 5   ·   sin(x) + x/2")
        lbl_ayuda = tk.Label(cont, text=ayuda, font=fuente(9), bg="#F9FAFB", fg=GRIS, wraplength=430,
                             justify="left", anchor="w", padx=10, pady=8)
        lbl_ayuda.pack(fill="x", pady=(8, 0))

        def _ajustar(e):   # el texto se adapta al ancho real del panel
            self.lbl_validacion.configure(wraplength=max(200, e.width - 8))
            lbl_ayuda.configure(wraplength=max(200, e.width - 28))
        cont.bind("<Configure>", _ajustar)

        self.var_funcion.trace_add("write", lambda *a: self._al_cambiar_funcion())

    def _campo(self, rejilla, clave, etiqueta, fila, col):
        c = CampoEtiquetado(rejilla, etiqueta)
        c.grid(row=fila, column=col, sticky="ew", padx=(0, 6) if col == 0 else (6, 0), pady=5)
        self.campos[clave] = c

    def _etiqueta_tolerancia(self):
        es_rel = self.campos["criterio"].get() == CRITERIOS[0]
        self.campos["tol"].set_etiqueta("Error tolerado (%)" if es_rel else "Error tolerado (longitud)")

    # ------------------------------------------------------------------ resultados (pestañas)
    def _construir_resultados(self, parent):
        self.nb = ttk.Notebook(parent)
        self.nb.grid(row=0, column=1, sticky="nsew")
        t_calc, t_proc, t_tabla, t_graf = (tk.Frame(self.nb, bg=FONDO) for _ in range(4))
        for t, nombre in ((t_calc, "  Calculadora  "), (t_proc, "  Procedimiento  "),
                          (t_tabla, "  Tabla de iteraciones  "), (t_graf, "  Gráfica  ")):
            self.nb.add(t, text=nombre)
        self._tab_calculadora(t_calc)
        self._tab_procedimiento(t_proc)
        self._tab_tabla(t_tabla)
        self._tab_grafica(t_graf)

    def _tab_calculadora(self, tab):
        tab.grid_rowconfigure(2, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.banner = tk.Label(tab, text="", font=fuente(12, "bold"), anchor="w", justify="left", padx=16,
                               pady=12, wraplength=700)
        self.banner.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        self.banner.bind("<Configure>", lambda e: self.banner.configure(wraplength=max(200, e.width - 40)))
        cuadro = tk.Frame(tab, bg=FONDO)
        cuadro.grid(row=1, column=0, sticky="ew", padx=10)
        cuadro.grid_columnconfigure(0, weight=1, uniform="t")
        cuadro.grid_columnconfigure(1, weight=1, uniform="t")
        titulos = (["RAÍZ APROXIMADA", "VALOR f(raíz)", "ERROR APROXIMADO ε_a", "ITERACIONES"]
                   if self.metodo == "secante" else
                   ["ÓPTIMO x*", "VALOR f(x*)", "INTERVALO FINAL", "ITERACIONES"])
        colores = [ROJO, NEGRO, ROJO, NEGRO]
        self.tarjetas = []
        for k, (t, col) in enumerate(zip(titulos, colores)):
            tj = TarjetaResultado(cuadro, t, col)
            tj.grid(row=k // 2, column=k % 2, sticky="ew", padx=4, pady=4)
            self.tarjetas.append(tj)
        marco, self.txt_resumen = crear_texto(tab)
        marco.grid(row=2, column=0, sticky="nsew", padx=10, pady=(6, 10))

    def _tab_procedimiento(self, tab):
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        barra = tk.Frame(tab, bg=FONDO)
        barra.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        barra.grid_columnconfigure(1, weight=1)
        self.btn_ant = BotonModerno(barra, "◀  Anterior", self._pag_anterior, ancho=125, alto=40,
                                    estilo="negro", bg=FONDO)
        self.btn_ant.grid(row=0, column=0)
        self.lbl_pag = tk.Label(barra, text="", font=fuente(10, "bold"), bg=FONDO, fg=TEXTO)
        self.lbl_pag.grid(row=0, column=1, sticky="ew", padx=6)
        self.btn_sig = BotonModerno(barra, "Siguiente  ▶", self._pag_siguiente, ancho=125, alto=40,
                                    estilo="rojo", bg=FONDO)
        self.btn_sig.grid(row=0, column=2, padx=(0, 6))
        self.btn_todo = BotonModerno(barra, "Ver todo", self._alternar_todo, ancho=105, alto=40,
                                     estilo="contorno", bg=FONDO)
        self.btn_todo.grid(row=0, column=3)
        marco, self.txt_proc = crear_texto(tab)
        marco.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def _tab_tabla(self, tab):
        tab.grid_rowconfigure(0, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        marco = tk.Frame(tab, bg=BLANCO, highlightbackground=BORDE, highlightthickness=1)
        marco.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        marco.grid_rowconfigure(0, weight=1)
        marco.grid_columnconfigure(0, weight=1)
        self.tabla = ttk.Treeview(marco, show="headings", selectmode="browse")
        sy = ttk.Scrollbar(marco, orient="vertical", command=self.tabla.yview)
        sx = ttk.Scrollbar(marco, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        self.tabla.tag_configure("par", background="#F9FAFB")
        self.tabla.tag_configure("impar", background=BLANCO)
        self.tabla.tag_configure("final", background=VERDE_SUAVE, font=fuente(11, "bold"))

    def _tab_grafica(self, tab):
        tab.grid_rowconfigure(1, weight=1)
        tab.grid_columnconfigure(0, weight=1)
        self.ctl_graf = tk.Frame(tab, bg=FONDO)
        self.ctl_graf.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        BotonModerno(self.ctl_graf, "◀", lambda: self._mover_iter(-1), ancho=50, alto=36, estilo="negro",
                     bg=FONDO).pack(side="left")
        self.lbl_iter_graf = tk.Label(self.ctl_graf, text="", font=fuente(11, "bold"), bg=FONDO, width=26)
        self.lbl_iter_graf.pack(side="left", padx=6)
        BotonModerno(self.ctl_graf, "▶", lambda: self._mover_iter(1), ancho=50, alto=36, estilo="rojo",
                     bg=FONDO).pack(side="left")
        BotonModerno(self.ctl_graf, "Ver el final", lambda: self._mover_iter(10 ** 6), ancho=120, alto=36,
                     estilo="contorno", bg=FONDO).pack(side="left", padx=8)
        self.fig = Figure(figsize=(7, 5), dpi=100, facecolor="white", layout="constrained")
        # El lienzo se coloca con place(): ignora el tamaño que pide Matplotlib (que crece en pantallas de alta
        # escala) y siempre ocupa exactamente el espacio disponible.
        marco_fig = tk.Frame(tab, bg=BLANCO, width=240, height=200)
        marco_fig.grid(row=1, column=0, sticky="nsew", padx=10, pady=8)
        self.canvas_fig = FigureCanvasTkAgg(self.fig, master=marco_fig)
        self.canvas_fig.get_tk_widget().place(x=0, y=0, relwidth=1, relheight=1)
        barra = NavigationToolbar2Tk(self.canvas_fig, tab, pack_toolbar=False)
        barra.update()
        barra.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))
        if self.metodo != "dorada":
            self.ctl_graf.grid_remove()

    # ------------------------------------------------------------------ validación y vista previa
    def _mostrar_ecuacion_funcion(self, f):
        """Dibuja f(x) con formato matemático (fracciones, exponentes...) bajo el campo de texto."""
        img = None
        if f is not None:
            tex = latex_de_funcion(f)
            if tex:
                ancho = max(200, (self.caja_eq.winfo_width() if self.caja_eq.winfo_width() > 50
                                  else int(420 * self.ventana.escala)) - 20)
                img = imagen_ecuacion("f(x)=" + tex, "eqprev", self.ventana.escala, ancho)
        self._img_funcion = img
        if img is not None:
            self.lbl_eq.configure(image=img, text="")
        else:
            self.lbl_eq.configure(image="", text="Aquí verá su función escrita como ecuación"
                                  if f is None else "f(x) = " + f.texto)

    def _al_cambiar_funcion(self):
        texto = self.var_funcion.get()
        f_ok = None
        if not texto.strip():
            self.f_edicion = None
            self.lbl_validacion.configure(text="Escriba una función o presione EJEMPLO.", fg=GRIS)
        else:
            try:
                f = FuncionMatematica(texto)
                self.f_edicion = f
                if not f.usa_x():
                    self.lbl_validacion.configure(text="✖ La función debe contener la variable x.", fg=ROJO)
                else:
                    self.lbl_validacion.configure(text="✔ Función válida", fg=VERDE)
                    f_ok = f
            except ErrorFuncion as e:
                self.f_edicion = None
                self.lbl_validacion.configure(text="✖ " + str(e), fg=ROJO)
        self._mostrar_ecuacion_funcion(f_ok)
        self._programar_preview()

    def _programar_preview(self):
        if self.resultado is not None and not self.obsoleto:
            self.obsoleto = True
            self._pintar_banner_obsoleto()
        if self._after_preview:
            self.after_cancel(self._after_preview)
        self._after_preview = self.after(450, self._dibujar_preview)

    def _pintar_banner_obsoleto(self):
        self.banner.configure(text="⚠ Los datos cambiaron. Presione CALCULAR para actualizar los resultados.",
                              bg=AMBAR_SUAVE, fg=AMBAR)

    def _rango_vista_previa(self):
        try:
            if self.metodo == "secante":
                x0 = valor_numerico(self.campos["x0"].get(), "x₀")
                h = max(3.0, 2 * abs(x0))
                return x0 - h, x0 + h
            a = valor_numerico(self.campos["a"].get(), "a")
            b = valor_numerico(self.campos["b"].get(), "b")
            if a < b:
                m = 0.06 * (b - a)
                return a - m, b + m
        except ErrorNumeraLab:
            pass
        return -10.0, 10.0

    def _dibujar_preview(self):
        self._after_preview = None
        xmin, xmax = self._rango_vista_previa()
        f = self.f_edicion if (self.f_edicion and self.f_edicion.usa_x()) else None
        graficas.vista_previa(self.fig, f, xmin, xmax)
        self.canvas_fig.draw_idle()
        if self.metodo == "dorada":
            self.lbl_iter_graf.configure(text="Vista previa (aún sin calcular)")

    # ------------------------------------------------------------------ acciones
    def _poner_datos(self, datos, vaciar_funcion=False):
        if "funcion" in datos or vaciar_funcion:
            self.var_funcion.set(datos.get("funcion", ""))
        for clave, campo in self.campos.items():
            if clave in datos:
                campo.set(datos[clave])
        if self.metodo == "dorada":
            self._etiqueta_tolerancia()

    def cargar_ejemplo(self):
        lista = EJEMPLOS[self.metodo]
        self._poner_datos(lista[self.ejemplo_idx % len(lista)])
        self.ventana.mostrar_aviso(f"Ejemplo {self.ejemplo_idx % len(lista) + 1} de {len(lista)} cargado. "
                                   "Presione CALCULAR.")
        self.ejemplo_idx += 1

    def limpiar(self):
        self.var_funcion.set("")
        self._poner_datos(PREDETERMINADOS[self.metodo])
        self.resultado, self.f_actual, self.obsoleto = None, None, False
        self._reiniciar_resultados()
        self.nb.select(0)
        self.entry_funcion.focus_set()

    def calcular(self):
        if self._after_preview:
            self.after_cancel(self._after_preview)
            self._after_preview = None
        try:
            f, res = calcular_metodo(self.metodo, self.var_funcion.get(),
                                     {k: c.get() for k, c in self.campos.items()})
        except ErrorNumeraLab as e:
            messagebox.showerror("Revise los datos", str(e), parent=self.winfo_toplevel())
            return False
        self.f_actual, self.resultado, self.obsoleto = f, res, False
        self.ventana.ocultar_aviso()
        self.iter_graf = res.n_iter if self.metodo == "dorada" else 1
        self._mostrar_resultado(res)
        self.nb.select(0)
        self.ventana.registrar_historial(self.metodo, res, self._entrada_actual())
        if res.estado != "convergio":
            messagebox.showwarning("El método no convergió", res.mensaje, parent=self.winfo_toplevel())
        return True

    def _entrada_actual(self):
        d = {k: c.get() for k, c in self.campos.items()}
        d["funcion"] = self.var_funcion.get()
        return d

    def restaurar(self, entrada):
        self._poner_datos(entrada)
        self.calcular()

    def ver_procedimiento(self):
        if self.resultado is None or self.obsoleto:
            if not self.calcular():
                return
        self.nb.select(1)

    def refrescar(self):
        """Vuelve a mostrar el resultado (por ejemplo, tras cambiar el número de decimales)."""
        if self.resultado is not None:
            self._mostrar_resultado(self.resultado)

    # ------------------------------------------------------------------ mostrar resultados
    def _reiniciar_resultados(self):
        self.banner.configure(text="Escriba una función, ajuste los datos y presione CALCULAR.",
                              bg=BLANCO, fg=GRIS)
        for t in self.tarjetas:
            t.actualizar("—")
        ayuda = m_sec.bloques_ayuda() if self.metodo == "secante" else m_dor.bloques_ayuda()
        pintar_bloques(self.txt_resumen, ayuda, self.ventana.escala)
        self.paginas, self.pagina_idx, self.ver_todo = [], 0, False
        pintar_bloques(self.txt_proc, [("h1", "Procedimiento paso a paso"),
                                       ("p", "Presione CALCULAR para ver aquí, iteración por iteración, "
                                             "la fórmula, la sustitución de números, las evaluaciones de f, "
                                             "el error y la condición de parada.")], self.ventana.escala)
        self.lbl_pag.configure(text="Sin cálculo todavía")
        self.btn_ant.configurar(activo=False)
        self.btn_sig.configurar(activo=False)
        self.tabla["columns"] = ()
        self.tabla.delete(*self.tabla.get_children())
        self._programar_preview()

    def _mostrar_resultado(self, res):
        dec = self.ventana.decimales
        # --- Calculadora
        if res.estado == "convergio":
            self.banner.configure(text="✔ " + res.mensaje, bg=VERDE_SUAVE, fg=VERDE)
        elif res.estado == "max_iter":
            self.banner.configure(text="⚠ " + res.mensaje, bg=AMBAR_SUAVE, fg=AMBAR)
        else:
            self.banner.configure(text="✖ " + res.mensaje, bg=ROJO_SUAVE, fg=ROJO_OSC)
        t = self.tarjetas
        if self.metodo == "secante":
            t[0].actualizar(fmt(res.raiz, dec), "x donde f(x) ≈ 0")
            t[1].actualizar(fmt(res.f_raiz, dec), "debe ser cercano a 0")
            t[2].actualizar(fmt_pct(res.ea_final, dec), f"tolerancia: {fmt(res.tol)} %")
            t[3].actualizar(str(res.n_iter), f"máximo permitido: {res.max_iter}")
        else:
            xl, xu = res.intervalo_final
            t[0].actualizar(fmt(res.xopt, dec), f"{res.nombre_objetivo()} aproximado")
            t[1].actualizar(fmt(res.fopt, dec), "valor de la función en x*")
            t[2].actualizar(f"[{fmt(xl, 4)}, {fmt(xu, 4)}]", f"longitud {fmt(xu - xl, 6)}")
            t[3].actualizar(str(res.n_iter), f"{res.evaluaciones} evaluaciones de f")
        pintar_bloques(self.txt_resumen, res.bloques_resumen(dec), self.ventana.escala)
        # --- Tabla
        self._llenar_tabla(res, dec)
        # --- Procedimiento
        gen = m_sec.generar_pasos if self.metodo == "secante" else m_dor.generar_pasos
        self.paginas = gen(res, dec)
        self.pagina_idx, self.ver_todo = 0, False
        self.btn_todo.configurar("Ver todo")
        self._mostrar_pagina()
        # --- Gráfica
        self._dibujar_resultado()

    def _llenar_tabla(self, res, dec):
        anchos = {"i": 45, "x_i": 115, "f(x_i)": 115, "x_i + δ·x_i": 125, "f(x_i + δ·x_i)": 135, "x_(i+1)": 125,
                  "ε_a (%)": 100, "a (x_L)": 92, "b (x_U)": 92, "x1": 92, "x2": 92, "f(x1)": 92, "f(x2)": 92,
                  "Intervalo actualizado": 170, "Longitud": 88}
        cols, filas = tabla_iteraciones(self.metodo, res, dec)
        self.tabla.delete(*self.tabla.get_children())
        self.tabla["columns"] = cols
        for c in cols:
            w = anchos.get(c, 100)
            self.tabla.heading(c, text=c)
            self.tabla.column(c, width=w, minwidth=w, anchor="center", stretch=True)
        for k, fila in enumerate(filas):
            ultima = k == len(filas) - 1 and res.convergio
            self.tabla.insert("", "end", values=fila, tags=("final" if ultima else ("par" if k % 2 else "impar"),))

    # ------------------------------------------------------------------ procedimiento: navegación
    def _mostrar_pagina(self):
        n = len(self.paginas)
        if n == 0:
            return
        if self.ver_todo:
            bloques = []
            for titulo, b in self.paginas:
                bloques += b + [("p", "")]
            self.lbl_pag.configure(text=f"Procedimiento completo ({n} secciones)")
            self.btn_ant.configurar(activo=False)
            self.btn_sig.configurar(activo=False)
        else:
            titulo, bloques = self.paginas[self.pagina_idx]
            self.lbl_pag.configure(text=f"{titulo}  ·  paso {self.pagina_idx + 1} de {n}")
            self.btn_ant.configurar(activo=self.pagina_idx > 0)
            self.btn_sig.configurar(activo=self.pagina_idx < n - 1)
        self.txt_proc.configure(cursor="watch")
        self.update_idletasks()
        pintar_bloques(self.txt_proc, bloques, self.ventana.escala)
        self.txt_proc.configure(cursor="arrow")

    def _pag_anterior(self):
        if self.pagina_idx > 0:
            self.pagina_idx -= 1
            self._mostrar_pagina()

    def _pag_siguiente(self):
        if self.pagina_idx < len(self.paginas) - 1:
            self.pagina_idx += 1
            self._mostrar_pagina()

    def _alternar_todo(self):
        if not self.paginas:
            return
        self.ver_todo = not self.ver_todo
        self.btn_todo.configurar("Paso a paso" if self.ver_todo else "Ver todo")
        self._mostrar_pagina()

    # ------------------------------------------------------------------ gráfica
    def _dibujar_resultado(self):
        res = self.resultado
        if res is None or self.f_actual is None:
            return
        if self.metodo == "secante":
            graficas.graficar_secante(self.fig, self.f_actual, res)
        else:
            self.iter_graf = max(1, min(self.iter_graf, res.n_iter))
            graficas.graficar_dorada(self.fig, self.f_actual, res, self.iter_graf)
            self.lbl_iter_graf.configure(text=f"Iteración {self.iter_graf} de {res.n_iter}")
        self.canvas_fig.draw_idle()

    def _mover_iter(self, delta):
        if self.resultado is None or self.obsoleto:
            return
        self.iter_graf = max(1, min(self.iter_graf + delta, self.resultado.n_iter))
        self._dibujar_resultado()
