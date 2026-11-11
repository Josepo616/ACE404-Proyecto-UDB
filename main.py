"""
main.py - Fase 3: Simulador DC Interactivo de Circuitos con Fuente Dependiente.
Análisis Nodal, Verificación por Mallas, Balance Energético y Procedimiento Paso a Paso.
"""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import subprocess
import tkinter as tk

from modelo import paso_a_paso, resolver_circuito

NOMINAL_R3 = 5.0
NOMINAL_K = 8.0
K_SINGULAR = -56.0 / 5.5  # ≈ -10.1818 Ω


class VisibleSlider(tk.Canvas):
    """
    Control deslizante de alta visibilidad dibujado directamente en Canvas.
    Garantiza que la barra y la perilla sean siempre visibles en macOS y Windows.
    """

    def __init__(self, parent, from_, to, value, command=None, **kwargs):
        super().__init__(parent, height=36, highlightthickness=0, bd=0, **kwargs)
        self.from_ = float(from_)
        self.to = float(to)
        self.val = float(value)
        self.command = command

        self.bind("<Configure>", self._draw)
        self.bind("<Button-1>", self._on_interaction)
        self.bind("<B1-Motion>", self._on_interaction)

    def _val_to_x(self, val, w=None):
        if w is None:
            w = self.winfo_width()
        if w < 50:
            w = 240
        margin = 16
        fraction = (val - self.from_) / (self.to - self.from_)
        return margin + fraction * max(1, w - 2 * margin)

    def _x_to_val(self, x, w=None):
        if w is None:
            w = self.winfo_width()
        if w < 50:
            w = 240
        margin = 16
        fraction = max(0.0, min(1.0, (x - margin) / max(1, w - 2 * margin)))
        return round(self.from_ + fraction * (self.to - self.from_), 1)

    def _draw(self, event=None):
        self.delete("all")
        if event is not None and hasattr(event, "width") and event.width > 50:
            w = event.width
        else:
            w = self.winfo_width()
        if w < 50:
            w = 240

        cy = 18
        margin = 16
        kx = self._val_to_x(self.val, w)

        # Fondo del riel (gris neutro oscuro)
        self.create_line(margin, cy, w - margin, cy, fill="#3A3A3C", width=6, capstyle="round")
        # Progreso activo del riel (azul visible #007AFF)
        self.create_line(margin, cy, kx, cy, fill="#007AFF", width=6, capstyle="round")
        # Perilla arrastrable (círculo blanco con borde azul)
        self.create_oval(kx - 10, cy - 10, kx + 10, cy + 10, fill="#FFFFFF", outline="#007AFF", width=2)

    def _on_interaction(self, event):
        self.val = self._x_to_val(event.x)
        self._draw()
        if self.command:
            self.command(self.val)

    def get(self):
        return self.val

    def set(self, val):
        self.val = max(self.from_, min(self.to, float(val)))
        self._draw()


def main():
    root = tk.Tk()
    root.title("Simulador DC - Circuito con Fuente Dependiente (Fase 3)")
    root.geometry("580x720")
    root.minsize(520, 660)

    # Contenedor centrado responsivo
    card = tk.Frame(root, padx=22, pady=16)
    card.place(relx=0.5, rely=0.5, anchor="center", width=530)

    # 1. Indicador general superior de entradas
    btn_info = tk.Button(
        card,
        text=f"Entradas: R3 = {NOMINAL_R3:.1f} Ω  |  k = {NOMINAL_K:.1f} Ω",
        font=("Helvetica", 13, "bold"),
        state="disabled",
        disabledforeground="#007AFF",
        relief="groove",
        pady=8,
    )
    btn_info.pack(fill="x", pady=(0, 10))

    # --- CONTROL R3 ---
    btn_r3_lbl = tk.Button(
        card,
        text=f"Resistencia R3: {NOMINAL_R3:.1f} Ω",
        font=("Helvetica", 11, "bold"),
        state="disabled",
        disabledforeground="#E0E0E0",
        relief="flat",
        anchor="w",
    )
    btn_r3_lbl.pack(fill="x")

    fila_r3 = tk.Frame(card)
    fila_r3.pack(fill="x", pady=(2, 8))

    def mod_r3(delta):
        slider_r3.set(slider_r3.get() + delta)
        actualizar_resumen()

    tk.Button(fila_r3, text="◀ -1", width=5, command=lambda: mod_r3(-1.0)).pack(side="left", padx=(0, 6))

    slider_r3 = VisibleSlider(
        fila_r3,
        from_=0.5,
        to=30.0,
        value=NOMINAL_R3,
        command=lambda _: actualizar_resumen(),
    )
    slider_r3.pack(side="left", fill="x", expand=True)

    tk.Button(fila_r3, text="+1 ▶", width=5, command=lambda: mod_r3(1.0)).pack(side="left", padx=(6, 0))

    # --- CONTROL k ---
    btn_k_lbl = tk.Button(
        card,
        text=f"Ganancia dependiente k: {NOMINAL_K:.1f} Ω",
        font=("Helvetica", 11, "bold"),
        state="disabled",
        disabledforeground="#E0E0E0",
        relief="flat",
        anchor="w",
    )
    btn_k_lbl.pack(fill="x")

    fila_k = tk.Frame(card)
    fila_k.pack(fill="x", pady=(2, 10))

    def mod_k(delta):
        slider_k.set(slider_k.get() + delta)
        actualizar_resumen()

    tk.Button(fila_k, text="◀ -1", width=5, command=lambda: mod_k(-1.0)).pack(side="left", padx=(0, 6))

    slider_k = VisibleSlider(
        fila_k,
        from_=-20.0,
        to=30.0,
        value=NOMINAL_K,
        command=lambda _: actualizar_resumen(),
    )
    slider_k.pack(side="left", fill="x", expand=True)

    tk.Button(fila_k, text="+1 ▶", width=5, command=lambda: mod_k(1.0)).pack(side="left", padx=(6, 0))

    # --- ESTADO Y ALERTA DE SINGULARIDAD ---
    btn_status = tk.Button(
        card,
        text="Estado: Normal (Solución única)",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        wraplength=450,
        pady=6,
    )
    btn_status.pack(fill="x", pady=(2, 8))

    # --- SECCIÓN RESULTADOS NODAL ---
    btn_res_tit = tk.Button(
        card,
        text="📊 Resultados Nodal (resolver_circuito)",
        font=("Helvetica", 11, "bold"),
        state="disabled",
        relief="flat",
        anchor="w",
    )
    btn_res_tit.pack(fill="x", pady=(2, 2))

    fila_med = tk.Frame(card)
    fila_med.pack(fill="x", pady=(0, 8))

    box_va = tk.Button(
        fila_med,
        text="VA: -- V",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_va.pack(side="left", fill="x", expand=True, padx=2)

    box_vb = tk.Button(
        fila_med,
        text="VB: -- V",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_vb.pack(side="left", fill="x", expand=True, padx=2)

    box_vc = tk.Button(
        fila_med,
        text="VC: -- V",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_vc.pack(side="left", fill="x", expand=True, padx=2)

    box_iphi = tk.Button(
        fila_med,
        text="iϕ: -- A",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_iphi.pack(side="left", fill="x", expand=True, padx=2)

    # --- SECCIÓN VERIFICACIÓN POR MALLAS ---
    btn_mallas_tit = tk.Button(
        card,
        text="🔄 Verificación por Mallas (i1, i2=iϕ, i3)",
        font=("Helvetica", 11, "bold"),
        state="disabled",
        relief="flat",
        anchor="w",
    )
    btn_mallas_tit.pack(fill="x", pady=(2, 2))

    fila_mallas = tk.Frame(card)
    fila_mallas.pack(fill="x", pady=(0, 8))

    box_m1 = tk.Button(
        fila_mallas,
        text="i1: -- A",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_m1.pack(side="left", fill="x", expand=True, padx=2)

    box_m2 = tk.Button(
        fila_mallas,
        text="i2: -- A",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_m2.pack(side="left", fill="x", expand=True, padx=2)

    box_m3 = tk.Button(
        fila_mallas,
        text="i3: -- A",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_m3.pack(side="left", fill="x", expand=True, padx=2)

    box_coincide = tk.Button(
        fila_mallas,
        text="Mallas: --",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_coincide.pack(side="left", fill="x", expand=True, padx=2)

    # --- SECCIÓN BALANCE ENERGÉTICO ---
    btn_bal_tit = tk.Button(
        card,
        text="⚡ Balance de Potencia (P_gen vs P_abs)",
        font=("Helvetica", 11, "bold"),
        state="disabled",
        relief="flat",
        anchor="w",
    )
    btn_bal_tit.pack(fill="x", pady=(2, 2))

    fila_bal = tk.Frame(card)
    fila_bal.pack(fill="x", pady=(0, 10))

    box_pgen = tk.Button(
        fila_bal,
        text="P_gen: -- W",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_pgen.pack(side="left", fill="x", expand=True, padx=2)

    box_pabs = tk.Button(
        fila_bal,
        text="P_abs: -- W",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_pabs.pack(side="left", fill="x", expand=True, padx=2)

    box_bal_ok = tk.Button(
        fila_bal,
        text="Balance: --",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        relief="groove",
        pady=6,
    )
    box_bal_ok.pack(side="left", fill="x", expand=True, padx=2)

    # Función que conecta los sliders con el modelo matemático y maneja errores
    def actualizar_resumen():
        r3_num = round(slider_r3.get(), 1)
        k_val = slider_k.get()

        if abs(k_val - K_SINGULAR) < 0.02:
            k_num = K_SINGULAR
            k_str = "-10.18"
        else:
            k_num = round(k_val, 1)
            k_str = f"{k_num:.1f}"

        btn_r3_lbl.configure(text=f"Resistencia R3: {r3_num:.1f} Ω")
        btn_k_lbl.configure(text=f"Ganancia dependiente k: {k_str} Ω")
        btn_info.configure(text=f"Entradas: R3 = {r3_num:.1f} Ω  |  k = {k_str} Ω")

        # Conexión con modelo.py
        res = resolver_circuito(R3=r3_num, k=k_num)

        if res.get("error"):
            btn_status.configure(text=f"⚠ ERROR: {res['error']}")

            box_va.configure(text="VA: -- V")
            box_vb.configure(text="VB: -- V")
            box_vc.configure(text="VC: -- V")
            box_iphi.configure(text="iϕ: -- A")

            box_m1.configure(text="i1: -- A")
            box_m2.configure(text="i2: -- A")
            box_m3.configure(text="i3: -- A")
            box_coincide.configure(text="Mallas: --")

            box_pgen.configure(text="P_gen: -- W")
            box_pabs.configure(text="P_abs: -- W")
            box_bal_ok.configure(text="Balance: --")
        else:
            det = res.get("det_G", 0.0)
            btn_status.configure(text=f"Estado: Normal | Solución única (det = {det:.3f})")

            box_va.configure(text=f"VA: {res['VA']:.3f} V")
            box_vb.configure(text=f"VB: {res['VB']:.3f} V")
            box_vc.configure(text=f"VC: {res['VC']:.3f} V")
            box_iphi.configure(text=f"iϕ: {res['iphi']:.4f} A")

            m = res.get("mallas", [0.0, 0.0, 0.0])
            box_m1.configure(text=f"i1: {m[0]:.3f} A")
            box_m2.configure(text=f"i2: {m[1]:.3f} A")
            box_m3.configure(text=f"i3: {m[2]:.3f} A")
            coinc_str = "✓ Coincide" if res.get("coincide_nodal_mallas") else "✗ Diferencia"
            box_coincide.configure(text=f"Mallas: {coinc_str}")

            box_pgen.configure(text=f"P_gen: {res['P_generada']:.3f} W")
            box_pabs.configure(text=f"P_abs: {res['P_absorbida']:.3f} W")
            bal_str = "✓ Se conserva" if res.get("balance_ok") else "✗ Desbalance"
            box_bal_ok.configure(text=f"Balance: {bal_str}")

    # --- ACCIONES FILA 1: RESTABLECER Y SINGULARIDAD ---
    fila_acciones1 = tk.Frame(card)
    fila_acciones1.pack(fill="x", pady=(0, 6))

    def restablecer():
        slider_r3.set(NOMINAL_R3)
        slider_k.set(NOMINAL_K)
        actualizar_resumen()

    btn_reset = tk.Button(
        fila_acciones1,
        text="↺ Restablecer Nominales",
        font=("Helvetica", 11, "bold"),
        command=restablecer,
        pady=8,
    )
    btn_reset.pack(side="left", fill="x", expand=True, padx=(0, 4))

    def probar_singularidad():
        slider_k.set(K_SINGULAR)
        actualizar_resumen()

    btn_sing = tk.Button(
        fila_acciones1,
        text="⚠ Probar Singularidad (k ≈ -10.18)",
        font=("Helvetica", 11, "bold"),
        command=probar_singularidad,
        pady=8,
    )
    btn_sing.pack(side="left", fill="x", expand=True, padx=(4, 0))

    # Inicializar estado
    actualizar_resumen()

    root.update_idletasks()
    root.update()

    root.mainloop()


if __name__ == "__main__":
    main()
