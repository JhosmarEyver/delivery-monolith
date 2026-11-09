class DomainException(Exception):
    """Excepción base para los errores de negocio del módulo restaurant."""
    pass


class RecursoNoEncontradoException(DomainException):
    pass


class RestauranteNoEncontradoException(RecursoNoEncontradoException):
    pass


class ProductoNoEncontradoException(RecursoNoEncontradoException):
    pass


class DatosInvalidosException(DomainException):
    pass


class OperacionNoPermitidaException(DomainException):
    pass
