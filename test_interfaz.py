"""
test_interfaz.py - Pruebas automatizadas para la interfaz gráfica (Fase 3).
Autor: José Rolando Álvarez Mejía (Equipo G01T - ACE941 / ACE404)

Verifica la inicialización, sincronización de controles, detección de singularidad,
balance energético y generación del procedimiento en modo no interactivo (headless).
"""

import tkinter as tk
import unittest

from ui.app import SimuladorApp
from ui.widgets import VisibleSlider


class TestInterfazSimulador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Crear ventana raíz oculta para ejecutar pruebas sin bloquear la pantalla
        cls.root = tk.Tk()
        cls.root.withdraw()
        cls.app = SimuladorApp(root=cls.root)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.root.destroy()
        except Exception:
            pass

    def test_01_valores_nominales_iniciales(self):
        """Verifica que los sliders y tarjetas inicien con los valores nominales de Fase 2."""
        r3, k = self.app.panel_controles.obtener_valores()
        self.assertAlmostEqual(r3, 5.0, places=1)
        self.assertAlmostEqual(k, 8.0, places=1)

        # Verificación de que las tarjetas métricas muestran los valores nominales esperados
        self.assertIn("16.000", self.app.panel_metricas.box_va.cget("text"))
        self.assertIn("10.000", self.app.panel_metricas.box_vb.cget("text"))
        self.assertIn("9.600", self.app.panel_metricas.box_vc.cget("text"))
        self.assertIn("1.2000", self.app.panel_metricas.box_iphi.cget("text"))
        self.assertIn("✓ Coincide", self.app.panel_metricas.box_coincide.cget("text"))
        self.assertIn("✓ Se conserva", self.app.panel_metricas.box_bal_ok.cget("text"))

    def test_02_modificacion_controles(self):
        """Verifica que los botones de incremento/decremento actualicen los sliders."""
        self.app.panel_controles.modificar_r3(1.0)
        r3, _ = self.app.panel_controles.obtener_valores()
        self.assertAlmostEqual(r3, 6.0, places=1)

        self.app.panel_controles.modificar_k(-2.0)
        _, k = self.app.panel_controles.obtener_valores()
        self.assertAlmostEqual(k, 6.0, places=1)

    def test_03_restablecer_nominales(self):
        """Verifica que la acción restablecer devuelva R3 a 5.0 Ω y k a 8.0 Ω."""
        self.app.restablecer()
        r3, k = self.app.panel_controles.obtener_valores()
        self.assertAlmostEqual(r3, 5.0, places=1)
        self.assertAlmostEqual(k, 8.0, places=1)

    def test_04_alerta_de_singularidad(self):
        """Verifica que al inducir singularidad (k ≈ -10.18 Ω) el panel muestre la alerta."""
        self.app.probar_singularidad()
        _, k = self.app.panel_controles.obtener_valores()
        self.assertAlmostEqual(k, -56.0 / 5.5, places=2)

        # El botón de estado debe reflejar el error
        texto_estado = self.app.panel_metricas.btn_status.cget("text")
        self.assertTrue(
            "ERROR" in texto_estado or "singular" in texto_estado.lower(),
            f"El estado no indicó singularidad: {texto_estado}",
        )

        # Restaurar nominales para no afectar pruebas posteriores
        self.app.restablecer()

    def test_05_copia_de_procedimiento(self):
        """Verifica que el procedimiento de 8 pasos se copie al portapapeles sin fallos."""
        self.app.copiar_procedimiento()
        contenido_clipboard = self.root.clipboard_get()
        self.assertIn("PASO 1", contenido_clipboard)
        self.assertIn("PASO 8", contenido_clipboard)
        self.assertIn("Balance de potencia", contenido_clipboard)


if __name__ == "__main__":
    unittest.main()
