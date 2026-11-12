# Simulador — DC Circuit Analysis (ACE941 / ACE404)

Simulador de circuitos en corriente directa (análisis nodal y de mallas) desarrollado en Python para el proyecto de cátedra (Fase 3) - Universidad Don Bosco, Ciclo 2, 2026.

## Equipo de Trabajo (G01T)
* **Katherine Gissell García Sánchez:** Núcleo de cálculo y validaciones matemáticas (`modelo.py`).
* **José Rolando Álvarez Mejía:** Arquitectura y desarrollo Frontend UI/UX (paquete modular `ui/`, `main.py`, `test_interfaz.py`).
* **Bryan Steven Cornejo Zavala:** Visualización de datos, gráficos en tiempo real con `matplotlib` y análisis comparativo Teoría vs. Python vs. MATLAB vs. LTspice (`ui/graficos.py`, `graficos.py`, `test_graficos.py`).
* **Carlos Francisco Peña Herrera:** Módulos de exportación CSV/PDF (`exportar.py`, `test_exportar.py`) y verificación con LTspice y MATLAB/GNU Octave (`simulaciones/`).
* **Kevin Adonay Martinez Ceron:** Integración del sistema, testing y aseguramiento de calidad.

## Funcionalidades Principales
* **Análisis nodal y por mallas:** Resolución exacta del sistema de ecuaciones y validación cruzada.
* **Mapa de calor nodal:** Visualización gráfica con gradiente térmico de los potenciales $V_A$, $V_B$, $V_C$ y tierra.
* **Controles What-If interactivos:** Sliders y campos numéricos para exploración dinámica de $R_3$ y $k$.
* **Monitor de balance energético en tiempo real:** Verificación automática de la conservación de energía ($P_{\text{gen}} = P_{\text{abs}}$) y desglose por componentes.
* **Procedimiento paso a paso:** Desglose completo de ecuaciones LCK, matrices $G$ y $R_m$, determinantes y solución con opción de copiado.
* **Visualización de datos y gráficos:** Gráficos de barras para potencias y curvas paramétricas $i_\phi$ vs $k$.
* **Detección y manejo de singularidad:** Identificación de matrices singulares (ej. $k \approx -10.1818\,\Omega$) y entradas no físicas.
* **Exportación de resultados:** Tabla de resultados en CSV (compatible con Excel) y reporte PDF con datos, resultados, esquemático, gráficos, procedimiento paso a paso y tabla comparativa.

## Instalación y Ejecución

1. **Crear y activar el entorno virtual:**

   * **macOS / Linux:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   * **Windows** (CMD / PowerShell):
     ```cmd
     python -m venv venv
     venv\Scripts\activate
     ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar el simulador:**
   ```bash
   python main.py
   ```

4. **Ejecutar la suite de pruebas:**
   ```bash
   python test_modelo.py     # Pruebas del núcleo matemático (8 pruebas)
   python test_interfaz.py   # Pruebas de integración UI/UX (7 pruebas)
   python test_graficos.py   # Pruebas de visualización y tabla comparativa (6 pruebas)
   python test_exportar.py   # Pruebas de exportación CSV y PDF (8 pruebas)
   ```

## Arquitectura del Frontend (`ui/`)
La interfaz de usuario sigue una arquitectura orientada a objetos modular:
* **`ui/app.py`:** Orquestador principal (`SimuladorApp`) que inicializa la ventana y coordina el ciclo de cálculo reactivo.
* **`ui/controles.py`:** Panel What-If con sliders continuos y botones de ajuste fino (◀ -1, +1 ▶) para $R_3$ y $k$.
* **`ui/metricas.py`:** Tarjetas de datos en tiempo real para voltajes nodales ($V_A, V_B, V_C$), corriente de control ($i_\phi$), verificación por mallas y balance de potencias.
* **`ui/acciones.py`:** Comandos rápidos para restablecer valores nominales, probar la singularidad del sistema, exportar el procedimiento, abrir gráficos HD y consultar la tabla comparativa.
* **`ui/esquema.py`:** Generador del diagrama esquemático del circuito en alta resolución con voltajes de nodo y parámetros en tiempo real para visualización nativa (Vista Previa / Visor de Fotos).
* **`ui/graficos.py`:** Panel interactivo con gráficos de `matplotlib` embebidos en la aplicación (`FigureCanvasTkAgg`) para el balance de potencia y la curva $i_\phi$ vs $k$, además de la tabla comparativa Teoría vs. Python vs. MATLAB vs. LTspice con análisis de porcentaje de error ($\approx 0\,\%$).
* **`ui/widgets.py`:** Control deslizante de alta visibilidad (`VisibleSlider`) implementado sobre `Canvas` para garantizar legibilidad en modo oscuro/claro en macOS y Windows.

