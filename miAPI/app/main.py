from typing import Optional
from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import asyncio
import secrets

app = FastAPI(
    title="Mi primera API",
    description="Victor Osvaldo RH",
    version="1.0"
)

# Base de datos ficticia
usuarios = [
    {"id": 1, "nombre": "Victor", "edad": 21},
    {"id": 2, "nombre": "Mauricio", "edad": 20},
    {"id": 3, "nombre": "Luis", "edad": 21},
]

# Seguridad básica HTTP
security = HTTPBasic()


def verificar_peticion(credentials: HTTPBasicCredentials = Depends(security)):
    usuario_auth = secrets.compare_digest(credentials.username, "vichdz")
    contra_auth = secrets.compare_digest(credentials.password, "1234")

    if not (usuario_auth and contra_auth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no válidas"
        )

    return credentials.username


# Modelo de validación
class UsuarioBase(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario", example=1)
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre del usuario", example="Victor")
    edad: int = Field(..., ge=0, le=121, description="Edad validada entre 0 y 121", example=30)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str):
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío")
        return value


# Endpoints básicos
@app.get("/", tags=["Inicio"])
async def holamundo():
    return {"mensaje": "Hola mundo FastAPI"}


@app.get("/v1/bienvenidos", tags=["Inicio"])
async def bienvenidos():
    return {"mensaje": "Bienvenidos a FastAPI"}


@app.get("/v1/calificaciones", tags=["Asincronia"])
async def calificaciones():
    await asyncio.sleep(2)
    return {"mensaje": "Tu calificación en TAI es 10"}


@app.get("/v1/parametroO/{id}", tags=["Parametro Obligatorio"])
async def consultar_usuario_por_id(id: int):
    await asyncio.sleep(1)
    return {"usuario_encontrado": id}


@app.get("/v1/ParametroOp", tags=["Parametro Opcional"])
async def consulta_op(id: Optional[int] = None):
    await asyncio.sleep(1)

    if id is not None:
        for usuario in usuarios:
            if usuario["id"] == id:
                return {"usuario_encontrado": id, "datos": usuario}
        return {"mensaje": "Usuario no encontrado"}

    return {"aviso": "No se proporcionó un ID"}


# CRUD
@app.get("/v1/usuarios/", tags=["CRUD usuarios"])
async def consultar_usuarios():
    return {
        "status": 200,
        "total": len(usuarios),
        "data": usuarios
    }


@app.get("/v1/usuarios/{id}", tags=["CRUD usuarios"])
async def consultar_usuario(id: int):
    for usuario in usuarios:
        if usuario["id"] == id:
            return {
                "status": 200,
                "data": usuario
            }

    raise HTTPException(
        status_code=404,
        detail="Usuario no encontrado"
    )


@app.post("/v1/usuarios/", tags=["CRUD usuarios"])
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


@app.put("/v1/usuarios/{id}", tags=["CRUD usuarios"])
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


@app.delete("/v1/usuarios/{id}", tags=["CRUD usuarios"])
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
    
    


##################################################################################
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from datetime import date, time, datetime
import secrets

app = FastAPI(
    title="API de Sistema de Reservas de Restaurante",
    version="1.0"
)

# Base de datos simulada y limpia (sin el campo "confirmada")
reservas = [
    {
        "id": 1,
        "nombre_cliente": "Roberto Carlos",
        "fecha": "2026-03-20", 
        "hora": "14:30:00",
        "numero_personas": 4
    },
    {
        "id": 2,
        "nombre_cliente": "Maria Antonieta",
        "fecha": "2026-03-21", 
        "hora": "20:00:00",
        "numero_personas": 2
    },
    {
        "id": 3,
        "nombre_cliente": "Familia Martinez",
        "fecha": "2026-03-24", 
        "hora": "09:00:00",
        "numero_personas": 8
    }
]

# Configuración de Seguridad
security = HTTPBasic()

def verificar_admin(credentials: HTTPBasicCredentials = Depends(security)):
    usuario_ok = secrets.compare_digest(credentials.username, "admin")
    contra_ok = secrets.compare_digest(credentials.password, "rest123")

    if not (usuario_ok and contra_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no válidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Modelo Pydantic 
class ReservaBase(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de la reserva", example=4)
    nombre_cliente: str = Field(..., min_length=6, description="Nombre del cliente", example="Carlos Slim")
    fecha: date = Field(..., description="Fecha de la reserva (YYYY-MM-DD)", example="2026-04-15")
    hora: time = Field(..., description="Hora de la reserva (HH:MM)", example="14:30")
    numero_personas: int = Field(..., ge=1, le=10, description="Número de personas (1 a 10)", example=4)

# ----------------------------------------------------
# ENDPOINTS
# ----------------------------------------------------

@app.get("/", tags=["Inicio"])
async def inicio():
    return {"mensaje": "API de Sistema de Reservas de Restaurante"}


# 1. LISTAR RESERVAS (Ruta Protegida)
@app.get("/v1/reservas/", tags=["Reservas"])
async def listar_reservas(usuario: str = Depends(verificar_admin)): 
    return {
        "status": 200,
        "usuario_autorizado": usuario,
        "total": len(reservas),
        "data": reservas
    }


# 2. CONSULTAR POR ID
@app.get("/v1/reservas/{id}", tags=["Reservas"])
async def consultar_reserva_por_id(id: int):
    for r in reservas:
        if r["id"] == id:
            return {
                "status": 200,
                "data": r
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Reserva con id {id} no encontrada"
    )


# 3. CREAR RESERVA
@app.post("/v1/reservas/", tags=["Reservas"], status_code=status.HTTP_201_CREATED)
async def crear_reserva(reserva: ReservaBase):
    for r in reservas:
        if r["id"] == reserva.id:
            raise HTTPException(
                status_code=400,
                detail="El ID de la reserva ya existe"
            )

    if reserva.fecha.weekday() == 6:
        raise HTTPException(
            status_code=400, 
            detail="El restaurante no acepta reservas en domingo"
        )

    if reserva.hora < time(8, 0) or reserva.hora > time(22, 0):
        raise HTTPException(
            status_code=400, 
            detail="Las reservas solo se permiten entre las 08:00 y las 22:00"
        )

    fecha_hora_reserva = datetime.combine(reserva.fecha, reserva.hora)
    if fecha_hora_reserva <= datetime.now():
        raise HTTPException(
            status_code=400, 
            detail="La reserva debe programarse para una fecha y hora en el futuro"
        )

    nueva_reserva = reserva.model_dump()
    nueva_reserva["fecha"] = str(nueva_reserva["fecha"])
    nueva_reserva["hora"] = str(nueva_reserva["hora"])
    
    reservas.append(nueva_reserva)

    return {
        "mensaje": "Reserva confirmada exitosamente", # Mensaje directo de confirmación
        "datos": nueva_reserva,
        "status": 201
    }


# 4. CONFIRMAR RESERVA (Por si se requiere hacer un check manual después)
@app.put("/v1/reservas/{id}/confirmar", tags=["Reservas"])
async def confirmar_reserva(id: int):
    for idx, r in enumerate(reservas):
        if r["id"] == id:
            # Usamos .get() para evitar error si la llave no existe en el JSON original
            if r.get("confirmada"):
                raise HTTPException(status_code=400, detail="Esta reserva ya fue confirmada previamente")
                
            reservas[idx]["confirmada"] = True
            return {
                "mensaje": "Reserva confirmada exitosamente",
                "datos": reservas[idx],
                "status": 200
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Reserva con id {id} no encontrada"
    )


# 5. CANCELAR (ELIMINAR) RESERVA (Ruta Protegida)
@app.delete("/v1/reservas/{id}/cancelar", tags=["Reservas"])
async def cancelar_reserva(id: int, usuario: str = Depends(verificar_admin)):
    for index, r in enumerate(reservas):
        if r["id"] == id: 
            reserva_cancelada = reservas.pop(index)
            return {
                "mensaje": f"Reserva cancelada y eliminada correctamente por {usuario}",
                "data": reserva_cancelada
            }

    raise HTTPException(
        status_code=404,
        detail="La reserva no existe"
    )