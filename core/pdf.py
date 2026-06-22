"""core/pdf.py — Genera el reporte de verificación en PDF (descargable).

Usa fpdf2 (ligero, puro Python — no rompe el deploy). Sanitiza el texto a
latin-1 para las fuentes core de fpdf: conserva tildes/ñ y reemplaza guiones
largos, viñetas y emojis que latin-1 no soporta.
"""
from __future__ import annotations

import datetime as dt

from fpdf import FPDF

_REEMPLAZOS = {
    "—": "-", "–": "-", "•": "-", "“": '"', "”": '"', "’": "'", "‘": "'",
    "🔴": "[ROJO] ", "🟡": "[AMBAR] ", "🟢": "[VERDE] ", "⚪": "", "🛡️": "", "🛡": "",
}
_ETIQUETA = {"ROJO": "RIESGO ALTO", "AMBAR": "PRECAUCION", "VERDE": "SIN ALERTAS"}
_COLOR = {"ROJO": (200, 0, 0), "AMBAR": (200, 140, 0), "VERDE": (0, 150, 0)}


def _s(texto) -> str:
    t = str(texto or "")
    for a, b in _REEMPLAZOS.items():
        t = t.replace(a, b)
    return t.encode("latin-1", "replace").decode("latin-1")


def generar_pdf(rep, reporte) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def linea(texto, size=10, estilo="", color=(0, 0, 0), h=6):
        # Reset de X al margen izquierdo antes de cada bloque -> evita el error
        # "Not enough horizontal space" de fpdf2 por una X residual.
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", estilo, size)
        pdf.set_text_color(*color)
        pdf.multi_cell(0, h, _s(texto))
        pdf.set_text_color(0, 0, 0)

    linea("Verifica - Reporte de verificacion de RUC", size=18, estilo="B", h=9)
    linea(f"Generado el {dt.date.today().isoformat()}  -  "
          "Fuentes: SUNAT (SSCO y padron RUC) y OSCE/OECE",
          size=9, color=(120, 120, 120), h=5)
    pdf.ln(3)

    linea(rep.razon_social or f"RUC {rep.ruc}", size=13, estilo="B", h=7)
    linea(f"Veredicto: {_ETIQUETA.get(reporte.nivel, reporte.nivel)}",
          size=12, estilo="B", color=_COLOR.get(reporte.nivel, (80, 80, 80)), h=8)
    linea(f"RUC: {rep.ruc}", size=10)
    pdf.ln(2)

    linea("Reporte", size=11, estilo="B", h=7)
    linea(reporte.texto)
    pdf.ln(1)

    if reporte.observaciones:
        linea("Observaciones", size=11, estilo="B", h=7)
        for o in reporte.observaciones:
            linea(f"- {o}")
        pdf.ln(1)

    linea("Criterios detectados y fuentes", size=11, estilo="B", h=7)
    for sgl in rep.senales:
        linea(f"- [{sgl.fuente}] {sgl.mensaje}")
    pdf.ln(1)

    linea("Detalle", size=11, estilo="B", h=7)
    for d in (
        f"Estado (SUNAT): {rep.estado or '-'}",
        f"Condicion de domicilio: {rep.condicion or '-'}",
        f"Departamento: {rep.departamento or '-'}",
        f"En lista SSCO: {'si' if rep.en_ssco else 'no'}",
        f"Sanciones OSCE registradas: {len(rep.osce)}",
    ):
        linea(f"- {d}")
    pdf.ln(2)

    linea("Verifica - demo academico. El veredicto se basa en reglas transparentes sobre "
          "datos publicos de SUNAT y OSCE; el reporte lo redacta un LLM. Demo sobre una "
          "muestra de datos.", size=8, estilo="I", color=(120, 120, 120), h=5)

    return bytes(pdf.output())
