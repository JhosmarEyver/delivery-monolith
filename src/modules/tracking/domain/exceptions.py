class DomainException(Exception):
    """Excepción base para los errores de negocio del módulo tracking."""
    pass


class RecursoNoEncontradoException(DomainException):
    pass


class RepartidorNoEncontradoException(RecursoNoEncontradoException):
    pass


class UbicacionNoEncontradaException(RecursoNoEncontradoException):
    pass


class DatosInvalidosException(DomainException):
    pass


class OperacionNoPermitidaException(DomainException):
    pass


class RepartidorNoDisponibleException(OperacionNoPermitidaException):
    pass
