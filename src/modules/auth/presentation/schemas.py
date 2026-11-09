from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioCreate(BaseModel):
    nombre_usuario: str
    email: EmailStr
    contrasenia: str
    rol_id: int
    estado_id: int


class UsuarioResponse(BaseModel):
    # Permite construir la respuesta desde objetos con atributos (entidad de dominio u ORM)
    model_config = ConfigDict(from_attributes=True)

    usuario_id: int
    nombre_usuario: str
    email: str
    rol_id: int
    estado_id: int
