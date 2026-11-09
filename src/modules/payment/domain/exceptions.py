class DomainException(Exception):
    """Excepción base para los errores de negocio del módulo payment."""
    pass


class RecursoNoEncontradoException(DomainException):
    pass


class PagoNoEncontradoException(RecursoNoEncontradoException):
    pass


class DatosInvalidosException(DomainException):
    pass


class ReferenciaInvalidaException(DatosInvalidosException):
    """El pago hace referencia a un pedido que no existe."""
    pass


class OperacionNoPermitidaException(DomainException):
    pass


class PagoDuplicadoException(OperacionNoPermitidaException):
    pass


class PagoRechazadoException(DomainException):
    pass
