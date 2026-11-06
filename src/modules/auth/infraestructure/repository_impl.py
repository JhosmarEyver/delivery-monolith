from sqlalchemy.orm import Session
from typing import Optional
from src.modules.auth.domain.repositories import IAuthRepository
from src.modules.auth.domain.models import Usuario
from src.modules.auth.infrastructure.models_db import UsuarioModel

class AuthRepositorySqlAlchemy(IAuthRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_domain(self, model: UsuarioModel) -> Optional[Usuario]:
        """Convierte un modelo ORM de BD a una Entidad Pura de Dominio."""
        if not model:
            return None
        return Usuario(
            usuario_id=model.usuario_id,
            nombre_usuario=model.nombre_usuario,
            email=model.email,
            contrasenia=model.contrasenia,
            rol_id=model.rol_id,
            estado_id=model.estado_id
        )

    def obtener_por_id(self, usuario_id: int) -> Optional[Usuario]:
        db_model = self.db.query(UsuarioModel).filter(UsuarioModel.usuario_id == usuario_id).first()
        return self._to_domain(db_model)

    def obtener_por_email(self, email: str) -> Optional[Usuario]:
        db_model = self.db.query(UsuarioModel).filter(UsuarioModel.email == email).first()
        return self._to_domain(db_model)

    def guardar(self, usuario: Usuario) -> Usuario:
        # Si ya tiene ID, actualizamos; si no, creamos el modelo de BD
        if usuario.usuario_id:
            db_model = self.db.query(UsuarioModel).filter(UsuarioModel.usuario_id == usuario.usuario_id).first()
            if db_model:
                db_model.nombre_usuario = usuario.nombre_usuario
                db_model.email = usuario.email
                db_model.contrasenia = usuario.contrasenia
                db_model.rol_id = usuario.rol_id
                db_model.estado_id = usuario.estado_id
        else:
            db_model = UsuarioModel(
                nombre_usuario=usuario.nombre_usuario,
                email=usuario.email,
                contrasenia=usuario.contrasenia,
                rol_id=usuario.rol_id,
                estado_id=usuario.estado_id
            )
            self.db.add(db_model)
        
        self.db.commit()
        self.db.refresh(db_model)
        return self._to_domain(db_model)