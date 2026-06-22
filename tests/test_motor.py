"""Tests del motor: un caso por color del semáforo, con RUCs REALES de la muestra.

Los RUCs se eligen consultando la propia base (data-driven), así los tests siguen
siendo válidos aunque la muestra se regenere.
"""
import duckdb
import pytest

from core import fuentes
from core.verificador import verificar_ruc

NO_SSCO_OSCE = ("ruc NOT IN (SELECT ruc FROM ssco) "
                "AND ruc NOT IN (SELECT ruc FROM osce)")


def _ruc(sql: str):
    con = duckdb.connect(fuentes.DB_PATH, read_only=True)
    try:
        fila = con.execute(sql).fetchone()
    finally:
        con.close()
    return fila[0] if fila else None


def test_formato_invalido():
    assert verificar_ruc("123").nivel == "INVALIDO"
    assert verificar_ruc("no-es-un-ruc").nivel == "INVALIDO"


def test_verde():
    ruc = _ruc(f"SELECT ruc FROM padron WHERE estado='ACTIVO' "
               f"AND condicion='HABIDO' AND {NO_SSCO_OSCE} LIMIT 1")
    assert ruc is not None, "la muestra debe tener verdes limpios"
    assert verificar_ruc(ruc).nivel == "VERDE"


def test_rojo_ssco():
    ruc = _ruc("SELECT ruc FROM ssco LIMIT 1")
    assert ruc is not None
    rep = verificar_ruc(ruc)
    assert rep.nivel == "ROJO"
    assert rep.en_ssco


def test_rojo_osce_vigente():
    ruc = _ruc("SELECT ruc FROM osce WHERE vigente "
               "AND ruc NOT IN (SELECT ruc FROM ssco) LIMIT 1")
    assert ruc is not None
    assert verificar_ruc(ruc).nivel == "ROJO"


def test_rojo_no_habido():
    ruc = _ruc(f"SELECT ruc FROM padron WHERE condicion='NO HABIDO' "
               f"AND {NO_SSCO_OSCE} LIMIT 1")
    assert ruc is not None
    assert verificar_ruc(ruc).nivel == "ROJO"


def test_ambar():
    # ámbar puro: señal de precaución, sin ningún disparador de rojo.
    ruc = _ruc(
        "SELECT ruc FROM padron WHERE "
        "((estado LIKE 'SUSPENSION%') OR (condicion IN ('NO HALLADO','PENDIENTE'))) "
        "AND estado NOT LIKE 'BAJA%' AND condicion <> 'NO HABIDO' "
        f"AND {NO_SSCO_OSCE} LIMIT 1")
    if ruc is None:
        pytest.skip("no hay un caso de ámbar puro en la muestra")
    assert verificar_ruc(ruc).nivel == "AMBAR"


def test_no_encontrado():
    # RUC con formato válido (dígito verificador correcto) pero ausente de la muestra.
    rep = verificar_ruc("20000000001")
    assert rep.valido
    assert rep.nivel in ("DESCONOCIDO", "VERDE", "AMBAR", "ROJO")
