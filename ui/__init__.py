"""
ui/__init__.py - Paquete de interfaz de usuario del Simulador DC.
"""

from ui.app import SimuladorApp, crear_interfaz
from ui.graficos import (
    PanelGraficos,
    construir_tabla_comparativa,
    formatear_tabla_comparativa_texto,
    generar_graficos_circuito,
)

__all__ = [
    "SimuladorApp",
    "crear_interfaz",
    "PanelGraficos",
    "construir_tabla_comparativa",
    "formatear_tabla_comparativa_texto",
    "generar_graficos_circuito",
]
