"""Genera docs/pitch_deck.pdf — el pitch deck de Verifica (13 slides 16:9).

Reproducible: `python docs/pitch_deck_generar.py`. Usa solo Pillow.
Renderiza cada slide como imagen y las combina en un PDF (también deja PNGs de
preview en data/raw/deck_preview/, que está gitignored).
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
TEAL, MORADO, TINTA, GRIS = (0, 121, 107), (123, 79, 191), (38, 38, 38), (130, 130, 130)
ROJO, AMBAR, VERDE = (211, 47, 47), (245, 124, 0), (56, 142, 60)
SUAVE = (224, 242, 241)
FDIR = r"C:\Windows\Fonts"
DEMO = "verifica-pe-decxqbd2bdqkst72icv6qr.streamlit.app"
REPO = "github.com/DiegoTurpo/verifica-pe"
TOTAL = 15
CAPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "capturas")


def F(sz, bold=True):
    p = os.path.join(FDIR, "arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(p, sz) if os.path.exists(p) else ImageFont.load_default()


def wrap(d, text, font, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    return out


def base(n, kicker=None, titulo=None):
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 18, H], fill=TEAL)
    d.text((60, 44), "VERIFICA", font=F(30), fill=TEAL)
    d.line([60, 852, W - 60, 852], fill=(225, 225, 225), width=2)
    d.text((60, 864), "Verifica  ·  Diego Turpo de la Cruz", font=F(20, False), fill=GRIS)
    nt = f"{n} / {TOTAL}"
    d.text((W - 60 - d.textlength(nt, font=F(20, False)), 864), nt, font=F(20, False), fill=GRIS)
    y = 150
    if kicker:
        d.text((60, y), kicker.upper(), font=F(26), fill=MORADO)
        y += 46
    if titulo:
        for ln in wrap(d, titulo, F(58), W - 140):
            d.text((60, y), ln, font=F(58), fill=TEAL)
            y += 70
    return img, d, y + 22


def bullets(d, items, y, size=33, gap=24, x=80, color=TINTA, dot=TEAL):
    f = F(size, False)
    for it in items:
        d.ellipse([x, y + 12, x + 14, y + 26], fill=dot)
        ty = y
        for ln in wrap(d, it, f, W - x - 110):
            d.text((x + 34, ty), ln, font=f, fill=color)
            ty += size + 8
        y = ty + gap
    return y


def caja(d, text, y, fill=SUAVE, borde=TEAL, tcolor=(0, 90, 80), size=33, pad=26, bold=True):
    f = F(size, bold)
    lines = wrap(d, text, f, W - 120 - 2 * pad)
    h = pad * 2 + len(lines) * (size + 8)
    d.rounded_rectangle([60, y, W - 60, y + h], radius=18, fill=fill, outline=borde, width=3)
    ty = y + pad
    for ln in lines:
        d.text((60 + pad, ty), ln, font=f, fill=tcolor)
        ty += size + 8
    return y + h + 22


def semaforo(d, x, y, r=16, gap=46):
    for i, c in enumerate((ROJO, AMBAR, VERDE)):
        d.ellipse([x + i * gap, y, x + i * gap + 2 * r, y + 2 * r], fill=c)


def captura(img, d, fn, cap, cx, top, maxw=700, maxh=470):
    """Pega una captura (centrada en cx) con su pie, escalada para caber."""
    p = os.path.join(CAPS, fn)
    if not os.path.exists(p):
        return
    im = Image.open(p).convert("RGB")
    im.thumbnail((maxw, maxh))
    img.paste(im, (int(cx - im.width / 2), top))
    w = d.textlength(cap, font=F(17, False))
    d.text((cx - w / 2, top + im.height + 8), cap, font=F(17, False), fill=(110, 110, 110))


slides = []

# 1 — Portada
img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 18, H], fill=TEAL)
semaforo(d, 90, 150, r=20, gap=58)
d.text((90, 220), "Verifica", font=F(130), fill=TEAL)
for i, ln in enumerate(wrap(d, "Sabe en 30 segundos, con solo un RUC, si la empresa con la que vas a "
                             "hacer negocios es legítima o un riesgo de fraude.", F(44, False), W - 200)):
    d.text((92, 410 + i * 58), ln, font=F(44, False), fill=TINTA)
d.text((92, 640), "Cruza empresas fantasma de SUNAT, sanciones del Estado y más —", font=F(28, False), fill=GRIS)
d.text((92, 678), "hoy dispersas en 6 portales públicos que nadie cruza.", font=F(28, False), fill=GRIS)
d.text((92, 800), f"Diego Turpo de la Cruz   ·   Demo: {DEMO}", font=F(22, False), fill=TEAL)
slides.append(img)

# 2 — Problema
img, d, y = base(2, "Problema", "Una factura falsa se vuelve TU problema")
y = bullets(d, [
    "Una MYPE contrata proveedores nuevos sin poder cruzar 6 portales públicos: contrata a ciegas.",
    "Si el proveedor resulta una empresa fantasma, SUNAT te desconoce el crédito fiscal del IGV y el gasto.",
    "El daño tributario y financiero cae sobre quien menos puede pagarlo: micro y pequeñas empresas.",
], y + 6)
caja(d, "Es prevenible y casi gratis HOY (antes de contratar); carísimo de revertir después.", y + 6)
slides.append(img)

# 3 — Evidencia (stats)
img, d, y = base(3, "La evidencia — dato oficial de SUNAT", "El problema ya está cuantificado")
data = [("S/ 3,195 M", "en crédito fiscal y gasto desconocido por facturas falsas"),
        ("78", "empresas fantasma (SSCO) lo generaron"),
        ("57,804", "clientes afectados por esas facturas"),
        ("39,177", "de los afectados son del Régimen MYPE")]
colx, rowy = [80, W // 2 + 30], [y + 10, y + 210]
for i, (num, lab) in enumerate(data):
    cx, cy = colx[i % 2], rowy[i // 2]
    d.text((cx, cy), num, font=F(82), fill=TEAL)
    for j, ln in enumerate(wrap(d, lab, F(27, False), W // 2 - 160)):
        d.text((cx, cy + 100 + j * 34), ln, font=F(27, False), fill=TINTA)
d.text((80, rowy[1] + 188), "Fuente: SUNAT — relación SSCO (Decreto Legislativo N.º 1532).",
       font=F(22, False), fill=GRIS)
slides.append(img)

# 4 — Solución & Insight
img, d, y = base(4, "Solución", "Un RUC, un semáforo de riesgo + reporte claro")
y = bullets(d, [
    "Cruza estado y condición del RUC (SUNAT) + lista SSCO de empresas fantasma + sanciones OSCE.",
    "Devuelve un veredicto rojo / ámbar / verde y un reporte en lenguaje claro, con sus fuentes.",
], y + 6)
caja(d, "Insight: la información que delata el fraude YA es pública y gratuita; pero está "
        "fragmentada en 6 portales que nadie cruza.", y + 10, fill=(237, 231, 246), borde=MORADO,
     tcolor=(80, 40, 130))
slides.append(img)

# 5 — Demo
img, d, y = base(5, "Demo en vivo", "Veámoslo funcionando")
y = bullets(d, [
    "Escribe un RUC  —o—  sube una foto de la factura (OCR con IA lee el RUC).",
    "En segundos: semáforo de riesgo + reporte explicado + descarga en PDF.",
], y + 6)
semaforo(d, 84, y + 4, r=18, gap=52)
d.text((84, y + 70), f"Pruébalo:  {DEMO}", font=F(30), fill=TEAL)
d.text((84, y + 120), "(cambiar a la app para el demo)", font=F(22, False), fill=GRIS)
slides.append(img)

# 6 — Why now
img, d, y = base(6, "Why now", "La ventana es ahora")
bullets(d, [
    "SUNAT recién sistematiza y publica la lista SSCO mensualmente (D.L. 1532).",
    "Los datos del SEACE / OSCE están abiertos en estándar OCDS.",
    "Un LLM convierte 6 fuentes crudas en un reporte legible por centavos.",
    "Tendencia global: Chile, Brasil y México actúan contra la facturación falsa; España opera Verifactu.",
], y + 6)
slides.append(img)

# 7 — Mercado
img, d, y = base(7, "Mercado", "TAM / SAM / SOM")
yy = int(y) + 8
for _sig, _desc in [
    ("TAM", "~2.3 millones de empresas formales en Perú (99.1% son MYPES)."),
    ("SAM", "MYPES de comercio y servicios con alta rotación de proveedores (cientos de miles)."),
    ("SOM — 12 meses", "Contadores (pagan y multiplican) + emprendedores en sus primeros 1-2 años."),
]:
    d.text((80, yy), _sig, font=F(27, True), fill=TEAL)
    yy += 40
    for _ln in wrap(d, _desc, F(21, False), W - 200):
        d.text((100, yy), _ln, font=F(21, False), fill=TINTA)
        yy += 30
    yy += 16
caja(d, "Expansión por capas: contadores y emprendedores → resto de MYPES → empresas grandes vía API.", yy + 6)
slides.append(img)

# 8 — Modelo de negocio
img, d, y = base(8, "Modelo de negocio", "SaaS con ancla de precio")
y = bullets(d, [
    "Free: 3 verificaciones al mes.",
    "Pro — S/39/mes: verificaciones ilimitadas (una por consulta).",
    "Contador — S/99/mes: ilimitadas + lote por Excel + panel multi-cliente.",
    "Margen de contribución ~90% (Pro) y ~95% (Contador).",
], y + 6)
caja(d, "Infocorp cobra S/39 por UNA consulta. Verifica da ilimitado al mismo precio — y cruza el "
        "dato SSCO que el buró no mira.", y + 8)
slides.append(img)

# 9 — Competencia & moat
img, d, y = base(9, "Competencia & moat", "Hay piezas sueltas; nadie hace esto")
y = bullets(d, [
    "Burós (Infocorp, Sentinel): miden solvencia, no legitimidad ni fraude; no cruzan SSCO.",
    "APIs de RUC (Perú API, MIGO): plomería para devs; sin SSCO, sin veredicto, sin OCR.",
    "Software enterprise (SAP Ariba): caro, para grandes empresas con ERP.",
], y + 6)
caja(d, "Moat: dataset propio acumulado (cada lista SSCO + sanciones) + foco legitimidad-no-solvencia "
        "+ precio MYPE + UX para usuario final.", y + 8)
slides.append(img)

# 10 — Go-to-market
img, d, y = base(10, "Go-to-market", "Crecimiento contador-a-contador")
bullets(d, [
    "Primeros 10: red propia (contadores conocidos, contactos UP) que usen el producto y den feedback.",
    "Primeros 100: grupos de contadores (Perucontable, Facebook/WhatsApp), foros regionales.",
    "Primeros 1,000: convenios con colegios de contadores y cámaras de comercio + contenido educativo.",
    "Motor: referidos contador-a-contador (coeficiente viral que baja el CAC).",
], y + 6)
slides.append(img)

# 11 — Tracción
img, d, y = base(11, "Tracción", "Día cero honesto")
y = bullets(d, [
    "Producto funcional verificando casos reales (rojos verificables contra la lista SSCO pública).",
    "Problema cuantificado oficialmente por SUNAT (S/3,195M; 39,177 MYPES afectadas).",
    "Siguiente hito: validación con contadores y cámaras — el primer paso de mi GTM.",
], y + 6)
caja(d, "Mi tracción es un producto que funciona y un problema validado por el Estado. No invento usuarios.",
     y + 8, fill=(255, 243, 224), borde=AMBAR, tcolor=(150, 80, 0))
slides.append(img)

# 12 — The ask
img, d, y = base(12, "The ask", "US$ 40,000 de pre-seed")
y = bullets(d, [
    "~60% (US$24k): sustento del founder full-time durante 12 meses.",
    "~US$4k: infraestructura nube 12 meses (BD administrada + app + LLM + dominio).",
    "US$5k go-to-market   ·   US$2k legal/constitución   ·   colchón para imprevistos.",
], y + 6)
caja(d, "Solo ~US$4k es infraestructura (mis datos son públicos): negocio capital-eficiente. "
        "Hito que desbloquea: 1,000 contadores de pago → valida la ronda seed.", y + 8)
slides.append(img)

# 13 — Capturas del flujo (1/2)
img, d, y = base(13, "El producto en acción", "Ingresa un RUC o sube la factura")
captura(img, d, "inicio.png", "Pantalla principal", 415, int(y) + 6)
captura(img, d, "ocr.png", "OCR: la IA lee el RUC de la foto", 1185, int(y) + 6)
slides.append(img)

# 14 — Capturas del flujo (2/2)
img, d, y = base(14, "El producto en acción", "Veredicto claro + reporte descargable")
captura(img, d, "rojo.png", "Semáforo + métricas + recomendación", 415, int(y) + 6)
captura(img, d, "pdf.png", "Reporte en PDF", 1185, int(y) + 6)
slides.append(img)

# 15 — Cierre
img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 18, H], fill=TEAL)
d.text((90, 230), "Verifica", font=F(120), fill=TEAL)
for i, ln in enumerate(wrap(d, "Legítima o riesgo de fraude — en 30 segundos, con solo un RUC.",
                            F(40, False), W - 200)):
    d.text((92, 420 + i * 54), ln, font=F(40, False), fill=TINTA)
d.text((92, 560), f"Demo:  {DEMO}", font=F(26), fill=TEAL)
d.text((92, 604), f"Repo:  {REPO}", font=F(26), fill=TEAL)
d.text((92, 690), "Gracias.  ·  Diego Turpo de la Cruz", font=F(28, False), fill=GRIS)
slides.append(img)

# Guardar PDF + previews
aqui = os.path.dirname(os.path.abspath(__file__))
pdf = os.path.join(aqui, "pitch_deck.pdf")
slides[0].save(pdf, "PDF", save_all=True, append_images=slides[1:], resolution=150)
prev = os.path.join(aqui, "..", "data", "raw", "deck_preview")
os.makedirs(prev, exist_ok=True)
for i, im in enumerate(slides, 1):
    im.save(os.path.join(prev, f"slide_{i:02d}.png"))
print("Generado:", pdf, "|", round(os.path.getsize(pdf) / 1024, 1), "KB |", len(slides), "slides")
