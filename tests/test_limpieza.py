"""Check runnable de las funciones de limpieza/normalización.
Ejecutar: python3 -m unittest tests.test_limpieza -v   (desde esta carpeta)
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from limpieza import (
    clave_duplicado_exacto,
    limpiar_texto,
    normalizar_rating,
    tokenizar_para_frecuencia,
)


class TestLimpiarTexto(unittest.TestCase):
    def test_minusculas_y_espacios(self):
        self.assertEqual(limpiar_texto("  MUY   Buena  "), "muy buena")

    def test_quita_emojis_y_signos(self):
        self.assertEqual(limpiar_texto("Genial! 👏🔥"), "genial")

    def test_conserva_acentos_y_enie(self):
        self.assertEqual(limpiar_texto("Año increíble"), "año increíble")

    def test_texto_none_o_vacio(self):
        self.assertEqual(limpiar_texto(None), "")
        self.assertEqual(limpiar_texto("   "), "")


class TestNormalizarRating(unittest.TestCase):
    def test_rating_valido(self):
        r = normalizar_rating("4")
        self.assertTrue(r.valido)
        self.assertEqual(r.valor, 4)
        self.assertFalse(r.recuperado_de_texto)

    def test_rating_textual_cinco(self):
        r = normalizar_rating("cinco")
        self.assertTrue(r.valido)
        self.assertEqual(r.valor, 5)
        self.assertTrue(r.recuperado_de_texto)

    def test_rating_vacio_invalido(self):
        r = normalizar_rating("")
        self.assertFalse(r.valido)
        self.assertIsNone(r.valor)

    def test_rating_fuera_de_rango_invalido(self):
        for crudo in ("-1", "0", "6", "7"):
            with self.subTest(crudo=crudo):
                r = normalizar_rating(crudo)
                self.assertFalse(r.valido)

    def test_rating_no_numerico_invalido(self):
        for crudo in ("?", "N/A"):
            with self.subTest(crudo=crudo):
                r = normalizar_rating(crudo)
                self.assertFalse(r.valido)


class TestTokenizarParaFrecuencia(unittest.TestCase):
    def test_descarta_stopwords(self):
        tokens = tokenizar_para_frecuencia("la app funciona muy bien")
        self.assertNotIn("la", tokens)
        self.assertNotIn("muy", tokens)
        self.assertIn("app", tokens)
        self.assertIn("funciona", tokens)
        self.assertIn("bien", tokens)

    def test_texto_vacio(self):
        self.assertEqual(tokenizar_para_frecuencia(""), [])


class TestClaveDuplicadoExacto(unittest.TestCase):
    def test_misma_fila_distinto_casing_y_espacios_es_igual(self):
        k1 = clave_duplicado_exacto("ana1", "2026-01-01", "5", "Genial la app")
        k2 = clave_duplicado_exacto("ana1", "2026-01-01", "5", "  genial   la app  ")
        self.assertEqual(k1, k2)

    def test_distinto_usuario_no_es_duplicado(self):
        k1 = clave_duplicado_exacto("ana1", "2026-01-01", "5", "Bien")
        k2 = clave_duplicado_exacto("ana2", "2026-01-01", "5", "Bien")
        self.assertNotEqual(k1, k2)


if __name__ == "__main__":
    unittest.main()
