from sqlalchemy import Column, Integer, Numeric, String, TIMESTAMP, ForeignKey, func
from src.core.database import Base

class PagoModel(Base):
    __tablename__ = "pago"
    id_pago = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedido.pedido_id", ondelete="CASCADE"))
    monto = Column(Numeric(10, 2), nullable=False)
    metodo_pago = Column(String(30), nullable=False) # tarjeta, qr, efectivo
    estado_pago = Column(String(30), default="completado")
    transaccion_id = Column(String(100))
    fecha = Column(TIMESTAMP, server_default=func.now())