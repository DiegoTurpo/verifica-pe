# Fuentes de datos y marco legal

## Las 3 fuentes del MVP

| # | Fuente | Qué aporta | Cómo se obtiene |
|---|---|---|---|
| 1 | **Padrón RUC (SUNAT)** | Estado (Activo/Baja) y condición (Habido/No Habido) | Descarga del padrón de datos abiertos (no consulta individual: tiene CAPTCHA) → DuckDB |
| 2 | **Lista SSCO** (Sujetos Sin Capacidad Operativa) | Empresas fantasma confirmadas → **rojo absoluto** | Descarga del documento oficial de SUNAT (xlsx) |
| 3 | **OSCE/RNP sancionados** | Inhabilitaciones a proveedores del Estado | **Scraper propio** (corre offline para poblar la base cacheada) |

**Principio de diseño:** el demo **siempre** consulta una base **cacheada en DuckDB**.
El scraping/descarga vive en `data/actualizar_datos.py`, **fuera de la ruta crítica**
del demo → nada se cae en vivo.

### URLs de las descargas (en `data/actualizar_datos.py`)

- **SSCO (SUNAT):** `https://www.sunat.gob.pe/padronesnotificaciones/ssco/sujesincapacidadOperativa.xlsx` (xlsx directo, ~110 filas).
- **OSCE/OECE sancionados:** documento oficial de sancionados (CSV) descargado y normalizado por el scraper (~9,500 filas).
- **Padrón RUC:** descarga manual del padrón reducido (~1.5 GB comprimido); se toma una **muestra estratificada** (no cabe completo en GitHub ni en la RAM de Streamlit).

## La muestra de datos (por qué no es el padrón completo)

- **Límite real:** la **RAM de Streamlit Cloud** (~1 GB), no GitHub. Un archivo de
  100 MB se infla 3-5x al procesarse.
- **Composición de la muestra (`data/verifica.duckdb`, ~5 MB):** las **110 SSCO**
  completas (rojos garantizados) + **9,543 sancionados OSCE** + ~**61,837 RUCs del
  padrón** con muestreo estratificado que cubre todos los colores del semáforo.
- **Producción (roadmap):** padrón completo en base administrada en la nube; el motor
  **no cambia una línea** — es cambio de infraestructura, no de arquitectura.

## Marco legal — Decreto Legislativo N.º 1532

- Regula el procedimiento de atribución de la condición de **Sujeto Sin Capacidad
  Operativa (SSCO)**.
- SUNAT publica la relación **mensualmente** en su web y en el diario oficial **El
  Peruano**; la condición se mantiene **4 años**.
- Solo se usa **data pública y oficial**; Verifica reporta **hechos verificables con
  fuente**, no scores difamatorios → cumplimiento de protección de datos.

## Contexto internacional (refuerza el "why now")

La lucha contra la facturación falsa es una **tendencia global**, no una rareza
peruana:

- **Chile, Brasil y México** implementaron medidas contra la facturación falsa.
- **España** opera el sistema **Verifactu** de verificación de facturas.

Sumado a que (a) SUNAT recién sistematiza y publica la lista SSCO (D.L. 1532), (b) los
datos del SEACE/OSCE están abiertos en estándar **OCDS**, y (c) un LLM convierte 6
fuentes crudas en un reporte legible por centavos → **la ventana es ahora.**
