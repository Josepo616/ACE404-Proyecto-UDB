"""
main.py - Paso 2: Sliders dinámicos visibles y compatibles en macOS Dark Mode / Windows.
"""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import tkinter as tk
from tkinter import ttk

NOMINAL_R3 = 5.0
NOMINAL_K = 8.0


def main():
    root = tk.Tk()
    root.title("Paso 2 - Sliders Dinámicos (R3 y k)")
    root.geometry("520x360")
    root.minsize(440, 300)

    # Usar tema 'clam' para evitar el bug de transparencia de sliders en macOS Dark Mode
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
        style.configure(
            "Horizontal.TScale",
            troughcolor="#404040",
            background="#007AFF",
            sliderlength=28,
            sliderthickness=16,
        )
    except Exception:
        pass

    frame = tk.Frame(root, padx=20, pady=16)
    frame.pack(fill="both", expand=True)

    # 1. Indicador general superior
    btn_info = tk.Button(
        frame,
        text=f"Valores: R3 = {NOMINAL_R3:.1f} Ω  |  k = {NOMINAL_K:.1f} Ω",
        font=("Helvetica", 13, "bold"),
        state="disabled",
        disabledforeground="#007AFF",
        relief="groove",
        pady=8,
    )
    btn_info.pack(fill="x", pady=(0, 16))

    def actualizar_resumen():
        r3_num = round(float(scale_r3.get()), 1)
        k_num = round(float(scale_k.get()), 1)
        btn_r3_lbl.configure(text=f"Resistencia R3: {r3_num:.1f} Ω")
        btn_k_lbl.configure(text=f"Ganancia dependiente k: {k_num:.1f} Ω")
        btn_info.configure(text=f"Valores: R3 = {r3_num:.1f} Ω  |  k = {k_num:.1f} Ω")

    # --- CONTROL R3 ---
    btn_r3_lbl = tk.Button(
        frame,
        text=f"Resistencia R3: {NOMINAL_R3:.1f} Ω",
        font=("Helvetica", 11, "bold"),
        state="disabled",
        disabledforeground="#E0E0E0",
        relief="flat",
        anchor="w",
    )
    btn_r3_lbl.pack(fill="x")

    fila_r3 = tk.Frame(frame)
    fila_r3.pack(fill="x", pady=(2, 14))

    def mod_r3(delta):
        nuevo = max(0.5, min(30.0, round(scale_r3.get() + delta, 1)))
        scale_r3.set(nuevo)
        actualizar_resumen()

    tk.Button(fila_r3, text="◀ -1", width=5, command=lambda: mod_r3(-1.0)).pack(side="left", padx=(0, 6))

    scale_r3 = ttk.Scale(
        fila_r3,
        from_=0.5,
        to=30.0,
        orient="horizontal",
        value=NOMINAL_R3,
        command=lambda _: actualizar_resumen(),
    )
    scale_r3.pack(side="left", fill="x", expand=True)

    tk.Button(fila_r3, text="+1 ▶", width=5, command=lambda: mod_r3(1.0)).pack(side="left", padx=(6, 0))

    # --- CONTROL k ---
    btn_k_lbl = tk.Button(
        frame,
        text=f"Ganancia dependiente k: {NOMINAL_K:.1f} Ω",
        font=("Helvetica", 11, "bold"),
        state="disabled",
        disabledforeground="#E0E0E0",
        relief="flat",
        anchor="w",
    )
    btn_k_lbl.pack(fill="x")

    fila_k = tk.Frame(frame)
    fila_k.pack(fill="x", pady=(2, 18))

    def mod_k(delta):
        nuevo = max(-20.0, min(30.0, round(scale_k.get() + delta, 1)))
        scale_k.set(nuevo)
        actualizar_resumen()

    tk.Button(fila_k, text="◀ -1", width=5, command=lambda: mod_k(-1.0)).pack(side="left", padx=(0, 6))

    scale_k = ttk.Scale(
        fila_k,
        from_=-20.0,
        to=30.0,
        orient="horizontal",
        value=NOMINAL_K,
        command=lambda _: actualizar_resumen(),
    )
    scale_k.pack(side="left", fill="x", expand=True)

    tk.Button(fila_k, text="+1 ▶", width=5, command=lambda: mod_k(1.0)).pack(side="left", padx=(6, 0))

    # --- BOTÓN RESTABLECER ---
    def restablecer():
        scale_r3.set(NOMINAL_R3)
        scale_k.set(NOMINAL_K)
        actualizar_resumen()

    btn_reset = tk.Button(
        frame,
        text="↺ Restablecer Nominales (R3 = 5.0 Ω, k = 8.0 Ω)",
        font=("Helvetica", 11),
        command=restablecer,
        pady=6,
    )
    btn_reset.pack(fill="x")

    root.update_idletasks()
    root.update()

    root.mainloop()


if __name__ == "__main__":
    main()
