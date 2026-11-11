"""
ui/metricas.py - Panel de resultados del análisis eléctrico y balance (Fase 3).
Autor: José Rolando Álvarez Mejía (Equipo G01T - ACE941 / ACE404)

Presenta en tiempo real los voltajes de nodo (VA, VB, VC), corriente de control (iϕ),
la verificación por método de mallas (i1, i2, i3) y el balance de potencias (P_gen vs P_abs).
Utiliza tarjetas basadas en botones nativos estilizados para garantizar nitidez y alto contraste.
"""

import tkinter as tk


class PanelMetricas(tk.Frame):
    """
    Panel de visualización en tiempo real para voltajes nodales,
    verificación de mallas, balance de potencias y detección de singularidad.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._construir_widgets()

    def _construir_widgets(self):
        # --- ESTADO Y ALERTA DE SINGULARIDAD ---
        self.btn_status = tk.Button(
            self,
            text="Estado: Normal (Solución única)",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            wraplength=450,
            pady=6,
        )
        self.btn_status.pack(fill="x", pady=(2, 8))

        # --- SECCIÓN RESULTADOS NODAL ---
        btn_res_tit = tk.Button(
            self,
            text="📊 Resultados Nodal (resolver_circuito)",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            relief="flat",
            anchor="w",
        )
        btn_res_tit.pack(fill="x", pady=(2, 2))

        fila_med = tk.Frame(self)
        fila_med.pack(fill="x", pady=(0, 8))

        self.box_va = tk.Button(
            fila_med,
            text="VA: -- V",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_va.pack(side="left", fill="x", expand=True, padx=2)

        self.box_vb = tk.Button(
            fila_med,
            text="VB: -- V",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_vb.pack(side="left", fill="x", expand=True, padx=2)

        self.box_vc = tk.Button(
            fila_med,
            text="VC: -- V",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_vc.pack(side="left", fill="x", expand=True, padx=2)

        self.box_iphi = tk.Button(
            fila_med,
            text="iϕ: -- A",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_iphi.pack(side="left", fill="x", expand=True, padx=2)

        # --- SECCIÓN VERIFICACIÓN POR MALLAS ---
        btn_mallas_tit = tk.Button(
            self,
            text="🔄 Verificación por Mallas (i1, i2=iϕ, i3)",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            relief="flat",
            anchor="w",
        )
        btn_mallas_tit.pack(fill="x", pady=(2, 2))

        fila_mallas = tk.Frame(self)
        fila_mallas.pack(fill="x", pady=(0, 8))

        self.box_m1 = tk.Button(
            fila_mallas,
            text="i1: -- A",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_m1.pack(side="left", fill="x", expand=True, padx=2)

        self.box_m2 = tk.Button(
            fila_mallas,
            text="i2: -- A",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_m2.pack(side="left", fill="x", expand=True, padx=2)

        self.box_m3 = tk.Button(
            fila_mallas,
            text="i3: -- A",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_m3.pack(side="left", fill="x", expand=True, padx=2)

        self.box_coincide = tk.Button(
            fila_mallas,
            text="Mallas: --",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_coincide.pack(side="left", fill="x", expand=True, padx=2)

        # --- SECCIÓN BALANCE ENERGÉTICO ---
        btn_bal_tit = tk.Button(
            self,
            text="⚡ Balance de Potencia (P_gen vs P_abs)",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            relief="flat",
            anchor="w",
        )
        btn_bal_tit.pack(fill="x", pady=(2, 2))

        fila_bal = tk.Frame(self)
        fila_bal.pack(fill="x", pady=(0, 10))

        self.box_pgen = tk.Button(
            fila_bal,
            text="P_gen: -- W",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_pgen.pack(side="left", fill="x", expand=True, padx=2)

        self.box_pabs = tk.Button(
            fila_bal,
            text="P_abs: -- W",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_pabs.pack(side="left", fill="x", expand=True, padx=2)

        self.box_bal_ok = tk.Button(
            fila_bal,
            text="Balance: --",
            font=("Helvetica", 10, "bold"),
            state="disabled",
            relief="groove",
            pady=6,
        )
        self.box_bal_ok.pack(side="left", fill="x", expand=True, padx=2)

    def actualizar(self, res):
        """Actualiza el texto y estado de todas las tarjetas numéricas."""
        if res.get("error"):
            self.btn_status.configure(text=f"⚠ ERROR: {res['error']}")

            self.box_va.configure(text="VA: -- V")
            self.box_vb.configure(text="VB: -- V")
            self.box_vc.configure(text="VC: -- V")
            self.box_iphi.configure(text="iϕ: -- A")

            self.box_m1.configure(text="i1: -- A")
            self.box_m2.configure(text="i2: -- A")
            self.box_m3.configure(text="i3: -- A")
            self.box_coincide.configure(text="Mallas: --")

            self.box_pgen.configure(text="P_gen: -- W")
            self.box_pabs.configure(text="P_abs: -- W")
            self.box_bal_ok.configure(text="Balance: --")
        else:
            det = res.get("det_G", 0.0)
            self.btn_status.configure(text=f"Estado: Normal | Solución única (det = {det:.3f})")

            self.box_va.configure(text=f"VA: {res['VA']:.3f} V")
            self.box_vb.configure(text=f"VB: {res['VB']:.3f} V")
            self.box_vc.configure(text=f"VC: {res['VC']:.3f} V")
            self.box_iphi.configure(text=f"iϕ: {res['iphi']:.4f} A")

            m = res.get("mallas", [0.0, 0.0, 0.0])
            self.box_m1.configure(text=f"i1: {m[0]:.3f} A")
            self.box_m2.configure(text=f"i2: {m[1]:.3f} A")
            self.box_m3.configure(text=f"i3: {m[2]:.3f} A")
            coinc_str = "✓ Coincide" if res.get("coincide_nodal_mallas") else "✗ Diferencia"
            self.box_coincide.configure(text=f"Mallas: {coinc_str}")

            self.box_pgen.configure(text=f"P_gen: {res['P_generada']:.3f} W")
            self.box_pabs.configure(text=f"P_abs: {res['P_absorbida']:.3f} W")
            bal_str = "✓ Se conserva" if res.get("balance_ok") else "✗ Desbalance"
            self.box_bal_ok.configure(text=f"Balance: {bal_str}")
