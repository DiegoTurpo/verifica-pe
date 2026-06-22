"""Motor de verificación de Verifica (Python puro, independiente de Streamlit)."""
from .verificador import ReporteVerificacion, verificar_ruc  # noqa: F401

__all__ = ["verificar_ruc", "ReporteVerificacion"]
