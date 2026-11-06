from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nombre_usuario: str
    email: EmailStr
    contrasenia: str
    rol_id: int
    estado_id: int

class UsuarioResponse(BaseModel):
    usuario_id: int
    nombre_usuario: str
    email: str
    rol_id: int
    estado_id: int

    class Config:
        from_attributes = True # Permite mapear modelos ORM directamente a Pydantic