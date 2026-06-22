"""Motor de verificación — la función central `verificar_ruc()`.

Python puro, independiente de Streamlit. Arma el perfil cruzando las 3 fuentes
(padrón RUC, SSCO, OSCE) y aplica las reglas transparentes del semáforo. La UI
solo lo invoca y pinta; el reporte en lenguaje natural (Gemini) es un paso aparte.

Uso rápido por consola:
    python -m core.verificador 20607648272
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import fuentes, riesgo
from .riesgo import Senal

INVALIDO = "INVALIDO"


@dataclass
class ReporteVerificacion:
    ruc: str
    valido: bool                       # el formato del RUC es válido
    encontrado: bool                   # existe en alguna de las 3 fuentes
    razon_social: str = ""
    estado: str = ""                   # del padrón (ACTIVO / BAJA / SUSPENSION...)
    condicion: str = ""                # del padrón (HABIDO / NO HABIDO...)
    departamento: str = ""
    en_ssco: bool = False
    ssco: dict | None = None
    osce: list = field(default_factory=list)
    nivel: str = riesgo.DESCONOCIDO    # ROJO / AMBAR / VERDE / DESCONOCIDO / INVALIDO
    senales: list = field(default_factory=list)

    @property
    def motivos(self) -> list[str]:
        """Lista plana de mensajes (para mostrar o pasar al LLM)."""
        return [s.mensaje for s in self.senales]


def _solo_digitos(texto: str) -> str:
    return "".join(c for c in (texto or "") if c.isdigit())


def verificar_ruc(ruc: str) -> ReporteVerificacion:
    """Verifica un RUC contra las 3 fuentes y devuelve un reporte con semáforo."""
    limpio = _solo_digitos(ruc)
    if len(limpio) != 11:
        return ReporteVerificacion(
            ruc=limpio or (ruc or ""), valido=False, encontrado=False,
            nivel=INVALIDO,
            senales=[Senal(INVALIDO, "formato",
                           "El RUC debe tener 11 dígitos numéricos.")])

    padron = fuentes.buscar_padron(limpio)
    ssco = fuentes.buscar_ssco(limpio)
    osce = fuentes.buscar_osce(limpio)

    rep = ReporteVerificacion(
        ruc=limpio, valido=True, encontrado=bool(padron or ssco or osce), osce=osce)

    if padron:
        rep.razon_social = padron.get("razon_social") or ""
        rep.estado = padron.get("estado") or ""
        rep.condicion = padron.get("condicion") or ""
        rep.departamento = padron.get("departamento") or ""
    if ssco:
        rep.en_ssco = True
        rep.ssco = ssco
        rep.razon_social = rep.razon_social or (ssco.get("razon_social") or "")
        rep.departamento = rep.departamento or (ssco.get("departamento") or "")
    if not rep.razon_social and osce:
        rep.razon_social = osce[0].get("razon_social") or ""

    rep.nivel, rep.senales = riesgo.evaluar(rep)
    return rep


if __name__ == "__main__":
    import sys

    objetivo = sys.argv[1] if len(sys.argv) > 1 else "20607648272"
    r = verificar_ruc(objetivo)
    print(f"RUC {r.ruc}  ->  {r.nivel}")
    if r.razon_social:
        print(f"  {r.razon_social}")
    for s in r.senales:
        print(f"  [{s.nivel}/{s.fuente}] {s.mensaje}")
