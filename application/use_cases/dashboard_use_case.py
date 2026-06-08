from typing import Dict, List
from collections import defaultdict

from application.ports.repositories import MatchRepository, AttendanceRepository
from domain.models import FanDashboardSnapshot, StadiumVisit, OpponentStreak, Stadium

class GenerateFanDashboardUseCase:
    """
    Caso de uso para calcular y generar las métricas del dashboard de un hincha.
    """
    def __init__(self, match_repository: MatchRepository, attendance_repository: AttendanceRepository):
        self._match_repository = match_repository
        self._attendance_repository = attendance_repository

    def _normalize_stadium(self, stadium: Stadium) -> Stadium:
        """
        Normaliza el nombre y ciudad del estadio para unificar registros equivalentes.
        """
        name = stadium.name.strip()
        name_lower = name.lower()
        
        # Nacional
        if "nacional" in name_lower and "ñuñoa" in name_lower:
            normalized_name = "Estadio Nacional, Ñuñoa, Santiago de Chile"
            normalized_city = "Santiago"
        # Santa Laura
        elif "santa laura" in name_lower:
            normalized_name = "Estadio Santa Laura, Independencia, Santiago de Chile"
            normalized_city = "Santiago"
        # San Carlos de Apoquindo
        elif "san carlos" in name_lower and "apoquindo" in name_lower:
            normalized_name = "Estadio San Carlos de Apoquindo, Las Condes, Santiago de Chile"
            normalized_city = "Santiago"
        # El Teniente
        elif "el teniente" in name_lower or ("teniente" in name_lower and "rancagua" in name_lower):
            normalized_name = "Estadio Bicentenario El Teniente, Rancagua"
            normalized_city = "Rancagua"
        # Ester Roa / Collao
        elif "ester roa" in name_lower or "collao" in name_lower:
            normalized_name = "Estadio Bicentenario Ester Roa, Collao, Concepción"
            normalized_city = "Concepción"
        # La Cisterna
        elif "cisterna" in name_lower:
            normalized_name = "Estadio Municipal, La Cisterna, Santiago de Chile"
            normalized_city = "Santiago"
        # Monumental
        elif "monumental" in name_lower or "pedrero" in name_lower:
            normalized_name = "Estadio Monumental, Macul, Santiago de Chile"
            normalized_city = "Santiago"
        # Francisco Sánchez Rumoroso
        elif "sánchez rumoroso" in name_lower or "sanchez rumoroso" in name_lower or "coquimbo" in name_lower:
            normalized_name = "Estadio Bicentenario Francisco Sánchez Rumoroso, Coquimbo"
            normalized_city = "Coquimbo"
        # Sausalito
        elif "sausalito" in name_lower or "viña del mar" in name_lower:
            normalized_name = "Estadio Sausalito, Viña del Mar"
            normalized_city = "Viña del Mar"
        # Elías Figueroa / Playa Ancha
        elif "elías figueroa" in name_lower or "elias figueroa" in name_lower or "playa ancha" in name_lower:
            normalized_name = "Estadio Elías Figueroa Brander, Playa Ancha, Valparaíso"
            normalized_city = "Valparaíso"
        # Lucio Fariña
        elif "lucio fariña" in name_lower or "lucio farina" in name_lower or "quillota" in name_lower:
            normalized_name = "Estadio Municipal Lucio Fariña Fernández, Quillota"
            normalized_city = "Quillota"
        # Calera
        elif "nicolás chahuán" in name_lower or "nicolas chahuan" in name_lower or "calera" in name_lower:
            normalized_name = "Estadio Municipal Nicolás Chahuán Nazar, La Calera"
            normalized_city = "La Calera"
        else:
            # Fallback
            normalized_name = name
            normalized_city = stadium.city

        return Stadium(
            id=stadium.id,
            name=normalized_name,
            city=normalized_city,
            country=stadium.country
        )

    def _calculate_snapshot(self, matches: List) -> FanDashboardSnapshot:
        total_matches = len(matches)
        if total_matches == 0:
            return FanDashboardSnapshot(
                total_matches_attended=0,
                wins=0,
                draws=0,
                losses=0,
                win_percentage=0.0,
                undefeated_percentage=0.0,
                most_visited_stadiums=[],
                goals_scored_seen=0,
                goals_conceded_seen=0
            )

        wins, draws, losses = 0, 0, 0
        goals_scored, goals_conceded = 0, 0
        
        stadium_counts: Dict[str, int] = defaultdict(int)
        stadium_objects: Dict[str, Stadium] = {}
        competition_counts: Dict[str, int] = defaultdict(int)

        for match in matches:
            res = match.udechile_result
            if res == "W":
                wins += 1
            elif res == "D":
                draws += 1
            elif res == "L":
                losses += 1

            if match.udechile_score is not None:
                goals_scored += match.udechile_score
            if match.opponent_score is not None:
                goals_conceded += match.opponent_score

            normalized_stadium = self._normalize_stadium(match.stadium)
            stadium_id = normalized_stadium.name
            stadium_counts[stadium_id] += 1
            stadium_objects[stadium_id] = normalized_stadium
            
            competition_counts[match.competition.name] += 1

        puntos_obtenidos = (wins * 3) + (draws * 1)
        puntos_posibles = total_matches * 3
        win_percentage = (puntos_obtenidos / puntos_posibles) * 100.0
        undefeated_percentage = ((wins + draws) / total_matches) * 100.0

        sorted_stadiums = sorted(stadium_counts.items(), key=lambda x: x[1], reverse=True)
        most_visited_stadiums = [
            StadiumVisit(stadium=stadium_objects[s_id], visit_count=count)
            for s_id, count in sorted_stadiums
        ]

        favorite_competition = None
        if competition_counts:
            favorite_competition = max(competition_counts.items(), key=lambda x: x[1])[0]

        return FanDashboardSnapshot(
            total_matches_attended=total_matches,
            wins=wins,
            draws=draws,
            losses=losses,
            win_percentage=round(win_percentage, 2),
            undefeated_percentage=round(undefeated_percentage, 2),
            most_visited_stadiums=most_visited_stadiums,
            goals_scored_seen=goals_scored,
            goals_conceded_seen=goals_conceded,
            favorite_competition=favorite_competition
        )

    def execute(self, user_id: str) -> FanDashboardSnapshot:
        # Obtener los IDs de los partidos a los que asistió
        attended_ids = self._attendance_repository.get_attended_match_ids(user_id)
        # Recuperar las instancias de los partidos
        matches = self._match_repository.get_matches_by_ids(attended_ids)
        return self._calculate_snapshot(matches)

    def execute_enriched(self, user_id: str) -> dict:
        """
        Calcula el snapshot general, agrupado por año y segmentado por clásicos.
        """
        attended_ids = self._attendance_repository.get_attended_match_ids(user_id)
        matches = self._match_repository.get_matches_by_ids(attended_ids)
        
        # 1. Snapshot General
        general_snap = self._calculate_snapshot(matches)
        
        # 2. Agrupado por año (usando el año de la fecha del partido)
        matches_by_year = defaultdict(list)
        for m in matches:
            year_str = str(m.date.year)
            matches_by_year[year_str].append(m)
            
        by_year_snaps = {}
        for y_str, y_matches in matches_by_year.items():
            by_year_snaps[y_str] = self._calculate_snapshot(y_matches)
            
        # 3. Clásicos
        colo_colo_matches = []
        uc_matches = []
        
        for m in matches:
            opp_lower = m.opponent.lower()
            if "colo" in opp_lower:
                colo_colo_matches.append(m)
            elif "catol" in opp_lower:
                uc_matches.append(m)
                
        combined_classics = colo_colo_matches + uc_matches
        
        classics_snaps = {
            "combined": self._calculate_snapshot(combined_classics),
            "cc": self._calculate_snapshot(colo_colo_matches),
            "uc": self._calculate_snapshot(uc_matches)
        }
        
        return {
            "general": general_snap,
            "by_year": by_year_snaps,
            "classics": classics_snaps
        }
