from typing import Protocol, List, Optional
from domain.models import Match

class MatchRepository(Protocol):
    """
    Puerto (interfaz) para el repositorio de partidos históricos.
    Define las operaciones que la capa de infraestructura deberá implementar.
    """
    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        """Busca un partido específico por su identificador."""
        ...

    def get_matches_by_ids(self, match_ids: List[str]) -> List[Match]:
        """Obtiene una lista de partidos por sus identificadores en una sola consulta batch."""
        ...

    def get_matches(self, year: Optional[int] = None, competition_id: Optional[str] = None, opponent: Optional[str] = None) -> List[Match]:
        """Obtiene una lista de partidos, permitiendo filtrar opcionalmente."""
        ...

class AttendanceRepository(Protocol):
    """
    Puerto (interfaz) para el repositorio de asistencias de usuarios.
    """
    def mark_as_attended(self, user_id: str, match_id: str) -> None:
        """Registra que un usuario asistió a un partido."""
        ...

    def unmark_as_attended(self, user_id: str, match_id: str) -> None:
        """Elimina el registro de asistencia de un usuario a un partido."""
        ...

    def get_attended_match_ids(self, user_id: str) -> List[str]:
        """Obtiene la lista de identificadores de partidos a los que asistió el usuario."""
        ...

from domain.models import LeagueTable

class LeagueTableRepository(Protocol):
    def insert_league_table(self, table: LeagueTable) -> None:
        ...

    def get_league_table(self, competition_id: str) -> Optional[LeagueTable]:
        ...
    
    def get_league_tables_by_season(self, season: str) -> List[LeagueTable]:
        ...
