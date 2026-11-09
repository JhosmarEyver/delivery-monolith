from dataclasses import dataclass
from datetime import date, time
from typing import Optional

from src.modules.tracking.domain.exceptions import (
    DatosInvalidosException,
    RepartidorNoDisponibleException,
)

# Valores permitidos por el CHECK de la tabla repartidor (init.sql)
TIPOS_VEHICULO = ("Bicicleta", "Moto", "Taxi")


@dataclass
class Repartidor:
    """Entidad pura de dominio: la persona que entrega los pedidos."""
    tipo_vehiculo: str
    placa: Optional[str] = None
    disponible: bool = True
    usuario_id: Optional[int] = None
    repartidor_id: Optional[int] = None

    def __post_init__(self):
        if self.tipo_vehiculo not in TIPOS_VEHICULO:
            raise DatosInvalidosException(f"Vehículo inválido: {self.tipo_vehiculo}. Use {TIPOS_VEHICULO}.")
        # Regla de negocio: los vehículos motorizados deben tener placa
        if self.tipo_vehiculo in ("Moto", "Taxi") and not self.placa:
            raise DatosInvalidosException(f"Un repartidor en {self.tipo_vehiculo} debe registrar su placa.")

    def marcar_ocupado(self):
        if not self.disponible:
            raise RepartidorNoDisponibleException(f"El repartidor {self.repartidor_id} no está disponible.")
        self.disponible = False

    def liberar(self):
        self.disponible = True


@dataclass
class UbicacionTracking:
    """Entidad pura de dominio: una posición GPS reportada por un repartidor."""
    repartidor_id: int
    latitud: float
    longitud: float
    fecha: date
    hora: time
    ubicacion_tracking_id: Optional[int] = None

    def __post_init__(self):
        if not -90 <= self.latitud <= 90:
            raise DatosInvalidosException("La latitud debe estar entre -90 y 90.")
        if not -180 <= self.longitud <= 180:
            raise DatosInvalidosException("La longitud debe estar entre -180 y 180.")
