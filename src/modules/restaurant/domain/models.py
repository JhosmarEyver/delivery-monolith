from sqlalchemy import Column, Integer, String, Time, Numeric, Boolean, ForeignKey
from src.core.database import Base

class RestauranteModel(Base):
    __tablename__ = "restaurante"
    restaurant_id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    direccion = Column(String(255), nullable=False)
    contacto = Column(String(50))
    horario_apertura = Column(Time)
    horario_cierre = Column(Time)
    estado = Column(String(30), default="abierto")

class ProductoModel(Base):
    __tablename__ = "producto"
    id_producto = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurante.restaurant_id", ondelete="CASCADE"))
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String)
    precio = Column(Numeric(10, 2), nullable=False)
    disponible = Column(Boolean, default=True)
    categoria = Column(String(50))