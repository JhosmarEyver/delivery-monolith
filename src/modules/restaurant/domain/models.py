from dataclasses import dataclass
from datetime import time
from decimal import Decimal
from typing import Optional

from src.modules.restaurant.domain.exceptions import DatosInvalidosException

# Valores permitidos por el CHECK de la tabla restaurante (init.sql)
ESTADOS_RESTAURANTE = ("Abierto", "Cerrado")


@dataclass
class Restaurante:
    """Entidad pura de dominio: un comercio que ofrece productos."""
    nombre: str
    direccion: str
    contacto: Optional[str] = None
    horario_apertura: Optional[time] = None
    horario_cierre: Optional[time] = None
    estado: str = "Abierto"
    restaurant_id: Optional[int] = None

    def __post_init__(self):
        if not self.nombre or not self.nombre.strip():
            raise DatosInvalidosException("El nombre del restaurante es obligatorio.")
        if self.estado not in ESTADOS_RESTAURANTE:
            raise DatosInvalidosException(f"Estado inválido: {self.estado}. Use {ESTADOS_RESTAURANTE}.")

    def esta_abierto(self) -> bool:
        return self.estado == "Abierto"

    def abrir(self):
        self.estado = "Abierto"

    def cerrar(self):
        self.estado = "Cerrado"


@dataclass
class Producto:
    """Entidad pura de dominio: un producto del menú de un restaurante."""
    nombre: str
    precio: Decimal
    categoria: str
    restaurant_id: int
    descripcion: Optional[str] = None
    disponible: bool = True
    producto_id: Optional[int] = None

    def __post_init__(self):
        if self.precio is None or Decimal(self.precio) < 0:
            raise DatosInvalidosException("El precio del producto no puede ser negativo.")
        if not self.categoria or not self.categoria.strip():
            raise DatosInvalidosException("La categoría del producto es obligatoria.")

    def cambiar_disponibilidad(self, disponible: bool):
        self.disponible = disponible
