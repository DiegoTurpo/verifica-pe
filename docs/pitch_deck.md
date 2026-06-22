# Pitch deck — guion y notas del orador

> El deck visual está en [`pitch_deck.pdf`](pitch_deck.pdf) (13 slides).
> Para regenerarlo: `python docs/pitch_deck_generar.py` (edita el contenido ahí).
> Este archivo es tu **teleprompter** para ensayar: qué decir en cada slide.

## Estructura de 7 minutos (con cronómetro)

| Tramo | Slides | Tiempo |
|---|---|---|
| Problema | 2-3 | ~1 min |
| Solución + Insight + **demo en vivo** | 4-5 | ~3-4 min |
| Mercado + modelo de negocio | 6-8 | ~1 min |
| Competencia / GTM / tracción + **the ask** | 9-12 | ~1 min |
| Cierre | 13 | 15 s |

**Plan B:** si falla internet/deploy, tener el **video demo** listo para proyectar.

---

## Slide por slide (qué decir)

**1 · Portada.** *"Verifica le dice a cualquier MYPE, en 30 segundos y con solo un RUC, si la empresa con la que va a hacer negocios es legítima o un riesgo de fraude."* — una frase, con energía.

**2 · Problema.** Una MYPE contrata proveedores sin poder cruzar 6 portales. Si el proveedor es fantasma, **SUNAT le desconoce el crédito fiscal**: el problema del proveedor se vuelve el suyo. Es barato prevenirlo, carísimo revertirlo.

**3 · Evidencia.** No es opinión: **S/3,195 millones** desconocidos, **78 empresas fantasma**, **57,804 clientes** afectados, **39,177 son MYPES**. Fuente: SUNAT (D.L. 1532). *(Deja que los números hablen.)*

**4 · Solución & Insight.** Un RUC → semáforo + reporte claro, cruzando SUNAT + SSCO + OSCE. **Insight:** la data que delata el fraude ya es pública y gratis, pero está fragmentada en 6 portales que nadie cruza.

**5 · DEMO EN VIVO (el corazón).** Cambia a la app. Guion del demo:
  1. RUC fantasma `20607648272` → 🔴 (explica: figura en SSCO de SUNAT).
  2. Sube la **foto de factura** → OCR lee el RUC → mismo veredicto.
  3. Un 🟡 y un 🟢 para contraste. Descarga el **PDF**.
  *Conduce con casos que SABES que funcionan.*

**6 · Why now.** SUNAT recién publica SSCO mensual; OSCE abierto (OCDS); un LLM lo hace legible por centavos; tendencia global (Verifactu en España).

**7 · Mercado.** TAM 2.3M empresas (99% MYPES) → SAM comercio/servicios → SOM: contadores + emprendedores nuevos. Expansión por capas.

**8 · Modelo.** Free / Pro S/39 / Contador S/99. Ancla: **Infocorp cobra S/39 por UNA consulta; yo doy ilimitado al mismo precio** y cruzo el SSCO que ellos no miran. Margen 90-95%.

**9 · Competencia & moat.** Hay piezas sueltas (burós, APIs, enterprise) pero **nadie cruza SSCO para una MYPE con veredicto claro en 30s**. Nunca decir "no existe nada parecido". Moat: dataset propio + foco legitimidad + precio MYPE.

**10 · Go-to-market.** 10 → 100 → 1,000 contadores; motor de referidos contador-a-contador.

**11 · Tracción.** Día cero honesto: producto funcional + problema validado por el Estado. El siguiente hito es validar con contadores (mi GTM). **No invento usuarios.**

**12 · The ask.** US$40k pre-seed: 60% mi sustento full-time, solo ~US$4k infraestructura → capital-eficiente. Hito: 1,000 contadores de pago → valida la seed.

**13 · Cierre.** Repite el one-liner. Demo + repo en pantalla. "Gracias."

---

## Guion de defensa (Q&A — 3 min)

- **"¿No hay competencia?"** → "Sí hay piezas sueltas: APIs de RUC, burós que miden solvencia, software enterprise. Lo que NO existe es cruzar la lista SSCO con el estado del RUC y dar un veredicto claro, para una MYPE, en 30s. Estudios como Ecovis y Quantum ya dicen que verificar la capacidad operativa es indispensable; yo lo automatizo." **(Nunca "no existe nada parecido".)**
- **"¿Hablaste con usuarios?"** → "Me apoyé en evidencia dura: SUNAT desconoció S/3,195M y 39 mil afectados son MYPES. El siguiente paso es llevar el demo a contadores — mi canal de GTM."
- **"¿Por qué salió roja esta empresa?"** → señala la regla transparente: "figura en SSCO" / "No Habido" / "inhabilitada vigente en OSCE".
- **"¿Cómo validaste el precio?"** → "Anclado a Infocorp (S/39 por consulta) + precio de penetración; la disposición exacta a pagar es parte del GTM."
- **"¿Escala a millones de empresas?"** → "El demo corre sobre muestra por el hosting gratuito. En producción el padrón completo vive en la nube; el motor no cambia una línea."
- **"¿Es OCR de verdad?"** → "Uso las capacidades multimodales de Gemini (document AI, Lec. 14) para extraer el RUC de la factura."
- **"¿Tu fuente SSCO es confiable?"** → "Es la relación oficial de SUNAT (D.L. 1532), publicada mensualmente en su web y en El Peruano."

---

## Checklist antes de presentar

- [ ] URL del demo viva (probar en incógnito).
- [ ] `GEMINI_API_KEY` y `GEMINI_MODEL` en Secrets (modelo `gemini-3.1-flash-lite`).
- [ ] Probar los 4 casos (2 rojos, 1 ámbar, 1 verde) + foto OCR.
- [ ] Video demo de respaldo subido (plan B).
- [ ] Ensayar 7 min con cronómetro ≥ 2 veces.
