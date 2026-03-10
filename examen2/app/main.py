from fastapi import FastAPI, status, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Literal
import secrets
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Optional
from fastapi import FastAPI, status, HTTPException, Depends
import asyncio


app = FastAPI(
    title="API de Gestión de Citas Médicas",
    version="1.0"
)
citas = [
    {
        "id": 1,
        "paciente": "Ana López",
        "doctor": "Dr. Ramírez",
        "especialidad": "Cardiología",
        "fecha": "2026-03-15",
        "hora": "09:00",
        "motivo": "Chequeo general",
        "estado": "programada"
    },
    {
        "id": 2,
        "paciente": "Luis Pérez",
        "doctor": "Dra. Martínez",
        "especialidad": "Dermatología",
        "fecha": "2026-03-16",
        "hora": "11:30",
        "motivo": "Revisión de piel",
        "estado": "programada"
    }
]

security = HTTPBasic()


def verificar_peticion(credentials: HTTPBasicCredentials = Depends(security)):
    usuario_auth = secrets.compare_digest(credentials.username, "root")
    contra_auth = secrets.compare_digest(credentials.password, "1234")

    if not (usuario_auth and contra_auth):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales no válidas"
        )

    return credentials.username


class CitaBase(BaseModel):
    id: int = Field(..., gt=0)
    paciente: str = Field(..., min_length=2, max_length=100)
    doctor: str = Field(..., min_length=2, max_length=100)
    especialidad: str = Field(..., min_length=2, max_length=100)
    fecha: str = Field(..., min_length=10, max_length=10)
    hora: str = Field(..., min_length=5, max_length=5)
    motivo: str = Field(..., min_length=2, max_length=200)
    estado: Literal["programada","atendida"] = "programada"


@app.get("/", tags=["Inicio"])
async def inicio():
    return {"mensaje": "API de Sistema de Citas Medicas"}


@app.get("/v1/citas/", tags=["CRUD Citas"])
async def listar_citas():
    return {
        "status": "200",
        "total": len(citas),
        "data": citas
    }


@app.post("/v1/citas/", tags=["CRUD Citas"])
async def registrar_cita(cita: CitaBase):
    for c in citas:
        if c["id"] == cita.id:
            raise HTTPException(
                status_code=400,
                detail="El ID de la cita ya existe"
            )

        if (
            c["doctor"].lower() == cita.doctor.lower()
            and c["fecha"] == cita.fecha
            and c["hora"] == cita.hora
            and c["estado"] == "programada"
        ):
            raise HTTPException(
                status_code=409,
                detail="El doctor ya tiene una cita programada en esa fecha y hora"
            )

    citas.append(cita.model_dump())

    return {
        "mensaje": "Cita registrada correctamente",
        "datos": cita,
        "status": "201"
    }


@app.put("/v1/citas/{id}/cancelar", tags=["CRUD Citas"])
async def cancelar_cita(id: int):
    for index, c in enumerate(citas):
        if c["id"] == id:
            if c["estado"] == "cancelada":
                raise HTTPException(
                    status_code=409,
                    detail="La cita ya está cancelada"
                )

            citas[index]["estado"] = "cancelada"

            return {
                "mensaje": "Cita cancelada correctamente",
                "status": "200"
            }

    raise HTTPException(
        status_code=404,
        detail="La cita no existe"
    )


@app.put("/v1/citas/{id}/atender", tags=["CRUD Citas"])
async def atender_cita(id: int):
    for index, c in enumerate(citas):
        if c["id"] == id:
            if c["estado"] == "atendida":
                raise HTTPException(
                    status_code=409,
                    detail="La cita ya fue atendida"
                )

            if c["estado"] == "cancelada":
                raise HTTPException(
                    status_code=409,
                    detail="No se puede atender una cita cancelada"
                )

            citas[index]["estado"] = "atendida"

            return {
                "mensaje": "Cita marcada como atendida",
                "status": "200"
            }

    raise HTTPException(
        status_code=404,
        detail="La cita no existe"
    )


@app.delete("/v1/citas/{id}", tags=["CRUD Citas"])
async def eliminar_cita(id: int):
    for index, c in enumerate(citas):
        if c["id"] == id:
            citas.pop(index)
            return {
                "mensaje": "Cita eliminada correctamente",
                "id_eliminado": id,
                "status": "200"
            }

    raise HTTPException(
        status_code=404,
        detail="La cita no existe"
    )