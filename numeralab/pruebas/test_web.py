"""Pruebas de la versión web (Streamlit AppTest). Se omiten si Streamlit no está instalado.

Ejecutar:  python -m unittest discover -s pruebas -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from streamlit.testing.v1 import AppTest
    HAY_STREAMLIT = True
except Exception:  # pragma: no cover
    HAY_STREAMLIT = False


def _app_secante():
    from web import paginas as P
    P.iniciar_estado()
    P.pagina_secante()


def _app_dorada():
    from web import paginas as P
    P.iniciar_estado()
    P.pagina_dorada()


def _texto(at):
    partes = [m.value for m in at.markdown] + [m.value for m in at.success] + [m.value for m in at.warning] \
        + [m.value for m in at.error] + [m.value for m in at.latex]
    partes += [str(x.value) for x in at.metric]
    return "\n".join(map(str, partes))


@unittest.skipUnless(HAY_STREAMLIT, "Streamlit no está instalado")
class PruebasWeb(unittest.TestCase):
    def _app(self, fn):
        at = AppTest.from_function(fn, default_timeout=60)
        at.run()
        self.assertFalse(at.exception, at.exception)
        return at

    def test_secante_ejemplo(self):
        at = self._app(_app_secante)
        at.button(key="secante:bej").click().run()            # ejemplo 1 (x0 = 0.5)
        at.button(key="secante:bej").click().run()            # ejemplo 2 (x0 = 1, ejemplo 6.8 de Chapra)
        self.assertEqual(at.text_input(key="secante:x0").value, "1")
        at.button(key="secante:btn").click().run()
        self.assertFalse(at.exception, at.exception)
        self.assertIn("0.567143", _texto(at))
        self.assertTrue(any("Convergió en 3" in m.value for m in at.success))

    def test_dorada_maximo(self):
        at = self._app(_app_dorada)
        at.button(key="dorada:bej").click().run()
        at.button(key="dorada:bej").click().run()            # ejemplo 2: máximo de 4x - 1.8x^2 + ...
        at.button(key="dorada:btn").click().run()
        self.assertFalse(at.exception, at.exception)
        self.assertIn("2.328157", _texto(at))
        self.assertTrue(any("Convergió en 11" in m.value for m in at.success))

    def test_funcion_invalida_muestra_error(self):
        at = self._app(_app_secante)
        at.text_input(key="secante:funcion").set_value("__import__('os')").run()
        self.assertTrue(at.error, "debe avisar que la función no es válida")
        at.button(key="secante:btn").click().run()
        self.assertFalse(at.exception, at.exception)
        self.assertTrue(any("Revise los datos" in e.value for e in at.error))

    def test_intervalo_invalido(self):
        at = self._app(_app_dorada)
        at.text_input(key="dorada:funcion").set_value("x^2").run()
        at.text_input(key="dorada:a").set_value("5").run()
        at.text_input(key="dorada:b").set_value("1").run()
        at.button(key="dorada:btn").click().run()
        self.assertTrue(any("menor que el límite superior" in e.value for e in at.error))

    def test_x0_cero(self):
        at = self._app(_app_secante)
        at.text_input(key="secante:funcion").set_value("exp(-x) - x").run()
        at.text_input(key="secante:x0").set_value("0").run()
        at.button(key="secante:btn").click().run()
        self.assertTrue(any("x₀ = 0" in e.value for e in at.error))

    def test_teclado_agrega_simbolos(self):
        at = self._app(_app_secante)
        for clave in ("tk_1_0", "tk_3_2"):                    # «4» y «x²»
            at.button(key=clave).click().run()
        self.assertEqual(at.text_input(key="secante:funcion").value, "4^2")
        at.button(key="tk_0_5").click().run()                 # «⌫» borra el último carácter
        self.assertEqual(at.text_input(key="secante:funcion").value, "4^")
        at.button(key="tk_1_5").click().run()                 # «C» limpia
        self.assertEqual(at.text_input(key="secante:funcion").value, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
