# Seguridad básica HTTP
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

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


