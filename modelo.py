"""
modelo.py - Núcleo de cálculo del simulador de circuitos DC (Fase 3, G01T).

Circuito patrón (Fase 1 y 2):
    Vs --R1-- A --R3-- B --R5-- C
              |        |        |
              R2       R4      fuente dependiente VC = k * iphi
              |        |        |
    tierra ---+--------+--------+

    iphi es la corriente por R3, de A hacia B.

Uso rápido:
    from modelo import resolver_circuito, paso_a_paso

    r = resolver_circuito()            # valores nominales
    r = resolver_circuito(R3=8, k=4)   # modo "what-if"
    if r["error"]:
        print(r["error"])              # entrada inválida o matriz singular
    else:
        print(r["VA"], r["VB"], r["iphi"])

    print(paso_a_paso())               # texto con ecuaciones, matrices y solución

Este módulo no importa nada de la interfaz: solo necesita NumPy.
"""

import math

import numpy as np

# Valores nominales del circuito de la Fase 1.
NOMINALES = {"Vs": 20.0, "R1": 2.0, "R2": 20.0, "R3": 5.0, "R4": 10.0, "R5": 2.0, "k": 8.0}

# Si el número de condición supera este límite, la matriz se trata como singular.
LIMITE_CONDICION = 1e12

NAN = float("nan")


# ---------------------------------------------------------------------------
# 1. Validación de entradas
# ---------------------------------------------------------------------------
def validar_entradas(Vs=20.0, R1=2.0, R2=20.0, R3=5.0, R4=10.0, R5=2.0, k=8.0):
    """
    Convierte las entradas a float y verifica que tengan sentido físico.

    Acepta números o texto (por ejemplo "4.7" o "4,7", como llega de un campo
    de la interfaz). Devuelve un diccionario con los siete valores en float.
    Lanza ValueError con un mensaje en español si algo está mal.
    """
    crudos = {"Vs": Vs, "R1": R1, "R2": R2, "R3": R3, "R4": R4, "R5": R5, "k": k}
    limpios = {}

    for nombre, valor in crudos.items():
        if isinstance(valor, bool):
            raise ValueError(f"{nombre} debe ser un número.")
        if isinstance(valor, str):
            valor = valor.strip().replace(",", ".")
            if valor == "":
                raise ValueError(f"{nombre} está vacío.")
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            raise ValueError(f"{nombre} debe ser un número (se recibió: {valor!r}).") from None
        if not math.isfinite(numero):
            raise ValueError(f"{nombre} debe ser un número finito.")
        if nombre.startswith("R") and numero <= 0:
            raise ValueError(f"{nombre} debe ser mayor que 0 Ω (se recibió: {numero:g}).")
        limpios[nombre] = numero

    return limpios


# ---------------------------------------------------------------------------
# 2. Construcción de las matrices
# ---------------------------------------------------------------------------
def construir_sistema_nodal(Vs, R1, R2, R3, R4, R5, k):
    """
    Devuelve (G, I) del sistema nodal G · [VA, VB] = I.

    Nodo A: (1/R1 + 1/R2 + 1/R3)·VA - (1/R3)·VB = Vs/R1
    Nodo B: -(1/R3 + k/(R3·R5))·VA + (1/R3 + 1/R4 + 1/R5 + k/(R3·R5))·VB = 0
    """
    acople = k / (R3 * R5)  # término que introduce la fuente dependiente
    G = np.array(
        [
            [1 / R1 + 1 / R2 + 1 / R3, -1 / R3],
            [-1 / R3 - acople, 1 / R3 + 1 / R4 + 1 / R5 + acople],
        ],
        dtype=np.float64,
    )
    I = np.array([Vs / R1, 0.0], dtype=np.float64)
    return G, I


def construir_sistema_mallas(Vs, R1, R2, R3, R4, R5, k):
    """
    Devuelve (Rm, E) del sistema de mallas Rm · [i1, i2, i3] = E.

    Malla 1: (R1 + R2)·i1 - R2·i2 = Vs
    Malla 2: -R2·i1 + (R2 + R3 + R4)·i2 - R4·i3 = 0
    Malla 3: (k - R4)·i2 + (R4 + R5)·i3 = 0        (iphi = i2)
    """
    Rm = np.array(
        [
            [R1 + R2, -R2, 0.0],
            [-R2, R2 + R3 + R4, -R4],
            [0.0, k - R4, R4 + R5],
        ],
        dtype=np.float64,
    )
    E = np.array([Vs, 0.0, 0.0], dtype=np.float64)
    return Rm, E


def _resolver_sistema(A, b):
    """Resuelve A·x = b. Lanza LinAlgError si A es singular o casi singular."""
    if np.linalg.cond(A) > LIMITE_CONDICION:
        raise np.linalg.LinAlgError("matriz singular o mal condicionada")
    return np.linalg.solve(A, b)


# ---------------------------------------------------------------------------
# 3. Función principal
# ---------------------------------------------------------------------------
def _resultado_vacio(mensaje, singular):
    """Diccionario con las mismas claves de siempre, para los casos de error."""
    return {
        "VA": NAN,
        "VB": NAN,
        "iphi": NAN,
        "P_generada": NAN,
        "P_absorbida": NAN,
        "potencias_resistencias": [NAN] * 5,
        "matriz_singular": singular,
        "error": mensaje,
        "VC": NAN,
        "corrientes": {"i1": NAN, "i_R2": NAN, "iphi": NAN, "i_R4": NAN, "i3": NAN},
        "P_fuente": NAN,
        "P_dependiente": NAN,
        "mallas": [NAN] * 3,
        "balance_ok": False,
        "coincide_nodal_mallas": False,
        "det_G": NAN,
        "cond_G": NAN,
        "residuo": NAN,
        "entradas": None,
    }


def resolver_circuito(Vs=20.0, R1=2.0, R2=20.0, R3=5.0, R4=10.0, R5=2.0, k=8.0):
    """
    Resuelve el circuito por análisis nodal y lo verifica por mallas.

    Nunca lanza excepciones: siempre devuelve un diccionario con las mismas
    claves. Si la entrada es inválida o la matriz es singular, "error" trae el
    mensaje y los valores numéricos quedan en NaN.

    Claves del contrato del equipo:
        VA, VB                  voltajes de nodo (V)
        iphi                    corriente de control por R3 (A)
        P_generada              potencia entregada por las fuentes (W)
        P_absorbida             potencia absorbida total (W)
        potencias_resistencias  [P_R1, P_R2, P_R3, P_R4, P_R5] (W)
        matriz_singular         True si el sistema no tiene solución única

    Claves adicionales:
        error                   None si todo salió bien; texto si no
        VC                      voltaje de la fuente dependiente (V)
        corrientes              dict con i1, i_R2, iphi, i_R4, i3 (A)
        P_fuente                potencia que entrega Vs (W); negativa si absorbe
        P_dependiente           potencia que absorbe la fuente dependiente (W);
                                negativa si entrega
        mallas                  [i1, i2, i3] del análisis de mallas (A)
        balance_ok              True si P_generada == P_absorbida
        coincide_nodal_mallas   True si ambos métodos dan lo mismo
        det_G, cond_G, residuo  diagnóstico numérico del sistema nodal
        entradas                dict con los valores usados, ya validados
    """
    try:
        e = validar_entradas(Vs, R1, R2, R3, R4, R5, k)
    except ValueError as err:
        return _resultado_vacio(str(err), singular=False)

    G, I = construir_sistema_nodal(**e)
    Rm, E = construir_sistema_mallas(**e)

    try:
        V = _resolver_sistema(G, I)
        im = _resolver_sistema(Rm, E)
    except np.linalg.LinAlgError:
        vacio = _resultado_vacio(
            "La matriz del sistema es singular: con estos valores el circuito "
            "no tiene solución única. Prueba con otro valor de k o de las resistencias.",
            singular=True,
        )
        vacio["entradas"] = e
        vacio["det_G"] = float(np.linalg.det(G))
        return vacio

    VA, VB = float(V[0]), float(V[1])

    # Corrientes de rama y fuente dependiente
    iphi = (VA - VB) / e["R3"]
    VC = e["k"] * iphi
    i1 = (e["Vs"] - VA) / e["R1"]
    i_R2 = VA / e["R2"]
    i_R4 = VB / e["R4"]
    i3 = (VB - VC) / e["R5"]

    # Potencias
    potencias_resistencias = [
        i1**2 * e["R1"],
        VA**2 / e["R2"],
        iphi**2 * e["R3"],
        VB**2 / e["R4"],
        i3**2 * e["R5"],
    ]
    P_fuente = e["Vs"] * i1  # entregada por Vs
    P_dependiente = VC * i3  # absorbida por la fuente dependiente

    # Cada fuente puede entregar o absorber según los valores del circuito.
    P_generada = max(P_fuente, 0.0) + max(-P_dependiente, 0.0)
    P_absorbida = sum(potencias_resistencias) + max(-P_fuente, 0.0) + max(P_dependiente, 0.0)

    escala = max(1.0, abs(P_generada), abs(P_absorbida))
    balance_ok = abs(P_generada - P_absorbida) <= 1e-9 * escala

    mallas = [float(x) for x in im]
    coincide = bool(np.allclose([i1, iphi, i3], mallas, rtol=1e-9, atol=1e-9))

    return {
        "VA": VA,
        "VB": VB,
        "iphi": iphi,
        "P_generada": P_generada,
        "P_absorbida": P_absorbida,
        "potencias_resistencias": potencias_resistencias,
        "matriz_singular": False,
        "error": None,
        "VC": VC,
        "corrientes": {"i1": i1, "i_R2": i_R2, "iphi": iphi, "i_R4": i_R4, "i3": i3},
        "P_fuente": P_fuente,
        "P_dependiente": P_dependiente,
        "mallas": mallas,
        "balance_ok": bool(balance_ok),
        "coincide_nodal_mallas": coincide,
        "det_G": float(np.linalg.det(G)),
        "cond_G": float(np.linalg.cond(G)),
        "residuo": float(np.linalg.norm(G @ V - I)),
        "entradas": e,
    }


# ---------------------------------------------------------------------------
# 4. Modo "paso a paso"
# ---------------------------------------------------------------------------
def _matriz_a_texto(M, sangria="    "):
    filas = ["[" + "  ".join(f"{x:10.4f}" for x in fila) + " ]" for fila in np.atleast_2d(M)]
    return "\n".join(sangria + f for f in filas)


def paso_a_paso(Vs=20.0, R1=2.0, R2=20.0, R3=5.0, R4=10.0, R5=2.0, k=8.0):
    """
    Devuelve un texto (str) con el procedimiento completo: ecuaciones LCK,
    matriz, determinante, solución, verificación por mallas y balance.
    Pensado para mostrarse en una caja de texto con fuente monoespaciada.
    """
    r = resolver_circuito(Vs, R1, R2, R3, R4, R5, k)
    e = r["entradas"]

    if e is None:  # entrada inválida
        return f"No se puede resolver el circuito.\n{r['error']}"

    G, I = construir_sistema_nodal(**e)
    Rm, E = construir_sistema_mallas(**e)

    L = []
    L.append("PASO 1. Datos del circuito")
    L.append(f"    Vs = {e['Vs']:g} V    k = {e['k']:g} Ω")
    L.append("    " + "    ".join(f"R{n} = {e[f'R{n}']:g} Ω" for n in range(1, 6)))
    L.append("")
    L.append("PASO 2. Ecuaciones LCK (corrientes que salen de cada nodo = 0)")
    L.append(f"    Nodo A: (VA - {e['Vs']:g})/{e['R1']:g} + VA/{e['R2']:g} + (VA - VB)/{e['R3']:g} = 0")
    L.append(f"    Nodo B: (VB - VA)/{e['R3']:g} + VB/{e['R4']:g} + (VB - VC)/{e['R5']:g} = 0")
    L.append(f"    Fuente dependiente: VC = k·iphi = {e['k']:g}·(VA - VB)/{e['R3']:g}")
    L.append("")
    L.append("PASO 3. Forma matricial G · [VA, VB] = I")
    L.append("    G =")
    L.append(_matriz_a_texto(G, "    "))
    L.append(f"    I = [ {I[0]:.4f}  {I[1]:.4f} ]")
    L.append("")
    L.append("PASO 4. Determinante")
    L.append(f"    det(G) = {r['det_G']:.6g}")

    if r["matriz_singular"]:
        L.append("    El determinante es (prácticamente) cero: la matriz es singular.")
        L.append("")
        L.append(r["error"])
        return "\n".join(L)

    L.append("    Es distinto de cero, así que el sistema tiene solución única.")
    L.append("")
    L.append("PASO 5. Solución con numpy.linalg.solve")
    L.append(f"    VA = {r['VA']:.4f} V")
    L.append(f"    VB = {r['VB']:.4f} V")
    L.append("")
    L.append("PASO 6. Corrientes de rama")
    c = r["corrientes"]
    L.append(f"    iphi = (VA - VB)/R3 = {c['iphi']:.4f} A")
    L.append(f"    VC   = k·iphi       = {r['VC']:.4f} V")
    L.append(f"    i1   = (Vs - VA)/R1 = {c['i1']:.4f} A")
    L.append(f"    i_R2 = VA/R2        = {c['i_R2']:.4f} A")
    L.append(f"    i_R4 = VB/R4        = {c['i_R4']:.4f} A")
    L.append(f"    i3   = (VB - VC)/R5 = {c['i3']:.4f} A")
    L.append("")
    L.append("PASO 7. Verificación por mallas Rm · [i1, i2, i3] = E")
    L.append("    Rm =")
    L.append(_matriz_a_texto(Rm, "    "))
    L.append(f"    E = [ {E[0]:.4f}  {E[1]:.4f}  {E[2]:.4f} ]")
    m = r["mallas"]
    L.append(f"    i1 = {m[0]:.4f} A    i2 = iphi = {m[1]:.4f} A    i3 = {m[2]:.4f} A")
    L.append("    Coincide con el análisis nodal: " + ("sí" if r["coincide_nodal_mallas"] else "NO"))
    L.append("")
    L.append("PASO 8. Balance de potencia")
    for n, p in enumerate(r["potencias_resistencias"], start=1):
        L.append(f"    P_R{n} = {p:9.4f} W")
    papel_vs = "entrega" if r["P_fuente"] >= 0 else "absorbe"
    papel_dep = "absorbe" if r["P_dependiente"] >= 0 else "entrega"
    L.append(f"    Fuente Vs ({papel_vs}):          {abs(r['P_fuente']):9.4f} W")
    L.append(f"    Fuente dependiente ({papel_dep}): {abs(r['P_dependiente']):9.4f} W")
    L.append(f"    P_generada  = {r['P_generada']:.4f} W")
    L.append(f"    P_absorbida = {r['P_absorbida']:.4f} W")
    L.append("    Se conserva la energía: " + ("sí" if r["balance_ok"] else "NO"))
    return "\n".join(L)


if __name__ == "__main__":
    print(paso_a_paso())
