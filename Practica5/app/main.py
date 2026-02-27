from typing import Optional, Literal
from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

app = FastAPI(
    title='API de Biblioteca',
    description='Victor',
    version='1.0'
)

libros = []
prestamos = []

CURRENT_YEAR = datetime.now().year

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50, description="Nombre del usuario", example="Victor") 
    correo: EmailStr = Field(..., description="Correo electrónico valido", example="victorrodher493@gmail.com")

class LibroBase(BaseModel):
    id: int = Field(..., gt=0, description="Identificador del libro", example=1)
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del libro", example="Enciclopedia Pokémon")
    anio_publicacion: int = Field(..., gt=1450, le=CURRENT_YEAR, description="Año de publicación validado", example=2016)
    paginas: int = Field(..., gt=1, description="Número de páginas validado", example=320)
    estado: Literal["disponible", "prestado"] = Field(default="disponible", description="Estado del libro", example="disponible")
    
class PrestamoBase(BaseModel):
    id_prestamo: int = Field(..., gt=0, description="Identificador del préstamo", example=1)
    id_libro: int = Field(..., gt=0, description="Identificador del libro a prestar", example=1)
    usuario: UsuarioBase

# Endpoints
@app.get("/", tags=['Inicio'])
async def holamundo():
    return {"mensaje": "API de Biblioteca - Activa"}

@app.post("/v1/libros/", tags=['CRUD Libros'])
async def registrar_libro(libro: LibroBase):
    for lib in libros:
        if lib["id"] == libro.id:
            raise HTTPException(
                status_code=400, 
                detail="El ID del libro ya existe"
            )
    
    libros.append(libro.model_dump()) 
    
    return {
        "mensaje": "Libro agregado",
        "datos": libro,
        "status": "201"
    }

@app.get("/v1/libros/disponibles", tags=['CRUD Libros'])
async def listar_disponibles():
    disponibles = [lib for lib in libros if lib["estado"] == "disponible"]
    return {
        "status": "200",
        "total": len(disponibles),
        "data": disponibles
    }

@app.get("/v1/libros/buscar", tags=['CRUD Libros'])
async def buscar_libro(nombre: str):
    encontrados = [lib for lib in libros if nombre.lower() in lib["nombre"].lower()]
    return {
        "status": "200",
        "total": len(encontrados),
        "data": encontrados
    }

@app.post("/v1/prestamos/", tags=['CRUD Prestamos'])
async def registrar_prestamo(prestamo: PrestamoBase):
    libro_encontrado = None
    for lib in libros:
        if lib["id"] == prestamo.id_libro:
            libro_encontrado = lib
            break
            
    if not libro_encontrado:
        raise HTTPException(
            status_code=400, 
            detail="El libro no existe"
        )
        
    if libro_encontrado["estado"] == "prestado":
        raise HTTPException(
            status_code=409, 
            detail="El libro ya está prestado"
        )

    for p in prestamos:
        if p["id_prestamo"] == prestamo.id_prestamo:
            raise HTTPException(
                status_code=400, 
                detail="El ID del préstamo ya existe"
            )

    nuevo_prestamo = prestamo.model_dump()
    nuevo_prestamo["estado_prestamo"] = "activo"
    prestamos.append(nuevo_prestamo)
    
    libro_encontrado["estado"] = "prestado"
    
    return {
        "mensaje": "Préstamo registrado",
        "datos": nuevo_prestamo,
        "status": "201"
    }

@app.put("/v1/prestamos/{id_prestamo}/devolver", tags=['CRUD Prestamos'])
async def devolver_libro(id_prestamo: int):
    for index, p in enumerate(prestamos):
        if p["id_prestamo"] == id_prestamo:
            if p["estado_prestamo"] == "devuelto":
                raise HTTPException(
                    status_code=409, 
                    detail="El libro ya fue devuelto"
                )
                
            prestamos[index]["estado_prestamo"] = "devuelto"
            
            for lib in libros:
                if lib["id"] == p["id_libro"]:
                    lib["estado"] = "disponible"
                    break
                    
            return {
                "mensaje": "Libro devuelto con éxito", 
                "status": "200"
            }
            
    raise HTTPException(
        status_code=409, 
        detail="El registro de préstamo activo no existe"
    )

@app.delete("/v1/prestamos/{id_prestamo}", tags=['CRUD Prestamos'])
async def eliminar_prestamo(id_prestamo: int):
    for index, p in enumerate(prestamos):
        if p["id_prestamo"] == id_prestamo:
            if p["estado_prestamo"] == "activo":
                for lib in libros:
                    if lib["id"] == p["id_libro"]:
                        lib["estado"] = "disponible"
                        break
                        
            prestamos.pop(index)
            return {
                "mensaje": "Registro de préstamo eliminado",
                "id_eliminado": id_prestamo,
                "status": "200"
            }
            
    raise HTTPException(
        status_code=409, 
        detail="El registro de préstamo ya no existe"
    )