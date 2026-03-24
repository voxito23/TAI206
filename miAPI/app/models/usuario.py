# Modelo de validación
from pydantic import BaseModel, Field
from typing import Optional 
class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre del usuario", example="Victor")
    edad: int = Field(..., ge=0, le=121, description="Edad validada entre 0 y 121", example=30)

