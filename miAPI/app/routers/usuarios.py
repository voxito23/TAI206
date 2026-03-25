from fastapi import status, HTTPException, Depends, APIRouter
from app.models.usuario import UsuarioBase
from app.security.auth import verificar_peticion
from typing import Dict, Any

from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.usuario import usuario as usuarioDB

router = APIRouter(
    prefix="/v1/usuarios",
    tags=["CRUD HTTP"]
)       

@router.get("/")
async def leer_usuarios(db: Session = Depends(get_db)):
    consultausuarios = db.query(usuarioDB).all()  
    
    return {
        "status": 200,
        "total": len(consultausuarios),
        "data": consultausuarios
    }

@router.get("/{id}")
async def leer_usuario(id: int, db: Session = Depends(get_db)):
    
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    return {
        "status": 200,
        "data": usuario
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario: UsuarioBase, db: Session = Depends(get_db)):
    
    nuevo_usuario = usuarioDB(nombre=usuario.nombre, edad=usuario.edad) 
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario agregado correctamente",
        "status": 201,
        "data": nuevo_usuario 
    }

@router.put("/{id}", status_code=status.HTTP_200_OK)
async def actualizar_usuario(id: int, usuario_actualizado: UsuarioBase, db: Session = Depends(get_db)):
    
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = usuario_actualizado.nombre
    usuario.edad = usuario_actualizado.edad

    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Usuario actualizado correctamente",
        "data_nueva": usuario
    }

@router.patch("/{id}", status_code=status.HTTP_200_OK)
async def modificacion_parcial_usuario(id: int, payload: Dict[str, Any], db: Session = Depends(get_db)):
    
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if "nombre" in payload:
        usuario.nombre = payload["nombre"]
    if "edad" in payload:
        usuario.edad = payload["edad"]

    db.commit()
    db.refresh(usuario)

    return {
        "mensaje": "Usuario modificado parcialmente de forma correcta",
        "data_nueva": usuario
    }
    
@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario(id: int, db: Session = Depends(get_db), usuario_auth: str = Depends(verificar_peticion)):
    
    usuario = db.query(usuarioDB).filter(usuarioDB.id == id).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()

    return {
        "mensaje": f"Usuario eliminado correctamente por {usuario_auth}",
        "id_eliminado": id
    }