"""
exportar.py - Exportación de resultados del simulador a CSV y PDF (Fase 3).
Autor: Carlos Francisco Peña Herrera (Equipo G01T - ACE941 / ACE404)

Uso rápido:
    from modelo import resolver_circuito
    from exportar import exportar_csv, exportar_pdf

    res = resolver_circuito(R3=5, k=8)
    exportar_csv(res, "resultados.csv")    # tabla para Excel / Google Sheets
    exportar_pdf(res, "reporte.pdf")       # reporte completo con imágenes

El PDF incluye: datos del circuito, resultados, balance de potencia, esquemático
(ui/esquema.py), gráficos (ui/graficos.py), procedimiento paso a paso
(modelo.paso_a_paso) y la tabla comparativa Teoría vs. Python vs. MATLAB vs.
LTspice. Si el esquemático o los gráficos no se pueden generar, el reporte se
crea igual sin ellos.

Integración sugerida en ui/app.py (José / Kevin):
    from tkinter import filedialog
    from exportar import exportar_csv, exportar_pdf, nombre_sugerido

    def exportar_reporte_pdf(self):
        res = resolver_circuito(R3=r3_num, k=k_num)   # mismos valores que la interfaz
        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf", initialfile=nombre_sugerido("pdf"),
            filetypes=[("PDF", "*.pdf")])
        if ruta:
            exportar_pdf(res, ruta)

Dependencias: modelo.py y fpdf2 (pip install fpdf2). Para los símbolos Ω, ϕ y ·
se usa la fuente DejaVu que trae matplotlib; si no existe, se reemplazan por texto.
"""

import csv
import math
import os
import tempfile
from datetime import datetime

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from modelo import paso_a_paso

TITULO_REPORTE = "Reporte del Simulador de Circuitos DC"
SUBTITULO_REPORTE = "Análisis de Circuitos Eléctricos (ACE941) · Universidad Don Bosco · Equipo G01T"

COLUMNAS_CSV = ["Seccion", "Variable", "Descripcion", "Valor", "Unidad"]

# Reemplazos para cuando no hay fuente Unicode disponible (fuentes base del PDF).
_REEMPLAZOS_LATIN1 = {
    "Ω": "Ohm", "ϕ": "phi", "φ": "phi", "·": "*", "≈": "~", "≤": "<=", "≥": ">=",
    "→": "->", "–": "-", "—": "-", "⚠": "!", "²": "^2", "₁": "1", "₂": "2", "₃": "3",
}


# ---------------------------------------------------------------------------
# 1. Tabla de resultados (base común para CSV y PDF)
# ---------------------------------------------------------------------------
def _es_numero_valido(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool) and math.isfinite(valor)


def tabla_resultados(res):
    """
    Convierte el diccionario de resolver_circuito() en filas:
        (seccion, variable, descripcion, valor, unidad)

    'valor' es float para datos numéricos o str para estados (Sí/No, mensajes).
    Funciona también cuando hay error: devuelve las entradas (si existen) y el estado.
    """
    filas = []
    e = res.get("entradas")

    if e:
        filas.append(("Entradas", "Vs", "Fuente independiente", e["Vs"], "V"))
        for n in range(1, 6):
            filas.append(("Entradas", f"R{n}", f"Resistencia R{n}", e[f"R{n}"], "Ω"))
        filas.append(("Entradas", "k", "Ganancia de la fuente dependiente (VC = k·iϕ)", e["k"], "Ω"))

    if res.get("error"):
        estado = "Matriz singular" if res.get("matriz_singular") else "Entrada inválida"
        filas.append(("Estado", "estado", estado, res["error"], ""))
        if _es_numero_valido(res.get("det_G")):
            filas.append(("Diagnóstico", "det_G", "Determinante de G", res["det_G"], ""))
        return filas

    filas.append(("Estado", "estado", "Resultado", "Solución única", ""))

    filas += [
        ("Voltajes", "VA", "Voltaje en el nodo A", res["VA"], "V"),
        ("Voltajes", "VB", "Voltaje en el nodo B", res["VB"], "V"),
        ("Voltajes", "VC", "Voltaje de la fuente dependiente (k·iϕ)", res["VC"], "V"),
    ]

    c = res["corrientes"]
    filas += [
        ("Corrientes", "iphi", "Corriente de control iϕ (R3, de A a B)", c["iphi"], "A"),
        ("Corrientes", "i1", "Corriente en R1 (malla 1)", c["i1"], "A"),
        ("Corrientes", "i_R2", "Corriente en R2", c["i_R2"], "A"),
        ("Corrientes", "i_R4", "Corriente en R4", c["i_R4"], "A"),
        ("Corrientes", "i3", "Corriente en R5 (malla 3)", c["i3"], "A"),
    ]
    for n, i in enumerate(res["mallas"], start=1):
        filas.append(("Mallas", f"I{n}", f"Corriente de malla {n} (verificación)", i, "A"))

    for n, p in enumerate(res["potencias_resistencias"], start=1):
        filas.append(("Potencias", f"P_R{n}", f"Potencia disipada en R{n}", p, "W"))
    filas += [
        ("Potencias", "P_fuente", "Potencia entregada por Vs", res["P_fuente"], "W"),
        ("Potencias", "P_dependiente", "Potencia absorbida por la fuente dependiente", res["P_dependiente"], "W"),
        ("Potencias", "P_generada", "Potencia total generada", res["P_generada"], "W"),
        ("Potencias", "P_absorbida", "Potencia total absorbida", res["P_absorbida"], "W"),
    ]

    filas += [
        ("Diagnóstico", "balance_ok", "Se conserva la energía", "Sí" if res["balance_ok"] else "No", ""),
        ("Diagnóstico", "coincide_nodal_mallas", "Nodos y mallas coinciden",
         "Sí" if res["coincide_nodal_mallas"] else "No", ""),
        ("Diagnóstico", "det_G", "Determinante de G", res["det_G"], ""),
        ("Diagnóstico", "cond_G", "Número de condición de G", res["cond_G"], ""),
        ("Diagnóstico", "residuo", "Residuo ||G·V - I||", res["residuo"], ""),
    ]
    return filas


def _formatear(valor, decimales=4):
    """Formato legible para el PDF (notación científica en valores muy pequeños)."""
    if not _es_numero_valido(valor):
        return str(valor)
    if valor != 0 and abs(valor) < 10 ** (-decimales):
        return f"{valor:.2e}"
    return f"{valor:.{decimales}f}"


def nombre_sugerido(extension="pdf"):
    """Nombre de archivo con fecha y hora, p. ej. reporte_circuito_2026-11-12_2130.pdf"""
    return f"reporte_circuito_{datetime.now():%Y-%m-%d_%H%M}.{extension.lstrip('.')}"


# ---------------------------------------------------------------------------
# 2. Exportación CSV
# ---------------------------------------------------------------------------
def exportar_csv(res, ruta):
    """
    Guarda los resultados en un CSV (UTF-8 con BOM, para que Excel muestre Ω y ϕ).
    Los números se guardan con 10 cifras significativas y punto decimal.
    Devuelve la ruta del archivo.
    """
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f)
        escritor.writerow(COLUMNAS_CSV)
        for seccion, variable, descripcion, valor, unidad in tabla_resultados(res):
            if _es_numero_valido(valor):
                valor = f"{valor:.10g}"
            escritor.writerow([seccion, variable, descripcion, valor, unidad])
    return ruta


# ---------------------------------------------------------------------------
# 3. Exportación PDF
# ---------------------------------------------------------------------------
def _ruta_fuente_dejavu(nombre):
    """Busca una fuente DejaVu dentro de la instalación de matplotlib."""
    try:
        import matplotlib

        ruta = os.path.join(matplotlib.get_data_path(), "fonts", "ttf", nombre)
        return ruta if os.path.isfile(ruta) else None
    except ImportError:
        return None


def _texto_seguro(texto):
    """Reemplaza símbolos que no existen en las fuentes base del PDF (Latin-1)."""
    for original, reemplazo in _REEMPLAZOS_LATIN1.items():
        texto = texto.replace(original, reemplazo)
    return texto.encode("latin-1", errors="replace").decode("latin-1")


class _ReportePDF(FPDF):
    """PDF A4 con encabezado y pie de página del equipo."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=18)
        self.unicode = self._registrar_fuentes()
        self.fuente = "DejaVu" if self.unicode else "helvetica"
        self.fuente_mono = "DejaVuMono" if self.unicode else "courier"

    def _registrar_fuentes(self):
        normal = _ruta_fuente_dejavu("DejaVuSans.ttf")
        negrita = _ruta_fuente_dejavu("DejaVuSans-Bold.ttf")
        mono = _ruta_fuente_dejavu("DejaVuSansMono.ttf")
        if not (normal and negrita and mono):
            return False
        self.add_font("DejaVu", "", normal)
        self.add_font("DejaVu", "B", negrita)
        self.add_font("DejaVuMono", "", mono)
        return True

    def texto(self, t):
        return t if self.unicode else _texto_seguro(t)

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font(self.fuente, "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, self.texto(TITULO_REPORTE + " · Fase 3"), align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font(self.fuente, "", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, self.texto(f"ACE941 · G01T · Página {self.page_no()}/{{nb}}"), align="C")

    def titulo_seccion(self, t, espacio_minimo=30):
        """Título de sección; salta de página si no cabe al menos espacio_minimo (mm)."""
        if self.get_y() + espacio_minimo > self.h - self.b_margin:
            self.add_page()
        self.ln(3)
        self.set_font(self.fuente, "B", 12)
        self.set_text_color(10, 70, 140)
        self.cell(0, 8, self.texto(t), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(10, 132, 255)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def parrafo(self, t, tam=10):
        self.set_font(self.fuente, "", tam)
        self.multi_cell(0, 5, self.texto(t), align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def tabla(self, filas, anchos, alinear=None):
        """Tabla con encabezado (primera fila) usando fpdf2 >= 2.7."""
        self.set_font(self.fuente, "", 8.5)
        with super().table(col_widths=anchos, text_align=alinear or "LEFT",
                           line_height=5, padding=(0.8, 1),
                           headings_style=self._estilo_encabezado()) as t:
            for fila in filas:
                r = t.row()
                for celda in fila:
                    r.cell(self.texto(str(celda)))
        self.ln(2)

    def _estilo_encabezado(self):
        from fpdf.fonts import FontFace

        return FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=(10, 70, 140))

    def imagen(self, ruta, titulo="", ancho=180):
        """Inserta una imagen centrada con su título, sin separarlos entre páginas."""
        from PIL import Image

        with Image.open(ruta) as im:
            alto = ancho * im.height / im.width
        if self.get_y() + alto + 8 > self.h - self.b_margin:
            self.add_page()
        if titulo:
            self.parrafo(titulo, tam=9.5)
        self.image(ruta, x=(self.w - ancho) / 2, w=ancho)
        self.ln(3)


def _generar_imagenes(res, carpeta):
    """
    Genera el esquemático y los gráficos con los módulos de la interfaz.
    Devuelve una lista de (titulo, ruta). Si algo falla, se omite esa imagen.
    """
    e = res.get("entradas") or {}
    r3, k = e.get("R3", 5.0), e.get("k", 8.0)
    error = bool(res.get("error"))

    def valor(clave):
        v = res.get(clave)
        return v if _es_numero_valido(v) else 0.0

    imagenes = []
    try:
        from ui.esquema import generar_diagrama_circuito

        ruta = generar_diagrama_circuito(
            r3=r3, k=k, va=valor("VA"), vb=valor("VB"), vc=valor("VC"), iphi=valor("iphi"),
            error=error, ruta_salida=os.path.join(carpeta, "esquema.png"),
        )
        imagenes.append(("Diagrama esquemático", ruta))
    except Exception:  # la interfaz no está disponible: el reporte sigue sin imagen
        pass

    try:
        from ui.graficos import generar_graficos_circuito

        ruta = generar_graficos_circuito(
            r3=r3, k=k, res=res, ruta_salida=os.path.join(carpeta, "graficos.png"),
        )
        imagenes.append(("Balance de potencia y curva iϕ vs k", ruta))
    except Exception:
        pass
    return imagenes


def _tabla_comparativa():
    """Tabla de Bryan (ui/graficos.py). Devuelve None si no está disponible."""
    try:
        from ui.graficos import construir_tabla_comparativa

        return construir_tabla_comparativa()
    except Exception:
        return None


def exportar_pdf(res, ruta, incluir_imagenes=True, incluir_comparativa=True):
    """
    Genera un reporte PDF con los resultados de resolver_circuito().
    Funciona también con resultados de error (entrada inválida o matriz singular).
    Devuelve la ruta del archivo.
    """
    pdf = _ReportePDF()
    pdf.set_title(TITULO_REPORTE)
    pdf.set_author("Equipo G01T - ACE941 / ACE404")
    pdf.add_page()

    # --- Portada / encabezado ---
    pdf.set_font(pdf.fuente, "B", 16)
    pdf.set_text_color(10, 70, 140)
    pdf.cell(0, 9, pdf.texto(TITULO_REPORTE), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font(pdf.fuente, "", 9.5)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 5, pdf.texto(SUBTITULO_REPORTE), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 5, pdf.texto(f"Generado: {datetime.now():%d/%m/%Y %H:%M}"),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)

    filas = tabla_resultados(res)
    entradas = [f for f in filas if f[0] == "Entradas"]
    resultados = [f for f in filas if f[0] not in ("Entradas", "Estado")]

    # --- 1. Datos del circuito ---
    pdf.titulo_seccion("1. Datos del circuito")
    pdf.parrafo("Circuito patrón: Vs - R1 - nodo A - R3 - nodo B - R5 - nodo C, con R2 y R4 a tierra "
                "y una fuente de voltaje dependiente VC = k·iϕ, donde iϕ es la corriente por R3 de A hacia B.")
    pdf.ln(1)
    if entradas:
        pdf.tabla([("Parámetro", "Descripción", "Valor", "Unidad")]
                  + [(v, d, _formatear(x, 2), u) for _, v, d, x, u in entradas],
                  anchos=(25, 105, 30, 20))

    # --- 2. Estado de la solución ---
    pdf.titulo_seccion("2. Estado de la solución")
    if res.get("error"):
        pdf.set_text_color(200, 40, 40)
        pdf.parrafo(res["error"], tam=10.5)
        pdf.set_text_color(0, 0, 0)
    else:
        pdf.parrafo(f"El sistema tiene solución única (det(G) = {res['det_G']:.4f}, "
                    f"cond(G) = {res['cond_G']:.4f}). "
                    f"Balance de potencia: generada {res['P_generada']:.4f} W = "
                    f"absorbida {res['P_absorbida']:.4f} W "
                    f"({'se conserva' if res['balance_ok'] else 'NO se conserva'} la energía). "
                    f"Nodos y mallas {'coinciden' if res['coincide_nodal_mallas'] else 'NO coinciden'}.")

    # --- 3. Resultados ---
    if resultados:
        pdf.titulo_seccion("3. Resultados")
        pdf.tabla([("Sección", "Variable", "Descripción", "Valor", "Unidad")]
                  + [(s, v, d, _formatear(x), u) for s, v, d, x, u in resultados],
                  anchos=(25, 30, 85, 25, 15))

    # --- 4. Esquemático y gráficos ---
    if incluir_imagenes:
        with tempfile.TemporaryDirectory() as carpeta:
            imagenes = _generar_imagenes(res, carpeta)
            if imagenes:
                pdf.titulo_seccion("4. Esquemático y gráficos")
                for titulo, ruta_img in imagenes:
                    pdf.imagen(ruta_img, titulo=titulo, ancho=170)

    # --- 5. Procedimiento paso a paso ---
    e = res.get("entradas")
    if e:
        pdf.add_page()
        pdf.titulo_seccion("5. Procedimiento paso a paso")
        pdf.set_font(pdf.fuente_mono, "", 8)
        pdf.multi_cell(0, 4, pdf.texto(paso_a_paso(**e)), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # --- 6. Validación con otras herramientas ---
    comparativa = _tabla_comparativa() if incluir_comparativa else None
    if comparativa:
        pdf.titulo_seccion("6. Validación: Teoría vs. Python vs. MATLAB vs. LTspice", espacio_minimo=110)
        pdf.parrafo("Valores nominales (R3 = 5 Ω, k = 8 Ω). Archivos de respaldo en simulaciones/ltspice "
                    "y simulaciones/octave.", tam=9)
        pdf.ln(1)
        pdf.tabla(
            [("Variable", "Teoría", "Python", "MATLAB", "LTspice", "Error LTspice %")]
            + [(f["variable"], _formatear(f["teoria"]), _formatear(f["python"]),
                _formatear(f["matlab"]), _formatear(f["ltspice"]),
                f"{f['error_pct_ltspice']:.2e}") for f in comparativa],
            anchos=(30, 28, 28, 28, 28, 38),
        )

    pdf.output(ruta)
    return ruta


if __name__ == "__main__":
    from modelo import resolver_circuito

    resultado = resolver_circuito()
    print("CSV:", exportar_csv(resultado, nombre_sugerido("csv")))
    print("PDF:", exportar_pdf(resultado, nombre_sugerido("pdf")))
