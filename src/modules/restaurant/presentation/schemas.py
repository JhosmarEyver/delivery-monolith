"""Schemas de respuesta HTTP del módulo restaurant."""
from datetime import time
from typing import Optional

from pydantic import BaseModel

from src.core.types import Dinero


class RestauranteResponse(BaseModel):
    restaurant_id: int
    nombre: str
    direccion: str
    contacto: Optional[str] = None
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    estado: str


class ProductoResponse(BaseModel):
    producto_id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: Dinero
    disponible: bool
    categoria: str
    restaurant_id: int
