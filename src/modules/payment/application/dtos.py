"""DTOs de entrada del módulo payment."""
from typing import Literal

from pydantic import BaseModel

MetodoPago = Literal["Efectivo", "Tarjeta", "QR"]
EstadoPago = Literal["Completado", "Fallido", "Pendiente"]


class PagoCrearDTO(BaseModel):
    # El monto NO se recibe del cliente: se cobra el total calculado del pedido
    pedido_id: int
    metodo_pago: MetodoPago
