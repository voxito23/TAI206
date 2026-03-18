from fastapi import FastAPI
from app.routers import usuarios, misc  


app = FastAPI(
    title="Mi primera API",
    description="Victor Osvaldo RH",
    version="1.0"
)

app.include_router(usuarios.router)
app.include_router(misc.router) 