from abc import ABC, abstractmethod
from typing import Optional, List
from src.modules.auth.infrastructure.models_db import UsuarioModel

class IAuthRepository(ABC):
    
    @abstractmethod
    def obtener_por_id(self, usuario_id: int) -> Optional[UsuarioModel]:
        pass

    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[UsuarioModel]:
        pass

    @abstractmethod
    def guardar(self, usuario: UsuarioModel) -> UsuarioModel:
        pass

    @abstractmethod
    def listar_todos(self) -> List[UsuarioModel]:
        pass