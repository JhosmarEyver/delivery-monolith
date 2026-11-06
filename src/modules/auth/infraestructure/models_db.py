# modulo auth : ''' Modelos de SQLAlchimy /ORM 
# =========================================
# Modelos ORM de SQLAlchemy (Tablas): Van estrictamente en infrastructure/models_db.py. 
# (Aquí es donde colocamos las clases que heredan de Base como
#  UsuarioModel, RestauranteModel, PedidoModel, etc.)'''

''' Entidades de Dominio / Values Objets
========================================'''
from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base

class RolModel(Base):
    __tablename__ = "rol"
    rol_id = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(50), unique=True, nullable=False)
    
    # Relación inversa
    usuarios = relationship("UsuarioModel", back_populates="rol")

class EstadoModel(Base):
    __tablename__ = "estado"
    estado_id = Column(Integer, primary_key=True, index=True)
    nombre_estado = Column(String(50), unique=True, nullable=False)
    
    # Relación inversa
    usuarios = relationship("UsuarioModel", back_populates="estado")

class UsuarioModel(Base):
    __tablename__ = "usuario"
    usuario_id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(64), nullable=False)
    contrasenia = Column(String(255), nullable=False)
    email = Column(String(128), unique=True, nullable=False)
    rol_id = Column(Integer, ForeignKey("rol.rol_id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estado.estado_id"), nullable=False)

    # Relaciones ORM
    rol = relationship("RolModel", back_populates="usuarios")
    estado = relationship("EstadoModel", back_populates="usuarios")
    contacto = relationship("ContactoModel", back_populates="usuario", uselist=False, cascade="all, delete-orphan")
    direcciones = relationship("DireccionModel", back_populates="usuario", cascade="all, delete-orphan")

class ContactoModel(Base):
    __tablename__ = "contacto"
    contacto_id = Column(Integer, primary_key=True, index=True)
    phone_personal = Column(String(20))
    phone_trabajo = Column(String(20))
    domicilio = Column(String(255))
    usuario_id = Column(Integer, ForeignKey("usuario.usuario_id", ondelete="CASCADE"), unique=True, nullable=False)

    # Relación ORM
    usuario = relationship("UsuarioModel", back_populates="contacto")

class DireccionModel(Base):
    __tablename__ = "direccion"
    direccion_id = Column(Integer, primary_key=True, index=True)
    direccion_texto = Column(String(255), nullable=False)
    latitud = Column(Numeric(10, 8))
    longitud = Column(Numeric(11, 8))
    referencia = Column(String(255))
    etiqueta = Column(String(50))
    es_temporal = Column(Boolean, default=False)
    usuario_id = Column(Integer, ForeignKey("usuario.usuario_id", ondelete="CASCADE"), nullable=False)

    # Relación ORM
    usuario = relationship("UsuarioModel", back_populates="direcciones")