from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
import os

#1. Definiendo la URL de conexión a la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://admin:123456@postgres:5432/DB_miapi"
    )

#2. Creamos el motor de la conexión a la base de datos
engine = create_engine(DATABASE_URL)

#3. Agregamos el gestor de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False, 
    bind=engine)

#4. Creamos la clase base para los modelos
Base = declarative_base()

#5 . Función para el manejo en sesion en los requests
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()