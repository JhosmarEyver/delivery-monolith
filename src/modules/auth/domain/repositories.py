from abc import ABC, abstractmethod
from typing import Optional, List

from src.modules.auth.domain.models import Usuario


class IAuthRepository(ABC):
    """Contrato del repositorio: solo conoce entidades de dominio, no SQLAlchemy."""

    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        pass

    @abstractmethod
    def guardar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def listar_todos(self) -> List[Usuario]:
        pass
