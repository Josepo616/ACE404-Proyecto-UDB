"""
interfaz.py - Diseño UI/UX y Frontend para el Simulador DC (Fase 3).
Análisis Nodal, Verificación por Mallas, Balance Energético y Procedimiento.
Estructurado en arquitectura orientada a objetos (POO) con Tkinter.
"""

import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import subprocess
import sys
import tempfile
import tkinter as tk

from modelo import paso_a_paso, resolver_circuito
from componentes import VisibleSlider

NOMINAL_R3 = 5.0
NOMINAL_K = 8.0
K_SINGULAR = -56.0 / 5.5  # ≈ -10.1818 Ω


class SimuladorApp:
    """
    Aplicación de escritorio para la simulación del circuito DC (Fase 3).
    Maneja la interfaz gráfica, eventos de usuario y enlace con el modelo matemático.
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

        # 1. Indicador general superior de entradas
        self.btn_info = tk.Button(
            self.card,
            text=f"Entradas: R3 = {self.NOMINAL_R3:.1f} Ω  |  k = {self.NOMINAL_K:.1f} Ω",
            font=("Helvetica", 13, "bold"),
            state="disabled",
            disabledforeground="#007AFF",
            relief="groove",
            pady=8,
        )
        self.btn_info.pack(fill="x", pady=(0, 10))

        # --- CONTROL R3 ---
        self.btn_r3_lbl = tk.Button(
            self.card,
            text=f"Resistencia R3: {self.NOMINAL_R3:.1f} Ω",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            disabledforeground="#E0E0E0",
            relief="flat",
            anchor="w",
        )
        self.btn_r3_lbl.pack(fill="x")

        fila_r3 = tk.Frame(self.card)
        fila_r3.pack(fill="x", pady=(2, 8))

        tk.Button(fila_r3, text="◀ -1", width=5, command=lambda: self.modificar_r3(-1.0)).pack(side="left", padx=(0, 6))

        self.slider_r3 = VisibleSlider(
            fila_r3,
            from_=0.5,
            to=30.0,
            value=self.NOMINAL_R3,
            command=lambda _: self.actualizar_resumen(),
        )
        self.slider_r3.pack(side="left", fill="x", expand=True)

        tk.Button(fila_r3, text="+1 ▶", width=5, command=lambda: self.modificar_r3(1.0)).pack(side="left", padx=(6, 0))

        # --- CONTROL k ---
        self.btn_k_lbl = tk.Button(
            self.card,
            text=f"Ganancia dependiente k: {self.NOMINAL_K:.1f} Ω",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            disabledforeground="#E0E0E0",
            relief="flat",
            anchor="w",
        )
        self.btn_k_lbl.pack(fill="x")

        fila_k = tk.Frame(self.card)
        fila_k.pack(fill="x", pady=(2, 10))

        tk.Button(fila_k, text="◀ -1", width=5, command=lambda: self.modificar_k(-1.0)).pack(side="left", padx=(0, 6))

        self.slider_k = VisibleSlider(
            fila_k,
            from_=-20.0,
            to=30.0,
            value=self.NOMINAL_K,
            command=lambda _: self.actualizar_resumen(),
        )
        self.slider_k.pack(side="left", fill="x", expand=True)

        tk.Button(fila_k, text="+1 ▶", width=5, command=lambda: self.modificar_k(1.0)).pack(side="left", padx=(6, 0))

        # --- ESTADO Y ALERTA DE SINGULARIDAD ---
        self.btn_status = tk.Button(
            self.card,
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
            self.card,
            text="📊 Resultados Nodal (resolver_circuito)",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            relief="flat",
            anchor="w",
        )
        btn_res_tit.pack(fill="x", pady=(2, 2))

        fila_med = tk.Frame(self.card)
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
            self.card,
            text="🔄 Verificación por Mallas (i1, i2=iϕ, i3)",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            relief="flat",
            anchor="w",
        )
        btn_mallas_tit.pack(fill="x", pady=(2, 2))

        fila_mallas = tk.Frame(self.card)
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
            self.card,
            text="⚡ Balance de Potencia (P_gen vs P_abs)",
            font=("Helvetica", 11, "bold"),
            state="disabled",
            relief="flat",
            anchor="w",
        )
        btn_bal_tit.pack(fill="x", pady=(2, 2))

        fila_bal = tk.Frame(self.card)
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

        # --- ACCIONES FILA 1: RESTABLECER Y SINGULARIDAD ---
        fila_acciones1 = tk.Frame(self.card)
        fila_acciones1.pack(fill="x", pady=(0, 6))

        self.btn_reset = tk.Button(
            fila_acciones1,
            text="↺ Restablecer Nominales",
            font=("Helvetica", 11, "bold"),
            command=self.restablecer,
            pady=8,
        )
        self.btn_reset.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_sing = tk.Button(
            fila_acciones1,
            text="⚠ Probar Singularidad (k ≈ -10.18)",
            font=("Helvetica", 11, "bold"),
            command=self.probar_singularidad,
            pady=8,
        )
        self.btn_sing.pack(side="left", fill="x", expand=True, padx=(4, 0))

        # --- ACCIONES FILA 2: PROCEDIMIENTO MATEMÁTICO COMPLETO ---
        fila_acciones2 = tk.Frame(self.card)
        fila_acciones2.pack(fill="x")

        self.btn_copiar = tk.Button(
            fila_acciones2,
            text="📋 Copiar Procedimiento (8 Pasos)",
            font=("Helvetica", 10, "bold"),
            command=self.copiar_procedimiento,
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
            fila_acciones2,
            text=texto_btn_abrir,
            font=("Helvetica", 10, "bold"),
            command=self.abrir_en_visor,
            pady=7,
        )
        self.btn_abrir.pack(side="left", fill="x", expand=True, padx=(4, 0))

    def modificar_r3(self, delta):
        """Ajusta la resistencia R3 sumando o restando el delta."""
        self.slider_r3.set(self.slider_r3.get() + delta)
        self.actualizar_resumen()

    def modificar_k(self, delta):
        """Ajusta la ganancia k sumando o restando el delta."""
        self.slider_k.set(self.slider_k.get() + delta)
        self.actualizar_resumen()

    def restablecer(self):
        """Restablece los valores nominales de diseño (R3=5Ω, k=8Ω)."""
        self.slider_r3.set(self.NOMINAL_R3)
        self.slider_k.set(self.NOMINAL_K)
        self.actualizar_resumen()

    def probar_singularidad(self):
        """Ajusta k al punto de singularidad (det(G)=0) para verificar estabilidad."""
        self.slider_k.set(self.K_SINGULAR)
        self.actualizar_resumen()

    def copiar_procedimiento(self):
        """Genera y copia el procedimiento de 8 pasos al portapapeles del sistema."""
        k_val = self.slider_k.get()
        k_calc = self.K_SINGULAR if abs(k_val - self.K_SINGULAR) < 0.02 else round(k_val, 1)
        texto = paso_a_paso(R3=round(self.slider_r3.get(), 1), k=k_calc)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        self.btn_copiar.configure(text="✓ ¡Procedimiento Copiado!")
        self.root.after(1800, lambda: self.btn_copiar.configure(text="📋 Copiar Procedimiento (8 Pasos)"))

    def abrir_en_visor(self):
        """Abre el procedimiento matemático completo en el visor nativo del sistema operativo."""
        k_val = self.slider_k.get()
        k_calc = self.K_SINGULAR if abs(k_val - self.K_SINGULAR) < 0.02 else round(k_val, 1)
        texto = paso_a_paso(R3=round(self.slider_r3.get(), 1), k=k_calc)
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
        r3_num = round(self.slider_r3.get(), 1)
        k_val = self.slider_k.get()

        if abs(k_val - self.K_SINGULAR) < 0.02:
            k_num = self.K_SINGULAR
            k_str = "-10.18"
        else:
            k_num = round(k_val, 1)
            k_str = f"{k_num:.1f}"

        self.btn_r3_lbl.configure(text=f"Resistencia R3: {r3_num:.1f} Ω")
        self.btn_k_lbl.configure(text=f"Ganancia dependiente k: {k_str} Ω")
        self.btn_info.configure(text=f"Entradas: R3 = {r3_num:.1f} Ω  |  k = {k_str} Ω")

        # Conexión con modelo.py
        res = resolver_circuito(R3=r3_num, k=k_num)

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

    def ejecutar(self):
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()


def crear_interfaz():
    """Función de compatibilidad para inicializar y ejecutar el simulador."""
    app = SimuladorApp()
    app.ejecutar()


if __name__ == "__main__":
    crear_interfaz()
