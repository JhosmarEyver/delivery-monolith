class DomainException(Exception):
    """Excepción base para los errores de negocio del módulo order."""
    pass


class RecursoNoEncontradoException(DomainException):
    pass


class PedidoNoEncontradoException(RecursoNoEncontradoException):
    pass


class DatosInvalidosException(DomainException):
    pass


class ReferenciaInvalidaException(DatosInvalidosException):
    """El pedido hace referencia a un usuario, restaurante, producto o repartidor que no existe."""
    pass


class OperacionNoPermitidaException(DomainException):
    pass


class TransicionEstadoInvalidaException(OperacionNoPermitidaException):
    pass


class PedidoNoCancelableException(OperacionNoPermitidaException):
    pass


class RepartidorNoDisponibleException(OperacionNoPermitidaException):
    pass
