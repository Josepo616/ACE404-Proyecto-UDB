"""
Pruebas del núcleo. Ejecutar con:  python test_modelo.py   (o  pytest)
"""

import json
import math

from modelo import paso_a_paso, resolver_circuito, validar_entradas

CLAVES_CONTRATO = {
    "VA", "VB", "iphi", "P_generada", "P_absorbida",
    "potencias_resistencias", "matriz_singular",
}


def cerca(a, b, tol=1e-9):
    return abs(a - b) <= tol


def test_valores_nominales_coinciden_con_fase_2():
    r = resolver_circuito()
    assert r["error"] is None and r["matriz_singular"] is False
    assert cerca(r["VA"], 16.0) and cerca(r["VB"], 10.0)
    assert cerca(r["iphi"], 1.2) and cerca(r["VC"], 9.6)
    assert cerca(r["P_generada"], 40.0) and cerca(r["P_absorbida"], 40.0)
    esperadas = [8.0, 12.8, 7.2, 10.0, 0.08]
    assert all(cerca(p, q) for p, q in zip(r["potencias_resistencias"], esperadas))
    assert cerca(r["P_dependiente"], 1.92)
    assert all(cerca(p, q) for p, q in zip(r["mallas"], [2.0, 1.2, 0.2]))
    assert r["balance_ok"] and r["coincide_nodal_mallas"]


def test_contrato_de_claves_siempre_presente():
    casos = [resolver_circuito(), resolver_circuito(R1=0), resolver_circuito(k=-56 / 5.5)]
    for r in casos:
        assert CLAVES_CONTRATO <= set(r)
        assert len(r["potencias_resistencias"]) == 5
    assert set(casos[0]) == set(casos[1]) == set(casos[2])


def test_resultado_es_serializable_a_json():
    json.dumps(resolver_circuito())


def test_matriz_singular():
    # Para los valores nominales, det(G) = 0.56 + 0.055·k, que se anula en k = -56/5.5
    r = resolver_circuito(k=-56 / 5.5)
    assert r["matriz_singular"] is True
    assert r["error"] and math.isnan(r["VA"])
    assert "singular" in paso_a_paso(k=-56 / 5.5)


def test_entradas_invalidas():
    for malos in ({"R1": 0}, {"R3": -5}, {"R2": "abc"}, {"Vs": ""}, {"k": None}, {"R4": float("inf")}):
        r = resolver_circuito(**malos)
        assert r["error"], malos
        assert r["matriz_singular"] is False
        assert math.isnan(r["VA"])


def test_acepta_texto_de_la_interfaz():
    assert validar_entradas(R3="4,7")["R3"] == 4.7
    r = resolver_circuito(Vs="20", R1=" 2 ", k="8.0")
    assert cerca(r["VA"], 16.0)


def test_balance_y_mallas_en_barrido_what_if():
    for R3 in (0.5, 1, 5, 20, 100):
        for k in (-20, -5, 0, 4, 8, 15, 50):
            for Vs in (-12, 5, 20):
                r = resolver_circuito(Vs=Vs, R3=R3, k=k)
                if r["matriz_singular"]:
                    continue
                assert r["balance_ok"], (Vs, R3, k)
                assert r["coincide_nodal_mallas"], (Vs, R3, k)
                assert r["P_generada"] >= 0 and r["P_absorbida"] >= 0


def test_paso_a_paso_devuelve_texto():
    texto = paso_a_paso()
    assert isinstance(texto, str)
    assert "16.0000" in texto and "det(G)" in texto
    assert "No se puede resolver" in paso_a_paso(R1=-1)


if __name__ == "__main__":
    pruebas = [f for nombre, f in sorted(globals().items()) if nombre.startswith("test_")]
    for prueba in pruebas:
        prueba()
        print(f"OK  {prueba.__name__}")
    print(f"\n{len(pruebas)} pruebas pasaron.")
