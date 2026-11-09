
# modulo order
''' Modelos ORM de SQLAlchemy
========================================
Modelos ORM de las tablas pedido y detalle_pedido.
'''

from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from src.core.database import Base


class PedidoModel(Base):
    __tablename__ = "pedido"

    pedido_id = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(DateTime, nullable=False, server_default=func.now())
    sum_total = Column(Numeric(10, 2), nullable=False, default=0.00)
    notas_cliente = Column(Text)
    estado = Column(String(30), default="Pendiente")
    tiempo_estimado_min = Column(Integer, default=30)
    permite_cancelacion = Column(Boolean, default=True)

    usuario_id = Column(Integer, ForeignKey("usuario.usuario_id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurante.restaurant_id"), nullable=False)
    repartidor_id = Column(
        Integer,
        ForeignKey("repartidor.repartidor_id", ondelete="SET NULL"),
        nullable=True
    )

    # Relaciones ORM
    detalles = relationship(
        "DetallePedidoModel",
        back_populates="pedido",
        cascade="all, delete-orphan"
    )
    pago = relationship(
        "PagoModel",
        back_populates="pedido",
        uselist=False,
        cascade="all, delete-orphan"
    )


class DetallePedidoModel(Base):
    __tablename__ = "detalle_pedido"

    detalle_pedido_id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)

    pedido_id = Column(
        Integer,
        ForeignKey("pedido.pedido_id", ondelete="CASCADE"),
        nullable=False
    )
    producto_id = Column(
        Integer,
        ForeignKey("producto.producto_id"),
        nullable=False
    )

    # Relaciones ORM
    pedido = relationship("PedidoModel", back_populates="detalles")
