from typing import List, Optional

from src.modules.order.application.dtos import PedidoCrearDTO
from src.modules.order.domain.exceptions import (
    OperacionNoPermitidaException,
    PedidoNoEncontradoException,
    ReferenciaInvalidaException,
    RepartidorNoDisponibleException,
)
from src.modules.order.domain.models import DetallePedido, Pedido
from src.modules.order.domain.repositories import (
    ICatalogoGateway,
    IPedidoRepository,
    IRepartidorGateway,
    IUsuarioGateway,
)


class OrderService:
    """Casos de uso del ciclo de vida de un pedido."""

    def __init__(
        self,
        pedidos: IPedidoRepository,
        catalogo: ICatalogoGateway,
        usuarios: IUsuarioGateway,
        repartidores: IRepartidorGateway,
    ):
        self.pedidos = pedidos
        self.catalogo = catalogo
        self.usuarios = usuarios
        self.repartidores = repartidores

    def crear_pedido(self, data: PedidoCrearDTO) -> Pedido:
        # 1. El cliente debe existir
        if not self.usuarios.existe_usuario(data.usuario_id):
            raise ReferenciaInvalidaException(f"No existe el usuario {data.usuario_id}.")

        # 2. El restaurante debe existir y estar abierto
        restaurante = self.catalogo.obtener_restaurante(data.restaurant_id)
        if not restaurante:
            raise ReferenciaInvalidaException(f"No existe el restaurante {data.restaurant_id}.")
        if not restaurante.abierto:
            raise OperacionNoPermitidaException("El restaurante está cerrado y no recibe pedidos.")

        # 3. Cada producto debe existir, pertenecer al restaurante y estar disponible.
        #    El precio se toma del catálogo (nunca del cliente).
        detalles = []
        for item in data.items:
            producto = self.catalogo.obtener_producto(item.producto_id)
            if not producto or producto.restaurant_id != data.restaurant_id:
                raise ReferenciaInvalidaException(
                    f"El producto {item.producto_id} no existe en el restaurante {data.restaurant_id}."
                )
            if not producto.disponible:
                raise OperacionNoPermitidaException(f"El producto '{producto.nombre}' no está disponible.")
            detalles.append(
                DetallePedido(producto_id=producto.producto_id, cantidad=item.cantidad,
                              precio_unitario=producto.precio)
            )

        # 4. El agregado calcula subtotales y total
        pedido = Pedido.crear(data.usuario_id, data.restaurant_id, detalles, data.notas_cliente)
        return self.pedidos.guardar(pedido)

    def obtener_pedido(self, pedido_id: int) -> Pedido:
        pedido = self.pedidos.obtener_por_id(pedido_id)
        if not pedido:
            raise PedidoNoEncontradoException(f"No existe el pedido {pedido_id}.")
        return pedido

    def listar_pedidos(self, usuario_id: Optional[int] = None, estado: Optional[str] = None) -> List[Pedido]:
        return self.pedidos.listar(usuario_id, estado)

    def cambiar_estado(self, pedido_id: int, nuevo_estado: str) -> Pedido:
        pedido = self.obtener_pedido(pedido_id)
        pedido.cambiar_estado(nuevo_estado)  # El dominio valida la transición
        guardado = self.pedidos.guardar(pedido)
        # Al terminar la entrega (o cancelar) el repartidor vuelve a estar disponible
        if guardado.esta_finalizado() and guardado.repartidor_id:
            self.repartidores.liberar(guardado.repartidor_id)
        return guardado

    def cancelar_pedido(self, pedido_id: int) -> Pedido:
        return self.cambiar_estado(pedido_id, "Cancelado")

    def asignar_repartidor(self, pedido_id: int, repartidor_id: int) -> Pedido:
        pedido = self.obtener_pedido(pedido_id)

        disponible = self.repartidores.esta_disponible(repartidor_id)
        if disponible is None:
            raise ReferenciaInvalidaException(f"No existe el repartidor {repartidor_id}.")
        if not disponible:
            raise RepartidorNoDisponibleException(f"El repartidor {repartidor_id} está ocupado.")

        pedido.asignar_repartidor(repartidor_id)  # Reglas del agregado
        self.repartidores.ocupar(repartidor_id)
        return self.pedidos.guardar(pedido)
