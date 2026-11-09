
# modulo restaurant
''' Modelos ORM de SQLAlchemy
========================================
Modelos ORM de las tablas restaurante y producto.
'''

from sqlalchemy import Column, Integer, String, Numeric, Boolean, Time, Text, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base


class RestauranteModel(Base):
    __tablename__ = "restaurante"

    restaurant_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(128), nullable=False)
    direccion = Column(String(255), nullable=False)
    contacto = Column(String(50))
    horario_apertura = Column(Time)
    horario_cierre = Column(Time)
    estado = Column(String(20), default="Abierto")

    # Relación ORM
    productos = relationship(
        "ProductoModel",
        back_populates="restaurante",
        cascade="all, delete-orphan"
    )


class ProductoModel(Base):
    __tablename__ = "producto"

    producto_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(128), nullable=False)
    descripcion = Column(Text)
    precio = Column(Numeric(10, 2), nullable=False)
    disponible = Column(Boolean, default=True)
    categoria = Column(String(64), nullable=False)

    restaurant_id = Column(
        Integer,
        ForeignKey("restaurante.restaurant_id", ondelete="CASCADE"),
        nullable=False
    )

    # Relación ORM
    restaurante = relationship(
        "RestauranteModel",
        back_populates="productos"
    )
