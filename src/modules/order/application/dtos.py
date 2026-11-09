"""DTOs de entrada del módulo order."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

EstadoPedido = Literal["Pendiente", "En_Preparacion", "En_Camino", "Entregado", "Cancelado"]


class ItemPedidoDTO(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0, le=100)


class PedidoCrearDTO(BaseModel):
    # El precio y el total NO se reciben: el servidor los calcula desde el catálogo
    usuario_id: int
    restaurant_id: int
    notas_cliente: Optional[str] = Field(default=None, max_length=500)
    items: List[ItemPedidoDTO] = Field(min_length=1)


class CambiarEstadoDTO(BaseModel):
    estado: EstadoPedido


class AsignarRepartidorDTO(BaseModel):
    repartidor_id: int
