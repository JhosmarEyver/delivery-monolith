"""Schemas de respuesta HTTP del módulo payment."""
from datetime import date
from typing import Optional

from pydantic import BaseModel

from src.core.types import Dinero


class PagoResponse(BaseModel):
    pago_id: int
    pedido_id: int
    monto: Dinero
    metodo_pago: str
    estado_pago: str
    transaccion_id: Optional[str] = None
    fecha: date
