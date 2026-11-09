"""Adaptadores del módulo payment hacia el módulo order y hacia la pasarela de pago."""
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from src.modules.payment.domain.models import PedidoInfo, ResultadoPasarela
from src.modules.payment.domain.repositories import IPasarelaPago, IPedidoGateway

# Módulo order
from src.modules.order.application.services import OrderService
from src.modules.order.domain.exceptions import PedidoNoEncontradoException
from src.modules.order.infrastructure.external_adapters import (
    CatalogoRestaurantAdapter,
    RepartidorTrackingAdapter,
    UsuarioAuthAdapter,
)
from src.modules.order.infrastructure.repository_impl import PedidoRepositorySqlAlchemy


class PedidoOrderAdapter(IPedidoGateway):
    def __init__(self, db: Session):
        self._service = OrderService(
            pedidos=PedidoRepositorySqlAlchemy(db),
            catalogo=CatalogoRestaurantAdapter(db),
            usuarios=UsuarioAuthAdapter(db),
            repartidores=RepartidorTrackingAdapter(db),
        )

    def obtener_pedido(self, pedido_id: int) -> Optional[PedidoInfo]:
        try:
            pedido = self._service.obtener_pedido(pedido_id)
        except PedidoNoEncontradoException:
            return None
        return PedidoInfo(pedido_id=pedido.pedido_id, sum_total=pedido.sum_total, estado=pedido.estado)


class PasarelaPagoSimulada(IPasarelaPago):
    """Simula un proveedor de pagos externo (para el entorno académico siempre aprueba).

    Para integrar un proveedor real solo habría que crear otra clase que implemente
    IPasarelaPago e inyectarla en el router; el servicio no cambia.
    """

    def procesar(self, monto: Decimal, metodo_pago: str) -> ResultadoPasarela:
        if metodo_pago == "Efectivo":
            # El efectivo se cobra al entregar: queda Pendiente hasta que se confirme
            return ResultadoPasarela(aprobado=True, transaccion_id=None, mensaje="Pago contra entrega")
        transaccion_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        return ResultadoPasarela(aprobado=True, transaccion_id=transaccion_id, mensaje="Pago aprobado")
