"""Pruebas de los cálculos (ejecutar:  python -m unittest discover -s pruebas -v)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metodos.secante_modificada import secante_modificada, generar_pasos as pasos_s
from metodos.seccion_dorada import seccion_dorada, generar_pasos as pasos_d
from metodos import secante_modificada as m_sec, seccion_dorada as m_dor
from utilidades.ecuaciones import latex_de_texto, png_ecuacion
from utilidades.evaluador_funciones import (ErrorEvaluacion, ErrorFuncion, ErrorParametro,
                                            FuncionMatematica, valor_numerico)


class PruebasEvaluador(unittest.TestCase):
    def test_basico(self):
        self.assertAlmostEqual(FuncionMatematica("exp(-x) - x").evaluar(0.0), 1.0)
        self.assertAlmostEqual(FuncionMatematica("x^3 + x + 16").evaluar(-3), -14.0)

    def test_multiplicacion_implicita(self):
        self.assertAlmostEqual(FuncionMatematica("2x + 3").evaluar(2), 7.0)
        self.assertAlmostEqual(FuncionMatematica("4x - 1.8x^2 + 1.2x^3 - 0.3x^4").evaluar(1.7082), 5.0075, places=3)
        self.assertAlmostEqual(FuncionMatematica("(x+1)(x-1)").evaluar(3), 8.0)
        self.assertAlmostEqual(FuncionMatematica("2pi").evaluar(0), 2 * math.pi)

    def test_potencias_y_logaritmos(self):
        self.assertAlmostEqual(FuncionMatematica("2^-x").evaluar(1), 0.5)
        self.assertAlmostEqual(FuncionMatematica("ln(e)").evaluar(0), 1.0)
        self.assertAlmostEqual(FuncionMatematica("log(1000)").evaluar(0), 3.0)
        self.assertAlmostEqual(FuncionMatematica("-x^2").evaluar(3), -9.0)

    def test_seguridad(self):
        for malo in ["__import__('os').system('dir')", "x.__class__", "open('a')", "[1,2]", "lambda: 1",
                     "sin x", "exec('1')", "x; y", "a+1", "'hola'"]:
            with self.assertRaises(ErrorFuncion, msg=malo):
                FuncionMatematica(malo)

    def test_errores(self):
        with self.assertRaises(ErrorFuncion):
            FuncionMatematica("")
        with self.assertRaises(ErrorFuncion):
            FuncionMatematica("2 + * x")
        with self.assertRaises(ErrorEvaluacion):
            FuncionMatematica("1/x").evaluar(0)
        with self.assertRaises(ErrorEvaluacion):
            FuncionMatematica("sqrt(x)").evaluar(-4)

    def test_numeros(self):
        self.assertAlmostEqual(valor_numerico("0,5", "a"), 0.5)
        self.assertAlmostEqual(valor_numerico("pi/2", "a"), math.pi / 2)
        with self.assertRaises(ErrorParametro):
            valor_numerico("abc", "a")
        with self.assertRaises(ErrorParametro):
            valor_numerico("x+1", "a")


class PruebasSecante(unittest.TestCase):
    def test_ejemplo_6_8_chapra(self):
        r = secante_modificada(FuncionMatematica("exp(-x) - x"), 1.0, 0.01, 0.01, 20)
        self.assertAlmostEqual(r.iteraciones[0].x_nuevo, 0.537263, places=5)
        self.assertAlmostEqual(r.iteraciones[1].x_nuevo, 0.567010, places=5)
        self.assertAlmostEqual(r.iteraciones[2].x_nuevo, 0.567143, places=5)
        self.assertAlmostEqual(r.iteraciones[0].ea, 86.13, places=1)
        self.assertTrue(r.convergio)
        self.assertAlmostEqual(r.raiz, 0.56714329, places=5)

    def test_ejemplo_precargado(self):
        r = secante_modificada(FuncionMatematica("exp(-x) - x"), 0.5, 0.01, 1, 100)
        self.assertTrue(r.convergio)
        self.assertAlmostEqual(r.raiz, 0.5671, places=3)
        self.assertLess(r.ea_final, 1)

    def test_otra_funcion(self):
        r = secante_modificada(FuncionMatematica("x^3 + x + 16"), -3, 0.01, 0.001, 100)
        self.assertTrue(r.convergio)
        self.assertAlmostEqual(r.f_raiz, 0, places=4)

    def test_x0_cero(self):
        with self.assertRaises(ErrorParametro):
            secante_modificada(FuncionMatematica("exp(-x) - x"), 0, 0.01, 1, 100)

    def test_parametros_invalidos(self):
        f = FuncionMatematica("x^2 - 2")
        for args in [(1, 0, 1, 10), (1, 0.01, -1, 10), (1, 0.01, 1, 0), (1, 0.01, 1, 2.5), (float("nan"), 0.01, 1, 5)]:
            with self.assertRaises(ErrorParametro):
                secante_modificada(f, *args)

    def test_no_converge_y_maximo(self):
        r = secante_modificada(FuncionMatematica("x^2 + 1"), 1, 0.01, 1e-12, 5)   # sin raíz real
        self.assertFalse(r.convergio)
        self.assertIn(r.estado, ("max_iter", "error"))

    def test_denominador_cero(self):
        r = secante_modificada(FuncionMatematica("5"), 1, 0.01, 1, 10)             # f constante
        self.assertEqual(r.estado, "error")
        self.assertIn("denominador", r.mensaje)

    def test_pasos(self):
        r = secante_modificada(FuncionMatematica("exp(-x) - x"), 1.0, 0.01, 1, 20)
        p = pasos_s(r)
        self.assertEqual(len(p), r.n_iter + 2)


class PruebasDorada(unittest.TestCase):
    def test_minimo_cuadratico(self):
        r = seccion_dorada(FuncionMatematica("(x - 2)^2 + 1"), 0, 5, "minimizar", 0.01, 100, "longitud")
        self.assertTrue(r.convergio)
        self.assertAlmostEqual(r.xopt, 2, delta=0.01)
        self.assertAlmostEqual(r.fopt, 1, places=3)
        self.assertLess(r.intervalo_final[1] - r.intervalo_final[0], 0.01)

    def test_maximo_clase(self):
        f = FuncionMatematica("4x - 1.8x^2 + 1.2x^3 - 0.3x^4")
        r = seccion_dorada(f, -2, 4, "maximizar", 1, 100, "relativo")
        self.assertTrue(r.convergio)
        self.assertEqual(r.n_iter, 11)
        self.assertAlmostEqual(r.xopt, 2.3282, delta=1e-3)
        self.assertAlmostEqual(r.fopt, 5.8853, delta=1e-3)
        it1 = r.iteraciones[0]
        self.assertAlmostEqual(it1.x1, 1.7082, places=3)
        self.assertAlmostEqual(it1.x2, 0.2918, places=3)
        self.assertAlmostEqual(it1.f1, 5.0075, places=3)
        self.assertAlmostEqual(it1.ea, 134.16, delta=0.05)
        self.assertAlmostEqual(r.ea_final, 0.80, delta=0.02)

    def test_ejemplo_de_la_presentacion(self):
        f = FuncionMatematica("2 sin(x) - x^2/10")
        r = seccion_dorada(f, 0, 4, "maximizar", 1, 100, "relativo")
        it1, it6 = r.iteraciones[0], r.iteraciones[5]
        self.assertAlmostEqual(it1.x1, 2.4721, places=3)
        self.assertAlmostEqual(it1.x2, 1.5279, places=3)
        self.assertAlmostEqual(it6.x1, 1.5279, places=3)
        self.assertAlmostEqual(it6.x2, 1.4427, places=3)
        # La diapositiva dice 9.0 % en la iteración 6, pero con la fórmula 0.381966·0.3606/1.4427 sale 9.55 %.
        self.assertAlmostEqual(it6.ea, 9.55, delta=0.05)
        for k, esperado in enumerate([100.0, 61.8, 38.2, 23.6, 14.6], start=0):
            self.assertAlmostEqual(r.iteraciones[k].ea, esperado, delta=0.1)
        self.assertAlmostEqual(r.xopt, 1.4276, delta=0.02)   # máximo real: x=1.4276, f=1.7757
        self.assertAlmostEqual(r.fopt, 1.7757, delta=0.001)

    def test_maximizar_invierte_criterio(self):
        f = FuncionMatematica("-(x - 1)^2")
        self.assertAlmostEqual(seccion_dorada(f, -3, 4, "maximizar", 1e-4, 100, "longitud").xopt, 1, delta=1e-3)
        self.assertAlmostEqual(seccion_dorada(f, -3, 4, "minimizar", 1e-4, 100, "longitud").xopt, -3, delta=1e-3)  # f(-3)=-16 < f(4)=-9

    def test_reutiliza_evaluaciones(self):
        r = seccion_dorada(FuncionMatematica("(x - 2)^2 + 1"), 0, 5, "minimizar", 0.01, 100, "longitud")
        self.assertEqual(r.evaluaciones, r.n_iter + 1)   # 2 iniciales + 1 nueva por iteración, menos la última

    def test_validaciones(self):
        f = FuncionMatematica("x^2")
        for args in [(5, 0, "minimizar", 1, 10, "relativo"), (1, 1, "minimizar", 1, 10, "relativo"),
                     (0, 1, "otro", 1, 10, "relativo"), (0, 1, "minimizar", 0, 10, "relativo"),
                     (0, 1, "minimizar", 1, 0, "relativo")]:
            with self.assertRaises(ErrorParametro):
                seccion_dorada(f, *args)

    def test_borde_y_pasos(self):
        r = seccion_dorada(FuncionMatematica("x"), 0, 4, "minimizar", 0.01, 100, "longitud")
        self.assertTrue(r.advertencias)       # función monótona: óptimo en el borde
        self.assertEqual(len(pasos_d(r)), r.n_iter + 2)

    def test_max_iteraciones(self):
        r = seccion_dorada(FuncionMatematica("(x - 2)^2"), 0, 5, "minimizar", 1e-12, 3, "longitud")
        self.assertFalse(r.convergio)
        self.assertEqual(r.estado, "max_iter")


class PruebasEcuaciones(unittest.TestCase):
    def test_funcion_a_latex(self):
        self.assertIn(r"\frac", latex_de_texto("(x^5 - 12)/sin(x^2)"))
        self.assertIn("x^{2}", latex_de_texto("x^2 + x^4"))
        self.assertIsNone(latex_de_texto("sin x"))

    def test_todas_las_ecuaciones_se_dibujan(self):
        f = FuncionMatematica
        casos = [(secante_modificada(f("exp(-x) - x"), 1.0, 0.01, 1e-9, 6), pasos_s),
                 (secante_modificada(f("x^3 + x + 16"), -3, 0.01, 1, 50), pasos_s),
                 (seccion_dorada(f("4x - 1.8x^2 + 1.2x^3 - 0.3x^4"), -2, 4, "maximizar", 1), pasos_d),
                 (seccion_dorada(f("(x - 2)^2 + 1"), 0, 5, "minimizar", 0.01, 100, "longitud"), pasos_d)]
        total = 0
        for res, gen in casos:
            for _, bloques in gen(res) + [("", res.bloques_resumen())]:
                for estilo, contenido in bloques:
                    if estilo in ("eq", "eqf", "eqr"):
                        total += 1
                        self.assertIsNotNone(png_ecuacion(contenido, 15), contenido)
        for estilo, contenido in m_sec.bloques_ayuda() + m_dor.bloques_ayuda():
            if estilo.startswith("eq"):
                self.assertIsNotNone(png_ecuacion(contenido, 15), contenido)
        self.assertGreater(total, 300)


if __name__ == "__main__":
    unittest.main(verbosity=2)
