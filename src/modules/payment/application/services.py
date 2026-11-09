from typing import List, Optional

from src.modules.payment.application.dtos import PagoCrearDTO
from src.modules.payment.domain.exceptions import (
    OperacionNoPermitidaException,
    PagoDuplicadoException,
    PagoNoEncontradoException,
    PagoRechazadoException,
    ReferenciaInvalidaException,
)
from src.modules.payment.domain.models import Pago
from src.modules.payment.domain.repositories import IPagoRepository, IPasarelaPago, IPedidoGateway


class PaymentService:
    """Casos de uso de cobro de pedidos."""

    def __init__(self, pagos: IPagoRepository, pedidos: IPedidoGateway, pasarela: IPasarelaPago):
        self.pagos = pagos
        self.pedidos = pedidos
        self.pasarela = pasarela

    def procesar_pago(self, data: PagoCrearDTO) -> Pago:
        # 1. El pedido debe existir y no estar cancelado
        pedido = self.pedidos.obtener_pedido(data.pedido_id)
        if not pedido:
            raise ReferenciaInvalidaException(f"No existe el pedido {data.pedido_id}.")
        if pedido.estado == "Cancelado":
            raise OperacionNoPermitidaException("No se puede pagar un pedido cancelado.")

        # 2. Un solo pago por pedido
        if self.pagos.obtener_por_pedido(data.pedido_id):
            raise PagoDuplicadoException(f"El pedido {data.pedido_id} ya tiene un pago registrado.")

        # 3. Cobrar en la pasarela el total del pedido
        resultado = self.pasarela.procesar(pedido.sum_total, data.metodo_pago)
        if not resultado.aprobado:
            raise PagoRechazadoException(f"Pago rechazado: {resultado.mensaje}")

        pago = Pago(pedido_id=data.pedido_id, monto=pedido.sum_total, metodo_pago=data.metodo_pago)
        if data.metodo_pago != "Efectivo":
            pago.completar(resultado.transaccion_id)
        return self.pagos.guardar(pago)

    def confirmar_pago_efectivo(self, pago_id: int) -> Pago:
        pago = self.obtener_pago(pago_id)
        if pago.metodo_pago != "Efectivo":
            raise OperacionNoPermitidaException("Solo los pagos en efectivo se confirman manualmente.")
        pago.completar()
        return self.pagos.guardar(pago)

    def obtener_pago(self, pago_id: int) -> Pago:
        pago = self.pagos.obtener_por_id(pago_id)
        if not pago:
            raise PagoNoEncontradoException(f"No existe el pago {pago_id}.")
        return pago

    def obtener_pago_por_pedido(self, pedido_id: int) -> Pago:
        pago = self.pagos.obtener_por_pedido(pedido_id)
        if not pago:
            raise PagoNoEncontradoException(f"El pedido {pedido_id} no tiene pagos registrados.")
        return pago

    def listar_pagos(self, estado: Optional[str] = None) -> List[Pago]:
        return self.pagos.listar(estado)
