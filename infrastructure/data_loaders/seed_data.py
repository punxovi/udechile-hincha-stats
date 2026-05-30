import os
import sys
import datetime

# Asegurarnos de que Python pueda encontrar los paquetes desde la raíz del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from domain.models import Match, Stadium, Competition
from infrastructure.persistence.sqlite_store import SqliteDatabase, SqliteMatchRepository, SqliteAttendanceRepository

def seed_database():
    print("Inicializando la base de datos...")
    db = SqliteDatabase("udechile_stats.db")
    db.initialize_schema()

    match_repo = SqliteMatchRepository(db)
    attendance_repo = SqliteAttendanceRepository(db)

    print("Creando partidos históricos semilla...")
    
    # 1. Final Sudamericana 2011 (Campeón invicto)
    match_1 = Match(
        id="match_2011_sud_final",
        date=datetime.date(2011, 12, 14),
        home_team="Universidad de Chile",
        away_team="LDU Quito",
        home_score=3,
        away_score=0,
        stadium=Stadium(id="st_nacional", name="Estadio Nacional", city="Santiago"),
        competition=Competition(id="comp_sud_2011", name="Copa Sudamericana", season="2011"),
        attendance_count=46000
    )

    # 2. Clásico Universitario Apertura 2011 (Final Vuelta Histórica 4-1)
    match_2 = Match(
        id="match_2011_cl_uc",
        date=datetime.date(2011, 6, 12),
        home_team="Universidad Católica",
        away_team="Universidad de Chile",
        home_score=1,
        away_score=4,
        stadium=Stadium(id="st_nacional", name="Estadio Nacional", city="Santiago"),
        competition=Competition(id="comp_ape_2011", name="Campeonato Nacional - Apertura", season="2011"),
        attendance_count=35000
    )

    # 3. Superclásico Apertura 2012 (Goleada 5-0)
    match_3 = Match(
        id="match_2012_cl_cc",
        date=datetime.date(2012, 4, 29),
        home_team="Universidad de Chile",
        away_team="Colo-Colo",
        home_score=5,
        away_score=0,
        stadium=Stadium(id="st_nacional", name="Estadio Nacional", city="Santiago"),
        competition=Competition(id="comp_ape_2012", name="Campeonato Nacional - Apertura", season="2012"),
        attendance_count=40000
    )

    # 4. Superclásico Monumental 2024 (Ruptura de la racha)
    match_4 = Match(
        id="match_2024_cl_cc",
        date=datetime.date(2024, 3, 10),
        home_team="Colo-Colo",
        away_team="Universidad de Chile",
        home_score=0,
        away_score=1,
        stadium=Stadium(id="st_monumental", name="Estadio Monumental", city="Santiago"),
        competition=Competition(id="comp_cam_2024", name="Campeonato Nacional", season="2024"),
        attendance_count=40000
    )

    # 5. Partido en Santa Laura contra la Unión (Campeonato 2023)
    match_5 = Match(
        id="match_2023_ue",
        date=datetime.date(2023, 7, 17),
        home_team="Unión Española",
        away_team="Universidad de Chile",
        home_score=3,
        away_score=0,
        stadium=Stadium(id="st_santa_laura", name="Estadio Santa Laura", city="Santiago"),
        competition=Competition(id="comp_cam_2023", name="Campeonato Nacional", season="2023"),
        attendance_count=12000
    )
    
    # 6. Empate de visita ante O'Higgins
    match_6 = Match(
        id="match_2023_ohi",
        date=datetime.date(2023, 2, 19),
        home_team="O'Higgins",
        away_team="Universidad de Chile",
        home_score=0,
        away_score=1, # Victoria en el Teniente
        stadium=Stadium(id="st_el_teniente", name="Estadio El Teniente", city="Rancagua"),
        competition=Competition(id="comp_cam_2023", name="Campeonato Nacional", season="2023"),
        attendance_count=9000
    )

    matches_to_insert = [match_1, match_2, match_3, match_4, match_5, match_6]
    
    for match in matches_to_insert:
        match_repo.insert_match(match)
        print(f"Partido insertado: {match.date} | {match.home_team} {match.home_score}-{match.away_score} {match.away_team}")

    # Cargar asistencias ficticias para "hincha_1"
    print("\nSimulando asistencia para 'hincha_1'...")
    user_id = "hincha_1"
    # Asistió a la final de 2011, la goleada del 2012 y el de Santa Laura 2023
    attended_match_ids = ["match_2011_sud_final", "match_2012_cl_cc", "match_2023_ue"]
    
    for match_id in attended_match_ids:
        attendance_repo.mark_as_attended(user_id, match_id)
        print(f"Marcado {match_id} como asistido para {user_id}")

    print("\n¡Semilla insertada correctamente!")

if __name__ == "__main__":
    seed_database()
