from abc import ABC, abstractmethod
from typing import List, Optional

from src.modules.tracking.domain.models import Repartidor, UbicacionTracking


class IRepartidorRepository(ABC):
    """Contrato de persistencia de repartidores."""

    @abstractmethod
    def obtener_por_id(self, repartidor_id: int) -> Optional[Repartidor]:
        pass

    @abstractmethod
    def listar(self, disponible: Optional[bool] = None) -> List[Repartidor]:
        pass

    @abstractmethod
    def guardar(self, repartidor: Repartidor) -> Repartidor:
        pass

    @abstractmethod
    def eliminar(self, repartidor_id: int) -> None:
        pass


class IUbicacionRepository(ABC):
    """Contrato de persistencia de ubicaciones GPS."""

    @abstractmethod
    def guardar(self, ubicacion: UbicacionTracking) -> UbicacionTracking:
        pass

    @abstractmethod
    def listar_por_repartidor(self, repartidor_id: int, limite: int = 50) -> List[UbicacionTracking]:
        pass

    @abstractmethod
    def obtener_ultima(self, repartidor_id: int) -> Optional[UbicacionTracking]:
        pass
