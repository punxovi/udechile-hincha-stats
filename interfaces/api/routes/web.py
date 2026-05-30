import os
from typing import Optional
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from infrastructure.persistence.postgres_store import PostgresDatabase, PostgresMatchRepository, PostgresAttendanceRepository, PostgresLeagueTableRepository
from application.use_cases.match_use_cases import GetHistoricalMatchesUseCase, MarkAttendanceUseCase, UnmarkAttendanceUseCase
from application.use_cases.dashboard_use_case import GenerateFanDashboardUseCase

from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

router = APIRouter()

# Asegurar que el template dir apunta correctamente
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=template_dir)

# Singleton-like database access para FastAPI Depends
db = PostgresDatabase()

def get_match_repo():
    return PostgresMatchRepository(db)

def get_attendance_repo():
    return PostgresAttendanceRepository(db)

def get_league_table_repo():
    return PostgresLeagueTableRepository(db)

def get_current_user(request: Request) -> Optional[dict]:
    """Helper para obtener el usuario autenticado desde las cookies de sesión."""
    user_id = request.cookies.get("session_user_id")
    user_email = request.cookies.get("session_user_email")
    user_name = request.cookies.get("session_user_name")
    if not user_id:
        return None
    return {"id": user_id, "email": user_email, "name": user_name or user_email}

class SessionPayload(BaseModel):
    user_id: str
    email: str
    access_token: str
    name: Optional[str] = None

@router.get("/login")
async def login_page(request: Request):
    """Renderiza la pantalla de acceso cargando las credenciales de Supabase."""
    db_url = os.getenv("SUPABASE_DB_URL")
    proj_ref = "bfeaevenqffrgjuduxmv"  # Referencia por defecto extraída
    if db_url and "@db." in db_url:
        try:
            proj_ref = db_url.split("@db.")[1].split(".supabase")[0]
        except Exception:
            pass
            
    supabase_url = f"https://{proj_ref}.supabase.co"
    supabase_anon_key = os.getenv("SUPABASE_ANON_KEY", "")
    
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "supabase_url": supabase_url,
            "supabase_anon_key": supabase_anon_key
        }
    )

@router.post("/api/auth/session")
async def set_auth_session(payload: SessionPayload):
    """Establece la sesión del servidor sincronizada desde el cliente."""
    response = JSONResponse(content={"status": "success"})
    # Configurar cookies httpOnly seguras con 30 días de duración
    response.set_cookie("session_user_id", payload.user_id, max_age=86400 * 30, httponly=True, samesite="lax")
    response.set_cookie("session_user_email", payload.email, max_age=86400 * 30, httponly=True, samesite="lax")
    response.set_cookie("session_user_name", payload.name or "", max_age=86400 * 30, httponly=True, samesite="lax")
    response.set_cookie("session_access_token", payload.access_token, max_age=86400 * 30, httponly=True, samesite="lax")
    return response

@router.get("/logout")
async def logout():
    """Cierra la sesión limpiando las cookies y redirigiendo al login."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_user_id")
    response.delete_cookie("session_user_email")
    response.delete_cookie("session_user_name")
    response.delete_cookie("session_access_token")
    return response

@router.get("/")
async def index(
    request: Request, 
    year: int = None, 
    competition_id: str = None, 
    sort_date: str = "desc", 
    match_repo = Depends(get_match_repo),
    table_repo = Depends(get_league_table_repo),
    attendance_repo = Depends(get_attendance_repo)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
        
    use_case = GetHistoricalMatchesUseCase(match_repo)
    
    # Si no se selecciona un año, mostramos 2025 por defecto ya que es la temporada más moderna
    selected_year = year if year else 2025
    matches_of_year = use_case.execute(year=selected_year)
    
    # Extraer diccionario de competencias únicas del año seleccionado
    competitions = {}
    for match in matches_of_year:
        if match.competition.id not in competitions:
            competitions[match.competition.id] = match.competition.name
            
    # Filtrar en memoria por competition_id si está presente
    if competition_id and competition_id != "all":
        matches = [m for m in matches_of_year if m.competition.id == competition_id]
    else:
        matches = matches_of_year
        
    # Ordenar por fecha (priorizando fecha)
    matches.sort(key=lambda m: m.date, reverse=(sort_date == "desc"))
    
    # Genera la lista de años disponibles (de 2025 a 2011 de mayor a menor)
    years = list(range(2025, 2010, -1))
    
    # Cargar tablas de posiciones para la temporada consultada
    league_tables = table_repo.get_league_tables_by_season(str(selected_year))
    
    # Obtener partidos asistidos por el usuario actual logueado
    attended_matches = attendance_repo.get_attended_match_ids(current_user["id"])
    
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "matches": matches,
            "years": years,
            "selected_year": selected_year,
            "competitions": competitions,
            "selected_competition": competition_id or "all",
            "sort_date": sort_date,
            "league_tables": league_tables,
            "attended_matches": attended_matches,
            "current_user": current_user
        }
    )

@router.get("/dashboard/{user_id}")
async def dashboard(
    request: Request, 
    user_id: str, 
    match_repo = Depends(get_match_repo), 
    attendance_repo = Depends(get_attendance_repo)
):
    current_user = get_current_user(request)
    
    use_case = GenerateFanDashboardUseCase(match_repo, attendance_repo)
    snapshot = use_case.execute(user_id)
    
    # Serializar directamente usando Pydantic
    dashboard_json = snapshot.model_dump_json()
    
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user_id": user_id, 
            "snapshot": snapshot,
            "dashboard_json": dashboard_json,
            "current_user": current_user
        }
    )

@router.post("/api/attend/{match_id}")
async def mark_attendance(
    request: Request,
    match_id: str, 
    attendance_repo = Depends(get_attendance_repo)
):
    current_user = get_current_user(request)
    if not current_user:
        return JSONResponse(status_code=401, content={"detail": "No autenticado"})
        
    use_case = MarkAttendanceUseCase(attendance_repo)
    use_case.execute(current_user["id"], match_id)
    return {"status": "ok", "match_id": match_id}

@router.delete("/api/attend/{match_id}")
async def unmark_attendance(
    request: Request,
    match_id: str, 
    attendance_repo = Depends(get_attendance_repo)
):
    current_user = get_current_user(request)
    if not current_user:
        return JSONResponse(status_code=401, content={"detail": "No autenticado"})
        
    use_case = UnmarkAttendanceUseCase(attendance_repo)
    use_case.execute(current_user["id"], match_id)
    return {"status": "ok", "match_id": match_id}
