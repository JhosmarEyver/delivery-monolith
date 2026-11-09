class DomainException(Exception):
    """Excepción base para los errores de negocio del módulo auth."""
    pass


class EmailYaRegistradoException(DomainException):
    """Se lanza cuando se intenta registrar un email que ya existe."""
    pass


class UsuarioNoEncontradoException(DomainException):
    """Se lanza cuando no existe el usuario buscado."""
    pass
