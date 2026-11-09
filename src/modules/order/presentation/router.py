from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.order.application.dtos import (
    AsignarRepartidorDTO,
    CambiarEstadoDTO,
    EstadoPedido,
    PedidoCrearDTO,
)
from src.modules.order.application.services import OrderService
from src.modules.order.domain.exceptions import (
    DomainException,
    OperacionNoPermitidaException,
    RecursoNoEncontradoException,
)
from src.modules.order.infrastructure.external_adapters import (
    CatalogoRestaurantAdapter,
    RepartidorTrackingAdapter,
    UsuarioAuthAdapter,
)
from src.modules.order.infrastructure.repository_impl import PedidoRepositorySqlAlchemy
from src.modules.order.presentation.schemas import PedidoResponse

router = APIRouter()


def get_order_service(db: Session = Depends(get_db)) -> OrderService:
    """Inyección de dependencias: repositorio propio + adaptadores hacia otros módulos."""
    return OrderService(
        pedidos=PedidoRepositorySqlAlchemy(db),
        catalogo=CatalogoRestaurantAdapter(db),
        usuarios=UsuarioAuthAdapter(db),
        repartidores=RepartidorTrackingAdapter(db),
    )


def _a_http(e: DomainException) -> HTTPException:
    if isinstance(e, RecursoNoEncontradoException):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(e, OperacionNoPermitidaException):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=str(e))


# Va antes de /{pedido_id} para que esa ruta no lo capture
@router.get("/health")
def order_health():
    return {"module": "order", "status": "ok"}


@router.post("/", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED)
def crear_pedido(data: PedidoCrearDTO, service: OrderService = Depends(get_order_service)):
    try:
        return service.crear_pedido(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/", response_model=List[PedidoResponse])
def listar_pedidos(
    usuario_id: Optional[int] = None,
    estado: Optional[EstadoPedido] = None,
    service: OrderService = Depends(get_order_service),
):
    return service.listar_pedidos(usuario_id, estado)


@router.get("/{pedido_id}", response_model=PedidoResponse)
def obtener_pedido(pedido_id: int, service: OrderService = Depends(get_order_service)):
    try:
        return service.obtener_pedido(pedido_id)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/{pedido_id}/estado", response_model=PedidoResponse)
def cambiar_estado(pedido_id: int, data: CambiarEstadoDTO, service: OrderService = Depends(get_order_service)):
    try:
        return service.cambiar_estado(pedido_id, data.estado)
    except DomainException as e:
        raise _a_http(e)


@router.post("/{pedido_id}/cancelar", response_model=PedidoResponse)
def cancelar_pedido(pedido_id: int, service: OrderService = Depends(get_order_service)):
    try:
        return service.cancelar_pedido(pedido_id)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/{pedido_id}/repartidor", response_model=PedidoResponse)
def asignar_repartidor(
    pedido_id: int, data: AsignarRepartidorDTO, service: OrderService = Depends(get_order_service)
):
    try:
        return service.asignar_repartidor(pedido_id, data.repartidor_id)
    except DomainException as e:
        raise _a_http(e)
