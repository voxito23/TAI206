from fastapi import APIRouter
import asyncio
from app.data.database import usuarios
from typing import Optional  

router = APIRouter(tags=["Varios"])

@router.get("/")
async def holamundo():
    return {"mensaje": "Hola mundo FastAPI"}


@router.get("/v1/bienvenidos")
async def bienvenidos():
    return {"mensaje": "Bienvenidos a FastAPI"}


@router.get("/v1/calificaciones")
async def calificaciones():
    await asyncio.sleep(2)
    return {"mensaje": "Tu calificación en TAI es 10"}


@router.get("/v1/parametroO/{id}")
async def consultar_usuario_por_id(id: int):
    await asyncio.sleep(1)
    return {"usuario_encontrado": id}


@router.get("/v1/ParametroOp")
async def consulta_op(id: Optional[int] = None):
    await asyncio.sleep(1)

    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"usuario_encontrado": id, "datos": usuario}
        return {"mensaje": "Usuario no encontrado"}

    return {"aviso": "No se proporcionó un ID"}


