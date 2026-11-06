from sqlalchemy.orm import Session
from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy
from src.modules.auth.infrastructure.models_db import UsuarioModel
from src.modules.auth.domain.exceptions import EmailYaRegistradoException
from src.modules.auth.presentation.schemas import UsuarioCreate

class AuthService:
    def __init__(self, db: Session):
        self.repository = AuthRepositorySqlAlchemy(db)

    def registrar_usuario(self, data: UsuarioCreate) -> UsuarioModel:
        # 1. Regla de negocio: Verificar si el email ya existe
        usuario_existente = self.repository.obtener_por_email(data.email)
        if usuario_existente:
            raise EmailYaRegistradoException(f"El correo {data.email} ya está registrado en el sistema.")

        # 2. En un entorno real, aquí harías el hash de la contraseña (ej. passlib / bcrypt)
        contrasenia_hasheada = data.contrasenia # (Simulado por simplicidad académica)

        # 3. Crear la instancia del modelo ORM de infraestructura
        nuevo_usuario = UsuarioModel(
            nombre_usuario=data.nombre_usuario,
            email=data.email,
            contrasenia=contrasenia_hasheada,
            rol_id=data.rol_id,
            estado_id=data.estado_id
        )

        # 4. Guardar a través del repositorio
        return self.repository.guardar(nuevo_usuario)