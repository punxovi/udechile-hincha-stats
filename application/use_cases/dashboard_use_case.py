from typing import Dict, List
from collections import defaultdict

from application.ports.repositories import MatchRepository, AttendanceRepository
from domain.models import FanDashboardSnapshot, StadiumVisit, OpponentStreak, Stadium
from domain.stadium_normalizer import normalize_stadium

class GenerateFanDashboardUseCase:
    """
    Caso de uso para calcular y generar las métricas del dashboard de un hincha.
    """
    def __init__(self, match_repository: MatchRepository, attendance_repository: AttendanceRepository):
        self._match_repository = match_repository
        self._attendance_repository = attendance_repository

    def _normalize_stadium(self, stadium: Stadium) -> Stadium:
        canon_name, canon_city, canon_country = normalize_stadium(
            stadium.name, stadium.city, stadium.country
        )
        return Stadium(id=stadium.id, name=canon_name, city=canon_city, country=canon_country)

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

        # Solo contamos partidos con resultado reconocido (equipo identificado en BD)
        recognized = wins + draws + losses
        puntos_obtenidos = (wins * 3) + draws
        if recognized == 0:
            win_percentage = 0.0
            undefeated_percentage = 0.0
        else:
            win_percentage = (puntos_obtenidos / (recognized * 3)) * 100.0
            undefeated_percentage = ((wins + draws) / recognized) * 100.0

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
            # 3.1 Detección proactiva de Colo-Colo
            if "colo" in opp_lower:
                colo_colo_matches.append(m)
            # 3.2 Detección proactiva de la UC (tolerante a caracteres rotos de codificación como 'Catlica')
            # Excluimos rivales internacionales con 'cat' (ej: U. Católica de Ecuador)
            elif "cat" in opp_lower:
                is_foreign = any(term in opp_lower for term in ["ecu", "quito", "boliv", "ecuador", "colomb", "chicago"])
                if not is_foreign:
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
