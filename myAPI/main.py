# importaciones
from fastapi import FastAPI

# Inicializacion
app = FastAPI()

# Endpoint
@app.get("/")
async def holamundo():
    return {"mensaje": "Hola mundo FastAPI"}

@app.get("/bienvenidos")
async def bienvenidos():
    return {"mensaje": "Bienvenidos a FastAPI"}

