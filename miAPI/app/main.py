# importaciones
from typing import Optional
from fastapi import FastAPI,status,HTTPException
import asyncio
from pydantic import BaseModel, Field

#cd myAPI
#uvicorn main:app --reload
# Inicializacion o Instancia de la API
app = FastAPI(
    title='Mi primera API',
    description='Victor Osvaldo RH',
    version='1.0'
)
#BD Ficticia
usuarios=[
    {"id":1, "nombre":"Victor","edad":21},
    {"id":2, "nombre":"Mauricio","edad":20},
    {"id":3, "nombre":"Luis","edad":21},
]


#Modelo de validacion Pydantic
class UsuarioBase(BaseModel):
    id: int = Field(..., gt=0,description="Identificador de usuario", example="1" )
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre del usuario", example="Victor") 
    edad: int = Field(..., ge=0, le=121, description="Edad validada entre 0 y 121", example="30")    
    
    
    
    
# Endpoints
@app.get("/", tags=['Inicio'])
async def holamundo():
    return {"mensaje": "Hola mundo FastAPI"}

@app.get("/v1/bienvenidos", tags=['Inicio'])
async def bienvenidos():
    return {"mensaje": "Bienvenidos a FastAPI"}

@app.get("/v1/calificaciones", tags=['Asincronia'])
async def calificaciones():
    await asyncio.sleep(6)
    return {"mensaje": "Tu calificacion en TAI es 10 "}


@app.get("/v1/parametroO/{id}", tags=['Parametro Obligatorio'])
async def ConsultarUsuarios(id: int):
    await asyncio.sleep(6)
    return {"usuario encontrado": id}

@app.get("/v1/ParametroOp", tags=['Parametro Opcional'])
async def ConsultaOp(id: Optional[int] = None):
    await asyncio.sleep(6)
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"usuario encontrado": id ,"Datos": usuario}
        return {"Mensaje": "usuario no encontrado"}
    else:
        return {"Aviso": "No se proporcionó un ID"}
    
    
@app.get("/v1/usuarios/", tags=['CRUD usuarios'])
async def ConsultarUsuarios():
    return{
        "status":"200",
        "total": len(usuarios),
        "data": usuarios
    }
    
@app.post("/v1/usuarios/", tags=['CRUD usuarios'])
async def agregar_usuarios(usuario:UsuarioBase):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400, 
                detail="El ID ya existe"
                )
    
    usuarios.append(usuario) 
    
    return {
        "mensaje": "Usuario agregado",
        "datos": usuario,
        "status": "200"
    }

@app.put("/v1/usuarios/{id}", tags=['CRUD usuarios'])
async def actualizar_usuarios(id: int, usuario_actualizado: dict):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuario_actualizado["id"] = id 
            
            usuarios[index] = usuario_actualizado
            return {
                "mensaje": "Usuario actualizado",
                "datos_anteriores": usr,
                "datos_nuevos": usuario_actualizado
            }
            
    raise HTTPException(
        status_code=404, 
        detail="Usuario no encontrado"
        )

@app.delete("/v1/usuarios/{id}", tags=['CRUD usuarios'])
async def eliminar_usuarios(id: int):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuarios.pop(index)
            return {
                "mensaje": "Usuario eliminado",
                "id_eliminado": id
            }
            
    raise HTTPException(
        status_code=404, 
        detail="Usuario no encontrado"
        )