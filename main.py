"""
main.py - Paso 3: Conexión con resolver_circuito() y despliegue de resultados (VA, VB, VC, iphi).
"""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import tkinter as tk

from modelo import resolver_circuito

NOMINAL_R3 = 5.0
NOMINAL_K = 8.0


class VisibleSlider(tk.Canvas):
    """
    Control deslizante de alta visibilidad dibujado directamente en Canvas.
    Garantiza que la barra y la perilla sean siempre visibles en macOS (Dark/Light) y Windows.
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

    def _val_to_x(self, val):
        w = self.winfo_width()
        margin = 16
        fraction = (val - self.from_) / (self.to - self.from_)
        return margin + fraction * max(1, w - 2 * margin)

    def _x_to_val(self, x):
        w = self.winfo_width()
        margin = 16
        fraction = max(0.0, min(1.0, (x - margin) / max(1, w - 2 * margin)))
        return round(self.from_ + fraction * (self.to - self.from_), 1)

    def _draw(self, event=None):
        self.delete("all")
        w = self.winfo_width()
        if w < 50:
            return

        cy = 18
        margin = 16
        kx = self._val_to_x(self.val)

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
        self.val = max(self.from_, min(self.to, round(float(val), 1)))
        self._draw()


def main():
    root = tk.Tk()
    root.title("Simulador DC - Paso 3: Resultados Nodal en Tiempo Real")
    root.geometry("560x520")
    root.minsize(480, 460)

    # Contenedor centrado responsivo
    card = tk.Frame(root, padx=24, pady=20)
    card.place(relx=0.5, rely=0.5, anchor="center", width=500)

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
    btn_info.pack(fill="x", pady=(0, 14))

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
    fila_r3.pack(fill="x", pady=(2, 12))

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
    fila_k.pack(fill="x", pady=(2, 16))

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

    # --- SECCIÓN RESULTADOS NODAL (PASO 3) ---
    btn_res_tit = tk.Button(
        card,
        text="📊 Resultados Nodal (resolver_circuito)",
        font=("Helvetica", 11, "bold"),
        state="disabled",
        disabledforeground="#A0A0A0",
        relief="flat",
        anchor="w",
    )
    btn_res_tit.pack(fill="x", pady=(2, 4))

    # Fila de tarjetas de medición
    fila_med = tk.Frame(card)
    fila_med.pack(fill="x", pady=(0, 16))

    box_va = tk.Button(
        fila_med,
        text="VA: -- V",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        disabledforeground="#38BDF8",
        relief="groove",
        pady=8,
    )
    box_va.pack(side="left", fill="x", expand=True, padx=2)

    box_vb = tk.Button(
        fila_med,
        text="VB: -- V",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        disabledforeground="#38BDF8",
        relief="groove",
        pady=8,
    )
    box_vb.pack(side="left", fill="x", expand=True, padx=2)

    box_vc = tk.Button(
        fila_med,
        text="VC: -- V",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        disabledforeground="#C084FC",
        relief="groove",
        pady=8,
    )
    box_vc.pack(side="left", fill="x", expand=True, padx=2)

    box_iphi = tk.Button(
        fila_med,
        text="iϕ: -- A",
        font=("Helvetica", 10, "bold"),
        state="disabled",
        disabledforeground="#4ADE80",
        relief="groove",
        pady=8,
    )
    box_iphi.pack(side="left", fill="x", expand=True, padx=2)

    # Función que conecta los sliders con el modelo matemático
    def actualizar_resumen():
        r3_num = round(slider_r3.get(), 1)
        k_num = round(slider_k.get(), 1)
        btn_r3_lbl.configure(text=f"Resistencia R3: {r3_num:.1f} Ω")
        btn_k_lbl.configure(text=f"Ganancia dependiente k: {k_num:.1f} Ω")
        btn_info.configure(text=f"Entradas: R3 = {r3_num:.1f} Ω  |  k = {k_num:.1f} Ω")

        # Conexión con modelo.py (Katherine)
        res = resolver_circuito(R3=r3_num, k=k_num)
        if not res.get("error"):
            box_va.configure(text=f"VA: {res['VA']:.3f} V")
            box_vb.configure(text=f"VB: {res['VB']:.3f} V")
            box_vc.configure(text=f"VC: {res['VC']:.3f} V")
            box_iphi.configure(text=f"iϕ: {res['iphi']:.4f} A")
        else:
            box_va.configure(text="VA: -- V")
            box_vb.configure(text="VB: -- V")
            box_vc.configure(text="VC: -- V")
            box_iphi.configure(text="iϕ: -- A")

    # --- BOTÓN RESTABLECER ---
    def restablecer():
        slider_r3.set(NOMINAL_R3)
        slider_k.set(NOMINAL_K)
        actualizar_resumen()

    btn_reset = tk.Button(
        card,
        text="↺ Restablecer Nominales (R3 = 5.0 Ω, k = 8.0 Ω)",
        font=("Helvetica", 11, "bold"),
        command=restablecer,
        pady=8,
    )
    btn_reset.pack(fill="x")

    # Inicializar con valores nominales
    actualizar_resumen()

    root.update_idletasks()
    root.update()

    root.mainloop()


if __name__ == "__main__":
    main()
