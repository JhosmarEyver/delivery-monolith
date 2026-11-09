from typing import List, Optional

from src.modules.restaurant.application.dtos import ProductoDTO, RestauranteDTO
from src.modules.restaurant.domain.exceptions import (
    ProductoNoEncontradoException,
    RestauranteNoEncontradoException,
)
from src.modules.restaurant.domain.models import Producto, Restaurante
from src.modules.restaurant.domain.repositories import IProductoRepository, IRestauranteRepository


class RestaurantService:
    """Casos de uso del catálogo: restaurantes y sus productos."""

    def __init__(self, restaurantes: IRestauranteRepository, productos: IProductoRepository):
        self.restaurantes = restaurantes
        self.productos = productos

    # ---------- Restaurantes ----------

    def crear_restaurante(self, data: RestauranteDTO) -> Restaurante:
        return self.restaurantes.guardar(Restaurante(**data.model_dump()))

    def listar_restaurantes(self, estado: Optional[str] = None) -> List[Restaurante]:
        return self.restaurantes.listar(estado)

    def obtener_restaurante(self, restaurant_id: int) -> Restaurante:
        restaurante = self.restaurantes.obtener_por_id(restaurant_id)
        if not restaurante:
            raise RestauranteNoEncontradoException(f"No existe el restaurante {restaurant_id}.")
        return restaurante

    def actualizar_restaurante(self, restaurant_id: int, data: RestauranteDTO) -> Restaurante:
        self.obtener_restaurante(restaurant_id)
        return self.restaurantes.guardar(Restaurante(restaurant_id=restaurant_id, **data.model_dump()))

    def eliminar_restaurante(self, restaurant_id: int) -> None:
        self.restaurantes.eliminar(restaurant_id)

    # ---------- Productos ----------

    def agregar_producto(self, restaurant_id: int, data: ProductoDTO) -> Producto:
        self.obtener_restaurante(restaurant_id)  # Regla: el restaurante debe existir
        return self.productos.guardar(Producto(restaurant_id=restaurant_id, **data.model_dump()))

    def listar_productos(self, restaurant_id: int, solo_disponibles: bool = False) -> List[Producto]:
        self.obtener_restaurante(restaurant_id)
        return self.productos.listar_por_restaurante(restaurant_id, solo_disponibles)

    def obtener_producto(self, producto_id: int) -> Producto:
        producto = self.productos.obtener_por_id(producto_id)
        if not producto:
            raise ProductoNoEncontradoException(f"No existe el producto {producto_id}.")
        return producto

    def actualizar_producto(self, producto_id: int, data: ProductoDTO) -> Producto:
        actual = self.obtener_producto(producto_id)
        return self.productos.guardar(
            Producto(producto_id=producto_id, restaurant_id=actual.restaurant_id, **data.model_dump())
        )

    def eliminar_producto(self, producto_id: int) -> None:
        self.productos.eliminar(producto_id)
