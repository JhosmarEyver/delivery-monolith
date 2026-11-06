from sqlalchemy import Column, Integer, TIMESTAMP, Numeric, Text, String, Boolean, ForeignKey, func
from src.core.database import Base

class PedidoModel(Base):
    __tablename__ = "pedido"
    pedido_id = Column(Integer, primary_key=True, index=True)
    fecha_hora = Column(TIMESTAMP, server_default=func.now())
    sum_total = Column(Numeric(10, 2), nullable=False)
    notas_cliente = Column(Text)
    estado = Column(String(30), default="pendiente")
    tiempo_estimado_min = Column(Integer, default=0)
    permite_cancelacion = Column(Boolean, default=True)
    usuario_id = Column(Integer, ForeignKey("usuario.usuario_id"))
    restaurant_id = Column(Integer, ForeignKey("restaurante.restaurant_id"))
    repartidor_id = Column(Integer, ForeignKey("repartidor.id_repartidor"), nullable=True)

class DetallePedidoModel(Base):
    __tablename__ = "detalle_pedido"
    id_detalle_pedido = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedido.pedido_id", ondelete="CASCADE"))
    id_producto = Column(Integer, ForeignKey("producto.id_producto"))
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)