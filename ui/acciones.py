"""
ui/acciones.py - Panel de acciones y exportación multiplataforma (Fase 3).
Autores: José Rolando Álvarez Mejía y Bryan Steven Cornejo Zavala (Equipo G01T - ACE941 / ACE404)

Proporciona botones de comando para:
1. Restablecer valores nominales de diseño.
2. Comprobación rápida de condición de singularidad (k ≈ -10.18 Ω).
3. Copia limpia del reporte matemático de 8 pasos al portapapeles del sistema.
4. Apertura del reporte en el visor nativo (TextEdit en macOS / Bloc de notas en Windows).
5. Visualización del diagrama esquemático en Vista Previa / Visor de Fotos.
6. Apertura de la Tabla Comparativa (Teoría vs. Python vs. MATLAB vs. LTspice) y gráficos HD.
"""

import sys
import tkinter as tk


class PanelAcciones(tk.Frame):
    """
    Panel inferior con botones de acción para restablecer el circuito,
    inducir la singularidad de prueba, copiar el reporte, abrir el visor nativo,
    visualizar el diagrama esquemático y abrir la tabla comparativa / gráficos HD.
    """

    def __init__(
        self,
        parent,
        on_restablecer=None,
        on_singularidad=None,
        on_copiar=None,
        on_abrir_visor=None,
        on_ver_diagrama=None,
        on_ver_graficos=None,
        on_ver_tabla=None,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.on_restablecer = on_restablecer
        self.on_singularidad = on_singularidad
        self.on_copiar = on_copiar
        self.on_abrir_visor = on_abrir_visor
        self.on_ver_diagrama = on_ver_diagrama
        self.on_ver_graficos = on_ver_graficos
        self.on_ver_tabla = on_ver_tabla

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
        self.btn_diagrama.pack(fill="x", pady=(0, 6))

        # --- FILA 4: GRÁFICOS HD Y TABLA COMPARATIVA (BRYAN) ---
        fila4 = tk.Frame(self)
        fila4.pack(fill="x")

        self.btn_graficos = tk.Button(
            fila4,
            text="📈 Abrir Gráficos HD",
            font=("Helvetica", 10, "bold"),
            command=self.on_ver_graficos,
            pady=7,
        )
        self.btn_graficos.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_tabla = tk.Button(
            fila4,
            text="📊 Tabla Comparativa (% Error)",
            font=("Helvetica", 10, "bold"),
            command=self.on_ver_tabla,
            pady=7,
        )
        self.btn_tabla.pack(side="left", fill="x", expand=True, padx=(4, 0))

    def _ejecutar_copia(self):
        if self.on_copiar:
            self.on_copiar()
            self.btn_copiar.configure(text="✓ ¡Procedimiento Copiado!")
            self.after(1800, lambda: self.btn_copiar.configure(text="📋 Copiar Procedimiento (8 Pasos)"))
