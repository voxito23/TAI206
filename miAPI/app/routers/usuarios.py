# CRUD
from fastapi import status, HTTPException, Depends, APIRouter
from app.models.usuario import UsuarioBase
from app.data.database import usuarios
from app.security.auth import verificar_peticion    

router= APIRouter(
    prefix="/v1/usuarios",
    tags=["CRUD HTTP"])       


@router.get("/")
async def consultar_usuarios():
    return {
        "status": 200,
        "total": len(usuarios),
        "data": usuarios
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
async def agregar_usuario(usuario: UsuarioBase):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400,
                detail="El ID ya existe"
            )

    nuevo_usuario = usuario.model_dump()
    usuarios.append(nuevo_usuario)

    return {
        "mensaje": "Usuario agregado correctamente",
        "status": 201,
        "data": nuevo_usuario
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
    
    