"""
Schemas Pydantic para Usuario.
"""
from datetime import date, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.usuario import RolEnum


class UsuarioBase(BaseModel):
    nombre:   str      = Field(..., min_length=2, max_length=100, examples=["Ana"])
    apellido: str | None = Field(None, max_length=100, examples=["García"])
    email:    EmailStr
    rol:      RolEnum
    fecha_nacimiento: date | None = None


class UsuarioCreate(UsuarioBase):
    """Datos para registrar un nuevo usuario."""
    password: str = Field(..., min_length=6, description="Contraseña en texto plano")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        return v


class UsuarioRead(UsuarioBase):
    """Datos que se devuelven al cliente. Nunca incluye el hash."""
    id:             int
    activo:         bool
    creado_en:      datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class UsuarioUpdate(BaseModel):
    """Todos los campos son opcionales para soportar PATCH parcial."""
    nombre:           str | None  = Field(None, min_length=2, max_length=100)
    apellido:         str | None  = Field(None, max_length=100)
    email:            EmailStr | None = None
    activo:           bool | None = None
    rol:              RolEnum | None = None
    fecha_nacimiento: date | None = None
    password:         str | None  = Field(None, min_length=6)
