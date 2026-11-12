"""
test_graficos.py - Pruebas automatizadas de visualización y análisis comparativo (Fase 3).
Autor: Bryan Steven Cornejo Zavala (Equipo G01T - ACE941 / ACE404)

Ejecutar con:  python test_graficos.py
Verifica:
1. Cálculo analítico exacto de k_singular y coincidencia con modelo.py.
2. Solución teórica cerrada vs. solución matricial de Python (error ≈ 0 %).
3. Barrido paramétrico de la curva iϕ en función de k (con separación en la asíntota).
4. Construcción de la tabla comparativa Teoría vs. Python vs. MATLAB vs. LTspice.
5. Generación de gráficos Matplotlib en alta resolución (barras de potencia y curva iϕ vs k).
6. Integración en vivo del componente PanelGraficos dentro de la interfaz Tkinter.
"""

import math
import os
import tkinter as tk
import unittest

from graficos import (
    PanelGraficos,
    calcular_curva_iphi_vs_k,
    calcular_k_singular,
    construir_tabla_comparativa,
    explicacion_error_cero,
    formatear_tabla_comparativa_texto,
    generar_graficos_circuito,
    solucion_teorica_exacta,
)
from modelo import resolver_circuito


class TestGraficosYComparacion(unittest.TestCase):
    def test_01_k_singular_nominal_y_variable(self):
        """Verifica que la fórmula de k_singular coincida con -56/5.5 en nominales y anule det(G)."""
        k_sing_nom = calcular_k_singular(R3=5.0)
        self.assertAlmostEqual(k_sing_nom, -56.0 / 5.5, places=12)

        for r3 in (1.0, 5.0, 10.0, 25.0):
            k_s = calcular_k_singular(R3=r3)
            res = resolver_circuito(R3=r3, k=k_s)
            self.assertTrue(res["matriz_singular"], f"No detectó singularidad para R3={r3}, k={k_s}")

    def test_02_solucion_teorica_vs_python_error_cero(self):
        """Verifica que la solución teórica cerrada y resolver_circuito tengan error relativo ≈ 0 %."""
        teo = solucion_teorica_exacta()
        py = resolver_circuito()
        self.assertAlmostEqual(teo["VA"], py["VA"], places=12)
        self.assertAlmostEqual(teo["VB"], py["VB"], places=12)
        self.assertAlmostEqual(teo["VC"], py["VC"], places=12)
        self.assertAlmostEqual(teo["iphi"], py["iphi"], places=12)
        self.assertAlmostEqual(teo["P_generada"], py["P_generada"], places=12)
        self.assertAlmostEqual(teo["P_absorbida"], py["P_absorbida"], places=12)

    def test_03_curva_iphi_vs_k(self):
        """Verifica que el barrido de iϕ(k) genere ambos tramos sin NaN fuera de la asíntota."""
        datos = calcular_curva_iphi_vs_k(r3=5.0, k_min=-20.0, k_max=30.0, puntos=100)
        self.assertAlmostEqual(datos["k_sing"], -56.0 / 5.5, places=6)
        self.assertGreater(len(datos["k_izq"]), 10)
        self.assertGreater(len(datos["k_der"]), 10)
        self.assertTrue(all(math.isfinite(x) for x in datos["iphi_izq"]))
        self.assertTrue(all(math.isfinite(x) for x in datos["iphi_der"]))

    def test_04_tabla_comparativa_y_porcentaje_error(self):
        """Verifica que la tabla comparativa incluya Teoría, Python, MATLAB y LTspice con error ≈ 0 %."""
        filas = construir_tabla_comparativa()
        self.assertEqual(len(filas), 16)
        for fila in filas:
            self.assertLess(fila["error_pct_python"], 1e-11, f"Error excesivo en {fila['variable']}")
            self.assertLess(fila["error_pct_matlab"], 1e-11)
            self.assertLess(fila["error_pct_ltspice"], 1e-11)

        reporte = formatear_tabla_comparativa_texto()
        self.assertIn("TEORÍA vs. PYTHON vs. MATLAB vs. LTSPICE", reporte)
        self.assertIn("LAPACK", reporte)
        self.assertIn("IEEE 754", explicacion_error_cero())

    def test_05_generacion_imagen_graficos(self):
        """Verifica que generar_graficos_circuito cree el archivo PNG tanto en estado normal como singular."""
        ruta_normal = generar_graficos_circuito(r3=5.0, k=8.0)
        self.assertTrue(os.path.exists(ruta_normal))
        self.assertGreater(os.path.getsize(ruta_normal), 5000)

        ruta_sing = generar_graficos_circuito(r3=5.0, k=-56.0 / 5.5)
        self.assertTrue(os.path.exists(ruta_sing))
        self.assertGreater(os.path.getsize(ruta_sing), 5000)

    def test_06_panel_graficos_tkinter(self):
        """Verifica que PanelGraficos se instancie y actualice dinámicamente en Tkinter."""
        root = tk.Tk()
        root.withdraw()
        try:
            panel = PanelGraficos(root, r3_inicial=5.0, k_inicial=8.0)
            panel.pack()
            panel.actualizar(r3=10.0, k=4.0)
            self.assertEqual(panel.r3_actual, 10.0)
            self.assertEqual(panel.k_actual, 4.0)
            # Probar en condición singular sin lanzar excepciones
            panel.actualizar(r3=5.0, k=-56.0 / 5.5)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
