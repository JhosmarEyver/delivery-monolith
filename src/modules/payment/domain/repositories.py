from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from src.modules.payment.domain.models import Pago, PedidoInfo, ResultadoPasarela


class IPagoRepository(ABC):
    """Contrato de persistencia de pagos."""

    @abstractmethod
    def obtener_por_id(self, pago_id: int) -> Optional[Pago]:
        pass

    @abstractmethod
    def obtener_por_pedido(self, pedido_id: int) -> Optional[Pago]:
        pass

    @abstractmethod
    def listar(self, estado: Optional[str] = None) -> List[Pago]:
        pass

    @abstractmethod
    def guardar(self, pago: Pago) -> Pago:
        pass


# ----- Puertos hacia otros módulos / servicios externos -----

class IPedidoGateway(ABC):
    """Consulta pedidos al módulo order."""

    @abstractmethod
    def obtener_pedido(self, pedido_id: int) -> Optional[PedidoInfo]:
        pass


class IPasarelaPago(ABC):
    """Pasarela de cobro externa (banco, QR, etc.)."""

    @abstractmethod
    def procesar(self, monto: Decimal, metodo_pago: str) -> ResultadoPasarela:
        pass
