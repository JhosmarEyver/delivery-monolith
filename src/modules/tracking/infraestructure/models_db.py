
# modulo tracking
''' Modelos ORM de SQLAlchemy
========================================
Modelos ORM de las tablas repartidor y ubicacion_tracking.
'''

from sqlalchemy import Column, Integer, String, Boolean, Numeric, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base


class RepartidorModel(Base):
    __tablename__ = "repartidor"

    repartidor_id = Column(Integer, primary_key=True, index=True)
    tipo_vehiculo = Column(String(20), nullable=False)
    placa = Column(String(20))
    disponible = Column(Boolean, default=True)

    usuario_id = Column(
        Integer,
        ForeignKey("usuario.usuario_id", ondelete="SET NULL"),
        nullable=True
    )

    # Relación ORM
    ubicaciones = relationship(
        "UbicacionTrackingModel",
        back_populates="repartidor",
        cascade="all, delete-orphan"
    )


class UbicacionTrackingModel(Base):
    __tablename__ = "ubicacion_tracking"

    ubicacion_tracking_id = Column(Integer, primary_key=True, index=True)
    latitud = Column(Numeric(10, 8), nullable=False)
    longitud = Column(Numeric(11, 8), nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(Time, nullable=False)

    repartidor_id = Column(
        Integer,
        ForeignKey("repartidor.repartidor_id", ondelete="CASCADE"),
        nullable=False
    )

    # Relación ORM
    repartidor = relationship(
        "RepartidorModel",
        back_populates="ubicaciones"
    )
