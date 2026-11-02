# NumeraLab — Calculadora de Métodos Numéricos

Aplicación de escritorio (Python + Tkinter) **y versión web (Streamlit)** para estudiar y presentar dos métodos numéricos:

1. **Secante Modificada** — encuentra raíces de f(x) sin derivar.
2. **Sección Dorada** — encuentra el máximo o mínimo local de f(x) dentro de un intervalo `[a, b]`
   (es un método de optimización; **no** sirve para hallar raíces).

Incluye teclado matemático en pantalla, **vista previa de la función como ecuación** (fracciones, exponentes),
procedimiento paso a paso con **ecuaciones tipográficas** (botones Anterior/Siguiente), tabla de iteraciones,
gráficas integradas, historial y validación de datos.

## 1. Instalar Python (Windows)

1. Descargue Python 3.10 o superior desde <https://www.python.org/downloads/>.
2. En el instalador marque **«Add python.exe to PATH»** y deje marcada la opción **«tcl/tk and IDLE»**
   (es lo que instala Tkinter).
3. Compruebe en una terminal (PowerShell o CMD): `python --version`

## 2. Abrir el proyecto en Visual Studio Code

1. Descomprima la carpeta `numeralab`.
2. En VS Code: **Archivo → Abrir carpeta…** y elija `numeralab`.
3. Abra una terminal: **Terminal → Nueva terminal**.

## 3. Instalar las dependencias

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

(Si PowerShell bloquea la activación: `Set-ExecutionPolicy -Scope Process Bypass` y repita.
También puede omitir el entorno virtual e instalar directamente con `pip install -r requirements.txt`.)

## 4. Ejecutar

```powershell
python main.py
```

## 4b. Versión web (Streamlit)

La misma calculadora, ahora en el navegador. Usa **exactamente los mismos módulos de cálculo** que la versión de
escritorio (`metodos/`, `utilidades/`), así que valida, calcula y explica igual. Las ecuaciones se muestran con KaTeX,
la tabla con Pandas (con botón para descargarla en CSV) y las gráficas con Matplotlib. Funciona también en celular.

**Ejecutar en su computador** (desde la carpeta `numeralab`, con las dependencias ya instaladas):

```powershell
streamlit run app_web.py
```

Se abre solo en <http://localhost:8501>. Si el comando `streamlit` no se reconoce: `python -m streamlit run app_web.py`.
Si el puerto está ocupado: `streamlit run app_web.py --server.port 8502`. Otros dispositivos conectados a la misma red
Wi-Fi pueden abrirla con la «Network URL» que aparece en la terminal.

**Publicarla en internet (gratis, con Streamlit Community Cloud):**
1. Suba la carpeta `numeralab` a un repositorio de GitHub (debe incluir `requirements.txt` y `.streamlit/`).
2. Entre a <https://share.streamlit.io>, inicie sesión con GitHub y elija **Create app**.
3. Seleccione el repositorio y la rama, y como archivo principal escriba `app_web.py`. Pulse **Deploy**.
4. Al terminar, recibirá un enlace público (`https://....streamlit.app`) para compartir. La web no necesita Tkinter.

(También sirve Hugging Face Spaces con el SDK de Streamlit.)

**Diferencias con la versión de escritorio:** el teclado de la web agrega los símbolos al final de la función (las
funciones se agregan con su paréntesis abierto: `sin(`); el historial dura mientras la pestaña del navegador esté
abierta; y las gráficas son imágenes (no tienen zoom interactivo). A cambio, agrega la descarga de la tabla en CSV.

## 5. Estructura

```
numeralab/
    main.py                       punto de entrada de la versión de escritorio
    app_web.py                    punto de entrada de la versión web (Streamlit)
    requirements.txt
    README.md
    interfaz/
        ventana_principal.py      ventana, menú lateral, inicio, historial, configuración
        pagina_metodo.py          panel de entrada + pestañas de resultados de cada método
        teclado_matematico.py     teclado en pantalla
        componentes.py            botones redondeados, tarjetas, campos, estilos
    web/
        paginas.py                páginas de la web (inicio, métodos, historial, configuración)
        render.py                 dibuja bloques de texto y ecuaciones (KaTeX)
        teclado.py                teclado matemático de la web
    .streamlit/config.toml        tema (rojo, negro y blanco) de la web
    metodos/
        secante_modificada.py     cálculo + procedimiento (sin depender de la interfaz)
        seccion_dorada.py         cálculo + procedimiento (sin depender de la interfaz)
        calculo.py                lee y valida los campos y ejecuta el método (lo usan escritorio y web)
        ejemplos.py               ejemplos y valores predeterminados compartidos
    utilidades/
        evaluador_funciones.py    analizador matemático SEGURO (no usa eval sobre el texto)
        graficas.py               gráficas con Matplotlib
        formato.py                formato de números
        tablas.py                 tabla de iteraciones (escritorio y web)
        ecuaciones.py             ecuaciones con formato matemático (LaTeX → imagen, sin instalar LaTeX)
    pruebas/
        test_metodos.py           24 pruebas (cálculos y ecuaciones)
        test_web.py               6 pruebas de la web (se omiten si Streamlit no está instalado)
```

## 6. Cómo escribir funciones

| Quiere escribir | Escriba |
|---|---|
| e⁻ˣ − x | `exp(-x) - x` |
| x³ − 2x − 5 | `x^3 - 2x - 5` (también vale `x^3 - 2*x - 5`) |
| 4x − 1.8x² | `4x - 1.8x^2` (el producto implícito `4x` vale) |
| ln x (natural) / log₁₀ x | `ln(x)` / `log(x)` |
| √x | `sqrt(x)` |
| π, e | `pi`, `e` |

Funciones permitidas: `sin cos tan asin acos atan sinh cosh tanh exp sqrt ln log abs`.
Los parámetros aceptan coma o punto decimal y expresiones como `pi/2` o `1e-3`.

## 7. Ejemplos de uso

El botón **EJEMPLO** carga datos de prueba. Cada clic pasa al siguiente ejemplo:

**Secante Modificada**
1. `exp(-x) - x`, x₀ = 0.5, δ = 0.01, tolerancia 1 % → raíz ≈ 0.5671
2. `exp(-x) - x`, x₀ = 1, δ = 0.01, tolerancia 1 % (ejemplo 6.8 de Chapra) →
   x₁ = 0.537263, x₂ = 0.567010, x₃ = 0.567143

**Sección Dorada**
1. `(x - 2)^2 + 1`, [0, 5], minimizar, longitud < 0.01 → x ≈ 2, f ≈ 1
2. `4x - 1.8x^2 + 1.2x^3 - 0.3x^4`, [-2, 4], maximizar, ε_a < 1 % →
   x ≈ 2.3282, f ≈ 5.8853, 11 iteraciones

**Criterio de parada de la Sección Dorada**
- *Error relativo (%)*: ε_a = (1 − R)·|(x_U − x_L)/x_opt|·100 (el que se usa en clase).
- *Longitud del intervalo*: se detiene cuando x_U − x_L < tolerancia (valor absoluto).

## 8. Pruebas de los cálculos

```powershell
python -m unittest discover -s pruebas -v
```

Verifican, entre otras cosas, el ejemplo 6.8 de Chapra (secante modificada), el máximo de
`4x − 1.8x² + 1.2x³ − 0.3x⁴`, la reutilización de evaluaciones en la sección dorada, el
rechazo de código malicioso y la validación de parámetros.

## 9. Solución de errores comunes

| Problema | Solución |
|---|---|
| `ModuleNotFoundError: No module named 'numpy'` (o matplotlib/sympy) | `pip install -r requirements.txt` |
| `No module named 'tkinter'` | Reinstale Python marcando «tcl/tk and IDLE» |
| `python` no se reconoce | Reinstale Python marcando «Add python.exe to PATH», o use `py main.py` |
| «x₀ = 0 … división entre cero» | La secante modificada usa δ·x₀; elija x₀ distinto de cero |
| «el denominador es cero» | f(x+δx) = f(x): cambie x₀ o δ |
| «no es un número finito» | La función se sale de su dominio (sqrt de negativo, ln de ≤ 0, 1/0) en ese punto |
| Sección dorada: óptimo pegado a un extremo | La función es monótona en [a, b]: amplíe el intervalo |
| Sección dorada con óptimo cerca de 0 y criterio relativo | Use el criterio «Longitud del intervalo» |
| Texto cortado en pantallas pequeñas | Maximice la ventana; el panel izquierdo tiene barra de desplazamiento |

## 10. Notas matemáticas

- **Secante modificada:** x_(i+1) = x_i − δ·x_i·f(x_i) / [f(x_i + δ·x_i) − f(x_i)].
  Para en ε_a < tolerancia o al llegar al máximo de iteraciones. Si el método no converge se informa.
- **Sección dorada:** R = (√5 − 1)/2; d = R(x_U − x_L); x₁ = x_L + d; x₂ = x_U − d.
  *Maximizar:* si f(x₁) > f(x₂) → x_L = x₂, si no → x_U = x₁. *Minimizar:* se invierte la comparación.
  En cada iteración solo se evalúa un punto nuevo (el otro se reutiliza).
  Encuentra un óptimo **local** dentro del intervalo: el resultado depende de la función y del intervalo.
