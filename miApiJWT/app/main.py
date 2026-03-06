from typing import Optional
from fastapi import FastAPI, status, HTTPException, Depends
import asyncio
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, timezone
import jwt 
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Inicializacion o Instancia de la API
app = FastAPI(
    title='Mi API JWT',
    description='Victor Osvaldo RH',
    version='1.0'
)

# BD Ficticia
usuarios = [
    {"id":1, "nombre":"Victor","edad":21},
    {"id":2, "nombre":"Mauricio","edad":20},
    {"id":3, "nombre":"Luis","edad":21},
]

# Modelo de validacion Pydantic
class UsuarioBase(BaseModel):
    id: int = Field(..., gt=0, description="Identificador de usuario", example="1" )
    nombre: str = Field(..., min_length=3, max_length=50, description="Nombre del usuario", example="Victor") 
    edad: int = Field(..., ge=0, le=121, description="Edad validada entre 0 y 121", example="30")    
    
# CONFIGURACIONES OAUTH2 Y JWT
SECRET_KEY = "mysecretkey1234"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Le decimos a FastAPI dónde se generara el token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencia para verificar el token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise credentials_exception
        
    return username
# ENDPOINT DE AUTENTICACION

@app.post("/login", tags=['Autenticación'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # Validacion
    if form_data.username != "vichdz" or form_data.password != "1234":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generar token de 30 minutos
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ENDPOINTS PUBLICOS Y CRUD
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
async def ConsultarUsuarioPorId(id: int):
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
async def agregar_usuarios(usuario: UsuarioBase):
    for usr in usuarios:
        if usr["id"] == usuario.id:
            raise HTTPException(
                status_code=400, 
                detail="El ID ya existe"
                )
    
    usuarios.append(usuario.model_dump()) 
    
    return {
        "mensaje": "Usuario agregado",
        "datos": usuario,
        "status": "200"
    }

# ENDPOINTS PROTEGIDOS CON JWT
@app.put("/v1/usuarios/{id}", tags=['CRUD usuarios'])
async def actualizar_usuarios(id: int, usuario_actualizado: dict, usuario_actual: str = Depends(get_current_user)):
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuario_actualizado["id"] = id 
            
            usuarios[index] = usuario_actualizado
            return {
                "mensaje": f"Usuario actualizado por {usuario_actual}",
                "datos_anteriores": usr,
                "datos_nuevos": usuario_actualizado
            }
            
    raise HTTPException(
        status_code=404, 
        detail="Usuario no encontrado"
        )

@app.delete("/v1/usuarios/{id}", tags=['CRUD usuarios'])
async def eliminar_usuario(id: int, usuario_actual: str = Depends(get_current_user)): 
    for index, usr in enumerate(usuarios):
        if usr["id"] == id:
            usuarios.pop(index)
            return {
                "mensaje": f"Usuario eliminado correctamente por {usuario_actual}", 
                "id_eliminado": id
            }
            
    raise HTTPException(
        status_code=404, 
        detail="Usuario no encontrado"
        )