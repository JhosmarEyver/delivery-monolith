"""Schemas de respuesta HTTP del módulo tracking."""
from datetime import date, time
from typing import Optional

from pydantic import BaseModel


class RepartidorResponse(BaseModel):
    repartidor_id: int
    tipo_vehiculo: str
    placa: Optional[str] = None
    disponible: bool
    usuario_id: Optional[int] = None


class UbicacionResponse(BaseModel):
    ubicacion_tracking_id: int
    repartidor_id: int
    latitud: float
    longitud: float
    fecha: date
    hora: time
