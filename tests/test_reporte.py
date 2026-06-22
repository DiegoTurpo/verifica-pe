"""Tests de la red de seguridad y la recomendación (core/reporte.py).

Son pruebas puras (no usan la base ni la API): blindan la regla de oro de que
Gemini nunca puede rebajar el veredicto por debajo de las reglas transparentes.
"""
from types import SimpleNamespace

from core import reporte


def test_red_seguridad_nunca_baja_de_las_reglas():
    # Gemini NO puede rebajar el piso que fijan las reglas...
    assert reporte._red_seguridad(SimpleNamespace(nivel="ROJO"), "VERDE") == "ROJO"
    assert reporte._red_seguridad(SimpleNamespace(nivel="AMBAR"), "VERDE") == "AMBAR"
    # ...pero SÍ puede subir la severidad si observa algo sustentado.
    assert reporte._red_seguridad(SimpleNamespace(nivel="VERDE"), "ROJO") == "ROJO"
    assert reporte._red_seguridad(SimpleNamespace(nivel="AMBAR"), "ROJO") == "ROJO"
    # Respuesta inválida del LLM -> manda el piso de las reglas.
    assert reporte._red_seguridad(SimpleNamespace(nivel="ROJO"), "basura") == "ROJO"


def test_fallback_incluye_recomendacion():
    rep = SimpleNamespace(nivel="ROJO", razon_social="ACME S.A.C.",
                          motivos=["motivo de prueba"], senales=[])
    r = reporte._fallback(rep)
    assert r.nivel == "ROJO"
    assert r.recomendacion          # no vacío
    assert r.motor.startswith("reglas")
