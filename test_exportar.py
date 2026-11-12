"""
test_exportar.py - Pruebas automatizadas de exportación CSV y PDF (Fase 3).
Autor: Carlos Francisco Peña Herrera (Equipo G01T - ACE941 / ACE404)

Ejecutar con:  python test_exportar.py
Verifica:
1. Contenido de la tabla de resultados (valores nominales de la Fase 1).
2. CSV nominal: encabezado, valores y lectura de vuelta.
3. CSV con matriz singular y con entrada inválida (sin errores al exportar).
4. PDF nominal con imágenes: archivo válido y con varias páginas.
5. PDF sin imágenes ni tabla comparativa (modo mínimo).
6. PDF con matriz singular y con entrada inválida.
7. Reemplazo de símbolos cuando no hay fuente Unicode.
8. Nombre de archivo sugerido.
"""

import csv
import os
import re
import tempfile
import unittest

from exportar import (
    COLUMNAS_CSV,
    _texto_seguro,
    exportar_csv,
    exportar_pdf,
    nombre_sugerido,
    tabla_resultados,
)
from modelo import resolver_circuito

K_SINGULAR = -56 / 5.5


def leer_csv(ruta):
    with open(ruta, newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


def contar_paginas_pdf(ruta):
    with open(ruta, "rb") as f:
        datos = f.read()
    return len(re.findall(rb"/Type\s*/Page(?![s\w])", datos))


class TestExportacion(unittest.TestCase):
    def setUp(self):
        self.carpeta = tempfile.TemporaryDirectory()
        self.dir = self.carpeta.name

    def tearDown(self):
        self.carpeta.cleanup()

    def ruta(self, nombre):
        return os.path.join(self.dir, nombre)

    def test_1_tabla_resultados_nominal(self):
        filas = tabla_resultados(resolver_circuito())
        valores = {f[1]: f[3] for f in filas}
        esperados = {"VA": 16.0, "VB": 10.0, "VC": 9.6, "iphi": 1.2, "i1": 2.0,
                     "i_R2": 0.8, "i_R4": 1.0, "i3": 0.2, "P_R3": 7.2,
                     "P_dependiente": 1.92, "P_generada": 40.0, "P_absorbida": 40.0}
        for clave, valor in esperados.items():
            self.assertAlmostEqual(valores[clave], valor, places=9, msg=clave)
        self.assertEqual(valores["balance_ok"], "Sí")
        self.assertEqual(valores["coincide_nodal_mallas"], "Sí")
        self.assertTrue(all(len(f) == 5 for f in filas))

    def test_2_csv_nominal(self):
        ruta = exportar_csv(resolver_circuito(), self.ruta("nominal.csv"))
        filas = leer_csv(ruta)
        self.assertEqual(filas[0], COLUMNAS_CSV)
        datos = {f[1]: f for f in filas[1:]}
        self.assertAlmostEqual(float(datos["VA"][3]), 16.0, places=9)
        self.assertAlmostEqual(float(datos["iphi"][3]), 1.2, places=9)
        self.assertAlmostEqual(float(datos["P_R3"][3]), 7.2, places=9)
        self.assertEqual(datos["R3"][4], "Ω")
        self.assertEqual(datos["estado"][3], "Solución única")

    def test_3_csv_singular_e_invalido(self):
        filas = leer_csv(exportar_csv(resolver_circuito(k=K_SINGULAR), self.ruta("sing.csv")))
        estado = [f for f in filas if f[1] == "estado"][0]
        self.assertEqual(estado[2], "Matriz singular")
        self.assertNotIn("VA", [f[1] for f in filas])

        filas = leer_csv(exportar_csv(resolver_circuito(R1=0), self.ruta("inv.csv")))
        estado = [f for f in filas if f[1] == "estado"][0]
        self.assertEqual(estado[2], "Entrada inválida")
        self.assertIn("R1", estado[3])

    def test_4_pdf_nominal_completo(self):
        ruta = exportar_pdf(resolver_circuito(), self.ruta("nominal.pdf"))
        with open(ruta, "rb") as f:
            self.assertEqual(f.read(5), b"%PDF-")
        self.assertGreaterEqual(contar_paginas_pdf(ruta), 3)

    def test_5_pdf_minimo(self):
        ruta = exportar_pdf(resolver_circuito(R3=8, k=4), self.ruta("minimo.pdf"),
                            incluir_imagenes=False, incluir_comparativa=False)
        self.assertGreaterEqual(contar_paginas_pdf(ruta), 2)
        completo = exportar_pdf(resolver_circuito(R3=8, k=4), self.ruta("completo.pdf"))
        self.assertLess(os.path.getsize(ruta), os.path.getsize(completo))

    def test_6_pdf_singular_e_invalido(self):
        for nombre, res in (("sing.pdf", resolver_circuito(k=K_SINGULAR)),
                            ("inv.pdf", resolver_circuito(R1=0))):
            ruta = exportar_pdf(res, self.ruta(nombre))
            self.assertTrue(os.path.getsize(ruta) > 0, nombre)
            self.assertGreaterEqual(contar_paginas_pdf(ruta), 1, nombre)

    def test_7_texto_seguro_latin1(self):
        texto = _texto_seguro("R3 = 5 Ω · iϕ ≈ 1.2 A")
        texto.encode("latin-1")  # no debe lanzar excepción
        self.assertIn("Ohm", texto)
        self.assertIn("phi", texto)

    def test_8_nombre_sugerido(self):
        self.assertTrue(re.fullmatch(r"reporte_circuito_\d{4}-\d{2}-\d{2}_\d{4}\.pdf", nombre_sugerido("pdf")))
        self.assertTrue(nombre_sugerido(".csv").endswith(".csv"))


if __name__ == "__main__":
    unittest.main()
