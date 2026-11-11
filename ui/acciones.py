"""
ui/acciones.py - Panel de acciones y exportación multiplataforma (Fase 3).
Autor: José Rolando Álvarez Mejía (Equipo G01T - ACE941 / ACE404)

Proporciona botones de comando para:
1. Restablecer valores nominales de diseño.
2. Comprobación rápida de condición de singularidad (k ≈ -10.18 Ω).
3. Copia limpia del reporte matemático de 8 pasos al portapapeles del sistema.
4. Apertura del reporte en el visor nativo (TextEdit en macOS / Bloc de notas en Windows).
5. Visualización del diagrama esquemático en Vista Previa / Visor de Fotos.
"""

import sys
import tkinter as tk


class PanelAcciones(tk.Frame):
    """
    Panel inferior con botones de acción para restablecer el circuito,
    inducir la singularidad de prueba, copiar el reporte, abrir el visor nativo
    y visualizar el diagrama esquemático.
    """

    def __init__(
        self,
        parent,
        on_restablecer=None,
        on_singularidad=None,
        on_copiar=None,
        on_abrir_visor=None,
        on_ver_diagrama=None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.on_restablecer = on_restablecer
        self.on_singularidad = on_singularidad
        self.on_copiar = on_copiar
        self.on_abrir_visor = on_abrir_visor
        self.on_ver_diagrama = on_ver_diagrama

        self._construir_widgets()

    def _construir_widgets(self):
        # --- FILA 1: RESTABLECER Y SINGULARIDAD ---
        fila1 = tk.Frame(self)
        fila1.pack(fill="x", pady=(0, 6))

        self.btn_reset = tk.Button(
            fila1,
            text="↺ Restablecer Nominales",
            font=("Helvetica", 11, "bold"),
            command=self.on_restablecer,
            pady=8,
        )
        self.btn_reset.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_sing = tk.Button(
            fila1,
            text="⚠ Probar Singularidad (k ≈ -10.18)",
            font=("Helvetica", 11, "bold"),
            command=self.on_singularidad,
            pady=8,
        )
        self.btn_sing.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # --- FILA 2: PROCEDIMIENTO MATEMÁTICO COMPLETO ---
        fila2 = tk.Frame(self)
        fila2.pack(fill="x", pady=(0, 6))

        self.btn_copiar = tk.Button(
            fila2,
            text="📋 Copiar Procedimiento (8 Pasos)",
            font=("Helvetica", 10, "bold"),
            command=self._ejecutar_copia,
            pady=7,
        )
        self.btn_copiar.pack(side="left", fill="x", expand=True, padx=(0, 4))

        texto_btn_abrir = (
            "📄 Ver en Bloc de notas"
            if sys.platform == "win32"
            else "📄 Ver en TextEdit"
            if sys.platform == "darwin"
            else "📄 Ver Procedimiento"
        )
        self.btn_abrir = tk.Button(
            fila2,
            text=texto_btn_abrir,
            font=("Helvetica", 10, "bold"),
            command=self.on_abrir_visor,
            pady=7,
        )
        self.btn_abrir.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # --- FILA 3: DIAGRAMA ESQUEMÁTICO DEL CIRCUITO ---
        texto_btn_diagrama = (
            "🖼️ Ver Diagrama en Vista Previa"
            if sys.platform == "darwin"
            else "🖼️ Ver Diagrama en Visor de Fotos"
            if sys.platform == "win32"
            else "🖼️ Ver Diagrama del Circuito"
        )
        self.btn_diagrama = tk.Button(
            self,
            text=texto_btn_diagrama,
            font=("Helvetica", 10, "bold"),
            command=self.on_ver_diagrama,
            pady=7,
        )
        self.btn_diagrama.pack(fill="x")

    def _ejecutar_copia(self):
        if self.on_copiar:
            self.on_copiar()
            self.btn_copiar.configure(text="✓ ¡Procedimiento Copiado!")
            self.after(1800, lambda: self.btn_copiar.configure(text="📋 Copiar Procedimiento (8 Pasos)"))
