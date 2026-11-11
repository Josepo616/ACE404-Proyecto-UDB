"""
ui/esquema.py - Generador del diagrama esquemático del circuito en alta resolución.
Autor: José Rolando Álvarez Mejía (Equipo G01T - ACE941 / ACE404)

Genera una imagen vectorial/rasterizada de alta definición del circuito DC con
los potenciales nodales (VA, VB, VC), corriente de control (iphi) y parámetros
actualizados en tiempo real. Se abre en el visor nativo (Vista Previa / Fotos)
garantizando 100% de visibilidad y calidad sin depender de Canvas de Tkinter.
"""

import os
import subprocess
import sys
import tempfile

os.environ["MPLCONFIGDIR"] = tempfile.gettempdir()

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def generar_diagrama_circuito(
    r3=5.0,
    k=8.0,
    va=16.0,
    vb=10.0,
    vc=9.6,
    iphi=1.2,
    error=False,
    ruta_salida=None,
):
    """
    Genera un diagrama técnico nítido del circuito patrón de Fase 3 con fondo oscuro
    y badges de voltajes nodales en tiempo real.
    """
    if ruta_salida is None:
        ruta_salida = os.path.join(tempfile.gettempdir(), "circuito_esquema_fase3.png")

    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    fig.patch.set_facecolor("#1C1C1E")
    ax.set_facecolor("#1C1C1E")

    # Coordenadas principales del circuito
    y_top = 2.7
    y_bot = 0.8
    x_vs = 1.0
    x_a = 3.3
    x_b = 5.8
    x_c = 8.3

    color_linea = "#8E8E93"
    color_txt = "#FFFFFF"

    # 1. Riel de tierra inferior
    ax.plot([x_vs, x_c], [y_bot, y_bot], color=color_linea, lw=2.5)

    # Símbolo estándar de tierra
    x_gnd = (x_a + x_b) / 2
    ax.plot([x_gnd, x_gnd], [y_bot, y_bot - 0.2], color=color_linea, lw=2.5)
    ax.plot([x_gnd - 0.35, x_gnd + 0.35], [y_bot - 0.2, y_bot - 0.2], color=color_linea, lw=2.5)
    ax.plot([x_gnd - 0.2, x_gnd + 0.2], [y_bot - 0.28, y_bot - 0.28], color=color_linea, lw=2)
    ax.plot([x_gnd - 0.08, x_gnd + 0.08], [y_bot - 0.36, y_bot - 0.36], color=color_linea, lw=1.5)
    ax.text(x_gnd, y_bot - 0.52, "Tierra (0 V)", color="#AEAEB2", fontsize=10, ha="center", weight="bold")

    # 2. Rama Vs (Fuente de voltaje independiente de 20 V)
    ax.plot([x_vs, x_vs], [y_bot, y_bot + 0.6], color=color_linea, lw=2.5)
    ax.plot([x_vs, x_vs], [y_bot + 1.3, y_top], color=color_linea, lw=2.5)
    circ_vs = patches.Circle((x_vs, y_bot + 0.95), 0.35, facecolor="#2C2C2E", edgecolor="#30D158", lw=2)
    ax.add_patch(circ_vs)
    ax.text(x_vs, y_bot + 0.95, "Vs\n20V", color=color_txt, fontsize=10, ha="center", va="center", weight="bold")
    ax.text(x_vs, y_bot + 1.15, "+", color="#30D158", fontsize=11, ha="center", va="center", weight="bold")
    ax.text(x_vs, y_bot + 0.75, "−", color="#FF453A", fontsize=11, ha="center", va="center", weight="bold")

    # 3. Resistencia R1 = 2 Ω (entre Vs y Nodo A)
    x_r1 = (x_vs + x_a) / 2
    ax.plot([x_vs, x_r1 - 0.55], [y_top, y_top], color=color_linea, lw=2.5)
    ax.plot([x_r1 + 0.55, x_a], [y_top, y_top], color=color_linea, lw=2.5)
    rect_r1 = patches.Rectangle((x_r1 - 0.55, y_top - 0.22), 1.1, 0.44, facecolor="#2C2C2E", edgecolor="#AEAEB2", lw=1.5)
    ax.add_patch(rect_r1)
    ax.text(x_r1, y_top, "R1 = 2 Ω", color=color_txt, fontsize=9.5, ha="center", va="center", weight="bold")

    # 4. Resistencia R2 = 20 Ω (entre Nodo A y Tierra)
    y_r2 = (y_top + y_bot) / 2
    ax.plot([x_a, x_a], [y_top, y_r2 + 0.5], color=color_linea, lw=2.5)
    ax.plot([x_a, x_a], [y_r2 - 0.5, y_bot], color=color_linea, lw=2.5)
    rect_r2 = patches.Rectangle((x_a - 0.25, y_r2 - 0.5), 0.5, 1.0, facecolor="#2C2C2E", edgecolor="#AEAEB2", lw=1.5)
    ax.add_patch(rect_r2)
    ax.text(x_a, y_r2, "R2\n20 Ω", color=color_txt, fontsize=9, ha="center", va="center", weight="bold")

    # 5. Resistencia variable R3 (entre Nodo A y Nodo B) con corriente iphi
    x_r3 = (x_a + x_b) / 2
    ax.plot([x_a, x_r3 - 0.65], [y_top, y_top], color=color_linea, lw=2.5)
    ax.plot([x_r3 + 0.65, x_b], [y_top, y_top], color=color_linea, lw=2.5)
    rect_r3 = patches.Rectangle((x_r3 - 0.65, y_top - 0.24), 1.3, 0.48, facecolor="#1E3A5F", edgecolor="#0A84FF", lw=2)
    ax.add_patch(rect_r3)
    ax.text(x_r3, y_top, f"R3 = {r3:.1f} Ω", color="#64D2FF", fontsize=9.5, ha="center", va="center", weight="bold")

    # Flecha y etiqueta de corriente iphi debajo de R3
    txt_iphi = "-- A" if error else f"{iphi:.4f} A"
    ax.annotate(
        "",
        xy=(x_r3 + 0.4, y_top - 0.45),
        xytext=(x_r3 - 0.4, y_top - 0.45),
        arrowprops=dict(arrowstyle="->", color="#30D158", lw=2),
    )
    ax.text(x_r3, y_top - 0.68, f"iϕ = {txt_iphi}", color="#30D158", fontsize=9.5, ha="center", va="center", weight="bold")

    # 6. Resistencia R4 = 10 Ω (entre Nodo B y Tierra)
    y_r4 = (y_top + y_bot) / 2
    ax.plot([x_b, x_b], [y_top, y_r4 + 0.5], color=color_linea, lw=2.5)
    ax.plot([x_b, x_b], [y_r4 - 0.5, y_bot], color=color_linea, lw=2.5)
    rect_r4 = patches.Rectangle((x_b - 0.25, y_r4 - 0.5), 0.5, 1.0, facecolor="#2C2C2E", edgecolor="#AEAEB2", lw=1.5)
    ax.add_patch(rect_r4)
    ax.text(x_b, y_r4, "R4\n10 Ω", color=color_txt, fontsize=9, ha="center", va="center", weight="bold")

    # 7. Resistencia R5 = 2 Ω (entre Nodo B y Nodo C)
    x_r5 = (x_b + x_c) / 2
    ax.plot([x_b, x_r5 - 0.55], [y_top, y_top], color=color_linea, lw=2.5)
    ax.plot([x_r5 + 0.55, x_c], [y_top, y_top], color=color_linea, lw=2.5)
    rect_r5 = patches.Rectangle((x_r5 - 0.55, y_top - 0.22), 1.1, 0.44, facecolor="#2C2C2E", edgecolor="#AEAEB2", lw=1.5)
    ax.add_patch(rect_r5)
    ax.text(x_r5, y_top, "R5 = 2 Ω", color=color_txt, fontsize=9.5, ha="center", va="center", weight="bold")

    # 8. Fuente dependiente de voltaje VC = k * iphi (diamante)
    y_vc = (y_top + y_bot) / 2
    ax.plot([x_c, x_c], [y_top, y_vc + 0.45], color=color_linea, lw=2.5)
    ax.plot([x_c, x_c], [y_vc - 0.45, y_bot], color=color_linea, lw=2.5)
    diam = patches.Polygon(
        [[x_c, y_vc + 0.45], [x_c + 0.42, y_vc], [x_c, y_vc - 0.45], [x_c - 0.42, y_vc]],
        facecolor="#3A2E1E",
        edgecolor="#FF9F0A",
        lw=2,
    )
    ax.add_patch(diam)
    ax.text(x_c, y_vc + 0.08, "k·iϕ", color="#FFD60A", fontsize=9.5, ha="center", va="center", weight="bold")
    ax.text(x_c, y_vc - 0.18, f"k={k:.1f}", color="#AEAEB2", fontsize=8, ha="center", va="center")

    # 9. Badges de voltajes nodales (VA, VB, VC)
    # Nodo A
    ax.plot(x_a, y_top, "o", color="#0A84FF", ms=8, zorder=5)
    txt_va = "-- V" if error else f"{va:.3f} V"
    ax.text(
        x_a, y_top + 0.65,
        f"Nodo A\nVA = {txt_va}",
        color="#64D2FF",
        fontsize=10,
        ha="center",
        va="center",
        weight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#1C2C3E", edgecolor="#0A84FF", lw=1.5),
    )

    # Nodo B
    ax.plot(x_b, y_top, "o", color="#FF9F0A", ms=8, zorder=5)
    txt_vb = "-- V" if error else f"{vb:.3f} V"
    ax.text(
        x_b, y_top + 0.65,
        f"Nodo B\nVB = {txt_vb}",
        color="#FFD60A",
        fontsize=10,
        ha="center",
        va="center",
        weight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#3A2E1E", edgecolor="#FF9F0A", lw=1.5),
    )

    # Nodo C
    ax.plot(x_c, y_top, "o", color="#BF5AF2", ms=8, zorder=5)
    txt_vc = "-- V" if error else f"{vc:.3f} V"
    ax.text(
        x_c, y_top + 0.65,
        f"Nodo C\nVC = {txt_vc}",
        color="#DA8FFF",
        fontsize=10,
        ha="center",
        va="center",
        weight="bold",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#2E1C3E", edgecolor="#BF5AF2", lw=1.5),
    )

    # Encabezados
    estado_str = "⚠ SISTEMA SINGULAR (det(G)=0)" if error else f"Entradas: R3 = {r3:.1f} Ω  |  k = {k:.1f} Ω"
    color_tit = "#FF453A" if error else "#0A84FF"
    ax.text(
        (x_vs + x_c) / 2, 4.25,
        "CIRCUITO DC CON FUENTE DEPENDIENTE (FASE 3 - G01T)",
        color="#FFFFFF",
        fontsize=12,
        ha="center",
        weight="bold",
    )
    ax.text(
        (x_vs + x_c) / 2, 3.9,
        estado_str,
        color=color_tit,
        fontsize=10.5,
        ha="center",
        weight="bold",
    )

    ax.set_xlim(0.2, 9.1)
    ax.set_ylim(0.0, 4.6)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(ruta_salida, dpi=150, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    return ruta_salida


def abrir_diagrama_en_visor(r3, k, va, vb, vc, iphi, error=False):
    """Genera la imagen y la abre en el visor predeterminado del sistema operativo."""
    ruta = generar_diagrama_circuito(r3=r3, k=k, va=va, vb=vb, vc=vc, iphi=iphi, error=error)
    if sys.platform == "win32":
        os.startfile(ruta)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", ruta])
    else:
        subprocess.Popen(["xdg-open", ruta])
