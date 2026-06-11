import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, computed_field

class Stadium(BaseModel):
    """
    Entidad que representa un Estadio donde se disputa un partido.
    """
    id: Optional[str] = Field(None, description="Identificador único del estadio")
    name: str = Field(..., min_length=1, description="Nombre oficial del estadio")
    city: Optional[str] = Field(None, description="Ciudad donde está ubicado el estadio")
    country: str = Field("Chile", description="País del estadio")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "st_nacional",
                "name": "Estadio Nacional Julio Martínez Prádanos",
                "city": "Santiago",
                "country": "Chile"
            }
        }


class Competition(BaseModel):
    """
    Entidad que representa un Torneo o Competencia (ej. Campeonato Nacional, Copa Libertadores).
    """
    id: Optional[str] = Field(None, description="Identificador de la competición")
    name: str = Field(..., min_length=1, description="Nombre del torneo")
    season: Optional[str] = Field(None, description="Temporada o año de la competición (ej: 2011, 2024)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "comp_campeonato_2011",
                "name": "Campeonato Nacional - Clausura",
                "season": "2011"
            }
        }


class Match(BaseModel):
    """
    Entidad que representa un partido histórico completo de Universidad de Chile.
    """
    id: str = Field(..., description="Identificador único del partido")
    date: datetime.date = Field(..., description="Fecha en la que se jugó el partido")
    home_team: str = Field(..., min_length=1, description="Nombre del equipo local")
    away_team: str = Field(..., min_length=1, description="Nombre del equipo visitante")
    home_score: int = Field(..., ge=0, description="Goles del equipo local")
    away_score: int = Field(..., ge=0, description="Goles del equipo visitante")
    home_penalties: Optional[int] = Field(None, ge=0, description="Penales anotados por el equipo local")
    away_penalties: Optional[int] = Field(None, ge=0, description="Penales anotados por el equipo visitante")
    stadium: Stadium = Field(..., description="Estadio donde se disputó el partido")
    competition: Competition = Field(..., description="Torneo o campeonato correspondiente")
    stage: Optional[str] = Field(None, description="Etapa o fecha del torneo (ej: Fecha 1, Semifinal (Ida))")
    attendance_count: Optional[int] = Field(None, description="Público controlado en el estadio")

    @computed_field
    @property
    def is_udechile_home(self) -> bool:
        """
        Determina si Universidad de Chile jugó de local.
        """
        name = self.home_team.lower()
        return "universidad de chile" in name or "u. de chile" in name or name == "u de chile"

    @computed_field
    @property
    def is_udechile_away(self) -> bool:
        """
        Determina si Universidad de Chile jugó de visita.
        """
        name = self.away_team.lower()
        return "universidad de chile" in name or "u. de chile" in name or name == "u de chile"

    @computed_field
    @property
    def opponent(self) -> str:
        """
        Retorna el nombre del equipo rival de Universidad de Chile.
        """
        if self.is_udechile_home:
            return self.away_team
        return self.home_team

    @computed_field
    @property
    def udechile_score(self) -> Optional[int]:
        """
        Retorna los goles anotados por Universidad de Chile.
        """
        if self.is_udechile_home:
            return self.home_score
        if self.is_udechile_away:
            return self.away_score
        return None

    @computed_field
    @property
    def opponent_score(self) -> Optional[int]:
        """
        Retorna los goles anotados por el rival de Universidad de Chile.
        """
        if self.is_udechile_home:
            return self.away_score
        if self.is_udechile_away:
            return self.home_score
        return None

    @computed_field
    @property
    def udechile_result(self) -> Optional[str]:
        """
        Retorna el resultado desde la perspectiva de Universidad de Chile:
        - 'W' para Victoria (Win)
        - 'D' para Empate (Draw)
        - 'L' para Derrota (Loss)
        Los penales se usan como desempate cuando el marcador regular es igualado.
        """
        u_goals = self.udechile_score
        o_goals = self.opponent_score

        if u_goals is None or o_goals is None:
            return None

        if u_goals > o_goals:
            return "W"
        elif u_goals < o_goals:
            return "L"
        else:
            # Empate en tiempo regular — desempatar por penales si están registrados
            u_pen = self.home_penalties if self.is_udechile_home else self.away_penalties
            o_pen = self.away_penalties if self.is_udechile_home else self.home_penalties
            if u_pen is not None and o_pen is not None:
                return "W" if u_pen > o_pen else "L"
            return "D"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "match_20111214_u_ldu",
                "date": "2011-12-14",
                "home_team": "Universidad de Chile",
                "away_team": "LDU Quito",
                "home_score": 3,
                "away_score": 0,
                "stadium": {
                    "id": "st_nacional",
                    "name": "Estadio Nacional",
                    "city": "Santiago",
                    "country": "Chile"
                },
                "competition": {
                    "id": "comp_sudamericana_2011",
                    "name": "Copa Sudamericana",
                    "season": "2011"
                },
                "attendance_count": 45000
            }
        }


class StadiumVisit(BaseModel):
    """
    Modelo secundario para representar las visitas de un hincha a un estadio.
    """
    stadium: Stadium = Field(..., description="Estadio visitado")
    visit_count: int = Field(..., ge=0, description="Cantidad de veces asistido a este estadio")


class OpponentStreak(BaseModel):
    """
    Modelo secundario para representar la mejor racha de un hincha contra un rival específico.
    """
    opponent: str = Field(..., description="Nombre del rival")
    streak_length: int = Field(..., ge=0, description="Largo de la racha de partidos")
    streak_type: str = Field("undefeated", description="Tipo de racha: 'wins' (victorias consecutivas) o 'undefeated' (partidos invicto)")
    description: Optional[str] = Field(None, description="Descripción amigable de la racha (ej. '5 partidos invicto')")


class FanDashboardSnapshot(BaseModel):
    """
    Modelo que representa el resultado analítico consolidado del dashboard de un hincha.
    """
    total_matches_attended: int = Field(..., ge=0, description="Total de partidos a los que asistió físicamente")
    wins: int = Field(..., ge=0, description="Victorias de la U presenciadas en vivo")
    draws: int = Field(..., ge=0, description="Empates de la U presenciados en vivo")
    losses: int = Field(..., ge=0, description="Derrotas de la U presenciadas en vivo")
    
    # Métricas calculadas
    win_percentage: float = Field(..., ge=0.0, le=100.0, description="Porcentaje de partidos ganados estando en el estadio ('Rendimiento de Hincha')")
    undefeated_percentage: float = Field(..., ge=0.0, le=100.0, description="Porcentaje de partidos en los que no se perdió (victorias + empates)")
    
    # Análisis de estadios y rachas
    most_visited_stadiums: List[StadiumVisit] = Field(default_factory=list, description="Lista de estadios con mayor asistencia")
    best_opponent_streak: Optional[OpponentStreak] = Field(None, description="Detalle del rival contra el que el hincha tiene su mejor racha de resultados")
    
    # Opcionales premium útiles para visualización
    goals_scored_seen: int = Field(0, ge=0, description="Total de goles a favor vistos en el estadio")
    goals_conceded_seen: int = Field(0, ge=0, description="Total de goles en contra vistos en el estadio")
    favorite_competition: Optional[str] = Field(None, description="Competición a la que más asistió")

    class Config:
        json_schema_extra = {
            "example": {
                "total_matches_attended": 25,
                "wins": 18,
                "draws": 4,
                "losses": 3,
                "win_percentage": 72.0,
                "undefeated_percentage": 88.0,
                "most_visited_stadiums": [
                    {
                        "stadium": {
                            "id": "st_nacional",
                            "name": "Estadio Nacional",
                            "city": "Santiago",
                            "country": "Chile"
                        },
                        "visit_count": 20
                    },
                    {
                        "stadium": {
                            "id": "st_santa_laura",
                            "name": "Estadio Santa Laura",
                            "city": "Santiago",
                            "country": "Chile"
                        },
                        "visit_count": 5
                    }
                ],
                "best_opponent_streak": {
                    "opponent": "Colo-Colo",
                    "streak_length": 4,
                    "streak_type": "undefeated",
                    "description": "4 partidos invicto (2 victorias, 2 empates)"
                },
                "goals_scored_seen": 42,
                "goals_conceded_seen": 15,
                "favorite_competition": "Campeonato Nacional"
            }
        }

class TableEntry(BaseModel):
    """Representa una fila de un equipo en la tabla de posiciones."""
    position: int = Field(..., ge=1)
    team_name: str = Field(..., min_length=1)
    played: int = Field(..., ge=0)
    won: int = Field(..., ge=0)
    drawn: int = Field(..., ge=0)
    lost: int = Field(..., ge=0)
    goals_for: int = Field(..., ge=0)
    goals_against: int = Field(..., ge=0)
    points: int = Field(..., ge=0)
    goal_difference: int = Field(...)

class LeagueTable(BaseModel):
    """Representa la tabla de posiciones completa de un torneo."""
    competition_id: str = Field(..., description="ID de la competición (ej. comp_nacional_2025)")
    competition_name: str = Field(..., description="Nombre del torneo (ej. Campeonato Nacional 2025)")
    season: str = Field(..., description="Temporada")
    entries: List[TableEntry] = Field(default_factory=list, description="Lista de posiciones ordenadas")
