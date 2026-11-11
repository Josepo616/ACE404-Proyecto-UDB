"""
interfaz.py - Fachada de compatibilidad para el módulo ui.
Autor: José Rolando Álvarez Mejía (Equipo G01T - ACE941 / ACE404)

Reenvía a ui.app.SimuladorApp para preservar importaciones existentes.
"""

from ui.app import SimuladorApp, crear_interfaz

__all__ = ["SimuladorApp", "crear_interfaz"]

if __name__ == "__main__":
    crear_interfaz()
