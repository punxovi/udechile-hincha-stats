import sqlite3
import json
import datetime
from typing import List, Optional

from application.ports.repositories import MatchRepository, AttendanceRepository
from domain.models import Match, Stadium, Competition

class SqliteDatabase:
    """Maneja la conexión a la base de datos SQLite y la inicialización del esquema."""
    def __init__(self, db_path: str = "udechile_stats.db"):
        self.db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        # Retorna resultados como diccionarios para facilitar el acceso
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_schema(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de partidos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    home_score INTEGER NOT NULL,
                    away_score INTEGER NOT NULL,
                    home_penalties INTEGER,
                    away_penalties INTEGER,
                    stadium TEXT NOT NULL, -- JSON string
                    competition TEXT NOT NULL, -- JSON string
                    stage TEXT,
                    attendance_count INTEGER
                )
            """)
            
            # Tabla de asistencia de usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_attendance (
                    user_id TEXT NOT NULL,
                    match_id TEXT NOT NULL,
                    PRIMARY KEY (user_id, match_id),
                    FOREIGN KEY (match_id) REFERENCES matches (id)
                )
            """)
            
            # Tabla de posiciones (League Tables)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS league_tables (
                    competition_id TEXT PRIMARY KEY,
                    competition_name TEXT NOT NULL,
                    season TEXT NOT NULL,
                    entries TEXT NOT NULL -- JSON string con la lista de TableEntry
                )
            """)
            
            conn.commit()

    def clear_all_data(self):
        """Borra todos los datos de las tablas para tener una base limpia."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_attendance;")
            cursor.execute("DELETE FROM matches;")
            cursor.execute("DELETE FROM league_tables;")
            conn.commit()


class SqliteMatchRepository(MatchRepository):
    """Implementación de infraestructura de MatchRepository usando SQLite."""
    def __init__(self, database: SqliteDatabase):
        self._db = database

    def _row_to_match(self, row: sqlite3.Row) -> Match:
        """Convierte una fila de base de datos a un modelo Pydantic Match."""
        # Se maneja .keys() por si corren queries con DB anterior sin migrar
        home_penalties = row["home_penalties"] if "home_penalties" in row.keys() else None
        away_penalties = row["away_penalties"] if "away_penalties" in row.keys() else None
        
        return Match(
            id=row["id"],
            date=datetime.date.fromisoformat(row["date"]),
            home_team=row["home_team"],
            away_team=row["away_team"],
            home_score=row["home_score"],
            away_score=row["away_score"],
            home_penalties=home_penalties,
            away_penalties=away_penalties,
            stadium=Stadium.model_validate_json(row["stadium"]),
            competition=Competition.model_validate_json(row["competition"]),
            stage=row["stage"],
            attendance_count=row["attendance_count"]
        )

    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM matches WHERE id = ?", (match_id,))
            row = cursor.fetchone()
            if row:
                return self._row_to_match(row)
            return None

    def get_matches_by_ids(self, match_ids: List[str]) -> List[Match]:
        if not match_ids:
            return []
        placeholders = ",".join("?" for _ in match_ids)
        query = f"SELECT * FROM matches WHERE id IN ({placeholders})"
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, match_ids)
            rows = cursor.fetchall()
            return [self._row_to_match(row) for row in rows]

    def get_matches(self, year: Optional[int] = None, competition_id: Optional[str] = None, opponent: Optional[str] = None) -> List[Match]:
        query = "SELECT * FROM matches WHERE 1=1"
        params = []

        if year is not None:
            query += " AND competition LIKE ?"
            params.append(f'%\"season\":\"{year}\"%')
            
        # Nota: competition_id requeriría parsear el JSON o usar json_extract si SQLite lo soporta.
        # Por simplicidad y compatibilidad lo filtramos usando LIKE en el texto JSON.
        if competition_id is not None:
            query += " AND competition LIKE ?"
            params.append(f'%"{competition_id}"%')

        if opponent is not None:
            query += " AND (home_team LIKE ? OR away_team LIKE ?)"
            params.extend([f"%{opponent}%", f"%{opponent}%"])

        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [self._row_to_match(row) for row in rows]

    def insert_match(self, match: Match) -> None:
        """Método auxiliar para la carga de datos."""
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            
            stadium_json = match.stadium.model_dump_json()
            competition_json = match.competition.model_dump_json()
            
            cursor.execute("""
                INSERT OR REPLACE INTO matches 
                (id, date, home_team, away_team, home_score, away_score, home_penalties, away_penalties, stadium, competition, stage, attendance_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                match.id,
                match.date.isoformat(),
                match.home_team,
                match.away_team,
                match.home_score,
                match.away_score,
                match.home_penalties,
                match.away_penalties,
                stadium_json,
                competition_json,
                match.stage,
                match.attendance_count
            ))
            conn.commit()


class SqliteAttendanceRepository(AttendanceRepository):
    """Implementación de infraestructura de AttendanceRepository usando SQLite."""
    def __init__(self, database: SqliteDatabase):
        self._db = database

    def mark_as_attended(self, user_id: str, match_id: str) -> None:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO user_attendance (user_id, match_id)
                VALUES (?, ?)
            """, (user_id, match_id))
            conn.commit()

    def unmark_as_attended(self, user_id: str, match_id: str) -> None:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM user_attendance 
                WHERE user_id = ? AND match_id = ?
            """, (user_id, match_id))
            conn.commit()

    def get_attended_match_ids(self, user_id: str) -> List[str]:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT match_id FROM user_attendance WHERE user_id = ?", (user_id,))
            rows = cursor.fetchall()
            return [row["match_id"] for row in rows]

from application.ports.repositories import LeagueTableRepository
from domain.models import LeagueTable, TableEntry

class SqliteLeagueTableRepository(LeagueTableRepository):
    def __init__(self, database: SqliteDatabase):
        self._db = database

    def insert_league_table(self, table: LeagueTable) -> None:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            # Serializamos la lista de entries a JSON
            entries_json = json.dumps([entry.model_dump() for entry in table.entries])
            
            cursor.execute("""
                INSERT OR REPLACE INTO league_tables 
                (competition_id, competition_name, season, entries)
                VALUES (?, ?, ?, ?)
            """, (
                table.competition_id,
                table.competition_name,
                table.season,
                entries_json
            ))
            conn.commit()

    def get_league_table(self, competition_id: str) -> Optional[LeagueTable]:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM league_tables WHERE competition_id = ?", (competition_id,))
            row = cursor.fetchone()
            if row:
                entries_list = json.loads(row["entries"])
                entries = [TableEntry(**e) for e in entries_list]
                return LeagueTable(
                    competition_id=row["competition_id"],
                    competition_name=row["competition_name"],
                    season=row["season"],
                    entries=entries
                )
            return None

    def get_league_tables_by_season(self, season: str) -> List[LeagueTable]:
        with self._db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM league_tables WHERE season = ?", (season,))
            rows = cursor.fetchall()
            tables = []
            for row in rows:
                entries_list = json.loads(row["entries"])
                entries = [TableEntry(**e) for e in entries_list]
                tables.append(LeagueTable(
                    competition_id=row["competition_id"],
                    competition_name=row["competition_name"],
                    season=row["season"],
                    entries=entries
                ))
            return tables
