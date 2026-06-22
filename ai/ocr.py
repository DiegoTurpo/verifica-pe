"""ai/ocr.py — Extrae el RUC de una foto de factura con Gemini multimodal.

[Herramienta del curso #3: Document AI / OCR — Lec. 14]

Es un PRE-paso del motor (NO decide riesgo): imagen de factura -> RUC -> el RUC
entra a `core.verificador.verificar_ruc()`. Usa la misma API key (GEMINI_API_KEY)
y el modelo de GEMINI_MODEL. Si no hay key o no se puede leer, devuelve None y la
app pide escribir el RUC a mano.
"""
from __future__ import annotations

import os
import re

_MODELO_DEFAULT = "gemini-3.1-flash-lite"  # multimodal; configurable por GEMINI_MODEL
_PREFIJOS_RUC = ("20", "10", "15", "16", "17")  # tipos de RUC más comunes


def extraer_ruc(imagen: bytes, mime_type: str = "image/jpeg") -> str | None:
    """Devuelve el RUC (11 dígitos) del emisor detectado en la imagen, o None."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key or not imagen:
        return None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)
        prompt = (
            "Esta es la foto de una factura o comprobante de pago peruano. Extrae el "
            "RUC del EMISOR (la empresa que emite el comprobante): son 11 dígitos. "
            "Responde SOLO con esos 11 dígitos, sin espacios ni texto. Si no hay un "
            "RUC legible, responde NONE.")
        resp = client.models.generate_content(
            model=os.environ.get("GEMINI_MODEL", _MODELO_DEFAULT),
            contents=[
                types.Part.from_bytes(data=imagen, mime_type=mime_type or "image/jpeg"),
                prompt,
            ],
            config=types.GenerateContentConfig(temperature=0),
        )
        candidatos = re.findall(r"\d{11}", resp.text or "")
        for c in candidatos:                      # preferir un RUC con prefijo válido
            if c[:2] in _PREFIJOS_RUC:
                return c
        return candidatos[0] if candidatos else None
    except Exception:
        return None
