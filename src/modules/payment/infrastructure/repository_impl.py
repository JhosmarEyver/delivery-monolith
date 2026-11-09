from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.modules.payment.domain.exceptions import PagoDuplicadoException, PagoNoEncontradoException
from src.modules.payment.domain.models import Pago
from src.modules.payment.domain.repositories import IPagoRepository
from src.modules.payment.infrastructure.models_db import PagoModel


class PagoRepositorySqlAlchemy(IPagoRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(model: Optional[PagoModel]) -> Optional[Pago]:
        if not model:
            return None
        return Pago(
            pago_id=model.pago_id,
            pedido_id=model.pedido_id,
            monto=model.monto,
            metodo_pago=model.metodo_pago,
            estado_pago=model.estado_pago,
            transaccion_id=model.transaccion_id,
            fecha=model.fecha,
        )

    def obtener_por_id(self, pago_id: int) -> Optional[Pago]:
        return self._to_domain(self.db.get(PagoModel, pago_id))

    def obtener_por_pedido(self, pedido_id: int) -> Optional[Pago]:
        model = self.db.query(PagoModel).filter(PagoModel.pedido_id == pedido_id).first()
        return self._to_domain(model)

    def listar(self, estado: Optional[str] = None) -> List[Pago]:
        query = self.db.query(PagoModel)
        if estado:
            query = query.filter(PagoModel.estado_pago == estado)
        return [self._to_domain(m) for m in query.order_by(PagoModel.pago_id.desc()).all()]

    def guardar(self, pago: Pago) -> Pago:
        if pago.pago_id:
            model = self.db.get(PagoModel, pago.pago_id)
            if not model:
                raise PagoNoEncontradoException(f"No existe el pago {pago.pago_id}.")
        else:
            model = PagoModel(pedido_id=pago.pedido_id)
            self.db.add(model)

        model.monto = pago.monto
        model.metodo_pago = pago.metodo_pago
        model.estado_pago = pago.estado_pago
        model.transaccion_id = pago.transaccion_id
        model.fecha = pago.fecha

        try:
            self.db.commit()
        except IntegrityError as e:
            # pedido_id y transaccion_id son UNIQUE en init.sql
            self.db.rollback()
            raise PagoDuplicadoException(f"Ya existe un pago registrado para el pedido {pago.pedido_id}.") from e
        self.db.refresh(model)
        return self._to_domain(model)
