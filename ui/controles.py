"""
ui/controles.py - Panel de control de parámetros de entrada R3 y k (Fase 3).
Autor: José Rolando Álvarez Mejía (Equipo G01T - ACE941 / ACE404)

Gestiona la interacción del usuario mediante sliders y botones incrementales de paso fino
(◀ -1, +1 ▶) para la exploración interactiva ("What-If") del circuito.
"""

import tkinter as tk
from ui.widgets import VisibleSlider


class PanelControles(tk.Frame):
    """
    Panel contenedor de controles de entrada para la resistencia R3 y la ganancia k.
    Sincroniza los valores numéricos y despacha eventos ante cualquier cambio.
    """

    def __init__(self, parent, nominal_r3=5.0, nominal_k=8.0, on_change=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_change = on_change
        self.nominal_r3 = nominal_r3
        self.nominal_k = nominal_k

        self._construir_widgets()

    def _construir_widgets(self):
        # 1. Indicador general superior de entradas
        self.btn_info = tk.Button(
            self,
            text=f"Entradas: R3 = {self.nominal_r3:.1f} Ω  |  k = {self.nominal_k:.1f} Ω",
            font=("Helvetica", 13, "bold"),
            state="disabled",
            disabledforeground="#007AFF",
            relief="groove",
            pady=8,
        )
        self.btn_info.pack(fill="x", pady=(0, 10))

        # --- CONTROL R3 ---
        self.btn_r3_lbl = tk.Button(
            self,
            text=f"Resistencia R3: {self.nominal_r3:.1f} Ω",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            disabledforeground="#E0E0E0",
            relief="flat",
            anchor="w",
        )
        self.btn_r3_lbl.pack(fill="x")

        fila_r3 = tk.Frame(self)
        fila_r3.pack(fill="x", pady=(2, 8))

        tk.Button(
            fila_r3,
            text="◀ -1",
            width=5,
            command=lambda: self.modificar_r3(-1.0),
        ).pack(side="left", padx=(0, 6))

        self.slider_r3 = VisibleSlider(
            fila_r3,
            from_=0.5,
            to=30.0,
            value=self.nominal_r3,
            command=lambda _: self._notificar_cambio(),
        )
        self.slider_r3.pack(side="left", fill="x", expand=True)

        tk.Button(
            fila_r3,
            text="+1 ▶",
            width=5,
            command=lambda: self.modificar_r3(1.0),
        ).pack(side="left", padx=(6, 0))

        # --- CONTROL k ---
        self.btn_k_lbl = tk.Button(
            self,
            text=f"Ganancia dependiente k: {self.nominal_k:.1f} Ω",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            disabledforeground="#E0E0E0",
            relief="flat",
            anchor="w",
        )
        self.btn_k_lbl.pack(fill="x")

        fila_k = tk.Frame(self)
        fila_k.pack(fill="x", pady=(2, 10))

        tk.Button(
            fila_k,
            text="◀ -1",
            width=5,
            command=lambda: self.modificar_k(-1.0),
        ).pack(side="left", padx=(0, 6))

        self.slider_k = VisibleSlider(
            fila_k,
            from_=-20.0,
            to=30.0,
            value=self.nominal_k,
            command=lambda _: self._notificar_cambio(),
        )
        self.slider_k.pack(side="left", fill="x", expand=True)

        tk.Button(
            fila_k,
            text="+1 ▶",
            width=5,
            command=lambda: self.modificar_k(1.0),
        ).pack(side="left", padx=(6, 0))

    def _notificar_cambio(self):
        if self.on_change:
            self.on_change()

    def modificar_r3(self, delta):
        self.slider_r3.set(self.slider_r3.get() + delta)
        self._notificar_cambio()

    def modificar_k(self, delta):
        self.slider_k.set(self.slider_k.get() + delta)
        self._notificar_cambio()

    def obtener_valores(self):
        return self.slider_r3.get(), self.slider_k.get()

    def establecer_valores(self, r3, k):
        self.slider_r3.set(r3)
        self.slider_k.set(k)

    def actualizar_etiquetas(self, r3_num, k_str):
        self.btn_r3_lbl.configure(text=f"Resistencia R3: {r3_num:.1f} Ω")
        self.btn_k_lbl.configure(text=f"Ganancia dependiente k: {k_str} Ω")
        self.btn_info.configure(text=f"Entradas: R3 = {r3_num:.1f} Ω  |  k = {k_str} Ω")
