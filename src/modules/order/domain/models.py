from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from src.modules.order.domain.exceptions import (
    DatosInvalidosException,
    OperacionNoPermitidaException,
    PedidoNoCancelableException,
    TransicionEstadoInvalidaException,
)

# Valores permitidos por el CHECK de la tabla pedido (init.sql)
ESTADOS_PEDIDO = ("Pendiente", "En_Preparacion", "En_Camino", "Entregado", "Cancelado")

# Máquina de estados del pedido: desde cada estado, a cuáles se puede pasar
TRANSICIONES = {
    "Pendiente": ("En_Preparacion", "Cancelado"),
    "En_Preparacion": ("En_Camino",),
    "En_Camino": ("Entregado",),
    "Entregado": (),
    "Cancelado": (),
}


@dataclass
class DetallePedido:
    """Línea del pedido. El subtotal siempre se calcula, nunca lo envía el cliente."""
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    detalle_pedido_id: Optional[int] = None
    pedido_id: Optional[int] = None
    subtotal: Decimal = field(init=False, default=Decimal("0.00"))

    def __post_init__(self):
        if self.cantidad <= 0:
            raise DatosInvalidosException("La cantidad de cada producto debe ser mayor a 0.")
        self.subtotal = Decimal(self.precio_unitario) * self.cantidad


@dataclass
class Pedido:
    """Raíz de agregado: el pedido controla sus detalles y su ciclo de vida."""
    usuario_id: int
    restaurant_id: int
    detalles: List[DetallePedido] = field(default_factory=list)
    notas_cliente: Optional[str] = None
    estado: str = "Pendiente"
    sum_total: Decimal = Decimal("0.00")
    tiempo_estimado_min: int = 30
    permite_cancelacion: bool = True
    repartidor_id: Optional[int] = None
    fecha_hora: Optional[datetime] = None
    pedido_id: Optional[int] = None

    @classmethod
    def crear(cls, usuario_id: int, restaurant_id: int, detalles: List[DetallePedido],
              notas_cliente: Optional[str] = None) -> "Pedido":
        if not detalles:
            raise DatosInvalidosException("El pedido debe tener al menos un producto.")
        pedido = cls(
            usuario_id=usuario_id,
            restaurant_id=restaurant_id,
            detalles=detalles,
            notas_cliente=notas_cliente,
            fecha_hora=datetime.now(),
        )
        pedido.calcular_total()
        return pedido

    def calcular_total(self) -> Decimal:
        self.sum_total = sum((d.subtotal for d in self.detalles), Decimal("0.00"))
        return self.sum_total

    def cambiar_estado(self, nuevo_estado: str):
        if nuevo_estado not in ESTADOS_PEDIDO:
            raise DatosInvalidosException(f"Estado inválido: {nuevo_estado}. Use {ESTADOS_PEDIDO}.")
        if nuevo_estado not in TRANSICIONES[self.estado]:
            raise TransicionEstadoInvalidaException(
                f"No se puede pasar de '{self.estado}' a '{nuevo_estado}'. "
                f"Permitidos: {TRANSICIONES[self.estado] or 'ninguno'}."
            )
        if nuevo_estado == "Cancelado" and not self.permite_cancelacion:
            raise PedidoNoCancelableException("Este pedido ya no se puede cancelar.")
        if nuevo_estado == "En_Camino" and not self.repartidor_id:
            raise OperacionNoPermitidaException("Asigne un repartidor antes de enviar el pedido.")

        self.estado = nuevo_estado
        # Regla de negocio: una vez que el restaurante empieza a preparar, ya no se cancela
        if nuevo_estado != "Pendiente":
            self.permite_cancelacion = False

    def cancelar(self):
        self.cambiar_estado("Cancelado")

    def asignar_repartidor(self, repartidor_id: int):
        if self.estado not in ("Pendiente", "En_Preparacion"):
            raise OperacionNoPermitidaException(
                f"No se puede asignar repartidor a un pedido en estado '{self.estado}'."
            )
        if self.repartidor_id:
            raise OperacionNoPermitidaException(
                f"El pedido ya tiene asignado el repartidor {self.repartidor_id}."
            )
        self.repartidor_id = repartidor_id

    def esta_finalizado(self) -> bool:
        return self.estado in ("Entregado", "Cancelado")


# ----- Objetos de valor que el módulo order recibe de otros módulos (vía adaptadores) -----

@dataclass(frozen=True)
class RestauranteInfo:
    restaurant_id: int
    abierto: bool


@dataclass(frozen=True)
class ProductoInfo:
    producto_id: int
    restaurant_id: int
    nombre: str
    precio: Decimal
    disponible: bool
