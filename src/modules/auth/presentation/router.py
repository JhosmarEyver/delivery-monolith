from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.core.database import get_db
from src.modules.auth.presentation.schemas import UsuarioCreate, UsuarioResponse
from src.modules.auth.application.services import AuthService
from src.modules.auth.domain.exceptions import DomainException

router = APIRouter()

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(data: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        usuario_creado = service.registrar_usuario(data)
        return usuario_creado
    except DomainException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))