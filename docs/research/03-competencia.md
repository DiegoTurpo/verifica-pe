# Competencia y diferenciación

> **Importante (verificado):** Verifica **NO** está en un vacío. Hay 3 capas de
> competencia, pero ninguna hace lo mismo. **Nunca decir "no existe nada parecido"**
> en el pitch — eso resta credibilidad.

## El panorama real

| Alternativa | Qué hace | Por qué NO es Verifica |
|---|---|---|
| No hacer nada / confiar | Gratis | Riesgo de perder el crédito fiscal |
| Revisar RUC + SSCO a mano (portal SUNAT) | Gratis | Fragmentado en varios links; sin veredicto; el usuario debe saber qué revisar |
| **Burós de crédito** (Infocorp/Equifax, Sentinel) | Solvencia, deudas, score (~S/ 39/consulta) | Miden **solvencia**, NO legitimidad/fraude; **no** cruzan la condición SSCO |
| **APIs de consulta RUC** (Perú API, MIGO API) | Razón social, estado, condición (data cruda) | **Plomería para desarrolladores**; sin SSCO, sin semáforo, sin reporte claro, sin OCR, sin UX final |
| **Software de gestión de proveedores** (SAP Ariba, Suplos) | Ciclo de compras/pagos para grandes empresas con ERP | Caro, enterprise; no es un verificador de fraude rápido para MYPE/contador |
| **VERIFICA** | Cruza SSCO + estado RUC + sanciones → semáforo + reporte claro + OCR, a precio MYPE, en 30s | — |

## El hueco real (diferenciación afinada)

Nadie ofrece, **para MYPES y contadores**, un verificador instantáneo que **cruce la
lista SSCO de empresas fantasma** + estado RUC + sanciones y devuelva un **veredicto
de riesgo accionable en lenguaje claro** con **OCR de factura**, a **precio MYPE**.

- Los burós miden **solvencia**, no legitimidad.
- Las APIs son **plomería** sin SSCO ni veredicto.
- El software enterprise es **caro** y para corporaciones con ERP.
- El proceso hoy es **manual y fragmentado** (lo confirma *Gestión*).

## Moat (defensibilidad)

1. **Dataset propio acumulado:** cada relación SSCO mensual + el histórico de sanciones.
2. **Grafo de representantes legales** (roadmap): detectar redes de empresas fantasma.
3. **Integración del dato que importa** (SSCO) en un veredicto que un no-técnico usa en 30s.
4. **Foco legitimidad-no-solvencia + precio MYPE + UX** para usuario final.

## Modelo de negocio y pricing

| | STARTER (Free) | PRO — S/39/mes | CONTADOR — S/99/mes |
|---|---|---|---|
| Verificaciones | 3/mes, 1 a 1 | Ilimitadas, **secuencial (1 a 1)** | Ilimitadas + **lote** |
| Varios RUC juntos | No | No (1 por consulta) | **Sí (sube Excel/CSV)** |
| Multi-cliente | No | No | **Sí (panel por cliente)** |
| PDF + alertas SSCO | No | Sí | Sí |

- **Muro anti-migración Pro→Contador:** no es cantidad (ambos ilimitados), es **flujo
  de trabajo**. Pro = ilimitado pero secuencial; Contador = masivo y paralelo (lote +
  multi-cliente). Se le vende **tiempo y organización**, no volumen.
- **Contribution margin:** costo variable ~S/ 3-5/usuario/mes (datos públicos S/0, LLM
  centavos, hosting ~S/0). **Pro → ~90%**; **Contador → ~95%**.
