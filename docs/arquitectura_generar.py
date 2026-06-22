"""Genera docs/arquitectura.png — diagrama de la arquitectura de Verifica.

Reproducible: `python docs/arquitectura_generar.py`. Usa solo Pillow.
Refleja la arquitectura REAL implementada (motor desacoplado + Gemini que decide
el color con red de seguridad + OCR pre-paso + ingesta offline que llena el caché).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1320, 1000
AZUL, MORADO, TEAL = (33, 150, 243), (123, 79, 191), (0, 121, 107)
AMBAR, GRIS, VERDE, CAFE = (245, 124, 0), (96, 125, 139), (56, 142, 60), (109, 76, 65)
TINTA, LINEA = (33, 33, 33), (110, 110, 110)


def font(sz, bold=False):
    ruta = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    return ImageFont.truetype(ruta, sz) if os.path.exists(ruta) else ImageFont.load_default()


def _centrar(d, cx, y, texto, f, fill):
    w = d.textlength(texto, font=f)
    d.text((cx - w / 2, y), texto, font=f, fill=fill)


def caja(d, x, y, w, h, titulo, subs, fill, borde):
    d.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=fill, outline=borde, width=3)
    cx = x + w / 2
    _centrar(d, cx, y + 12, titulo, font(21, True), borde)
    yy = y + 44
    for s, mono in subs:
        _centrar(d, cx, yy, s, font(15, mono), (90, 90, 90) if mono else TINTA)
        yy += 22


def flecha(d, p1, p2, label=None, color=LINEA, width=3):
    d.line([p1, p2], fill=color, width=width)
    ang = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    L, sp = 15, 0.42
    a1 = (p2[0] - L * math.cos(ang - sp), p2[1] - L * math.sin(ang - sp))
    a2 = (p2[0] - L * math.cos(ang + sp), p2[1] - L * math.sin(ang + sp))
    d.polygon([p2, a1, a2], fill=color)
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        f = font(14, True)
        w = d.textlength(label, font=f)
        d.rectangle([mx - w / 2 - 4, my - 11, mx + w / 2 + 4, my + 11], fill=(255, 255, 255))
        d.text((mx - w / 2, my - 8), label, font=f, fill=color)


img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

_centrar(d, W / 2, 22, "Verifica — Arquitectura", font(34, True), TEAL)
_centrar(d, W / 2, 64, "Motor desacoplado · el demo siempre lee el caché · la IA decide el color con red de seguridad",
         font(16), (90, 90, 90))

# Cajas
caja(d, 360, 104, 600, 92, "1 · USUARIO — App Streamlit",
     [("app/streamlit_app.py", True), ("Escribe un RUC   o   sube una foto de factura", False)],
     (227, 242, 253), AZUL)
caja(d, 720, 236, 430, 92, "2 · OCR (pre-paso) — Gemini multimodal",
     [("ai/ocr.py", True), ("foto de factura  →  RUC", False)], (237, 231, 246), MORADO)
caja(d, 360, 368, 600, 90, "3 · MOTOR DE VERIFICACIÓN",
     [("core/verificador.py", True), ("verificar_ruc(ruc)  →  ReporteVerificacion", False)],
     (224, 242, 241), TEAL)
caja(d, 70, 498, 372, 122, "Fuentes · DuckDB",
     [("core/fuentes.py", True), ("SSCO + Padrón RUC + OSCE", False), ("(cacheado, solo lectura)", False)],
     (255, 243, 224), AMBAR)
caja(d, 474, 498, 372, 122, "Reglas del semáforo",
     [("core/riesgo.py", True), ("rojo / ámbar / verde", False), ("(transparentes, citables)", False)],
     (236, 239, 241), GRIS)
caja(d, 878, 498, 372, 122, "Reporte",
     [("core/reporte.py", True), ("Gemini decide color + redacta", False), ("+ red de seguridad / fallback", False)],
     (237, 231, 246), MORADO)
caja(d, 360, 690, 600, 100, "4 · RESULTADO",
     [("Semáforo + reporte en lenguaje claro", False), ("descarga PDF  ·  core/pdf.py", True)],
     (232, 245, 233), VERDE)
caja(d, 70, 838, 520, 110, "INGESTA OFFLINE (no en vivo)",
     [("data/actualizar_datos.py", True), ("scraping OSCE + descargas SUNAT", False),
      ("construye data/verifica.duckdb", False)], (239, 235, 233), CAFE)

# Semáforo dibujado en el resultado (PIL no renderiza emojis a color)
for i, c in enumerate([(211, 47, 47), (245, 124, 0), (56, 142, 60)]):
    d.ellipse([790 + i * 26, 700, 810 + i * 26, 720], fill=c)

# Flechas
flecha(d, (560, 196), (560, 368), "RUC")                 # usuario -> motor (manual)
flecha(d, (840, 196), (905, 236), "foto")                # usuario -> OCR
flecha(d, (905, 328), (840, 368), "RUC")                 # OCR -> motor
flecha(d, (470, 458), (300, 498))                        # motor -> fuentes
flecha(d, (660, 458), (660, 498))                        # motor -> reglas
flecha(d, (850, 458), (1010, 498))                       # motor -> reporte
flecha(d, (300, 620), (520, 690))                        # fuentes -> resultado
flecha(d, (660, 620), (660, 690))                        # reglas -> resultado
flecha(d, (1010, 620), (800, 690))                       # reporte -> resultado
flecha(d, (256, 838), (256, 620), "llena el caché", CAFE)  # ingesta -> fuentes

ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arquitectura.png")
img.save(ruta)
print("Generado:", ruta, "|", round(os.path.getsize(ruta) / 1024, 1), "KB")
