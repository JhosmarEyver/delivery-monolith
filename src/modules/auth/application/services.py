from typing import List

from src.modules.auth.domain.exceptions import EmailYaRegistradoException, UsuarioNoEncontradoException
from src.modules.auth.domain.models import Usuario
from src.modules.auth.domain.repositories import IAuthRepository
from src.modules.auth.presentation.schemas import UsuarioCreate


class AuthService:
    # El servicio depende del contrato (IAuthRepository), no de SQLAlchemy.
    # La implementación concreta se inyecta desde la capa de presentación.
    def __init__(self, repository: IAuthRepository):
        self.repository = repository

    def registrar_usuario(self, data: UsuarioCreate) -> Usuario:
        # 1. Regla de negocio: el email no puede estar registrado
        if self.repository.obtener_por_email(data.email):
            raise EmailYaRegistradoException(f"El correo {data.email} ya está registrado en el sistema.")

        # 2. Entidad pura de dominio (en un entorno real la contraseña se hashea con bcrypt)
        nuevo_usuario = Usuario(
            nombre_usuario=data.nombre_usuario,
            email=data.email,
            contrasenia=data.contrasenia,
            rol_id=data.rol_id,
            estado_id=data.estado_id,
        )

        # 3. Guardar mediante el contrato del repositorio
        return self.repository.guardar(nuevo_usuario)

    def obtener_usuario(self, usuario_id: int) -> Usuario:
        usuario = self.repository.obtener_por_id(usuario_id)
        if not usuario:
            raise UsuarioNoEncontradoException(f"No existe el usuario con id {usuario_id}.")
        return usuario

    def listar_usuarios(self) -> List[Usuario]:
        return self.repository.listar_todos()
