import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from infrastructure.persistence.postgres_store import PostgresDatabase
from interfaces.api.routes.web import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa la base de datos PostgreSQL de Supabase al arrancar
    db = PostgresDatabase()
    db.initialize_schema()
    yield

def create_app() -> FastAPI:
    app = FastAPI(title="U de Chile Fan Dashboard", lifespan=lifespan)
    
    # Crear carpeta static si no existe (por precaución)
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    app.include_router(router)
    
    return app
