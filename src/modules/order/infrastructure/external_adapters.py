"""Adaptadores hacia otros módulos del monolito (capa anticorrupción).

Cada adaptador implementa un puerto de order/domain/repositories.py usando el
servicio de aplicación del otro módulo, y traduce sus entidades y excepciones a
los objetos de valor y excepciones propios del módulo order.
"""
from typing import Optional

from sqlalchemy.orm import Session

from src.modules.order.domain.exceptions import RepartidorNoDisponibleException
from src.modules.order.domain.models import ProductoInfo, RestauranteInfo
from src.modules.order.domain.repositories import ICatalogoGateway, IRepartidorGateway, IUsuarioGateway

# Módulo auth
from src.modules.auth.application.services import AuthService
from src.modules.auth.domain.exceptions import UsuarioNoEncontradoException
from src.modules.auth.infrastructure.repository_impl import AuthRepositorySqlAlchemy

# Módulo restaurant
from src.modules.restaurant.application.services import RestaurantService
from src.modules.restaurant.domain.exceptions import (
    ProductoNoEncontradoException,
    RestauranteNoEncontradoException,
)
from src.modules.restaurant.infrastructure.repository_impl import (
    ProductoRepositorySqlAlchemy,
    RestauranteRepositorySqlAlchemy,
)

# Módulo tracking
from src.modules.tracking.application.services import TrackingService
from src.modules.tracking.domain.exceptions import (
    RepartidorNoDisponibleException as TrackingRepartidorNoDisponible,
)
from src.modules.tracking.domain.exceptions import RepartidorNoEncontradoException
from src.modules.tracking.infrastructure.repository_impl import (
    RepartidorRepositorySqlAlchemy,
    UbicacionRepositorySqlAlchemy,
)


class CatalogoRestaurantAdapter(ICatalogoGateway):
    def __init__(self, db: Session):
        self._service = RestaurantService(RestauranteRepositorySqlAlchemy(db), ProductoRepositorySqlAlchemy(db))

    def obtener_restaurante(self, restaurant_id: int) -> Optional[RestauranteInfo]:
        try:
            r = self._service.obtener_restaurante(restaurant_id)
        except RestauranteNoEncontradoException:
            return None
        return RestauranteInfo(restaurant_id=r.restaurant_id, abierto=r.esta_abierto())

    def obtener_producto(self, producto_id: int) -> Optional[ProductoInfo]:
        try:
            p = self._service.obtener_producto(producto_id)
        except ProductoNoEncontradoException:
            return None
        return ProductoInfo(
            producto_id=p.producto_id,
            restaurant_id=p.restaurant_id,
            nombre=p.nombre,
            precio=p.precio,
            disponible=p.disponible,
        )


class UsuarioAuthAdapter(IUsuarioGateway):
    def __init__(self, db: Session):
        self._service = AuthService(AuthRepositorySqlAlchemy(db))

    def existe_usuario(self, usuario_id: int) -> bool:
        try:
            self._service.obtener_usuario(usuario_id)
            return True
        except UsuarioNoEncontradoException:
            return False


class RepartidorTrackingAdapter(IRepartidorGateway):
    def __init__(self, db: Session):
        self._service = TrackingService(RepartidorRepositorySqlAlchemy(db), UbicacionRepositorySqlAlchemy(db))

    def esta_disponible(self, repartidor_id: int) -> Optional[bool]:
        try:
            return self._service.obtener_repartidor(repartidor_id).disponible
        except RepartidorNoEncontradoException:
            return None

    def ocupar(self, repartidor_id: int) -> None:
        try:
            self._service.marcar_ocupado(repartidor_id)
        except TrackingRepartidorNoDisponible as e:
            raise RepartidorNoDisponibleException(str(e)) from e

    def liberar(self, repartidor_id: int) -> None:
        try:
            self._service.liberar(repartidor_id)
        except RepartidorNoEncontradoException:
            pass  # Si el repartidor fue eliminado no hay nada que liberar
