"""core/reporte.py — Reporte en lenguaje claro con Gemini.

[Herramienta del curso #2: LLM vía API — Lec. 9]

Diseño acordado con el founder: las REGLAS (core/riesgo.py) son los CRITERIOS;
Gemini los toma en cuenta, DECIDE el color y redacta el reporte, y puede añadir
observaciones extra SIEMPRE que estén sustentadas en los datos provistos.

RED DE SEGURIDAD: un fraude confirmado por dato oficial (figura en SSCO o está
inhabilitado VIGENTE en OSCE) nunca puede bajarse a verde — ahí mandan las reglas.

Si no hay API key, no está instalada la librería, o Gemini falla / llega al límite,
cae a un reporte armado con las reglas. Así el demo NUNCA se cae.

1 request por RUC. Modelo Flash del tier gratuito (configurable por entorno).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

_SEV = {"VERDE": 0, "AMBAR": 1, "ROJO": 2}
_MODELO_DEFAULT = "gemini-2.0-flash"  # configurable por la variable de entorno GEMINI_MODEL

_CRITERIOS = """\
Criterios del semáforo de riesgo:
- ROJO si se cumple CUALQUIERA: el RUC figura en la lista SSCO de SUNAT (empresa
  fantasma); o su condición de domicilio es NO HABIDO; o su estado es de BAJA; o
  está inhabilitado VIGENTE en OSCE para contratar con el Estado.
- ÁMBAR (precaución): estado SUSPENSIÓN TEMPORAL; o condición NO HALLADO / PENDIENTE;
  o una sanción OSCE histórica (no vigente).
- VERDE: activo y habido, sin coincidencias en SSCO ni en sanciones vigentes de OSCE.
Filosofía: rojo conservador (un falso "verde" es el peor error)."""


@dataclass
class ReporteIA:
    nivel: str                    # color final (Gemini + red de seguridad, o reglas)
    texto: str                    # reporte en lenguaje claro
    observaciones: list = field(default_factory=list)
    motor: str = "reglas"         # "gemini" | "reglas (fallback)"


def _perfil_texto(rep) -> str:
    lineas = [
        f"RUC: {rep.ruc}",
        f"Razón social: {rep.razon_social or 'desconocida'}",
        f"Estado del contribuyente (SUNAT): {rep.estado or 'sin dato'}",
        f"Condición de domicilio (SUNAT): {rep.condicion or 'sin dato'}",
        f"Departamento: {rep.departamento or 'sin dato'}",
        f"¿Figura en la lista SSCO (empresa fantasma)?: {'SÍ' if rep.en_ssco else 'no'}",
    ]
    if rep.ssco:
        lineas.append(f"  Detalle SSCO: resolución {rep.ssco.get('resolucion', '')}, "
                      f"publicada {rep.ssco.get('fecha_publicacion', '')}")
    vigentes = [s for s in rep.osce if s.get("vigente")]
    lineas.append(f"Sanciones OSCE vigentes: {len(vigentes)}")
    for s in vigentes[:3]:
        lineas.append(f"  - {s.get('tipo_sancion', '')}: {s.get('motivo', '')}")
    return "\n".join(lineas)


def _texto_reglas(rep) -> str:
    if rep.nivel == "VERDE":
        return (f"{rep.razon_social or 'La empresa'} figura activa y habida ante SUNAT, "
                "sin coincidencias en la lista SSCO ni en sanciones vigentes del OSCE. "
                "No se detectaron alertas con la información disponible.")
    if rep.nivel in ("INVALIDO", "DESCONOCIDO"):
        return rep.senales[0].mensaje if rep.senales else "Sin información disponible."
    cabecera = ("Se detectaron señales de RIESGO ALTO:" if rep.nivel == "ROJO"
                else "Se detectaron señales de PRECAUCIÓN:")
    bullets = "\n".join(f"• {m}" for m in rep.motivos)
    return f"{cabecera}\n{bullets}"


def _fallback(rep, motivo: str = "reglas (fallback)") -> ReporteIA:
    return ReporteIA(nivel=rep.nivel, texto=_texto_reglas(rep), motor=motivo)


def _red_seguridad(rep, nivel_ia: str) -> str:
    """No deja que un fraude confirmado por dato oficial baje de rojo."""
    piso = "ROJO" if (rep.en_ssco or any(s.get("vigente") for s in rep.osce)) else "VERDE"
    ia = nivel_ia if nivel_ia in _SEV else "VERDE"
    return max((ia, piso), key=lambda n: _SEV[n])


def generar_reporte(rep) -> ReporteIA:
    """Reporte del RUC. Gemini decide el color (con red de seguridad) y redacta;
    si no hay key o algo falla, cae a un reporte por reglas."""
    if rep.nivel in ("INVALIDO", "DESCONOCIDO"):
        return ReporteIA(nivel=rep.nivel, texto=_texto_reglas(rep), motor="reglas")

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return _fallback(rep, "reglas (no se cargó GEMINI_API_KEY)")

    try:
        from google import genai
        from google.genai import types

        sistema = (
            "Eres un asistente que evalúa el riesgo de fraude de una empresa peruana "
            "para una MYPE o un contador. Decide el nivel del semáforo (ROJO, AMBAR o "
            "VERDE) usando ÚNICAMENTE los datos provistos y los criterios de abajo. "
            "Puedes añadir observaciones SOLO si están sustentadas en esos datos; no "
            "inventes nada. Escribe en español claro y breve.\n\n" + _CRITERIOS)

        instruccion = (
            "Datos de la empresa:\n" + _perfil_texto(rep) + "\n\n"
            "Devuelve SOLO un JSON con esta forma exacta:\n"
            '{"nivel": "ROJO|AMBAR|VERDE", '
            '"reporte": "explicación clara de 2 a 4 frases para el usuario", '
            '"observaciones": ["dato extra sustentado en los datos", "..."]}')

        client = genai.Client(api_key=key)
        resp = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", _MODELO_DEFAULT),
            contents=instruccion,
            config=types.GenerateContentConfig(
                system_instruction=sistema,
                temperature=0,
                response_mime_type="application/json",
            ),
        )
        data = json.loads(resp.text)
        nivel_final = _red_seguridad(rep, str(data.get("nivel", "")).upper())
        return ReporteIA(
            nivel=nivel_final,
            texto=str(data.get("reporte", "")).strip() or _texto_reglas(rep),
            observaciones=[str(o) for o in (data.get("observaciones") or [])][:5],
            motor="gemini",
        )
    except Exception as e:
        return _fallback(rep, f"reglas (error Gemini: {type(e).__name__}: {str(e)[:140]})")
