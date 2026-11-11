"""
ui/app.py - Orquestador principal de la aplicación gráfica Simulador DC (Fase 3).
Autor: José Rolando Álvarez Mejía (Equipo G01T - ACE941 / ACE404)

Ensambla la ventana de escritorio, los paneles modulares de control, métricas y acciones,
y coordina el enlace reactivo con el motor matemático (modelo.py).
"""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import subprocess
import sys
import tempfile
import tkinter as tk

from modelo import paso_a_paso, resolver_circuito
from ui.controles import PanelControles
from ui.metricas import PanelMetricas
from ui.acciones import PanelAcciones

NOMINAL_R3 = 5.0
NOMINAL_K = 8.0
K_SINGULAR = -56.0 / 5.5  # ≈ -10.1818 Ω


class SimuladorApp:
    """
    Aplicación de escritorio para la simulación del circuito DC (Fase 3).
    Coordina la ventana principal, los paneles de control, métricas y acciones.
    """

    NOMINAL_R3 = NOMINAL_R3
    NOMINAL_K = NOMINAL_K
    K_SINGULAR = K_SINGULAR

    def __init__(self, root=None):
        if root is None:
            self.root = tk.Tk()
            self._root_creada = True
        else:
            self.root = root
            self._root_creada = False

        self.root.title("Simulador DC - Circuito con Fuente Dependiente (Fase 3)")
        self.root.geometry("580x720")
        self.root.minsize(520, 660)

        self._construir_ui()
        self.actualizar_resumen()

        self.root.update_idletasks()
        self.root.update()

    def _construir_ui(self):
        # Contenedor centrado responsivo
        self.card = tk.Frame(self.root, padx=22, pady=16)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=530)

        # 1. Panel de controles (Sliders R3 y k)
        self.panel_controles = PanelControles(
            self.card,
            nominal_r3=self.NOMINAL_R3,
            nominal_k=self.NOMINAL_K,
            on_change=self.actualizar_resumen,
        )
        self.panel_controles.pack(fill="x")

        # 2. Panel de métricas (Nodal, Mallas, Balance y Estado)
        self.panel_metricas = PanelMetricas(self.card)
        self.panel_metricas.pack(fill="x")

        # 3. Panel de acciones (Restablecer, Singularidad, Reporte)
        self.panel_acciones = PanelAcciones(
            self.card,
            on_restablecer=self.restablecer,
            on_singularidad=self.probar_singularidad,
            on_copiar=self.copiar_procedimiento,
            on_abrir_visor=self.abrir_en_visor,
        )
        self.panel_acciones.pack(fill="x")

    def restablecer(self):
        """Restablece los valores nominales de diseño (R3=5Ω, k=8Ω)."""
        self.panel_controles.establecer_valores(self.NOMINAL_R3, self.NOMINAL_K)
        self.actualizar_resumen()

    def probar_singularidad(self):
        """Ajusta k al punto de singularidad (det(G)=0) para verificar estabilidad."""
        r3, _ = self.panel_controles.obtener_valores()
        self.panel_controles.establecer_valores(r3, self.K_SINGULAR)
        self.actualizar_resumen()

    def copiar_procedimiento(self):
        """Genera y copia el procedimiento de 8 pasos al portapapeles del sistema."""
        r3_raw, k_raw = self.panel_controles.obtener_valores()
        k_calc = self.K_SINGULAR if abs(k_raw - self.K_SINGULAR) < 0.02 else round(k_raw, 1)
        texto = paso_a_paso(R3=round(r3_raw, 1), k=k_calc)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)

    def abrir_en_visor(self):
        """Abre el procedimiento matemático completo en el visor nativo del sistema operativo."""
        r3_raw, k_raw = self.panel_controles.obtener_valores()
        k_calc = self.K_SINGULAR if abs(k_raw - self.K_SINGULAR) < 0.02 else round(k_raw, 1)
        texto = paso_a_paso(R3=round(r3_raw, 1), k=k_calc)
        ruta = os.path.join(tempfile.gettempdir(), "procedimiento_circuito.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)
        if sys.platform == "win32":
            os.startfile(ruta)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", ruta])
        else:
            subprocess.Popen(["xdg-open", ruta])

    def actualizar_resumen(self):
        """Calcula el circuito con modelo.py y actualiza todos los componentes de la interfaz."""
        r3_raw, k_raw = self.panel_controles.obtener_valores()
        r3_num = round(r3_raw, 1)

        if abs(k_raw - self.K_SINGULAR) < 0.02:
            k_num = self.K_SINGULAR
            k_str = "-10.18"
        else:
            k_num = round(k_raw, 1)
            k_str = f"{k_num:.1f}"

        self.panel_controles.actualizar_etiquetas(r3_num, k_str)

        res = resolver_circuito(R3=r3_num, k=k_num)
        self.panel_metricas.actualizar(res)

    def ejecutar(self):
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()


def crear_interfaz():
    """Función de compatibilidad para inicializar y ejecutar el simulador."""
    app = SimuladorApp()
    app.ejecutar()


if __name__ == "__main__":
    crear_interfaz()
