from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.modules.tracking.domain.exceptions import (
    DatosInvalidosException,
    RepartidorNoEncontradoException,
)
from src.modules.tracking.domain.models import Repartidor, UbicacionTracking
from src.modules.tracking.domain.repositories import IRepartidorRepository, IUbicacionRepository
from src.modules.tracking.infrastructure.models_db import RepartidorModel, UbicacionTrackingModel


class RepartidorRepositorySqlAlchemy(IRepartidorRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(model: Optional[RepartidorModel]) -> Optional[Repartidor]:
        if not model:
            return None
        return Repartidor(
            repartidor_id=model.repartidor_id,
            tipo_vehiculo=model.tipo_vehiculo,
            placa=model.placa,
            disponible=model.disponible,
            usuario_id=model.usuario_id,
        )

    def obtener_por_id(self, repartidor_id: int) -> Optional[Repartidor]:
        return self._to_domain(self.db.get(RepartidorModel, repartidor_id))

    def listar(self, disponible: Optional[bool] = None) -> List[Repartidor]:
        query = self.db.query(RepartidorModel)
        if disponible is not None:
            query = query.filter(RepartidorModel.disponible.is_(disponible))
        return [self._to_domain(m) for m in query.order_by(RepartidorModel.repartidor_id).all()]

    def guardar(self, repartidor: Repartidor) -> Repartidor:
        if repartidor.repartidor_id:
            model = self.db.get(RepartidorModel, repartidor.repartidor_id)
            if not model:
                raise RepartidorNoEncontradoException(f"No existe el repartidor {repartidor.repartidor_id}.")
        else:
            model = RepartidorModel()
            self.db.add(model)

        model.tipo_vehiculo = repartidor.tipo_vehiculo
        model.placa = repartidor.placa
        model.disponible = repartidor.disponible
        model.usuario_id = repartidor.usuario_id

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise DatosInvalidosException(
                "Datos de repartidor inválidos (verifique que el usuario_id exista)."
            ) from e
        self.db.refresh(model)
        return self._to_domain(model)

    def eliminar(self, repartidor_id: int) -> None:
        model = self.db.get(RepartidorModel, repartidor_id)
        if not model:
            raise RepartidorNoEncontradoException(f"No existe el repartidor {repartidor_id}.")
        # Las ubicaciones se borran en cascada; en los pedidos el repartidor queda en NULL (init.sql)
        self.db.delete(model)
        self.db.commit()


class UbicacionRepositorySqlAlchemy(IUbicacionRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(model: Optional[UbicacionTrackingModel]) -> Optional[UbicacionTracking]:
        if not model:
            return None
        return UbicacionTracking(
            ubicacion_tracking_id=model.ubicacion_tracking_id,
            repartidor_id=model.repartidor_id,
            latitud=float(model.latitud),
            longitud=float(model.longitud),
            fecha=model.fecha,
            hora=model.hora,
        )

    def _query_repartidor(self, repartidor_id: int):
        return (
            self.db.query(UbicacionTrackingModel)
            .filter(UbicacionTrackingModel.repartidor_id == repartidor_id)
            .order_by(
                UbicacionTrackingModel.fecha.desc(),
                UbicacionTrackingModel.hora.desc(),
                UbicacionTrackingModel.ubicacion_tracking_id.desc(),
            )
        )

    def guardar(self, ubicacion: UbicacionTracking) -> UbicacionTracking:
        model = UbicacionTrackingModel(
            repartidor_id=ubicacion.repartidor_id,
            latitud=ubicacion.latitud,
            longitud=ubicacion.longitud,
            fecha=ubicacion.fecha,
            hora=ubicacion.hora,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def listar_por_repartidor(self, repartidor_id: int, limite: int = 50) -> List[UbicacionTracking]:
        return [self._to_domain(m) for m in self._query_repartidor(repartidor_id).limit(limite).all()]

    def obtener_ultima(self, repartidor_id: int) -> Optional[UbicacionTracking]:
        return self._to_domain(self._query_repartidor(repartidor_id).first())
