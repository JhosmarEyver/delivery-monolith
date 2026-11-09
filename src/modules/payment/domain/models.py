from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Optional

from src.modules.payment.domain.exceptions import DatosInvalidosException, OperacionNoPermitidaException

# Valores permitidos por los CHECK de la tabla pago (init.sql)
METODOS_PAGO = ("Efectivo", "Tarjeta", "QR")
ESTADOS_PAGO = ("Completado", "Fallido", "Pendiente")


@dataclass
class Pago:
    """Entidad pura de dominio: el pago de un pedido (un pago por pedido)."""
    pedido_id: int
    monto: Decimal
    metodo_pago: str
    estado_pago: str = "Pendiente"
    transaccion_id: Optional[str] = None
    fecha: date = field(default_factory=date.today)
    pago_id: Optional[int] = None

    def __post_init__(self):
        if self.monto is None or Decimal(self.monto) <= 0:
            raise DatosInvalidosException("El monto del pago debe ser mayor a 0.")
        if self.metodo_pago not in METODOS_PAGO:
            raise DatosInvalidosException(f"Método de pago inválido: {self.metodo_pago}. Use {METODOS_PAGO}.")
        if self.estado_pago not in ESTADOS_PAGO:
            raise DatosInvalidosException(f"Estado de pago inválido: {self.estado_pago}.")

    def completar(self, transaccion_id: Optional[str] = None):
        if self.estado_pago == "Completado":
            raise OperacionNoPermitidaException("El pago ya está completado.")
        self.estado_pago = "Completado"
        if transaccion_id:
            self.transaccion_id = transaccion_id

    def marcar_fallido(self):
        self.estado_pago = "Fallido"


# ----- Objetos de valor -----

@dataclass(frozen=True)
class PedidoInfo:
    """Lo que payment necesita saber de un pedido (lo entrega el módulo order)."""
    pedido_id: int
    sum_total: Decimal
    estado: str


@dataclass(frozen=True)
class ResultadoPasarela:
    aprobado: bool
    transaccion_id: Optional[str]
    mensaje: str
