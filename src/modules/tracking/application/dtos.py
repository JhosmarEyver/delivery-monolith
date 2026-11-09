"""DTOs de entrada del módulo tracking."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class RepartidorDTO(BaseModel):
    tipo_vehiculo: Literal["Bicicleta", "Moto", "Taxi"]
    placa: Optional[str] = Field(default=None, max_length=20)
    disponible: bool = True
    usuario_id: Optional[int] = None


class DisponibilidadDTO(BaseModel):
    disponible: bool


class UbicacionDTO(BaseModel):
    # La fecha y la hora las asigna el servidor al momento de recibir la posición
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
