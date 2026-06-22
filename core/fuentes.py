"""Consultas a la base cacheada DuckDB — la capa de datos del motor.

El demo SIEMPRE lee de aquí (lectura, read-only): nunca hace scraping en vivo.
La base se actualiza offline con `data/actualizar_datos.py`.
"""
from __future__ import annotations

import os

import duckdb

DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "verifica.duckdb",
)

_con: duckdb.DuckDBPyConnection | None = None


def _conn() -> duckdb.DuckDBPyConnection:
    """Conexión read-only perezosa y cacheada a la base."""
    global _con
    if _con is None:
        _con = duckdb.connect(DB_PATH, read_only=True)
    return _con


def _fila(sql: str, params: list) -> dict | None:
    cur = _conn().execute(sql, params)
    row = cur.fetchone()
    if row is None:
        return None
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))


def _filas(sql: str, params: list) -> list[dict]:
    cur = _conn().execute(sql, params)
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def buscar_padron(ruc: str) -> dict | None:
    """Estado y condición del RUC en el padrón (o None si no está en la muestra)."""
    return _fila("SELECT * FROM padron WHERE ruc = ?", [ruc])


def buscar_ssco(ruc: str) -> dict | None:
    """Fila de la lista SSCO (empresa fantasma) o None."""
    return _fila("SELECT * FROM ssco WHERE ruc = ?", [ruc])


def buscar_osce(ruc: str) -> list[dict]:
    """Sanciones OSCE/OECE del RUC (puede tener varias); lista vacía si no hay."""
    return _filas("SELECT * FROM osce WHERE ruc = ?", [ruc])
