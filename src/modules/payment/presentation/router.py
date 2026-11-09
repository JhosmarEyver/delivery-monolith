from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.modules.payment.application.dtos import EstadoPago, PagoCrearDTO
from src.modules.payment.application.services import PaymentService
from src.modules.payment.domain.exceptions import (
    DomainException,
    OperacionNoPermitidaException,
    PagoRechazadoException,
    RecursoNoEncontradoException,
)
from src.modules.payment.infrastructure.external_adapters import PasarelaPagoSimulada, PedidoOrderAdapter
from src.modules.payment.infrastructure.repository_impl import PagoRepositorySqlAlchemy
from src.modules.payment.presentation.schemas import PagoResponse

router = APIRouter()


def get_payment_service(db: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(
        pagos=PagoRepositorySqlAlchemy(db),
        pedidos=PedidoOrderAdapter(db),
        pasarela=PasarelaPagoSimulada(),
    )


def _a_http(e: DomainException) -> HTTPException:
    if isinstance(e, RecursoNoEncontradoException):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(e, OperacionNoPermitidaException):
        code = status.HTTP_409_CONFLICT
    elif isinstance(e, PagoRechazadoException):
        code = status.HTTP_402_PAYMENT_REQUIRED
    else:
        code = status.HTTP_400_BAD_REQUEST
    return HTTPException(status_code=code, detail=str(e))


@router.get("/health")
def payment_health():
    return {"module": "payment", "status": "ok"}


@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def procesar_pago(data: PagoCrearDTO, service: PaymentService = Depends(get_payment_service)):
    try:
        return service.procesar_pago(data)
    except DomainException as e:
        raise _a_http(e)


@router.get("/", response_model=List[PagoResponse])
def listar_pagos(
    estado: Optional[EstadoPago] = None, service: PaymentService = Depends(get_payment_service)
):
    return service.listar_pagos(estado)


@router.get("/pedido/{pedido_id}", response_model=PagoResponse)
def obtener_pago_por_pedido(pedido_id: int, service: PaymentService = Depends(get_payment_service)):
    try:
        return service.obtener_pago_por_pedido(pedido_id)
    except DomainException as e:
        raise _a_http(e)


@router.get("/{pago_id}", response_model=PagoResponse)
def obtener_pago(pago_id: int, service: PaymentService = Depends(get_payment_service)):
    try:
        return service.obtener_pago(pago_id)
    except DomainException as e:
        raise _a_http(e)


@router.patch("/{pago_id}/confirmar", response_model=PagoResponse)
def confirmar_pago_efectivo(pago_id: int, service: PaymentService = Depends(get_payment_service)):
    try:
        return service.confirmar_pago_efectivo(pago_id)
    except DomainException as e:
        raise _a_http(e)
