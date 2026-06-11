import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from infrastructure.persistence.sqlite_store import SqliteDatabase
from infrastructure.persistence.postgres_store import PostgresDatabase
from interfaces.api.routes.web import router

# Variable global para guardar la instancia de la DB y que las rutas puedan usarla
db_instance = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_instance
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        db_instance = PostgresDatabase(db_url)
    else:
        db_instance = SqliteDatabase("udechile_stats.db")
        
    db_instance.initialize_schema()
    yield

def create_app() -> FastAPI:
    app = FastAPI(title="U de Chile Fan Dashboard", lifespan=lifespan)
    
    # Crear carpeta static si no existe (por precaución)
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    os.makedirs(static_dir, exist_ok=True)
    
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    app.include_router(router)
    
    return app
