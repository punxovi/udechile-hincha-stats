import os
from typing import Optional
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from infrastructure.persistence.sqlite_store import SqliteDatabase, SqliteMatchRepository, SqliteAttendanceRepository, SqliteLeagueTableRepository
from application.use_cases.match_use_cases import GetHistoricalMatchesUseCase, MarkAttendanceUseCase, UnmarkAttendanceUseCase
from application.use_cases.dashboard_use_case import GenerateFanDashboardUseCase

from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel

router = APIRouter()

# Asegurar que el template dir apunta correctamente
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=template_dir)

# Singleton-like database access para FastAPI Depends
db = SqliteDatabase("udechile_stats.db")

def get_match_repo():
    return SqliteMatchRepository(db)

def get_attendance_repo():
    return SqliteAttendanceRepository(db)

def get_league_table_repo():
    return SqliteLeagueTableRepository(db)

def get_current_user(request: Request) -> Optional[dict]:
    """Helper para obtener el usuario autenticado desde las cookies de sesión."""
    user_id = request.cookies.get("session_user_id")
    user_email = request.cookies.get("session_user_email")
    user_name = request.cookies.get("session_user_name")
    if not user_id:
        return None
    return {"id": user_id, "email": user_email, "name": user_name or user_email}

class LoginPayload(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

@router.get("/login")
async def login_page(request: Request):
    """Renderiza la pantalla de acceso local."""
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )

@router.post("/api/auth/login")
async def local_login(payload: LoginPayload):
    """Autenticación local mockeada sin Supabase."""
    import hashlib
    
    email_lower = payload.email.lower()
    prefix = payload.email.split("@")[0].lower()
    
    # Manejo especial para cuentas de pruebas históricas y del usuario principal
    if email_lower == "hincha_1" or prefix == "hincha_1":
        user_id = "hincha_1"
        display_name = payload.name or "Hincha Uno"
    elif prefix == "bustamantevicente12" or email_lower == "vicente_bg" or prefix == "vicente_bg":
        user_id = "Vicente_Bg"
        display_name = payload.name or "Vicente Bg"
    else:
        user_id = hashlib.md5(payload.email.encode()).hexdigest()
        display_name = payload.name or payload.email.split('@')[0]
    
    response = JSONResponse(content={"status": "success"})
    # Configurar cookies httpOnly
    response.set_cookie("session_user_id", user_id, max_age=86400 * 30, httponly=True, samesite="lax")
    response.set_cookie("session_user_email", payload.email, max_age=86400 * 30, httponly=True, samesite="lax")
    response.set_cookie("session_user_name", display_name, max_age=86400 * 30, httponly=True, samesite="lax")
    response.set_cookie("session_access_token", "local_token", max_age=86400 * 30, httponly=True, samesite="lax")
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
    enriched_data = use_case.execute_enriched(user_id)
    
    import json
    # Serializar a nivel de dict convirtiendo los snapshots a dict primero
    serialized_data = {
        "general": enriched_data["general"].model_dump(),
        "by_year": {y: snap.model_dump() for y, snap in enriched_data["by_year"].items()},
        "classics": {
            "combined": enriched_data["classics"]["combined"].model_dump(),
            "cc": enriched_data["classics"]["cc"].model_dump(),
            "uc": enriched_data["classics"]["uc"].model_dump()
        }
    }
    dashboard_json = json.dumps(serialized_data)
    
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user_id": user_id, 
            "snapshot": enriched_data["general"],
            "enriched_data": enriched_data,
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
