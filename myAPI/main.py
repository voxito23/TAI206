# importaciones
from typing import Optional
from fastapi import FastAPI
import asyncio

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



@app.get("/v1/usuarios/{id}", tags=['Parametro Obligatorio'])
async def ConsultarUsuarios(id: int):
    await asyncio.sleep(6)
    return {"usuario encontrado": id}


@app.get("/v1/usuarios_op", tags=['Parametro Opcional'])
async def ConsultaOp(id: Optional[int] = None):
    await asyncio.sleep(6)
    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"usuario encontrado": id ,
                        "Datos": usuario}
        return {"Mensaje": "usuario no encontrado"}
    else:
        return {"Aviso": "No se proporcionó un ID"}
    
    
    
    