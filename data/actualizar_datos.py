"""
actualizar_datos.py — Ingesta de datos (OFFLINE) para Verifica.

[Herramienta del curso #1: Ingesta web / scraping — Lec. 2-3]

Este script recolecta las fuentes públicas del Estado peruano y construye la base
cacheada `data/verifica.duckdb` que el demo consulta. Se ejecuta FUERA de la ruta
del demo (no en vivo): así el demo nunca depende de una descarga en tiempo real y
no se cae si una fuente está lenta o caída.

Fuentes:
  1. SSCO (Sujetos Sin Capacidad Operativa) — SUNAT, D.L. 1532.
     Excel oficial publicado mensualmente.  ->  tabla `ssco`   [DATOS REALES]
  2. Proveedores sancionados / inhabilitados — OSCE/OECE.
     ->  tabla `osce`   (ver NOTA_OSCE)
  3. Padrón RUC — SUNAT (estado / condición).
     ->  tabla `padron` (ver NOTA_PADRON)

Uso:
    python data/actualizar_datos.py
"""
from __future__ import annotations

import io
import os
import zipfile

import duckdb
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
DB_PATH = os.path.join(HERE, "verifica.duckdb")
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; VerificaBot/1.0)"}

# Fuente oficial SSCO (SUNAT). Excel único, actualizado el último día de cada mes.
URL_SSCO = "https://www.sunat.gob.pe/padronesnotificaciones/ssco/sujesincapacidadOperativa.xlsx"

# NOTA_OSCE: el OSCE pasó a ser OECE y sus URLs de consulta antiguas ya no responden.
# La relación de proveedores sancionados/inhabilitados se publica en la Plataforma
# Nacional de Datos Abiertos (https://www.datosabiertos.gob.pe — busca "proveedores
# sancionados con inhabilitación vigente"). Esa plataforma sirve el archivo por
# JavaScript, así que la forma robusta de refrescarlo es descargar el CSV a mano a
# `data/raw/osce.csv` y volver a correr este script. Si ese archivo no existe, se
# usan filas de EJEMPLO (origen='ejemplo') para poder demostrar el flujo del semáforo.
RUTA_OSCE_LOCAL = os.path.join(RAW, "osce.csv")

# NOTA_PADRON: el padrón reducido completo de SUNAT pesa varios GB (no cabe en la RAM
# gratuita de Streamlit ni en GitHub). El demo trabaja con una MUESTRA. Aquí cargamos
# casos VERDES de ejemplo (empresas activas/habidas). Para refrescar con data real,
# descarga el padrón desde http://www.sunat.gob.pe/descargaPRR/mrc137_padron_reducido.html
# y muestrea las columnas estado/condición.
#
# Candidatos donde buscar el padrón descargado manualmente (.zip o .txt):
RUTA_PADRON_CANDIDATAS = [
    os.path.join(RAW, "padron_reducido_ruc.txt"),
    os.path.join(RAW, "padron.txt"),
    os.path.join(RAW, "padron_reducido_RUC.zip"),
    os.path.join(RAW, "padron.zip"),
]
N_MUESTRA_PADRON = 50_000


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
def _ensure_dirs() -> None:
    os.makedirs(RAW, exist_ok=True)


# 25 departamentos del Perú (Callao incluido). SUNAT los escribe en MAYÚSCULAS sin tilde.
_DEPARTAMENTOS = [
    "AMAZONAS", "ANCASH", "APURIMAC", "AREQUIPA", "AYACUCHO", "CAJAMARCA",
    "CALLAO", "CUSCO", "HUANCAVELICA", "HUANUCO", "ICA", "JUNIN", "LA LIBERTAD",
    "LAMBAYEQUE", "LIMA", "LORETO", "MADRE DE DIOS", "MOQUEGUA", "PASCO",
    "PIURA", "PUNO", "SAN MARTIN", "TACNA", "TUMBES", "UCAYALI",
]
# Orden por longitud desc: así "LA LIBERTAD" se detecta antes que "LIMA" y no se parte.
_DEPARTAMENTOS_ORD = sorted(_DEPARTAMENTOS, key=len, reverse=True)


def _departamento_desde_domicilio(dom: str) -> str:
    """Extrae el departamento del domicilio fiscal de SUNAT.

    El formato termina en '... DEPARTAMENTO - PROVINCIA - DISTRITO', pero el
    departamento va pegado a la dirección (sin ' - ' delante). Tomamos el campo
    antepenúltimo y lo cotejamos contra la lista oficial de departamentos.
    """
    if not isinstance(dom, str):
        return ""
    partes = [p.strip() for p in dom.split(" - ")]
    campo = (partes[-3] if len(partes) >= 3 else dom).upper()
    for d in _DEPARTAMENTOS_ORD:
        if campo.endswith(d):
            return d
    full = dom.upper()
    for d in _DEPARTAMENTOS_ORD:
        if d in full:
            return d
    return ""


def digito_verificador_ruc(ruc10: str) -> int:
    """Dígito verificador del RUC peruano (módulo 11)."""
    pesos = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    s = sum(int(d) * p for d, p in zip(ruc10, pesos))
    r = 11 - (s % 11)
    return 0 if r == 10 else (1 if r == 11 else r)


def ruc_valido(ruc: str) -> bool:
    """True si `ruc` tiene 11 dígitos y su dígito verificador es correcto."""
    if not (isinstance(ruc, str) and ruc.isdigit() and len(ruc) == 11):
        return False
    return int(ruc[-1]) == digito_verificador_ruc(ruc[:10])


def _mk_ruc(base10: str) -> str:
    """Construye un RUC válido (11 díg.) a partir de un cuerpo de 10 dígitos."""
    return base10 + str(digito_verificador_ruc(base10))


# --------------------------------------------------------------------------- #
# 1) SSCO — empresas fantasma (DATOS REALES de SUNAT)
# --------------------------------------------------------------------------- #
def descargar_ssco() -> pd.DataFrame:
    _ensure_dirs()
    dest = os.path.join(RAW, "ssco.xlsx")
    try:
        r = requests.get(URL_SSCO, headers=HEADERS, timeout=90)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
        print(f"[SSCO] descargado: {len(r.content):,} bytes")
    except Exception as e:  # noqa: BLE001
        if not os.path.exists(dest):
            raise RuntimeError(f"No se pudo descargar SSCO y no hay copia local: {e}")
        print(f"[SSCO] descarga falló ({e}); uso copia local en {dest}")

    df = pd.read_excel(dest)
    ren = {
        "RUC": "ruc",
        "Razón social": "razon_social",
        "Domicilio fiscal": "domicilio_fiscal",
        "Resolución de atribución como SSCO": "resolucion",
        "Fecha de emisión de la resolución de atribución": "fecha_emision",
        "Fecha en la que la resolución de atribución quedó firme": "fecha_firme",
        "RUC o documento de identidad del representante legal": "rep_legal_doc",
        "Apellidos y nombres del representante legal": "rep_legal_nombre",
        "Fecha de publicación": "fecha_publicacion",
    }
    df = df.rename(columns=ren)
    df["ruc"] = (
        df["ruc"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
    )
    for c in ["fecha_emision", "fecha_firme", "fecha_publicacion"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce").dt.strftime("%Y-%m-%d")
    df["departamento"] = df["domicilio_fiscal"].apply(_departamento_desde_domicilio)
    df["origen"] = "SUNAT-SSCO"

    cols = [
        "ruc", "razon_social", "domicilio_fiscal", "departamento", "resolucion",
        "fecha_emision", "fecha_firme", "rep_legal_doc", "rep_legal_nombre",
        "fecha_publicacion", "origen",
    ]
    return df[[c for c in cols if c in df.columns]]


# --------------------------------------------------------------------------- #
# 2) OSCE — proveedores sancionados / inhabilitados
# --------------------------------------------------------------------------- #
def _osce_ejemplo() -> pd.DataFrame:
    """Filas de EJEMPLO para demostrar el flujo OSCE (no son empresas reales)."""
    filas = [
        # Inhabilitación VIGENTE -> dispara ROJO
        (_mk_ruc("2050010001"), "CONSTRUCTORA EJEMPLO INHABILITADA S.A.C.",
         "INHABILITACION", True, "2025-02-01", "2027-02-01",
         "Resolución TCE N° 0001-2025"),
        # Inhabilitación NO vigente (histórica) -> dispara ÁMBAR
        (_mk_ruc("2050010002"), "SERVICIOS EJEMPLO SANCIONADO E.I.R.L.",
         "INHABILITACION", False, "2019-05-01", "2021-05-01",
         "Resolución TCE N° 0123-2019"),
        # Multa vigente -> señal de precaución (ÁMBAR)
        (_mk_ruc("2050010003"), "COMERCIAL EJEMPLO MULTADO S.A.",
         "MULTA", True, "2024-08-01", None,
         "Resolución TCE N° 0456-2024"),
    ]
    df = pd.DataFrame(
        filas,
        columns=["ruc", "razon_social", "tipo_sancion", "vigente",
                 "fecha_inicio", "fecha_fin", "resolucion"],
    )
    df["origen"] = "ejemplo"
    return df


def descargar_osce() -> pd.DataFrame:
    """Carga OSCE real desde data/raw/osce.csv si existe; si no, usa el ejemplo.

    Ver NOTA_OSCE arriba. El normalizador es flexible: busca columnas que
    parezcan RUC / razón social / tipo de sanción para tolerar cambios de formato.
    """
    if not os.path.exists(RUTA_OSCE_LOCAL):
        print("[OSCE] sin data/raw/osce.csv -> uso filas de ejemplo")
        return _osce_ejemplo()

    try:
        try:
            df = pd.read_csv(RUTA_OSCE_LOCAL, sep=None, engine="python", encoding="utf-8")
        except Exception:
            df = pd.read_csv(RUTA_OSCE_LOCAL, sep=None, engine="python", encoding="latin-1")
        cols = {c.lower(): c for c in df.columns}

        def pick(*claves):
            for k in claves:
                for low, orig in cols.items():
                    if k in low:
                        return orig
            return None

        c_ruc = pick("ruc")
        c_razon = pick("razon", "razón", "nombre", "proveedor")
        c_tipo = pick("tipo", "sancion", "sanción")
        if not c_ruc:
            print("[OSCE] no encontré columna RUC -> uso ejemplo")
            return _osce_ejemplo()

        out = pd.DataFrame()
        out["ruc"] = df[c_ruc].astype(str).str.replace(r"\.0$", "", regex=True).str.strip()
        out["razon_social"] = df[c_razon] if c_razon else ""
        out["tipo_sancion"] = df[c_tipo] if c_tipo else "INHABILITACION"
        out["vigente"] = True  # el dataset "vigente" lista solo sanciones activas
        out["fecha_inicio"] = None
        out["fecha_fin"] = None
        out["resolucion"] = ""
        out["origen"] = "OSCE-datosabiertos"
        out = out[out["ruc"].str.len() == 11]
        print(f"[OSCE] cargado real: {len(out)} filas")
        return out
    except Exception as e:  # noqa: BLE001
        print(f"[OSCE] error leyendo CSV ({e}) -> uso ejemplo")
        return _osce_ejemplo()


# --------------------------------------------------------------------------- #
# 3) Padrón RUC — casos verdes de muestra
# --------------------------------------------------------------------------- #
def _padron_ejemplo() -> pd.DataFrame:
    """Casos de EJEMPLO del padrón (no son empresas reales). Ver NOTA_PADRON."""
    filas = [
        (_mk_ruc("2060020001"), "EMPRESA EJEMPLO ACTIVA S.A.C.", "ACTIVO", "HABIDO",
         "LIMA", "2015-03-12"),
        (_mk_ruc("2060020002"), "COMERCIAL EJEMPLO CONFIABLE E.I.R.L.", "ACTIVO", "HABIDO",
         "AREQUIPA", "2012-07-01"),
        (_mk_ruc("2060020003"), "DISTRIBUIDORA EJEMPLO S.A.", "ACTIVO", "HABIDO",
         "LA LIBERTAD", "2009-11-20"),
        # Caso NO HABIDO -> dispara ROJO por condición
        (_mk_ruc("2060020004"), "EMPRESA EJEMPLO NO HABIDA S.A.C.", "ACTIVO", "NO HABIDO",
         "LIMA", "2022-01-05"),
        # Caso de BAJA -> dispara ROJO por estado
        (_mk_ruc("2060020005"), "NEGOCIO EJEMPLO DADO DE BAJA E.I.R.L.", "BAJA DE OFICIO", "NO HABIDO",
         "CALLAO", "2018-09-30"),
    ]
    df = pd.DataFrame(
        filas,
        columns=["ruc", "razon_social", "estado", "condicion",
                 "departamento", "fecha_inscripcion"],
    )
    df["origen"] = "ejemplo"
    return df


# --------------------------------------------------------------------------- #
# Construcción de la base DuckDB
# --------------------------------------------------------------------------- #
def construir_duckdb(db_path: str = DB_PATH) -> None:
    _ensure_dirs()
    ssco = descargar_ssco()
    osce = descargar_osce()
    padron_local = next((p for p in RUTA_PADRON_CANDIDATAS if os.path.exists(p)), None)
    if padron_local:
        rucs_obj = set(ssco["ruc"]) | set(osce["ruc"])
        padron = muestrear_padron(padron_local, rucs_objetivo=rucs_obj)
    else:
        print("[padron] sin archivo local en data/raw -> uso filas de ejemplo")
        padron = _padron_ejemplo()

    con = duckdb.connect(db_path)
    for nombre, df in [("ssco", ssco), ("osce", osce), ("padron", padron)]:
        con.register("_tmp", df)
        con.execute(f"CREATE OR REPLACE TABLE {nombre} AS SELECT * FROM _tmp")
        con.unregister("_tmp")

    print("\n== Resumen de la base cacheada ==")
    for nombre in ["ssco", "osce", "padron"]:
        n = con.execute(f"SELECT COUNT(*) FROM {nombre}").fetchone()[0]
        print(f"  {nombre:8s}: {n} filas")
    con.close()
    print(f"\nBase escrita en {db_path}")


# --------------------------------------------------------------------------- #
# Muestreo del padrón (memory-safe, por chunks) — se corre OFFLINE
# --------------------------------------------------------------------------- #
def _abrir_padron_texto(ruta: str):
    """Devuelve (stream_texto, handle_a_cerrar) del padrón. Acepta .zip o .txt.

    No extrae el ZIP a disco ni lo carga entero en memoria: lo lee como stream.
    """
    if ruta.lower().endswith(".zip"):
        zf = zipfile.ZipFile(ruta)
        interno = max(zf.infolist(), key=lambda i: i.file_size).filename
        binario = zf.open(interno, "r")
        return io.TextIOWrapper(binario, encoding="latin-1", errors="replace"), zf
    return open(ruta, "r", encoding="latin-1", errors="replace"), None


def _detectar_columnas_padron(ruta: str):
    """Lee SOLO la cabecera para detectar el separador y las columnas clave."""
    stream, handle = _abrir_padron_texto(ruta)
    try:
        cabecera = stream.readline().rstrip("\r\n")
    finally:
        stream.close()
        if handle:
            handle.close()
    sep = "|" if cabecera.count("|") >= cabecera.count(",") else ","
    cols = [c.strip() for c in cabecera.split(sep)]

    def buscar(*claves):
        for c in cols:
            cu = c.upper()
            if any(k in cu for k in claves):
                return c
        return None

    mapa = {
        "ruc": buscar("RUC"),
        "razon": buscar("RAZON", "RAZÓN", "NOMBRE"),
        "estado": buscar("ESTADO"),
        "condicion": buscar("CONDIC", "DOMICIL"),
        "departamento": buscar("DEPARTAMENTO"),
    }
    return sep, mapa


def muestrear_padron(ruta: str, rucs_objetivo=None, n_muestra: int = N_MUESTRA_PADRON,
                     chunksize: int = 200_000) -> pd.DataFrame:
    """Extrae una muestra ligera del padrón reducido leyendo por chunks.

    Incluye (a) TODAS las filas cuyo RUC esté en `rucs_objetivo` (enriquece a los
    SSCO/OSCE con su estado/condición real) y (b) hasta `n_muestra` empresas
    ACTIVAS y HABIDAS como casos verdes. Nunca carga el archivo completo en RAM.
    """
    rucs_objetivo = set(rucs_objetivo or [])
    sep, mapa = _detectar_columnas_padron(ruta)
    c_ruc = mapa["ruc"]
    if not c_ruc:
        print("[padron] no se detectó la columna RUC -> uso ejemplos")
        return _padron_ejemplo()

    stream, handle = _abrir_padron_texto(ruta)
    matched, verdes, n_verdes = [], [], 0
    try:
        for chunk in pd.read_csv(stream, sep=sep, dtype=str, header=0,
                                 chunksize=chunksize, on_bad_lines="skip"):
            chunk.columns = [c.strip() for c in chunk.columns]
            chunk[c_ruc] = chunk[c_ruc].astype(str).str.strip()

            if rucs_objetivo:
                m = chunk[chunk[c_ruc].isin(rucs_objetivo)]
                if len(m):
                    matched.append(m)

            if n_verdes < n_muestra:
                cand = chunk
                if mapa["estado"]:
                    act = cand[mapa["estado"]].astype(str).str.upper()
                    cand = cand[act.str.contains("ACTIVO", na=False)]
                if mapa["condicion"]:
                    cond = cand[mapa["condicion"]].astype(str).str.upper()
                    cand = cand[cond.str.contains("HABIDO", na=False) & ~cond.str.contains("NO HABIDO", na=False)]
                if len(cand):
                    take = cand.head(n_muestra - n_verdes)
                    verdes.append(take)
                    n_verdes += len(take)

            if n_verdes >= n_muestra and not rucs_objetivo:
                break
    finally:
        stream.close()
        if handle:
            handle.close()

    partes = []
    if matched:
        partes.append(pd.concat(matched))
    if verdes:
        partes.append(pd.concat(verdes))
    if not partes:
        return _padron_ejemplo()
    bruto = pd.concat(partes).drop_duplicates(subset=[c_ruc])

    out = pd.DataFrame()
    out["ruc"] = bruto[c_ruc]
    out["razon_social"] = bruto[mapa["razon"]] if mapa["razon"] else ""
    out["estado"] = bruto[mapa["estado"]] if mapa["estado"] else ""
    out["condicion"] = bruto[mapa["condicion"]] if mapa["condicion"] else ""
    out["departamento"] = (
        bruto[mapa["departamento"]].astype(str).str.upper() if mapa["departamento"] else ""
    )
    out["fecha_inscripcion"] = None
    out["origen"] = "SUNAT-padron"
    out = out[out["ruc"].str.len() == 11].reset_index(drop=True)
    print(f"[padron] muestra: {len(out)} filas "
          f"({len(pd.concat(matched)) if matched else 0} SSCO/OSCE enriquecidos)")
    return out


if __name__ == "__main__":
    construir_duckdb()
