"""Verifica — interfaz Streamlit (demo en vivo).

Ingresa un RUC (o una foto de factura) → el motor (`core.verificador`) lo cruza
con las 3 fuentes públicas y pinta el semáforo de riesgo + el reporte de Gemini.
La UI solo invoca al motor y pinta (lógica desacoplada).
"""
import os
import sys

# En Streamlit Cloud el script corre desde app/, así que agregamos la raíz del
# repo a sys.path para poder importar los paquetes `core` y `ai`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from ai.ocr import extraer_ruc
from core.reporte import generar_reporte
from core.verificador import verificar_ruc

st.set_page_config(page_title="Verifica — riesgo de proveedores", page_icon="🛡️",
                   layout="centered")

# En local, carga el .env si existe (en Cloud se usan los Secrets de Streamlit).
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# En Streamlit Cloud la API key vive en Secrets; la exponemos como variable de
# entorno para que core.reporte / ai.ocr la lean (sin acoplar el core a Streamlit).
try:
    for _clave in ("GEMINI_API_KEY", "GEMINI_MODEL"):
        if _clave in st.secrets:
            os.environ.setdefault(_clave, str(st.secrets[_clave]))
except Exception:
    pass

st.markdown("""<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 2.2rem;}
.hero {background: linear-gradient(135deg,#00796b,#004d40); color:#fff;
       padding:26px 30px; border-radius:16px; margin-bottom:18px;}
.hero h1 {margin:0; font-size:2.2rem; font-weight:800;}
.hero p {margin:.55rem 0 0; font-size:1.02rem; line-height:1.5; opacity:.96;}
.veredicto {border-radius:14px; padding:18px 22px; margin:4px 0;}
.veredicto .vtag {font-size:.8rem; font-weight:800; letter-spacing:.07em;}
.veredicto .vname {font-size:1.5rem; font-weight:800; color:#1f2937; margin-top:3px; line-height:1.2;}
.veredicto .vruc {font-size:.9rem; color:#6b7280; margin-top:2px;}
.reco {background:#e3f2fd; border-left:6px solid #1565c0; border-radius:10px;
       padding:12px 16px; margin:12px 0; font-size:1.02rem;}
</style>""", unsafe_allow_html=True)

st.markdown(
    '<div class="hero"><h1>🛡️ Verifica</h1>'
    '<p>¿La empresa con la que vas a hacer negocios es <b>legítima o un riesgo de '
    'fraude</b>? Ingresa un RUC y lo cruzamos con las empresas fantasma de SUNAT '
    '(SSCO), el padrón RUC y los sancionados del OSCE — en segundos.</p></div>',
    unsafe_allow_html=True)

# RUCs REALES de la muestra, uno por color, para conducir el demo en vivo.
EJEMPLOS = [
    ("🔴 Empresa fantasma", "20607648272"),
    ("🔴 No habido / OSCE", "20100994128"),
    ("🟡 Precaución", "10198565470"),
    ("🟢 Sin alertas", "10452159428"),
]
ICONO = {"ROJO": "🔴", "AMBAR": "🟡", "VERDE": "🟢"}
_ESTILO = {
    "ROJO": ("#fdecea", "#c62828", "🔴", "RIESGO ALTO"),
    "AMBAR": ("#fff4e5", "#e65100", "🟡", "PRECAUCIÓN"),
    "VERDE": ("#e8f5e9", "#2e7d32", "🟢", "SIN ALERTAS"),
}


def _mostrar(rep, reporte) -> None:
    nivel = reporte.nivel
    if nivel == "INVALIDO":
        st.info("⚠️ El RUC debe tener **11 dígitos** numéricos.")
        return
    if nivel == "DESCONOCIDO":
        st.info(f"⚪ No encontramos el RUC **{rep.ruc}** en la muestra del demo. "
                "En producción se consultaría el padrón completo en la nube.")
        return

    bg, col, icono, etiqueta = _ESTILO[nivel]
    titular = rep.razon_social or f"RUC {rep.ruc}"
    st.markdown(
        f'<div class="veredicto" style="background:{bg};border-left:10px solid {col};">'
        f'<div class="vtag" style="color:{col};">{icono} {etiqueta}</div>'
        f'<div class="vname">{titular}</div>'
        f'<div class="vruc">RUC {rep.ruc}</div></div>',
        unsafe_allow_html=True)

    # Hechos clave de un vistazo.
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Estado (SUNAT)", (rep.estado or "—").title())
    c2.metric("Condición", (rep.condicion or "—").title())
    c3.metric("En SSCO", "Sí" if rep.en_ssco else "No")
    c4.metric("Sanciones OSCE", len(rep.osce))

    # Reporte en lenguaje claro (Gemini; o reglas si no hay key / falla).
    st.markdown(reporte.texto)

    if reporte.recomendacion:
        st.markdown(f'<div class="reco">💡 <b>Qué hacer:</b> {reporte.recomendacion}</div>',
                    unsafe_allow_html=True)

    if reporte.observaciones:
        st.markdown("**Observaciones adicionales:**")
        for o in reporte.observaciones:
            st.markdown(f"- {o}")

    try:
        from core.pdf import generar_pdf
        st.download_button(
            "📄 Descargar reporte en PDF", data=generar_pdf(rep, reporte),
            file_name=f"verifica_{rep.ruc}.pdf", mime="application/pdf")
    except Exception:
        pass

    with st.expander("🔎 Criterios detectados y fuentes"):
        for s in rep.senales:
            st.markdown(
                f"{ICONO.get(s.nivel, '•')} {s.mensaje}  \n"
                f"<span style='color:gray;font-size:0.8em'>fuente: {s.fuente}</span>",
                unsafe_allow_html=True)
        st.caption(f"Reporte generado por: {reporte.motor}")


# --------------------------------------------------------------- entrada
if "ruc" not in st.session_state:
    st.session_state.ruc = ""

st.caption("Prueba con un caso real:")
for col, (etiqueta, valor) in zip(st.columns(len(EJEMPLOS)), EJEMPLOS):
    if col.button(etiqueta, use_container_width=True):
        st.session_state.ruc = valor

foto = st.file_uploader("…o sube una foto de la factura (extraigo el RUC con IA)",
                        type=["png", "jpg", "jpeg"])
if foto is not None:
    _fid = getattr(foto, "file_id", None) or f"{foto.name}-{getattr(foto, 'size', '')}"
    if st.session_state.get("_foto_id") != _fid:
        st.session_state["_foto_id"] = _fid
        with st.spinner("Leyendo el RUC de la factura…"):
            _ruc_ocr = extraer_ruc(foto.getvalue(), foto.type)
        if _ruc_ocr:
            st.session_state.ruc = _ruc_ocr
            st.success(f"RUC detectado en la factura: **{_ruc_ocr}**")
        else:
            st.warning("No pude leer un RUC en la imagen. Escríbelo manualmente abajo.")

if st.button("Usar una factura de ejemplo (OCR)"):
    _ruta = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "docs", "ejemplo_factura.png")
    try:
        with open(_ruta, "rb") as _f:
            _datos = _f.read()
        with st.spinner("Leyendo el RUC de la factura de ejemplo…"):
            _ruc_ej = extraer_ruc(_datos, "image/png")
        if _ruc_ej:
            st.session_state.ruc = _ruc_ej
            st.success(f"RUC detectado en la factura de ejemplo: **{_ruc_ej}**")
        else:
            st.warning("No se pudo leer el RUC de la imagen de ejemplo.")
    except Exception:
        st.warning("No encontré la factura de ejemplo.")

ruc = st.text_input("RUC (11 dígitos)", key="ruc", max_chars=11,
                    placeholder="Ej. 20607648272")
st.button("Verificar", type="primary", use_container_width=True)

if ruc and ruc.strip():
    rep = verificar_ruc(ruc)
    _mostrar(rep, generar_reporte(rep))

st.divider()
st.caption(
    "Datos: SUNAT (lista SSCO y padrón RUC) y OSCE/OECE. El demo corre sobre una "
    "muestra cacheada. · [Repositorio](https://github.com/DiegoTurpo/verifica-pe)")
