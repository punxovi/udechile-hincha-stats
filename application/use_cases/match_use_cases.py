from typing import List, Optional
from application.ports.repositories import MatchRepository, AttendanceRepository
from domain.models import Match

class GetHistoricalMatchesUseCase:
    """
    Caso de uso para buscar y filtrar partidos históricos en el catálogo.
    """
    def __init__(self, match_repository: MatchRepository):
        self._match_repository = match_repository

    def execute(
        self, 
        year: Optional[int] = None, 
        competition_id: Optional[str] = None, 
        opponent: Optional[str] = None
    ) -> List[Match]:
        """
        Delega la búsqueda al puerto del repositorio usando los filtros.
        """
        return self._match_repository.get_matches(
            year=year, 
            competition_id=competition_id, 
            opponent=opponent
        )

class MarkAttendanceUseCase:
    """
    Caso de uso para registrar que un hincha asistió físicamente a un partido.
    """
    def __init__(self, attendance_repository: AttendanceRepository):
        self._attendance_repository = attendance_repository

    def execute(self, user_id: str, match_id: str) -> None:
        """
        Registra la asistencia delegando la operación al repositorio.
        """
        self._attendance_repository.mark_as_attended(user_id, match_id)

class UnmarkAttendanceUseCase:
    """
    Caso de uso para eliminar el registro de asistencia de un hincha a un partido.
    """
    def __init__(self, attendance_repository: AttendanceRepository):
        self._attendance_repository = attendance_repository

    def execute(self, user_id: str, match_id: str) -> None:
        """
        Elimina la asistencia delegando la operación al repositorio.
        """
        self._attendance_repository.unmark_as_attended(user_id, match_id)
