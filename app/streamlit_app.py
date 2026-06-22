"""Verifica — interfaz Streamlit (demo en vivo).

Ingresa un RUC → el motor (`core.verificador`) lo cruza con las 3 fuentes
públicas y pinta el semáforo de riesgo + las señales transparentes que lo
explican. La UI solo invoca al motor y pinta (lógica desacoplada).
"""
import os
import sys

# En Streamlit Cloud el script corre desde app/, así que agregamos la raíz del
# repo a sys.path para poder importar el paquete `core`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from core.reporte import generar_reporte
from core.verificador import verificar_ruc

st.set_page_config(page_title="Verifica", page_icon="🛡️", layout="centered")

# En Streamlit Cloud la API key de Gemini vive en Secrets; la exponemos como variable
# de entorno para que core.reporte la lea (sin acoplar el core a Streamlit).
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ.setdefault("GEMINI_API_KEY", st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

# RUCs REALES de la muestra, uno por color, para el demo en vivo.
EJEMPLOS = [
    ("🔴 Empresa fantasma", "20607648272"),
    ("🔴 No habido / OSCE", "20100994128"),
    ("🟡 Precaución", "10198565470"),
    ("🟢 Sin alertas", "10452159428"),
]

ICONO = {"ROJO": "🔴", "AMBAR": "🟡", "VERDE": "🟢"}


def _mostrar(rep, reporte) -> None:
    nivel = reporte.nivel
    if nivel == "INVALIDO":
        st.info("⚠️ El RUC debe tener **11 dígitos** numéricos.")
        return
    if nivel == "DESCONOCIDO":
        st.info(
            f"⚪ No encontramos el RUC **{rep.ruc}** en la muestra del demo. "
            "En producción se consultaría el padrón completo en la nube.")
        return

    titular = rep.razon_social or f"RUC {rep.ruc}"
    if nivel == "ROJO":
        st.error(f"🔴 **RIESGO ALTO** — {titular}")
    elif nivel == "AMBAR":
        st.warning(f"🟡 **PRECAUCIÓN** — {titular}")
    else:
        st.success(f"🟢 **SIN ALERTAS** — {titular}")

    # Reporte en lenguaje claro (Gemini; o reglas si no hay key / falla).
    st.markdown(reporte.texto)
    if reporte.observaciones:
        st.markdown("**Observaciones adicionales:**")
        for o in reporte.observaciones:
            st.markdown(f"- {o}")

    with st.expander("Criterios detectados y fuentes"):
        for s in rep.senales:
            st.markdown(
                f"{ICONO.get(s.nivel, '•')} {s.mensaje}  \n"
                f"<span style='color:gray;font-size:0.8em'>fuente: {s.fuente}</span>",
                unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f"- **RUC:** {rep.ruc}")
        if rep.estado:
            st.markdown(f"- **Estado (SUNAT):** {rep.estado}")
        if rep.condicion:
            st.markdown(f"- **Condición de domicilio:** {rep.condicion}")
        if rep.departamento:
            st.markdown(f"- **Departamento:** {rep.departamento}")
        st.markdown(f"- **En lista SSCO:** {'sí' if rep.en_ssco else 'no'}")
        st.markdown(f"- **Sanciones OSCE registradas:** {len(rep.osce)}")
        st.caption(f"Reporte generado por: {reporte.motor}")


st.title("🛡️ Verifica")
st.markdown(
    "¿La empresa con la que vas a hacer negocios es **legítima o un riesgo de "
    "fraude**? Ingresa un RUC y lo cruzamos con las empresas fantasma de SUNAT "
    "(**SSCO**), el **padrón RUC** y los sancionados del **OSCE** — en segundos.")

if "ruc" not in st.session_state:
    st.session_state.ruc = ""

st.caption("Prueba con un caso real:")
for col, (etiqueta, valor) in zip(st.columns(len(EJEMPLOS)), EJEMPLOS):
    if col.button(etiqueta, use_container_width=True):
        st.session_state.ruc = valor

ruc = st.text_input("RUC (11 dígitos)", key="ruc", max_chars=11,
                    placeholder="Ej. 20607648272")
st.button("Verificar", type="primary", use_container_width=True)

if ruc and ruc.strip():
    rep = verificar_ruc(ruc)
    _mostrar(rep, generar_reporte(rep))

st.divider()
st.caption(
    "Datos: SUNAT (lista SSCO y padrón RUC) y OSCE/OECE. El demo corre sobre una "
    "muestra cacheada. · "
    "[Repositorio](https://github.com/DiegoTurpo/verifica-pe)")
