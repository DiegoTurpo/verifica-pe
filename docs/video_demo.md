# Video demo (2-3 min)

> 🎥 **Link del video:** _pendiente_ — súbelo a YouTube o Loom y pega el enlace
> aquí y en el [README](../README.md).

## Guion sugerido (2-3 min)

1. **(0:00–0:20) Gancho.** Qué es Verifica en una frase + el problema: una factura
   falsa de un proveedor fantasma le cuesta a una MYPE su crédito fiscal.
2. **(0:20–1:40) Demo en vivo.**
   - RUC fantasma `20607648272` → 🔴 (explica: figura en la lista SSCO de SUNAT).
   - Sube la **foto de factura** (`docs/ejemplo_factura.png`) → el OCR lee el RUC.
   - Muestra un 🟡 y un 🟢 para contraste.
   - **Descarga el PDF** del reporte.
3. **(1:40–2:30) Cierre.** El insight: la data que delata el fraude ya es pública,
   pero está fragmentada en 6 portales que nadie cruza. A quién sirve (contadores
   y MYPES) y el llamado a la acción.

## Tips de grabación

- Graba la pantalla con el demo en vivo:
  <https://verifica-pe-decxqbd2bdqkst72icv6qr.streamlit.app>
- Verifica que `GEMINI_API_KEY` y `GEMINI_MODEL` estén en los Secrets de Streamlit
  para que el reporte salga marcado como "gemini".
- Conduce el demo con los **casos que sabes que funcionan** (los 4 botones de ejemplo).
- **Plan B de la presentación:** este video sirve si falla el internet o el deploy
  el día del pitch.
