from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.auth.application.services import AuthService
from src.modules.auth.domain.exceptions import (
    DomainException,
    EmailYaRegistradoException,
    UsuarioNoEncontradoException,
)
from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy
from src.modules.auth.presentation.schemas import UsuarioCreate, UsuarioResponse

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Inyección de dependencias: aquí se conecta la implementación concreta del repositorio."""
    return AuthService(AuthRepositorySqlAlchemy(db))


@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(data: UsuarioCreate, service: AuthService = Depends(get_auth_service)):
    try:
        return service.registrar_usuario(data)
    except EmailYaRegistradoException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/users", response_model=List[UsuarioResponse])
def listar_usuarios(service: AuthService = Depends(get_auth_service)):
    return service.listar_usuarios()


@router.get("/users/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario(usuario_id: int, service: AuthService = Depends(get_auth_service)):
    try:
        return service.obtener_usuario(usuario_id)
    except UsuarioNoEncontradoException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
