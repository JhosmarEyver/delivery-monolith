from abc import ABC, abstractmethod
from typing import List, Optional

from src.modules.order.domain.models import Pedido, ProductoInfo, RestauranteInfo


class IPedidoRepository(ABC):
    """Contrato de persistencia de pedidos (el agregado incluye sus detalles)."""

    @abstractmethod
    def obtener_por_id(self, pedido_id: int) -> Optional[Pedido]:
        pass

    @abstractmethod
    def listar(self, usuario_id: Optional[int] = None, estado: Optional[str] = None) -> List[Pedido]:
        pass

    @abstractmethod
    def guardar(self, pedido: Pedido) -> Pedido:
        pass


# ----- Puertos hacia otros módulos -----
# El módulo order NO consulta las tablas de otros módulos: les pregunta a través de
# estos contratos, implementados en infrastructure/external_adapters.py.

class ICatalogoGateway(ABC):
    @abstractmethod
    def obtener_restaurante(self, restaurant_id: int) -> Optional[RestauranteInfo]:
        pass

    @abstractmethod
    def obtener_producto(self, producto_id: int) -> Optional[ProductoInfo]:
        pass


class IUsuarioGateway(ABC):
    @abstractmethod
    def existe_usuario(self, usuario_id: int) -> bool:
        pass


class IRepartidorGateway(ABC):
    @abstractmethod
    def esta_disponible(self, repartidor_id: int) -> Optional[bool]:
        """True/False según disponibilidad, o None si el repartidor no existe."""
        pass

    @abstractmethod
    def ocupar(self, repartidor_id: int) -> None:
        pass

    @abstractmethod
    def liberar(self, repartidor_id: int) -> None:
        pass
