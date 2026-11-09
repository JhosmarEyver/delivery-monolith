from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.restaurant.application.dtos import ProductoDTO, RestauranteDTO
from src.modules.restaurant.application.services import RestaurantService
from src.modules.restaurant.domain.exceptions import (
    DomainException,
    OperacionNoPermitidaException,
    RecursoNoEncontradoException,
)
from src.modules.restaurant.infrastructure.repository_impl import (
    ProductoRepositorySqlAlchemy,
    RestauranteRepositorySqlAlchemy,
)
from src.modules.restaurant.presentation.schemas import ProductoResponse, RestauranteResponse

router = APIRouter()


def get_restaurant_service(db: Session = Depends(get_db)) -> RestaurantService:
    """Inyección de dependencias: conecta los repositorios concretos con el servicio."""
    return RestaurantService(RestauranteRepositorySqlAlchemy(db), ProductoRepositorySqlAlchemy(db))


def _a_http(e: DomainException) -> HTTPException:
    """Traduce errores de dominio a códigos HTTP."""
    if isinstance(e, RecursoNoEncontradoException):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(e, OperacionNoPermitidaException):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=str(e))


@router.get("/health")
def restaurant_health():
    return {"module": "restaurant", "status": "ok"}


# ======================= Restaurantes =======================

@router.post("/", response_model=RestauranteResponse, status_code=status.HTTP_201_CREATED)
def crear_restaurante(data: RestauranteDTO, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        return service.crear_restaurante(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/", response_model=List[RestauranteResponse])
def listar_restaurantes(
    estado: Optional[Literal["Abierto", "Cerrado"]] = None,
    service: RestaurantService = Depends(get_restaurant_service),
):
    return service.listar_restaurantes(estado)


@router.get("/{restaurant_id}", response_model=RestauranteResponse)
def obtener_restaurante(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        return service.obtener_restaurante(restaurant_id)
    except DomainException as e:
        raise _a_http(e)


@router.put("/{restaurant_id}", response_model=RestauranteResponse)
def actualizar_restaurante(
    restaurant_id: int, data: RestauranteDTO, service: RestaurantService = Depends(get_restaurant_service)
):
    try:
        return service.actualizar_restaurante(restaurant_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_restaurante(restaurant_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        service.eliminar_restaurante(restaurant_id)
    except DomainException as e:
        raise _a_http(e)


# ======================= Productos =======================

@router.post(
    "/{restaurant_id}/productos", response_model=ProductoResponse, status_code=status.HTTP_201_CREATED
)
def agregar_producto(
    restaurant_id: int, data: ProductoDTO, service: RestaurantService = Depends(get_restaurant_service)
):
    try:
        return service.agregar_producto(restaurant_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/{restaurant_id}/productos", response_model=List[ProductoResponse])
def listar_productos(
    restaurant_id: int,
    solo_disponibles: bool = False,
    service: RestaurantService = Depends(get_restaurant_service),
):
    try:
        return service.listar_productos(restaurant_id, solo_disponibles)
    except DomainException as e:
        raise _a_http(e)


@router.get("/productos/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        return service.obtener_producto(producto_id)
    except DomainException as e:
        raise _a_http(e)


@router.put("/productos/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(
    producto_id: int, data: ProductoDTO, service: RestaurantService = Depends(get_restaurant_service)
):
    try:
        return service.actualizar_producto(producto_id, data)
    except DomainException as e:
        raise _a_http(e)


@router.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_producto(producto_id: int, service: RestaurantService = Depends(get_restaurant_service)):
    try:
        service.eliminar_producto(producto_id)
    except DomainException as e:
        raise _a_http(e)
