"""Genera docs/pitch_deck.pdf — el dossier de Verifica (Formato Y Combinator).

Sigue las 14 secciones del PDF de la rúbrica EN ORDEN: 1 One-liner · 2 Founder ·
3 Problema · 4 Solución & Insight · 5 Why now · 6 Mercado · 7 Competencia & moat ·
8 Producto (demo + arquitectura + capturas) · 9 Modelo & pricing · 10 Go-to-market ·
11 Tracción · 12 Roadmap · 13 Riesgos · 14 The ask.

Reproducible: `python docs/pitch_deck_generar.py`. Usa solo Pillow.
Deja PNGs de preview en data/raw/deck_preview/ (gitignored).
"""
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 900
TEAL, MORADO, TINTA, GRIS = (0, 121, 107), (123, 79, 191), (38, 38, 38), (130, 130, 130)
ROJO, AMBAR, VERDE = (211, 47, 47), (245, 124, 0), (56, 142, 60)
SUAVE = (224, 242, 241)
FDIR = r"C:\Windows\Fonts"
AQUI = os.path.dirname(os.path.abspath(__file__))
CAPS = os.path.join(AQUI, "capturas")
DEMO = "verifica-pe-decxqbd2bdqkst72icv6qr.streamlit.app"
REPO = "github.com/DiegoTurpo/verifica-pe"
TOTAL = 19


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
        for ln in wrap(d, titulo, F(54), W - 140):
            d.text((60, y), ln, font=F(54), fill=TEAL)
            y += 66
    return img, d, y + 20


def bullets(d, items, y, size=30, gap=22, x=80, color=TINTA, dot=TEAL, maxw=None):
    f = F(size, False)
    mw = maxw if maxw else (W - x - 110)
    for it in items:
        d.ellipse([x, y + 11, x + 13, y + 24], fill=dot)
        ty = y
        for ln in wrap(d, it, f, mw):
            d.text((x + 32, ty), ln, font=f, fill=color)
            ty += size + 7
        y = ty + gap
    return y


def bloques(d, items, y, sig_size=25, sig_color=TEAL, gap=16):
    """Lista 'etiqueta + descripción' (TAM/SAM/SOM, roadmap, riesgos)."""
    yy = int(y)
    for sig, desc in items:
        d.text((80, yy), sig, font=F(sig_size, True), fill=sig_color)
        yy += sig_size + 11
        for ln in wrap(d, desc, F(21, False), W - 200):
            d.text((100, yy), ln, font=F(21, False), fill=TINTA)
            yy += 30
        yy += gap
    return yy


def caja(d, text, y, fill=SUAVE, borde=TEAL, tcolor=(0, 90, 80), size=30, pad=24, bold=True):
    f = F(size, bold)
    lines = wrap(d, text, f, W - 120 - 2 * pad)
    h = pad * 2 + len(lines) * (size + 8)
    d.rounded_rectangle([60, y, W - 60, y + h], radius=18, fill=fill, outline=borde, width=3)
    ty = y + pad
    for ln in lines:
        d.text((60 + pad, ty), ln, font=f, fill=tcolor)
        ty += size + 8
    return y + h + 20


def semaforo(d, x, y, r=16, gap=46):
    for i, c in enumerate((ROJO, AMBAR, VERDE)):
        d.ellipse([x + i * gap, y, x + i * gap + 2 * r, y + 2 * r], fill=c)


def imagen(img, d, fn, cx, top, cap=None, maxw=700, maxh=470, base_dir=CAPS):
    p = os.path.join(base_dir, fn)
    if not os.path.exists(p):
        return 0
    im = Image.open(p).convert("RGB")
    im.thumbnail((maxw, maxh))
    img.paste(im, (int(cx - im.width / 2), top))
    if cap:
        w = d.textlength(cap, font=F(17, False))
        d.text((cx - w / 2, top + im.height + 8), cap, font=F(17, False), fill=(110, 110, 110))
    return im.height


slides = []

# 1 · One-liner (portada)
img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 18, H], fill=TEAL)
semaforo(d, 90, 150, r=20, gap=58)
d.text((90, 220), "Verifica", font=F(130), fill=TEAL)
for i, ln in enumerate(wrap(d, "Le dice a una MYPE, en 30 segundos y con solo un RUC, si la empresa "
                             "con la que va a hacer negocios es legítima o un riesgo de fraude.",
                             F(42, False), W - 200)):
    d.text((92, 408 + i * 56), ln, font=F(42, False), fill=TINTA)
d.text((92, 648), "Cruza empresas fantasma de SUNAT, sanciones del Estado y más —", font=F(27, False), fill=GRIS)
d.text((92, 684), "hoy dispersas en 6 portales públicos que nadie cruza.", font=F(27, False), fill=GRIS)
d.text((92, 802), f"Diego Turpo de la Cruz   ·   {DEMO}", font=F(22, False), fill=TEAL)
slides.append(img)

# 2 · Founder
img, d, y = base(2, "Founder", "Diego Turpo de la Cruz")
ph = imagen(img, d, "founder.png", W - 200, 160, maxw=300, maxh=430, base_dir=AQUI)  # foto opcional
y = bullets(d, [
    "Estudiante de Economía (Universidad del Pacífico); foco en data science para problemas públicos peruanos.",
    "Founder-market fit: entiende por qué una factura irregular golpea el crédito fiscal (economía y finanzas).",
    "Sabe extraer y cruzar datos públicos dispersos, y construir con IA (LLMs, OCR, clasificadores).",
], y + 6, maxw=1080 if ph else None)
caja(d, "Solo founder con IA: Claude Code = CTO de backend · scrapers = equipo de datos · "
        "LLM = analista de riesgo · Codex/Cursor = frontend.", max(y, 160 + ph + 16) + 6)
slides.append(img)

# 3 · Problema
img, d, y = base(3, "Problema", "Una factura falsa se vuelve TU problema")
y = bullets(d, [
    "Segmento: micro y pequeñas empresas de comercio y servicios que contratan proveedores nuevos seguido.",
    "Hoy no pueden cruzar 6 portales públicos → contratan a ciegas.",
    "Si el proveedor es una empresa fantasma, SUNAT le desconoce el crédito fiscal del IGV y el gasto.",
], y + 6)
caja(d, "Es prevenible y casi gratis HOY (antes de contratar); carísimo de revertir después.", y + 8)
slides.append(img)

# 4 · Problema — evidencia (parte de §3)
img, d, y = base(4, "Problema — evidencia oficial", "El problema ya está cuantificado")
data = [("S/ 3,195 M", "en crédito fiscal y gasto desconocido por facturas falsas"),
        ("78", "empresas fantasma (SSCO) lo generaron"),
        ("57,804", "clientes afectados por esas facturas"),
        ("39,177", "de los afectados son del Régimen MYPE")]
colx, rowy = [80, W // 2 + 30], [int(y) + 6, int(y) + 200]
for i, (num, lab) in enumerate(data):
    cx, cy = colx[i % 2], rowy[i // 2]
    d.text((cx, cy), num, font=F(78), fill=TEAL)
    for j, ln in enumerate(wrap(d, lab, F(26, False), W // 2 - 160)):
        d.text((cx, cy + 96 + j * 32), ln, font=F(26, False), fill=TINTA)
d.text((80, rowy[1] + 184), "Fuente: SUNAT — relación SSCO (Decreto Legislativo N.º 1532).",
       font=F(22, False), fill=GRIS)
slides.append(img)

# 5 · Solución & Insight
img, d, y = base(5, "Solución & Insight", "Un RUC, un semáforo de riesgo + reporte claro")
y = bullets(d, [
    "Cruza estado y condición del RUC (SUNAT) + lista SSCO de empresas fantasma + sanciones OSCE.",
    "Devuelve un veredicto rojo / ámbar / verde y un reporte en lenguaje claro, con sus fuentes.",
], y + 6)
caja(d, "Insight: la información que delata el fraude YA es pública y gratuita; pero está "
        "fragmentada en 6 portales que nadie cruza.", y + 10, fill=(237, 231, 246), borde=MORADO,
     tcolor=(80, 40, 130))
slides.append(img)

# 6 · Why now
img, d, y = base(6, "Why now", "La ventana es ahora")
bullets(d, [
    "SUNAT recién sistematiza y publica la lista SSCO mensualmente (D.L. 1532).",
    "Los datos del SEACE / OSCE están abiertos en estándar OCDS.",
    "Un LLM convierte 6 fuentes crudas en un reporte legible por centavos.",
    "Tendencia global: Chile, Brasil y México actúan contra la facturación falsa; España opera Verifactu.",
], y + 6)
slides.append(img)

# 7 · Mercado
img, d, y = base(7, "Mercado", "TAM / SAM / SOM")
yy = bloques(d, [
    ("TAM", "~2.3 millones de empresas formales en Perú (99.1% son MYPES)."),
    ("SAM", "MYPES de comercio y servicios con alta rotación de proveedores (cientos de miles)."),
    ("SOM — 12 meses", "Contadores (pagan y multiplican) + emprendedores en sus primeros 1-2 años."),
], y + 8)
caja(d, "Expansión por capas: contadores y emprendedores → resto de MYPES → empresas grandes vía API.", yy + 6)
slides.append(img)

# 8 · Competencia & moat
img, d, y = base(8, "Competencia & moat", "Hay piezas sueltas; nadie hace esto")
y = bullets(d, [
    "Burós (Infocorp, Sentinel): miden solvencia, no legitimidad ni fraude; no cruzan SSCO.",
    "APIs de RUC (Perú API, MIGO): plomería para devs; sin SSCO, sin veredicto, sin OCR.",
    "Software enterprise (SAP Ariba): caro, para grandes empresas con ERP.",
], y + 6)
caja(d, "Moat: dataset propio acumulado (cada lista SSCO + sanciones) + foco legitimidad-no-solvencia "
        "+ precio MYPE + UX para usuario final.", y + 8)
slides.append(img)

# 9 · Producto — Demo
img, d, y = base(9, "Producto — Demo en vivo", "Veámoslo funcionando")
y = bullets(d, [
    "Escribe un RUC  —o—  sube una foto de la factura (OCR con IA lee el RUC).",
    "En segundos: semáforo de riesgo + reporte explicado + recomendación + descarga en PDF.",
    "IA: Gemini Flash (tier gratuito) redacta el reporte y hace el OCR multimodal → deploy ligero.",
], y + 6)
semaforo(d, 84, int(y) + 4, r=18, gap=52)
d.text((84, int(y) + 72), f"Pruébalo en vivo:  {DEMO}", font=F(28), fill=TEAL)
slides.append(img)

# 10 · Producto — Arquitectura
img, d, y = base(10, "Producto — Arquitectura", "Motor desacoplado; el demo lee caché")
h = imagen(img, d, "arquitectura.png", W / 2, int(y) + 4, maxw=1160, maxh=470, base_dir=AQUI)
rl = f"Repositorio: {REPO}"
d.text((W / 2 - d.textlength(rl, font=F(21, False)) / 2, int(y) + 8 + h + 8), rl, font=F(21, False), fill=TEAL)
slides.append(img)

# 11 · Producto — Capturas (1/2)
img, d, y = base(11, "Producto — capturas", "Del RUC (o la foto) al veredicto")
imagen(img, d, "inicio.png", 415, int(y) + 6, cap="Pantalla principal")
imagen(img, d, "ocr.png", 1185, int(y) + 6, cap="OCR: la IA lee el RUC de la foto")
slides.append(img)

# 12 · Producto — Capturas (2/2)
img, d, y = base(12, "Producto — capturas", "Veredicto claro + reporte descargable")
imagen(img, d, "rojo.png", 415, int(y) + 6, cap="Semáforo + métricas + recomendación")
imagen(img, d, "pdf.png", 1185, int(y) + 6, cap="Reporte en PDF")
slides.append(img)

# 13 · Modelo de negocio & pricing
img, d, y = base(13, "Modelo de negocio & pricing", "SaaS con ancla de precio")
y = bullets(d, [
    "Free: 3 verificaciones al mes.",
    "Pro — S/39/mes: verificaciones ilimitadas (una por consulta).",
    "Contador — S/99/mes: ilimitadas + lote por Excel + panel multi-cliente.",
    "Margen de contribución ~90% (Pro) y ~95% (Contador).",
], y + 6)
caja(d, "Infocorp cobra S/39 por UNA consulta. Verifica da ilimitado al mismo precio — y cruza el "
        "dato SSCO que el buró no mira.", y + 8)
slides.append(img)

# 14 · Go-to-market
img, d, y = base(14, "Go-to-market", "Crecimiento contador-a-contador")
bullets(d, [
    "Primeros 10: red propia (contadores conocidos, contactos UP) que usen el producto y den feedback.",
    "Primeros 100: grupos de contadores (Perucontable, Facebook/WhatsApp), foros regionales.",
    "Primeros 1,000: convenios con colegios de contadores y cámaras de comercio + contenido educativo.",
    "Motor: referidos contador-a-contador (coeficiente viral que baja el CAC).",
], y + 6)
slides.append(img)

# 15 · Tracción
img, d, y = base(15, "Tracción", "Día cero honesto")
y = bullets(d, [
    "Producto funcional verificando casos reales (rojos verificables contra la lista SSCO pública).",
    "Problema cuantificado oficialmente por SUNAT (S/3,195M; 39,177 MYPES afectadas).",
    "Siguiente hito: validación con contadores y cámaras — el primer paso de mi GTM.",
], y + 6)
caja(d, "Mi tracción es un producto que funciona y un problema validado por el Estado. No invento usuarios.",
     y + 8, fill=(255, 243, 224), borde=AMBAR, tcolor=(150, 80, 0))
slides.append(img)

# 16 · Roadmap
img, d, y = base(16, "Roadmap", "De las 3 fuentes a una API B2B")
yy = bloques(d, [
    ("3 meses", "SUNAT + SSCO + OSCE estable; grafo de representantes legales."),
    ("6 meses", "INFOBRAS (obras paralizadas) + Poder Judicial + alertas automáticas."),
    ("12 meses", "API B2B para ERPs y sistemas contables."),
], y + 8)
caja(d, "Roadmap de ingresos: SaaS a individuos → API a empresas grandes → B2G. "
        "Mismo motor, tickets crecientes.", yy + 6)
slides.append(img)

# 17 · Riesgos & mitigación
img, d, y = base(17, "Riesgos & mitigación", "Identificados y acotados")
bloques(d, [
    ("Técnico — los scrapers se rompen", "Cacheamos las listas oficiales; el demo no depende de scraping en vivo."),
    ("Legal — datos personales", "Solo data pública y oficial; reportamos hechos verificables con fuente, no scores."),
    ("Mercado — entra un buró grande", "Velocidad + foco legitimidad-no-solvencia + precio MYPE + UX para usuario final."),
], y + 8, sig_size=24)
slides.append(img)

# 18 · The ask
img, d, y = base(18, "The ask", "US$ 40,000 de pre-seed")
y = bullets(d, [
    "~60% (US$24k): sustento del founder full-time durante 12 meses.",
    "~US$4k: infraestructura nube 12 meses (BD administrada + app + LLM + dominio).",
    "US$5k go-to-market   ·   US$2k legal/constitución   ·   colchón para imprevistos.",
], y + 6)
caja(d, "Solo ~US$4k es infraestructura (mis datos son públicos): negocio capital-eficiente. "
        "Hito que desbloquea: 1,000 contadores de pago → valida la ronda seed.", y + 8)
slides.append(img)

# 19 · Cierre
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
pdf = os.path.join(AQUI, "pitch_deck.pdf")
slides[0].save(pdf, "PDF", save_all=True, append_images=slides[1:], resolution=150)
prev = os.path.join(AQUI, "..", "data", "raw", "deck_preview")
os.makedirs(prev, exist_ok=True)
for i, im in enumerate(slides, 1):
    im.save(os.path.join(prev, f"slide_{i:02d}.png"))
print(f"Generado: {pdf} | {round(os.path.getsize(pdf) / 1024, 1)} KB | {len(slides)} slides")
