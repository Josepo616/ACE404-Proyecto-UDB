"""
graficos.py - Fachada de compatibilidad para el módulo de visualización y comparación (ui.graficos).
Autor: Bryan Steven Cornejo Zavala (Equipo G01T - ACE941 / ACE404)

Permite importar las funciones de gráficos y tabla comparativa desde la raíz del proyecto
o ejecutar directamente `python graficos.py` para imprimir la tabla comparativa y generar
la imagen de gráficos en alta resolución.
"""

from ui.graficos import (
    DATOS_REFERENCIA_NOMINALES,
    PanelGraficos,
    abrir_graficos_en_visor,
    abrir_tabla_en_visor,
    abrir_ventana_tabla_comparativa,
    calcular_curva_iphi_vs_k,
    calcular_k_singular,
    construir_tabla_comparativa,
    dibujar_graficos_en_figura,
    explicacion_error_cero,
    formatear_tabla_comparativa_texto,
    generar_graficos_circuito,
    solucion_teorica_exacta,
)

__all__ = [
    "DATOS_REFERENCIA_NOMINALES",
    "PanelGraficos",
    "abrir_graficos_en_visor",
    "abrir_tabla_en_visor",
    "abrir_ventana_tabla_comparativa",
    "calcular_curva_iphi_vs_k",
    "calcular_k_singular",
    "construir_tabla_comparativa",
    "dibujar_graficos_en_figura",
    "explicacion_error_cero",
    "formatear_tabla_comparativa_texto",
    "generar_graficos_circuito",
    "solucion_teorica_exacta",
]

if __name__ == "__main__":
    print(formatear_tabla_comparativa_texto())
    ruta = generar_graficos_circuito()
    print(f"Gráficos generados exitosamente en: {ruta}")
