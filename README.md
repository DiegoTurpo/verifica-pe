# 🛡️ Verifica

> Verifica le dice a cualquier MYPE peruana, en 30 segundos y con solo un RUC, si la empresa con la que va a hacer negocios es **legítima o un riesgo de fraude** — cruzando empresas fantasma de SUNAT (SSCO), sanciones del Estado (OSCE) y el estado del RUC, que hoy están dispersos en varios portales.

**Proyecto final — Data Science con Python (Universidad del Pacífico, 2026-I).**
Founder (solo founder): **Diego Turpo de la Cruz**.

- 🌐 **Demo en vivo:** **<https://verifica-pe-decxqbd2bdqkst72icv6qr.streamlit.app>** — ingresa un RUC; no requiere instalar nada ni iniciar sesión.
- 🎥 **Video demo (2-3 min):** _próximamente_
- 📊 **Pitch deck:** _próximamente en [`docs/`](docs/)_

---

## El problema (validado con data oficial)

Según SUNAT (relación al 31-dic-2025), **78 empresas fantasma (SSCO)** emitieron **~455 mil facturas falsas** a **57,804 clientes**, llevando a que SUNAT desconociera más de **S/ 3,195 millones** en crédito fiscal y gasto. **39,177 de los afectados pertenecen al Régimen MYPE Tributario** — el daño cae sobre las pequeñas empresas.

La información que delata a estas empresas **ya es pública y gratuita**, pero está **fragmentada en seis portales que nadie cruza**. Verifica los cruza por ti.

## Cómo funciona

Ingresas un RUC (escrito o desde una foto de factura) → Verifica arma el perfil cruzando fuentes públicas → devuelve un **semáforo de riesgo** con **reglas transparentes** y un **reporte en lenguaje claro**:

- 🔴 **Rojo:** figura en lista SSCO, RUC de baja / no habido, o inhabilitado vigente en OSCE.
- 🟡 **Ámbar:** señales de precaución (p. ej. sanción OSCE histórica no vigente).
- 🟢 **Verde:** activo, habido, sin SSCO ni sanciones.

> El **nivel** del semáforo lo decide una lógica explícita y auditable (`core/riesgo.py`); el LLM solo **redacta** la explicación.

## Arquitectura

Motor de verificación **desacoplado** (Python puro): `verificar_ruc(ruc) -> ReporteVerificacion`. Streamlit solo lo invoca y pinta. Los datos viven **cacheados en DuckDB** → consulta rápida y sin scraping en vivo durante el demo.

```
[Streamlit]  --verificar_ruc()-->  [Motor de verificación]
                                        |--> [DuckDB] padrón RUC + SSCO + OSCE (lectura cacheada)
                                        \--> [Gemini] redacta el reporte
  [OCR Gemini multimodal]  foto factura --> RUC --> Motor
[data/actualizar_datos.py]  descargas SUNAT + scraper OSCE  (offline, fuera del demo)
```

_Diagrama detallado: `docs/arquitectura.png` (próximamente)._

## Herramientas del curso usadas

| # | Herramienta (lección) | Dónde en el código |
|---|---|---|
| 1 | Ingesta web / scraping (Lec. 2-3) | [`data/actualizar_datos.py`](data/actualizar_datos.py) |
| 2 | LLM vía API (Lec. 9) | [`core/reporte.py`](core/reporte.py) — Gemini redacta el reporte |
| 3 | Document AI / OCR (Lec. 14) | [`ai/ocr.py`](ai/ocr.py) — Gemini multimodal extrae el RUC de la factura |

> Las clases mostraron que el OCR/LLM puede implementarse con distintas APIs (Claude, Gemini, etc.). Se eligió **Gemini Flash** por su tier gratuito, suficiente para el demo, manteniendo el deploy ligero.

## Cómo correr localmente

```bash
pip install -r requirements.txt
cp .env.example .env          # coloca tu GEMINI_API_KEY
streamlit run app/streamlit_app.py
```

Consigue una API key gratis de Gemini en <https://aistudio.google.com/apikey>.

## Estructura del repositorio

```
verifica-pe/
├── app/        # interfaz Streamlit (input RUC + subir factura)
├── core/       # motor: verificador, fuentes (DuckDB), riesgo (reglas), reporte (LLM)
├── ai/         # OCR con Gemini multimodal + prompts
├── data/       # actualizar_datos.py (offline) + verifica.duckdb (muestra ligera)
├── docs/       # pitch deck, diagrama, video, research/ (evidencia del problema)
└── notebooks/  # exploracion.ipynb (EDA de las 3 fuentes)
```

## Datos y fuentes

- **Padrón RUC** (SUNAT, datos abiertos) — estado y condición.
- **Relación de Sujetos Sin Capacidad Operativa (SSCO)** (SUNAT, D.L. 1532) — empresas fantasma.
- **Proveedores sancionados / inhabilitados** (OSCE / RNP).

El demo usa una **muestra ligera** cacheada en DuckDB. En producción el padrón completo vive en una base en la nube; el motor no cambia una línea.

## Licencia

MIT — ver [LICENSE](LICENSE).
