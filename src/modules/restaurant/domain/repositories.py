from abc import ABC, abstractmethod
from typing import List, Optional

from src.modules.restaurant.domain.models import Producto, Restaurante


class IRestauranteRepository(ABC):
    """Contrato de persistencia de restaurantes (no depende de SQLAlchemy)."""

    @abstractmethod
    def obtener_por_id(self, restaurant_id: int) -> Optional[Restaurante]:
        pass

    @abstractmethod
    def listar(self, estado: Optional[str] = None) -> List[Restaurante]:
        pass

    @abstractmethod
    def guardar(self, restaurante: Restaurante) -> Restaurante:
        pass

    @abstractmethod
    def eliminar(self, restaurant_id: int) -> None:
        pass


class IProductoRepository(ABC):
    """Contrato de persistencia de productos."""

    @abstractmethod
    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        pass

    @abstractmethod
    def listar_por_restaurante(self, restaurant_id: int, solo_disponibles: bool = False) -> List[Producto]:
        pass

    @abstractmethod
    def guardar(self, producto: Producto) -> Producto:
        pass

    @abstractmethod
    def eliminar(self, producto_id: int) -> None:
        pass
