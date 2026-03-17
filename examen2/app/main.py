from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, field_validator
from datetime import date
import secrets

app = FastAPI(
    title="API de Gestion de Citas Medicas",
    version="1.0"
)

citas = [
    {
        "id": 1,
        "paciente": "Ana Lopez",
        "doctor": "Dr. Ramirez",
        "especialidad": "Cardiologia",
        "fecha": "2026-03-15",
        "motivo": "Chequeo general"
    },
    {
        "id": 2,
        "paciente": "Luis Perez",
        "doctor": "Dra. Martinez",
        "especialidad": "Dermatología",
        "fecha": "2026-03-16",
        "motivo": "Revisión de piel"
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
    id: int = Field(..., gt=0, description="Identificador de la cita", example=1)
    paciente: str = Field(..., min_length=2, max_length=100, description="Nombre del paciente", example="Osvaldo")
    doctor: str = Field(..., min_length=2, max_length=100, description="Nombre del Medico", example="Saul Silva")
    especialidad: str = Field(..., min_length=2, max_length=100, description="Nombre de la Especialidad", example="Psiquiatra")
    fecha: date = Field(..., description="Fecha de la cita en formato YYYY-MM-DD", example="2026-03-16")
    motivo: str = Field(..., min_length=2, max_length=200, description="Motivo", example="Revision de piel")

    @field_validator("fecha")
    @classmethod
    def validar_fecha(cls, value: date):
        if value < date.today():
            raise ValueError("La fecha no puede ser menor a la actual")
        return value

class ConfirmarCita(BaseModel):
    confirmada: bool = Field(..., description="Estado de confirmación", example=True)


@app.get("/", tags=["Inicio"])
async def inicio():
    return {"mensaje": "API de Sistema de Citas Medicas"}


@app.get("/v1/citas/", tags=["CRUD Citas"])
async def listar_citas(usuario: str = Depends(verificar_peticion)): 
    return {
        "status": "200",
        "usuario": usuario,
        "total": len(citas),
        "data": citas
    }


@app.get("/v1/citas/{id}/consulta", tags=["CRUD Citas"])
async def consultar_cita_por_id(id: int):
    for c in citas:
        if c["id"] == id:
            return {
                "status": 200,
                "data": c
            }
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cita con id {id} no encontrada"
    )


@app.post("/v1/citas/", tags=["CRUD Citas"], status_code=status.HTTP_201_CREATED)
async def registrar_cita(cita: CitaBase):
    for c in citas:
        if c["id"] == cita.id:
            raise HTTPException(
                status_code=400,
                detail="El ID de la cita ya existe"
            )

        if (
            c["doctor"].lower() == cita.doctor.lower()
            and c["fecha"] == str(cita.fecha)
        ):
            raise HTTPException(
                status_code=409,
                detail="El doctor ya tiene una cita programada en esa fecha"
            )

    citas_mismo_paciente_mismo_dia = 0
    for c in citas:
        if c["paciente"].lower() == cita.paciente.lower() and c["fecha"] == str(cita.fecha):
            citas_mismo_paciente_mismo_dia += 1

    if citas_mismo_paciente_mismo_dia >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se permiten más de 3 citas en un día por paciente"
        )

    nueva_cita = cita.model_dump()
    nueva_cita["fecha"] = str(nueva_cita["fecha"])
    citas.append(nueva_cita)

    return {
        "mensaje": "Cita confirmada exitosamente",
        "datos": nueva_cita,
        "status": "201"
    }


@app.put("/v1/citas/{id}/confirmar", tags=["CRUD Citas"])
async def confirmar_cita(id: int, datos_confirmacion: ConfirmarCita):
    for idx, c in enumerate(citas):
        if c["id"] == id:
            citas[idx]["confirmada"] = datos_confirmacion.confirmada
            return {
                "mensaje": "Estado de confirmación actualizado correctamente",
                "datos": citas[idx],
                "status": 200
            }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Cita con id {id} no encontrada"
    )


@app.delete("/v1/citas/{id}/eliminar", tags=["CRUD Citas"])
async def eliminar_cita(id: int, usuario_auth: str = Depends(verificar_peticion)):
    for index, c in enumerate(citas):
        if c["id"] == id: 
            cita_eliminada = citas.pop(index)
            return {
                "mensaje": f"Cita eliminada correctamente por {usuario_auth}",
                "data": cita_eliminada
            }

    raise HTTPException(
        status_code=404,
        detail="La cita no existe"
    )