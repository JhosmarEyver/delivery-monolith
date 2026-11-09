from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.tracking.application.dtos import DisponibilidadDTO, RepartidorDTO, UbicacionDTO
from src.modules.tracking.application.services import TrackingService
from src.modules.tracking.domain.exceptions import (
    DomainException,
    OperacionNoPermitidaException,
    RecursoNoEncontradoException,
)
from src.modules.tracking.infrastructure.repository_impl import (
    RepartidorRepositorySqlAlchemy,
    UbicacionRepositorySqlAlchemy,
)
from src.modules.tracking.presentation.schemas import RepartidorResponse, UbicacionResponse

router = APIRouter()


def get_tracking_service(db: Session = Depends(get_db)) -> TrackingService:
    return TrackingService(RepartidorRepositorySqlAlchemy(db), UbicacionRepositorySqlAlchemy(db))


def _a_http(e: DomainException) -> HTTPException:
    if isinstance(e, RecursoNoEncontradoException):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(e, OperacionNoPermitidaException):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=str(e))


@router.get("/health")
def tracking_health():
    return {"module": "tracking", "status": "ok"}


# ======================= Repartidores =======================

@router.post("/repartidores", response_model=RepartidorResponse, status_code=status.HTTP_201_CREATED)
def crear_repartidor(data: RepartidorDTO, service: TrackingService = Depends(get_tracking_service)):
    try:
        return service.crear_repartidor(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores", response_model=List[RepartidorResponse])
def listar_repartidores(
    disponible: Optional[bool] = None, service: TrackingService = Depends(get_tracking_service)
):
    return service.listar_repartidores(disponible)


@router.get("/repartidores/{repartidor_id}", response_model=RepartidorResponse)
def obtener_repartidor(repartidor_id: int, service: TrackingService = Depends(get_tracking_service)):
    try:
        return service.obtener_repartidor(repartidor_id)
    except DomainException as e:
        raise _a_http(e)


@router.put("/repartidores/{repartidor_id}", response_model=RepartidorResponse)
def actualizar_repartidor(
    repartidor_id: int, data: RepartidorDTO, service: TrackingService = Depends(get_tracking_service)
):
    try:
        return service.actualizar_repartidor(repartidor_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/repartidores/{repartidor_id}/disponibilidad", response_model=RepartidorResponse)
def cambiar_disponibilidad(
    repartidor_id: int, data: DisponibilidadDTO, service: TrackingService = Depends(get_tracking_service)
):
    try:
        return service.cambiar_disponibilidad(repartidor_id, data.disponible)
    except DomainException as e:
        raise _a_http(e)


@router.delete("/repartidores/{repartidor_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_repartidor(repartidor_id: int, service: TrackingService = Depends(get_tracking_service)):
    try:
        service.eliminar_repartidor(repartidor_id)
    except DomainException as e:
        raise _a_http(e)


# ======================= Ubicaciones GPS =======================

@router.post(
    "/repartidores/{repartidor_id}/ubicaciones",
    response_model=UbicacionResponse,
    status_code=status.HTTP_201_CREATED,
)
def registrar_ubicacion(
    repartidor_id: int, data: UbicacionDTO, service: TrackingService = Depends(get_tracking_service)
):
    try:
        return service.registrar_ubicacion(repartidor_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores/{repartidor_id}/ubicaciones", response_model=List[UbicacionResponse])
def obtener_historial(
    repartidor_id: int,
    limite: int = Query(50, ge=1, le=500),
    service: TrackingService = Depends(get_tracking_service),
):
    try:
        return service.obtener_historial(repartidor_id, limite)
    except DomainException as e:
        raise _a_http(e)


@router.get("/repartidores/{repartidor_id}/ubicacion-actual", response_model=UbicacionResponse)
def obtener_ubicacion_actual(repartidor_id: int, service: TrackingService = Depends(get_tracking_service)):
    try:
        return service.obtener_ubicacion_actual(repartidor_id)
    except DomainException as e:
        raise _a_http(e)
