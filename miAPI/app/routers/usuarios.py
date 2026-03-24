# CRUD
from fastapi import status, HTTPException, Depends, APIRouter
from app.models.usuario import UsuarioBase
from app.data.database import usuarios
from app.security.auth import verificar_peticion
    
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.usuario import usuario as usuarioDB

router= APIRouter(
    prefix="/v1/usuarios",
    tags=["CRUD HTTP"])       


@router.get("/")
async def leer_usuarios(db: Session = Depends(get_db)):
    
    consultausuarios = db.query(usuarioDB).all()  
    
    return {
        "status": 200,
        "total": len(consultausuarios),
        "data": consultausuarios
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: UsuarioBase,db: Session = Depends(get_db)):
    
    nuevo_usuario = usuarioDB(nombre=usuario.nombre,edad=usuario.edad) 
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)


    return {
        "mensaje": "Usuario agregado correctamente",
        "status": 201,
    }


@router.put("/{id}",status_code=status.HTTP_200_OK)
async def actualizar_usuario(id: int, usuario_actualizado: UsuarioBase):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            datos_anteriores = usuarios[index].copy()

            nuevos_datos = usuario_actualizado.model_dump()
            nuevos_datos["id"] = id  # fuerza el ID de la URL

            usuarios[index] = nuevos_datos

            return {
                "mensaje": "Usuario actualizado correctamente",
                "data_anterior": datos_anteriores,
                "data_nueva": nuevos_datos
            }

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, usuario_auth: str = Depends(verificar_peticion)):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuario_eliminado = usuarios.pop(index)
            return {
                "mensaje": f"Usuario eliminado correctamente por {usuario_auth}",
                "data": usuario_eliminado
            }

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )
    
    