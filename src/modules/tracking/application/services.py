from datetime import datetime
from typing import List, Optional

from src.modules.tracking.application.dtos import RepartidorDTO, UbicacionDTO
from src.modules.tracking.domain.exceptions import (
    RepartidorNoEncontradoException,
    UbicacionNoEncontradaException,
)
from src.modules.tracking.domain.models import Repartidor, UbicacionTracking
from src.modules.tracking.domain.repositories import IRepartidorRepository, IUbicacionRepository


class TrackingService:
    """Casos de uso de repartidores y seguimiento GPS."""

    def __init__(self, repartidores: IRepartidorRepository, ubicaciones: IUbicacionRepository):
        self.repartidores = repartidores
        self.ubicaciones = ubicaciones

    # ---------- Repartidores ----------

    def crear_repartidor(self, data: RepartidorDTO) -> Repartidor:
        return self.repartidores.guardar(Repartidor(**data.model_dump()))

    def listar_repartidores(self, disponible: Optional[bool] = None) -> List[Repartidor]:
        return self.repartidores.listar(disponible)

    def obtener_repartidor(self, repartidor_id: int) -> Repartidor:
        repartidor = self.repartidores.obtener_por_id(repartidor_id)
        if not repartidor:
            raise RepartidorNoEncontradoException(f"No existe el repartidor {repartidor_id}.")
        return repartidor

    def actualizar_repartidor(self, repartidor_id: int, data: RepartidorDTO) -> Repartidor:
        self.obtener_repartidor(repartidor_id)
        return self.repartidores.guardar(Repartidor(repartidor_id=repartidor_id, **data.model_dump()))

    def cambiar_disponibilidad(self, repartidor_id: int, disponible: bool) -> Repartidor:
        repartidor = self.obtener_repartidor(repartidor_id)
        if disponible:
            repartidor.liberar()
        else:
            repartidor.marcar_ocupado()
        return self.repartidores.guardar(repartidor)

    def eliminar_repartidor(self, repartidor_id: int) -> None:
        self.repartidores.eliminar(repartidor_id)

    # Usados por el módulo order (a través de su adaptador) al asignar / liberar un repartidor
    def marcar_ocupado(self, repartidor_id: int) -> Repartidor:
        return self.cambiar_disponibilidad(repartidor_id, False)

    def liberar(self, repartidor_id: int) -> Repartidor:
        return self.cambiar_disponibilidad(repartidor_id, True)

    # ---------- Ubicaciones ----------

    def registrar_ubicacion(self, repartidor_id: int, data: UbicacionDTO) -> UbicacionTracking:
        self.obtener_repartidor(repartidor_id)
        ahora = datetime.now()
        ubicacion = UbicacionTracking(
            repartidor_id=repartidor_id,
            latitud=data.latitud,
            longitud=data.longitud,
            fecha=ahora.date(),
            hora=ahora.time().replace(microsecond=0),
        )
        return self.ubicaciones.guardar(ubicacion)

    def obtener_historial(self, repartidor_id: int, limite: int = 50) -> List[UbicacionTracking]:
        self.obtener_repartidor(repartidor_id)
        return self.ubicaciones.listar_por_repartidor(repartidor_id, limite)

    def obtener_ubicacion_actual(self, repartidor_id: int) -> UbicacionTracking:
        self.obtener_repartidor(repartidor_id)
        ubicacion = self.ubicaciones.obtener_ultima(repartidor_id)
        if not ubicacion:
            raise UbicacionNoEncontradaException(
                f"El repartidor {repartidor_id} aún no ha reportado ubicaciones."
            )
        return ubicacion
