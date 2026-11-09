
# modulo payment
''' Modelos ORM de SQLAlchemy
========================================
Modelos ORM de la tabla pago.
'''

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base


class PagoModel(Base):
    __tablename__ = "pago"

    pago_id = Column(Integer, primary_key=True, index=True)
    monto = Column(Numeric(10, 2), nullable=False)
    metodo_pago = Column(String(20), nullable=False)
    estado_pago = Column(String(20), default="Pendiente")
    transaccion_id = Column(String(128), unique=True)
    fecha = Column(Date, nullable=False)

    pedido_id = Column(
        Integer,
        ForeignKey("pedido.pedido_id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    # Relación ORM
    pedido = relationship("PedidoModel", back_populates="pago")
