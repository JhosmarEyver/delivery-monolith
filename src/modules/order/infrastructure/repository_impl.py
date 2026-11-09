from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.modules.order.domain.exceptions import (
    DatosInvalidosException,
    PedidoNoEncontradoException,
)
from src.modules.order.domain.models import DetallePedido, Pedido
from src.modules.order.domain.repositories import IPedidoRepository
from src.modules.order.infrastructure.models_db import DetallePedidoModel, PedidoModel


class PedidoRepositorySqlAlchemy(IPedidoRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(model: Optional[PedidoModel]) -> Optional[Pedido]:
        if not model:
            return None
        detalles = [
            DetallePedido(
                detalle_pedido_id=d.detalle_pedido_id,
                pedido_id=d.pedido_id,
                producto_id=d.producto_id,
                cantidad=d.cantidad,
                precio_unitario=d.precio_unitario,
            )
            for d in sorted(model.detalles, key=lambda d: d.detalle_pedido_id)
        ]
        return Pedido(
            pedido_id=model.pedido_id,
            fecha_hora=model.fecha_hora,
            sum_total=model.sum_total,
            notas_cliente=model.notas_cliente,
            estado=model.estado,
            tiempo_estimado_min=model.tiempo_estimado_min,
            permite_cancelacion=model.permite_cancelacion,
            usuario_id=model.usuario_id,
            restaurant_id=model.restaurant_id,
            repartidor_id=model.repartidor_id,
            detalles=detalles,
        )

    def obtener_por_id(self, pedido_id: int) -> Optional[Pedido]:
        return self._to_domain(self.db.get(PedidoModel, pedido_id))

    def listar(self, usuario_id: Optional[int] = None, estado: Optional[str] = None) -> List[Pedido]:
        query = self.db.query(PedidoModel)
        if usuario_id is not None:
            query = query.filter(PedidoModel.usuario_id == usuario_id)
        if estado:
            query = query.filter(PedidoModel.estado == estado)
        return [self._to_domain(m) for m in query.order_by(PedidoModel.pedido_id.desc()).all()]

    def guardar(self, pedido: Pedido) -> Pedido:
        if pedido.pedido_id:
            # Actualización: los detalles no cambian después de creado el pedido
            model = self.db.get(PedidoModel, pedido.pedido_id)
            if not model:
                raise PedidoNoEncontradoException(f"No existe el pedido {pedido.pedido_id}.")
            model.estado = pedido.estado
            model.permite_cancelacion = pedido.permite_cancelacion
            model.repartidor_id = pedido.repartidor_id
            model.notas_cliente = pedido.notas_cliente
            model.tiempo_estimado_min = pedido.tiempo_estimado_min
            model.sum_total = pedido.sum_total
        else:
            model = PedidoModel(
                fecha_hora=pedido.fecha_hora,
                sum_total=pedido.sum_total,
                notas_cliente=pedido.notas_cliente,
                estado=pedido.estado,
                tiempo_estimado_min=pedido.tiempo_estimado_min,
                permite_cancelacion=pedido.permite_cancelacion,
                usuario_id=pedido.usuario_id,
                restaurant_id=pedido.restaurant_id,
                repartidor_id=pedido.repartidor_id,
                detalles=[
                    DetallePedidoModel(
                        producto_id=d.producto_id,
                        cantidad=d.cantidad,
                        precio_unitario=d.precio_unitario,
                        subtotal=d.subtotal,
                    )
                    for d in pedido.detalles
                ],
            )
            self.db.add(model)

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise DatosInvalidosException("Los datos del pedido no cumplen las reglas de la base de datos.") from e
        self.db.refresh(model)
        return self._to_domain(model)
