from sqlalchemy import Column, Integer, String, Boolean, Numeric, TIMESTAMP, ForeignKey, func
from src.core.database import Base

class RepartidorModel(Base):
    __tablename__ = "repartidor"
    id_repartidor = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.usuario_id", ondelete="CASCADE"))
    placa = Column(String(20))
    tipo_vehiculo = Column(String(30)) # bicicleta, moto, taxi
    disponible = Column(Boolean, default=True)

class UbicacionTrackingModel(Base):
    __tablename__ = "ubicacion_tracking"
    id_ubicacion_tracking = Column(Integer, primary_key=True, index=True)
    id_repartidor = Column(Integer, ForeignKey("repartidor.id_repartidor", ondelete="CASCADE"))
    latitud = Column(Numeric(10, 8), nullable=False)
    longitud = Column(Numeric(11, 8), nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())