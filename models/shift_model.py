# models/shift_model.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class DetalleEfectivo:
    denominacion: int
    cantidad: int
    subtotal: float


@dataclass
class AperturaTurno:
    id_usuario_fk: int
    fecha_hora_apertura: datetime
    monto_inicial: float
    observacion: str
    detalles: List[DetalleEfectivo]
    id_apertura: Optional[int] = None
    estado: str = "ABIERTO"


@dataclass
class CierreTurno:
    id_apertura: int
    id_usuario_cierre_fk: int
    fecha_hora_cierre: datetime
    monto_contado: float
    monto_esperado: float
    diferencia: float
    observacion: str
    detalles_cierre: List[DetalleEfectivo]