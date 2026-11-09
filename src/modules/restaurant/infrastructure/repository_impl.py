from typing import List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.modules.restaurant.domain.exceptions import (
    DatosInvalidosException,
    OperacionNoPermitidaException,
    ProductoNoEncontradoException,
    RestauranteNoEncontradoException,
)
from src.modules.restaurant.domain.models import Producto, Restaurante
from src.modules.restaurant.domain.repositories import IProductoRepository, IRestauranteRepository
from src.modules.restaurant.infrastructure.models_db import ProductoModel, RestauranteModel


class RestauranteRepositorySqlAlchemy(IRestauranteRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(model: Optional[RestauranteModel]) -> Optional[Restaurante]:
        if not model:
            return None
        return Restaurante(
            restaurant_id=model.restaurant_id,
            nombre=model.nombre,
            direccion=model.direccion,
            contacto=model.contacto,
            horario_apertura=model.horario_apertura,
            horario_cierre=model.horario_cierre,
            estado=model.estado,
        )

    def obtener_por_id(self, restaurant_id: int) -> Optional[Restaurante]:
        return self._to_domain(self.db.get(RestauranteModel, restaurant_id))

    def listar(self, estado: Optional[str] = None) -> List[Restaurante]:
        query = self.db.query(RestauranteModel)
        if estado:
            query = query.filter(RestauranteModel.estado == estado)
        return [self._to_domain(m) for m in query.order_by(RestauranteModel.restaurant_id).all()]

    def guardar(self, restaurante: Restaurante) -> Restaurante:
        if restaurante.restaurant_id:
            model = self.db.get(RestauranteModel, restaurante.restaurant_id)
            if not model:
                raise RestauranteNoEncontradoException(f"No existe el restaurante {restaurante.restaurant_id}.")
        else:
            model = RestauranteModel()
            self.db.add(model)

        model.nombre = restaurante.nombre
        model.direccion = restaurante.direccion
        model.contacto = restaurante.contacto
        model.horario_apertura = restaurante.horario_apertura
        model.horario_cierre = restaurante.horario_cierre
        model.estado = restaurante.estado

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise DatosInvalidosException("Los datos del restaurante no cumplen las reglas de la base de datos.") from e
        self.db.refresh(model)
        return self._to_domain(model)

    def eliminar(self, restaurant_id: int) -> None:
        model = self.db.get(RestauranteModel, restaurant_id)
        if not model:
            raise RestauranteNoEncontradoException(f"No existe el restaurante {restaurant_id}.")
        try:
            self.db.delete(model)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise OperacionNoPermitidaException(
                "No se puede eliminar el restaurante porque tiene pedidos asociados."
            ) from e


class ProductoRepositorySqlAlchemy(IProductoRepository):
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_domain(model: Optional[ProductoModel]) -> Optional[Producto]:
        if not model:
            return None
        return Producto(
            producto_id=model.producto_id,
            nombre=model.nombre,
            descripcion=model.descripcion,
            precio=model.precio,
            disponible=model.disponible,
            categoria=model.categoria,
            restaurant_id=model.restaurant_id,
        )

    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        return self._to_domain(self.db.get(ProductoModel, producto_id))

    def listar_por_restaurante(self, restaurant_id: int, solo_disponibles: bool = False) -> List[Producto]:
        query = self.db.query(ProductoModel).filter(ProductoModel.restaurant_id == restaurant_id)
        if solo_disponibles:
            query = query.filter(ProductoModel.disponible.is_(True))
        return [self._to_domain(m) for m in query.order_by(ProductoModel.producto_id).all()]

    def guardar(self, producto: Producto) -> Producto:
        if producto.producto_id:
            model = self.db.get(ProductoModel, producto.producto_id)
            if not model:
                raise ProductoNoEncontradoException(f"No existe el producto {producto.producto_id}.")
        else:
            model = ProductoModel()
            self.db.add(model)

        model.nombre = producto.nombre
        model.descripcion = producto.descripcion
        model.precio = producto.precio
        model.disponible = producto.disponible
        model.categoria = producto.categoria
        model.restaurant_id = producto.restaurant_id

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise DatosInvalidosException("Los datos del producto no cumplen las reglas de la base de datos.") from e
        self.db.refresh(model)
        return self._to_domain(model)

    def eliminar(self, producto_id: int) -> None:
        model = self.db.get(ProductoModel, producto_id)
        if not model:
            raise ProductoNoEncontradoException(f"No existe el producto {producto_id}.")
        try:
            self.db.delete(model)
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            raise OperacionNoPermitidaException(
                "No se puede eliminar el producto porque aparece en pedidos. Márquelo como no disponible."
            ) from e
