import psycopg2
from psycopg2.extras import DictCursor
import json
import datetime
from typing import List, Optional

from application.ports.repositories import MatchRepository, AttendanceRepository, LeagueTableRepository
from domain.models import Match, Stadium, Competition, LeagueTable, TableEntry

class PostgresDatabase:
    """Maneja la conexión a la base de datos PostgreSQL y la inicialización del esquema."""
    def __init__(self, db_url: str):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def initialize_schema(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
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
                        stadium JSONB NOT NULL,
                        competition JSONB NOT NULL,
                        stage TEXT,
                        attendance_count INTEGER DEFAULT 0
                    )
                """)
                
                # Tabla de asistencia de usuarios
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_attendance (
                        user_id TEXT NOT NULL,
                        match_id TEXT NOT NULL,
                        PRIMARY KEY (user_id, match_id),
                        FOREIGN KEY (match_id) REFERENCES matches (id) ON DELETE CASCADE
                    )
                """)
                
                # Tabla de posiciones (League Tables)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS league_tables (
                        competition_id TEXT PRIMARY KEY,
                        competition_name TEXT NOT NULL,
                        season TEXT NOT NULL,
                        entries JSONB NOT NULL
                    )
                """)
            conn.commit()


class PostgresMatchRepository(MatchRepository):
    """Implementación de infraestructura de MatchRepository usando PostgreSQL."""
    def __init__(self, database: PostgresDatabase):
        self._db = database

    def _row_to_match(self, row) -> Match:
        # row is a dictionary-like object if using DictCursor
        return Match(
            id=row["id"],
            date=datetime.date.fromisoformat(row["date"]),
            home_team=row["home_team"],
            away_team=row["away_team"],
            home_score=row["home_score"],
            away_score=row["away_score"],
            home_penalties=row["home_penalties"],
            away_penalties=row["away_penalties"],
            stadium=Stadium.model_validate(row["stadium"] if isinstance(row["stadium"], dict) else json.loads(row["stadium"])),
            competition=Competition.model_validate(row["competition"] if isinstance(row["competition"], dict) else json.loads(row["competition"])),
            stage=row["stage"],
            attendance_count=row["attendance_count"]
        )

    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM matches WHERE id = %s", (match_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_match(row)
                return None

    def get_matches_by_ids(self, match_ids: List[str]) -> List[Match]:
        if not match_ids:
            return []
        placeholders = ",".join("%s" for _ in match_ids)
        query = f"SELECT * FROM matches WHERE id IN ({placeholders})"
        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, tuple(match_ids))
                rows = cursor.fetchall()
                return [self._row_to_match(row) for row in rows]

    def get_matches(self, year: Optional[int] = None, competition_id: Optional[str] = None, opponent: Optional[str] = None) -> List[Match]:
        query = "SELECT * FROM matches WHERE 1=1"
        params = []

        if year is not None:
            query += " AND date LIKE %s"
            params.append(f"{year}-%")
            
        if competition_id is not None:
            # PostgreSQL cast JSONB -> text for LIKE or use jsonb operators
            query += " AND competition::text LIKE %s"
            params.append(f'%"{competition_id}"%')

        if opponent is not None:
            query += " AND (home_team ILIKE %s OR away_team ILIKE %s)"
            params.extend([f"%{opponent}%", f"%{opponent}%"])

        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, tuple(params))
                rows = cursor.fetchall()
                return [self._row_to_match(row) for row in rows]

    def insert_match(self, match: Match) -> None:
        """Método auxiliar para la carga de datos."""
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                # Use psycopg2 json extras or just strings, psycopg2 handles string to jsonb well
                stadium_json = match.stadium.model_dump_json()
                competition_json = match.competition.model_dump_json()
                
                cursor.execute("""
                    INSERT INTO matches 
                    (id, date, home_team, away_team, home_score, away_score, home_penalties, away_penalties, stadium, competition, stage, attendance_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                    date = EXCLUDED.date,
                    home_team = EXCLUDED.home_team,
                    away_team = EXCLUDED.away_team,
                    home_score = EXCLUDED.home_score,
                    away_score = EXCLUDED.away_score,
                    home_penalties = EXCLUDED.home_penalties,
                    away_penalties = EXCLUDED.away_penalties,
                    stadium = EXCLUDED.stadium,
                    competition = EXCLUDED.competition,
                    stage = EXCLUDED.stage,
                    attendance_count = EXCLUDED.attendance_count
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
                    match.attendance_count or 0
                ))
            conn.commit()


class PostgresAttendanceRepository(AttendanceRepository):
    """Implementación de infraestructura de AttendanceRepository usando PostgreSQL."""
    def __init__(self, database: PostgresDatabase):
        self._db = database

    def mark_as_attended(self, user_id: str, match_id: str) -> None:
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_attendance (user_id, match_id) 
                    VALUES (%s, %s)
                    ON CONFLICT (user_id, match_id) DO NOTHING
                """, (user_id, match_id))
                
                cursor.execute("""
                    UPDATE matches 
                    SET attendance_count = attendance_count + 1 
                    WHERE id = %s
                """, (match_id,))
            conn.commit()

    def unmark_as_attended(self, user_id: str, match_id: str) -> None:
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM user_attendance WHERE user_id = %s AND match_id = %s", (user_id, match_id))
                # cursor.rowcount nos dice si efectivamente borró
                if cursor.rowcount > 0:
                    cursor.execute("""
                        UPDATE matches 
                        SET attendance_count = GREATEST(0, attendance_count - 1) 
                        WHERE id = %s
                    """, (match_id,))
            conn.commit()

    def get_attended_match_ids(self, user_id: str) -> List[str]:
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT match_id FROM user_attendance WHERE user_id = %s", (user_id,))
                rows = cursor.fetchall()
                return [row[0] for row in rows]


class PostgresTableRepository(LeagueTableRepository):
    def __init__(self, database: PostgresDatabase):
        self._db = database
        
    def _row_to_table(self, row) -> LeagueTable:
        entries_json = row["entries"] if isinstance(row["entries"], list) else json.loads(row["entries"])
        entries = [TableEntry.model_validate(e) for e in entries_json]
        return LeagueTable(
            competition_id=row["competition_id"],
            competition_name=row["competition_name"],
            season=row["season"],
            entries=entries
        )

    def get_league_tables_by_season(self, season: str) -> List[LeagueTable]:
        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM league_tables WHERE season = %s", (season,))
                rows = cursor.fetchall()
                return [self._row_to_table(row) for row in rows]
                
    def get_league_table(self, competition_id: str) -> Optional[LeagueTable]:
        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT * FROM league_tables WHERE competition_id = %s", (competition_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_table(row)
                return None
                
    def insert_league_table(self, league_table: LeagueTable) -> None:
        entries_json = json.dumps([e.model_dump() for e in league_table.entries])
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO league_tables (competition_id, competition_name, season, entries)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (competition_id) DO UPDATE SET
                    competition_name = EXCLUDED.competition_name,
                    season = EXCLUDED.season,
                    entries = EXCLUDED.entries
                """, (
                    league_table.competition_id,
                    league_table.competition_name,
                    league_table.season,
                    entries_json
                ))
            conn.commit()

class PostgresUserRepository:
    def __init__(self, database: PostgresDatabase):
        self._db = database

    def create_user(self, user_id: str, email: str, password_hash: str, name: str) -> bool:
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute("""
                        INSERT INTO users (id, email, password_hash, name)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, email, password_hash, name))
                    conn.commit()
                    return True
                except psycopg2.IntegrityError:
                    return False

    def get_user_by_email(self, email: str) -> Optional[dict]:
        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT id, email, password_hash, name FROM users WHERE email = %s", (email,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
