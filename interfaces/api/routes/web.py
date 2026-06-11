import os
import json
import datetime
import bcrypt
from typing import Optional
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates

from infrastructure.persistence.sqlite_store import SqliteDatabase, SqliteMatchRepository, SqliteAttendanceRepository, SqliteLeagueTableRepository
from infrastructure.persistence.postgres_store import PostgresDatabase, PostgresMatchRepository, PostgresAttendanceRepository, PostgresTableRepository
from application.use_cases.match_use_cases import GetHistoricalMatchesUseCase, MarkAttendanceUseCase, UnmarkAttendanceUseCase
from application.use_cases.dashboard_use_case import GenerateFanDashboardUseCase
from infrastructure.game.game_data import PLANTELES_HISTORICOS

from fastapi.responses import RedirectResponse, JSONResponse
import pydantic
from pydantic import BaseModel

# En producción (SECURE_COOKIES=true) las cookies llevan el flag Secure
# para que el browser no las envíe por HTTP plano.
_SECURE_COOKIES = os.getenv("SECURE_COOKIES", "false").lower() == "true"

router = APIRouter()

# Asegurar que el template dir apunta correctamente
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=template_dir)

def get_match_repo():
    from interfaces.api.app import db_instance
    if isinstance(db_instance, PostgresDatabase):
        return PostgresMatchRepository(db_instance)
    return SqliteMatchRepository(db_instance)

def get_attendance_repo():
    from interfaces.api.app import db_instance
    if isinstance(db_instance, PostgresDatabase):
        return PostgresAttendanceRepository(db_instance)
    return SqliteAttendanceRepository(db_instance)

def get_league_table_repo():
    from interfaces.api.app import db_instance
    if isinstance(db_instance, PostgresDatabase):
        return PostgresTableRepository(db_instance)
    return SqliteLeagueTableRepository(db_instance)

def get_current_user(request: Request) -> Optional[dict]:
    """Devuelve el usuario autenticado desde las cookies de sesión, o None."""
    user_id = request.cookies.get("session_user_id")
    if not user_id:
        return None
    user_name = request.cookies.get("session_user_name", "")
    return {"id": user_id, "name": user_name}

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
    import uuid
    from interfaces.api.app import db_instance
    from infrastructure.persistence.postgres_store import PostgresDatabase, PostgresUserRepository

    email_lower = payload.email.lower().strip()

    if isinstance(db_instance, PostgresDatabase):
        user_repo = PostgresUserRepository(db_instance)

        if payload.name:
            # ── Registro ──────────────────────────────────────────────────────
            # bcrypt con factor de coste 12: ~250ms por hash, impráctible de brute-forcear.
            # Cada hash incluye una salt única aleatoria, por lo que dos usuarios con la
            # misma contraseña producen hashes distintos.
            pw_hash = bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt(rounds=12)).decode()
            user_id = str(uuid.uuid4())
            success = user_repo.create_user(user_id, email_lower, pw_hash, payload.name)
            if not success:
                return JSONResponse(status_code=400, content={"status": "error", "message": "El correo ya está registrado."})
            display_name = payload.name
        else:
            # ── Login ─────────────────────────────────────────────────────────
            user_data = user_repo.get_user_by_email(email_lower)
            if not user_data:
                return JSONResponse(status_code=401, content={"status": "error", "message": "Credenciales incorrectas."})
            stored_hash = user_data["password_hash"]
            # Soporte de migración: si el hash existente es SHA-256 (64 hex chars),
            # se verifica con SHA-256 y se migra a bcrypt de forma transparente.
            import hashlib
            if stored_hash.startswith("$2"):
                valid = bcrypt.checkpw(payload.password.encode(), stored_hash.encode())
            else:
                valid = (stored_hash == hashlib.sha256(payload.password.encode()).hexdigest())
                if valid:
                    new_hash = bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt(rounds=12)).decode()
                    user_repo.update_password_hash(user_data["id"], new_hash)
            if not valid:
                return JSONResponse(status_code=401, content={"status": "error", "message": "Credenciales incorrectas."})
            user_id = user_data["id"]
            display_name = user_data["name"]
    else:
        # Fallback SQLite local — solo para desarrollo, no expuesto en producción
        user_id = str(uuid.uuid4())
        display_name = payload.name or payload.email.split("@")[0]

    response = JSONResponse(content={"status": "success"})
    response.set_cookie("session_user_id", user_id, max_age=86400 * 30, httponly=True, samesite="lax", secure=_SECURE_COOKIES)
    response.set_cookie("session_user_name", display_name, max_age=86400 * 30, httponly=True, samesite="lax", secure=_SECURE_COOKIES)
    return response

@router.get("/logout")
async def logout():
    """Cierra la sesión limpiando las cookies y redirigiendo al login."""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_user_id")
    response.delete_cookie("session_user_name")
    # Limpiar cookies legacy en caso de que existan de sesiones anteriores
    response.delete_cookie("session_user_email")
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
    
    # Genera la lista de años disponibles (de 2025 a 2005 de mayor a menor)
    years = list(range(2025, 1996, -1))
    
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
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    # Un usuario solo puede ver su propio dashboard.
    if current_user["id"] != user_id:
        return RedirectResponse(url=f"/dashboard/{current_user['id']}", status_code=303)
    
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

class SaveDreamTeamPayload(BaseModel):
    team_name: str = pydantic.Field(..., max_length=80)
    formation: str = pydantic.Field(..., max_length=20)
    rating: float
    players: list
    campaign: Optional[list] = None

@router.get("/juego")
async def game_page(request: Request):
    """Renderiza la pantalla principal del juego de alineaciones."""
    from interfaces.api.app import db_instance
    from infrastructure.persistence.postgres_store import PostgresDatabase
    import psycopg2.extras
    
    current_user = get_current_user(request)
    
    # Obtener el muro de honor existente de este usuario si esta logueado
    muro_honor = []
    if current_user:
        with db_instance.get_connection() as conn:
            is_pg = isinstance(db_instance, PostgresDatabase)
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) if is_pg else conn.cursor()
            param = "%s" if is_pg else "?"
            cursor.execute(
                f"SELECT team_name, formation, rating, players, date, campaign FROM dream_teams WHERE user_id = {param} ORDER BY id DESC",
                (current_user["id"],)
            )
            for row in cursor.fetchall():
                try:
                    row_dict = dict(row)
                except Exception:
                    row_dict = row
                    
                campaign_data = []
                if "campaign" in row_dict and row_dict["campaign"]:
                    try:
                        campaign_data = row_dict["campaign"] if isinstance(row_dict["campaign"], list) else json.loads(row_dict["campaign"])
                    except Exception:
                        pass
                
                players_data = row_dict["players"] if isinstance(row_dict["players"], list) else json.loads(row_dict["players"])
                
                muro_honor.append({
                    "team_name": row_dict["team_name"],
                    "formation": row_dict["formation"],
                    "rating": row_dict["rating"],
                    "players": players_data,
                    "date": row_dict["date"],
                    "campaign": campaign_data
                })

    return templates.TemplateResponse(
        request=request,
        name="juego.html",
        context={
            "current_user": current_user,
            "planteles_json": json.dumps(PLANTELES_HISTORICOS),
            "muro_honor": muro_honor
        }
    )

@router.post("/api/juego/guardar")
async def save_dream_team(request: Request, payload: SaveDreamTeamPayload):
    """Guarda un Dream Team en el Muro de Honor en SQLite o Postgres."""
    from interfaces.api.app import db_instance
    from infrastructure.persistence.postgres_store import PostgresDatabase
    
    current_user = get_current_user(request)
    if not current_user:
        return JSONResponse(status_code=401, content={"detail": "Debes iniciar sesión para guardar tu equipo"})
        
    date_str = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    
    with db_instance.get_connection() as conn:
        cursor = conn.cursor()
        is_pg = isinstance(db_instance, PostgresDatabase)
        param = "%s" if is_pg else "?"
        cursor.execute(
            f"INSERT INTO dream_teams (user_id, team_name, formation, rating, players, date, campaign) VALUES ({param}, {param}, {param}, {param}, {param}, {param}, {param})",
            (
                current_user["id"],
                payload.team_name,
                payload.formation,
                payload.rating,
                json.dumps(payload.players),
                date_str,
                json.dumps(payload.campaign) if payload.campaign else None
            )
        )
        conn.commit()
        
    return {"status": "ok", "message": "¡Tu Dream Team ha sido inmortalizado en el Muro de Honor!"}

@router.get("/api/juego/muro")
async def get_muro_honor(request: Request):
    """Obtiene los registros del muro de honor en formato JSON."""
    from interfaces.api.app import db_instance
    from infrastructure.persistence.postgres_store import PostgresDatabase
    import psycopg2.extras
    
    current_user = get_current_user(request)
    if not current_user:
        return []
        
    muro = []
    with db_instance.get_connection() as conn:
        is_pg = isinstance(db_instance, PostgresDatabase)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) if is_pg else conn.cursor()
        param = "%s" if is_pg else "?"
        cursor.execute(
            f"SELECT team_name, formation, rating, players, date, campaign FROM dream_teams WHERE user_id = {param} ORDER BY id DESC",
            (current_user["id"],)
        )
        for row in cursor.fetchall():
            try:
                row_dict = dict(row)
            except Exception:
                row_dict = row
                
            campaign_data = []
            if "campaign" in row_dict and row_dict["campaign"]:
                try:
                    campaign_data = row_dict["campaign"] if isinstance(row_dict["campaign"], list) else json.loads(row_dict["campaign"])
                except Exception:
                    pass
            
            players_data = row_dict["players"] if isinstance(row_dict["players"], list) else json.loads(row_dict["players"])
            
            muro.append({
                "team_name": row_dict["team_name"],
                "formation": row_dict["formation"],
                "rating": row_dict["rating"],
                "players": players_data,
                "date": row_dict["date"],
                "campaign": campaign_data
            })
    return muro
