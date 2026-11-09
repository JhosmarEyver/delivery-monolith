"""Schemas de respuesta HTTP del módulo order."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.core.types import Dinero


class DetallePedidoResponse(BaseModel):
    detalle_pedido_id: int
    producto_id: int
    cantidad: int
    precio_unitario: Dinero
    subtotal: Dinero


class PedidoResponse(BaseModel):
    pedido_id: int
    fecha_hora: datetime
    estado: str
    sum_total: Dinero
    notas_cliente: Optional[str] = None
    tiempo_estimado_min: int
    permite_cancelacion: bool
    usuario_id: int
    restaurant_id: int
    repartidor_id: Optional[int] = None
    detalles: List[DetallePedidoResponse]
