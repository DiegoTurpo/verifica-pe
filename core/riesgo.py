"""Reglas TRANSPARENTES del semáforo de riesgo.

El NIVEL lo decide esta lógica explícita y auditable (NO una caja negra ni el LLM):
cada `Señal` explica por sí misma por qué se asignó — clave para responder
"¿por qué salió rojo?" en el Q&A.

Filosofía: **rojo conservador**. Un falso verde (decir "confiable" a una empresa
fantasma) es mucho peor que un falso ámbar.
"""
from __future__ import annotations

from dataclasses import dataclass

ROJO = "ROJO"
AMBAR = "AMBAR"
VERDE = "VERDE"
DESCONOCIDO = "DESCONOCIDO"

# Severidad relativa para elegir el nivel final (gana la más alta).
_SEVERIDAD = {VERDE: 0, AMBAR: 1, ROJO: 2}


@dataclass
class Senal:
    """Un motivo explícito que aporta al veredicto."""
    nivel: str   # ROJO / AMBAR / VERDE
    fuente: str  # SSCO / SUNAT / OSCE
    mensaje: str


def evaluar(rep) -> tuple[str, list[Senal]]:
    """Calcula (nivel, señales) a partir de un perfil ya armado (`rep`).

    `rep` es un objeto con: encontrado, en_ssco, ssco, estado, condicion, osce.
    """
    if not rep.encontrado:
        return DESCONOCIDO, [Senal(
            DESCONOCIDO, "-",
            "No se encontró el RUC en la muestra. En producción se consultaría "
            "el padrón completo en la nube.")]

    senales: list[Senal] = []
    estado = (rep.estado or "").upper()
    condicion = (rep.condicion or "").upper()

    # ----------------------- ROJO (cualquiera dispara rojo) -----------------------
    if rep.en_ssco:
        d = rep.ssco or {}
        extra = ""
        if d.get("resolucion"):
            extra = f" (según {d['resolucion']}"
            extra += f", publicada el {d['fecha_publicacion']})" if d.get("fecha_publicacion") else ")"
        senales.append(Senal(
            ROJO, "SSCO",
            "Figura en la lista oficial de Sujetos Sin Capacidad Operativa (SSCO) "
            f"de SUNAT — empresa fantasma{extra}."))

    if "NO HABIDO" in condicion:
        senales.append(Senal(ROJO, "SUNAT", "Condición de domicilio ante SUNAT: NO HABIDO."))

    if estado.startswith("BAJA"):
        senales.append(Senal(ROJO, "SUNAT", f"Estado del RUC ante SUNAT: {rep.estado}."))

    osce_vigentes = [s for s in rep.osce if s.get("vigente")]
    if osce_vigentes:
        motivo = (osce_vigentes[0].get("motivo") or "").strip()
        msg = "Inhabilitado VIGENTE para contratar con el Estado (OSCE/OECE)"
        msg += f": {motivo}." if motivo else "."
        senales.append(Senal(ROJO, "OSCE", msg))

    # ----------------------------- ÁMBAR (precaución) -----------------------------
    if estado.startswith("SUSPENSION"):
        senales.append(Senal(AMBAR, "SUNAT", f"Estado del RUC: {rep.estado} (precaución)."))

    if "NO HALLADO" in condicion or "PENDIENTE" in condicion:
        senales.append(Senal(AMBAR, "SUNAT", f"Condición de domicilio: {rep.condicion} (precaución)."))

    osce_historicas = [s for s in rep.osce if not s.get("vigente")]
    if osce_historicas:
        senales.append(Senal(AMBAR, "OSCE", "Registra una sanción OSCE histórica (no vigente)."))

    # ------------------------------- decisión final -------------------------------
    nivel = VERDE
    for s in senales:
        if _SEVERIDAD[s.nivel] > _SEVERIDAD[nivel]:
            nivel = s.nivel

    if nivel == VERDE:
        detalle = f" Estado {rep.estado}, condición {rep.condicion}." if rep.estado else ""
        senales.append(Senal(
            VERDE, "SUNAT",
            f"RUC activo y habido, sin coincidencias en SSCO ni OSCE.{detalle}"))

    return nivel, senales
