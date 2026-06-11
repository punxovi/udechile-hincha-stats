import sqlite3
import os
import json
from dotenv import load_dotenv
from infrastructure.persistence.postgres_store import PostgresDatabase, PostgresMatchRepository, PostgresTableRepository
from domain.models import Match, Stadium, Competition, LeagueTable, TableEntry
import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("No DATABASE_URL found in .env")
    exit(1)

postgres_db = PostgresDatabase(DATABASE_URL)
postgres_db.initialize_schema()

pg_match_repo = PostgresMatchRepository(postgres_db)
pg_table_repo = PostgresTableRepository(postgres_db)

sqlite_conn = sqlite3.connect(r"c:\Users\bich0\OneDrive\Escritorio\u de chile\udechile_stats.db")
sqlite_conn.row_factory = sqlite3.Row

# 1. Migrate Matches
print("Migrando partidos...")
cursor = sqlite_conn.cursor()
cursor.execute("SELECT * FROM matches")
matches = cursor.fetchall()
for m in matches:
    d = dict(m)
    match = Match(
        id=d["id"],
        date=datetime.date.fromisoformat(d["date"]),
        home_team=d["home_team"],
        away_team=d["away_team"],
        home_score=d["home_score"],
        away_score=d["away_score"],
        home_penalties=d["home_penalties"],
        away_penalties=d["away_penalties"],
        stadium=Stadium.model_validate(json.loads(d["stadium"])),
        competition=Competition.model_validate(json.loads(d["competition"])),
        stage=d["stage"],
        attendance_count=d["attendance_count"]
    )
    pg_match_repo.insert_match(match)

print(f"{len(matches)} partidos migrados.")

# 2. Migrate Tables
print("Migrando tablas de posiciones...")
cursor.execute("SELECT * FROM league_tables")
tables = cursor.fetchall()
for t in tables:
    d = dict(t)
    entries = [TableEntry.model_validate(e) for e in json.loads(d["entries"])]
    league_table = LeagueTable(
        competition_id=d["competition_id"],
        competition_name=d["competition_name"],
        season=d["season"],
        entries=entries
    )
    pg_table_repo.insert_league_table(league_table)

print(f"{len(tables)} tablas migradas.")

# 3. Migrate User Attendance
print("Migrando asistencias...")
cursor.execute("SELECT * FROM user_attendance")
attendances = cursor.fetchall()
with postgres_db.get_connection() as pg_conn:
    with pg_conn.cursor() as pg_cursor:
        for a in attendances:
            pg_cursor.execute("""
                INSERT INTO user_attendance (user_id, match_id) 
                VALUES (%s, %s)
                ON CONFLICT (user_id, match_id) DO NOTHING
            """, (a["user_id"], a["match_id"]))
    pg_conn.commit()

print(f"{len(attendances)} asistencias migradas.")
print("¡Migración completada exitosamente!")
