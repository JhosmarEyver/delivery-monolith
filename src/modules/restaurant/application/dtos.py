"""DTOs de entrada del módulo restaurant (lo que el cliente envía a los casos de uso)."""
from datetime import time
from decimal import Decimal
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RestauranteDTO(BaseModel):
    nombre: str = Field(min_length=1, max_length=128)
    direccion: str = Field(min_length=1, max_length=255)
    contacto: Optional[str] = Field(default=None, max_length=50)
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    estado: Literal["Abierto", "Cerrado"] = "Abierto"


class ProductoDTO(BaseModel):
    nombre: str = Field(min_length=1, max_length=128)
    descripcion: Optional[str] = None
    precio: Decimal = Field(ge=0, max_digits=10, decimal_places=2)
    disponible: bool = True
    categoria: str = Field(min_length=1, max_length=64)
