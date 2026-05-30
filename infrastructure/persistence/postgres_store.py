import os
import json
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from typing import List, Optional
from dotenv import load_dotenv

from application.ports.repositories import MatchRepository, AttendanceRepository, LeagueTableRepository
from domain.models import Match, Stadium, Competition, LeagueTable, TableEntry

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class PostgresDatabase:
    """Maneja la conexión a la base de datos PostgreSQL de Supabase e inicializa el esquema utilizando un pool persistente."""
    def __init__(self, connection_url: Optional[str] = None):
        self.connection_url = connection_url or os.getenv("SUPABASE_DB_URL")
        if not self.connection_url:
            raise ValueError("La variable de entorno SUPABASE_DB_URL no está configurada en el archivo .env")
        
        # Inicializar un pool de conexiones persistentes (mínimo 2, máximo 20)
        self._pool = ThreadedConnectionPool(2, 20, self.connection_url)

    def get_connection(self):
        # Retorna un wrapper context manager para devolver automáticamente la conexión al pool y manejar transacciones
        class ConnectionContext:
            def __init__(self, pool):
                self.pool = pool
                self.conn = None
            def __enter__(self):
                self.conn = self.pool.getconn()
                return self.conn
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is not None:
                    try:
                        self.conn.rollback()
                    except Exception:
                        pass
                else:
                    try:
                        self.conn.commit()
                    except Exception:
                        pass
                self.pool.putconn(self.conn)
                
        return ConnectionContext(self._pool)

    def initialize_schema(self):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Tabla de partidos
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS matches (
                        id VARCHAR(255) PRIMARY KEY,
                        date DATE NOT NULL,
                        home_team VARCHAR(255) NOT NULL,
                        away_team VARCHAR(255) NOT NULL,
                        home_score INTEGER NOT NULL,
                        away_score INTEGER NOT NULL,
                        home_penalties INTEGER,
                        away_penalties INTEGER,
                        stadium TEXT NOT NULL, -- JSON string
                        competition TEXT NOT NULL, -- JSON string
                        stage VARCHAR(255),
                        attendance_count INTEGER
                    )
                """)
                
                # Tabla de asistencia de usuarios
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_attendance (
                        user_id VARCHAR(255) NOT NULL,
                        match_id VARCHAR(255) REFERENCES matches (id) ON DELETE CASCADE,
                        PRIMARY KEY (user_id, match_id)
                    )
                """)
                
                # Tabla de posiciones (League Tables)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS league_tables (
                        competition_id VARCHAR(255) PRIMARY KEY,
                        competition_name VARCHAR(255) NOT NULL,
                        season VARCHAR(50) NOT NULL,
                        entries TEXT NOT NULL -- JSON string con la lista de TableEntry
                    )
                """)
                conn.commit()

    def clear_all_data(self):
        """Borra todos los datos de las tablas en PostgreSQL."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("TRUNCATE TABLE user_attendance CASCADE;")
                cursor.execute("TRUNCATE TABLE matches CASCADE;")
                cursor.execute("TRUNCATE TABLE league_tables CASCADE;")
                conn.commit()


class PostgresMatchRepository(MatchRepository):
    """Implementación de infraestructura de MatchRepository usando PostgreSQL."""
    def __init__(self, database: PostgresDatabase):
        self._db = database

    def _row_to_match(self, row) -> Match:
        """Convierte una fila de PostgreSQL a un modelo Pydantic Match."""
        # row es una tupla o dict según el cursor, usamos RealDictCursor
        date_val = row["date"]
        if isinstance(date_val, str):
            date_obj = datetime.date.fromisoformat(date_val)
        else:
            date_obj = date_val  # En PostgreSQL psycopg2 retorna objetos datetime.date directamente

        return Match(
            id=row["id"],
            date=date_obj,
            home_team=row["home_team"],
            away_team=row["away_team"],
            home_score=row["home_score"],
            away_score=row["away_score"],
            home_penalties=row["home_penalties"],
            away_penalties=row["away_penalties"],
            stadium=Stadium.model_validate_json(row["stadium"]),
            competition=Competition.model_validate_json(row["competition"]),
            stage=row["stage"],
            attendance_count=row["attendance_count"]
        )

    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM matches WHERE id = %s", (match_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_match(row)
                return None

    def get_matches_by_ids(self, match_ids: List[str]) -> List[Match]:
        if not match_ids:
            return []
        query = "SELECT * FROM matches WHERE id IN %s"
        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, (tuple(match_ids),))
                rows = cursor.fetchall()
                return [self._row_to_match(row) for row in rows]

    def get_matches(self, year: Optional[int] = None, competition_id: Optional[str] = None, opponent: Optional[str] = None) -> List[Match]:
        query = "SELECT * FROM matches WHERE 1=1"
        params = []

        if year is not None:
            query += " AND competition LIKE %s"
            params.append(f'%\"season\":\"{year}\"%')
            
        if competition_id is not None:
            query += " AND competition LIKE %s"
            params.append(f'%"{competition_id}"%')

        if opponent is not None:
            query += " AND (home_team ILIKE %s OR away_team ILIKE %s)"
            params.extend([f"%{opponent}%", f"%{opponent}%"])

        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [self._row_to_match(row) for row in rows]

    def insert_match(self, match: Match) -> None:
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
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
                    match.attendance_count
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
                    ON CONFLICT DO NOTHING
                """, (user_id, match_id))
                conn.commit()

    def unmark_as_attended(self, user_id: str, match_id: str) -> None:
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM user_attendance 
                    WHERE user_id = %s AND match_id = %s
                """, (user_id, match_id))
                conn.commit()

    def get_attended_match_ids(self, user_id: str) -> List[str]:
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT match_id FROM user_attendance WHERE user_id = %s", (user_id,))
                rows = cursor.fetchall()
                return [row[0] for row in rows]


class PostgresLeagueTableRepository(LeagueTableRepository):
    """Implementación de infraestructura de LeagueTableRepository usando PostgreSQL."""
    def __init__(self, database: PostgresDatabase):
        self._db = database

    def insert_league_table(self, table: LeagueTable) -> None:
        with self._db.get_connection() as conn:
            with conn.cursor() as cursor:
                entries_json = json.dumps([entry.model_dump() for entry in table.entries])
                
                cursor.execute("""
                    INSERT INTO league_tables 
                    (competition_id, competition_name, season, entries)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (competition_id) DO UPDATE SET
                        competition_name = EXCLUDED.competition_name,
                        season = EXCLUDED.season,
                        entries = EXCLUDED.entries
                """, (
                    table.competition_id,
                    table.competition_name,
                    table.season,
                    entries_json
                ))
                conn.commit()

    def get_league_table(self, competition_id: str) -> Optional[LeagueTable]:
        with self._db.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM league_tables WHERE competition_id = %s", (competition_id,))
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
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM league_tables WHERE season = %s", (season,))
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
