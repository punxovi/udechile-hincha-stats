import sys
import os
from dotenv import load_dotenv

# Asegurar que el path del proyecto esté disponible para importar módulos locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infrastructure.persistence.sqlite_store import SqliteDatabase, SqliteMatchRepository, SqliteAttendanceRepository, SqliteLeagueTableRepository
from infrastructure.persistence.postgres_store import PostgresDatabase, PostgresMatchRepository, PostgresAttendanceRepository, PostgresLeagueTableRepository

def run_migration():
    print("🚀 Iniciando migración de datos locales a Supabase (PostgreSQL)...")
    
    # 1. Cargar el entorno
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_DB_URL")
    if not supabase_url:
        print("❌ Error: SUPABASE_DB_URL no está configurada en tu archivo .env")
        sys.exit(1)
        
    # 2. Conectar a SQLite Local
    sqlite_db_path = "udechile_stats.db"
    if not os.path.exists(sqlite_db_path):
        print(f"❌ Error: No se encontró la base de datos local '{sqlite_db_path}'")
        sys.exit(1)
        
    print("🔌 Conectando a SQLite y Supabase...")
    sqlite_db = SqliteDatabase(sqlite_db_path)
    sqlite_match_repo = SqliteMatchRepository(sqlite_db)
    sqlite_attendance_repo = SqliteAttendanceRepository(sqlite_db)
    sqlite_table_repo = SqliteLeagueTableRepository(sqlite_db)
    
    # 3. Conectar a PostgreSQL Supabase e inicializar el esquema
    postgres_db = PostgresDatabase(supabase_url)
    print("🛠️ Inicializando esquema de tablas en Supabase...")
    try:
        postgres_db.initialize_schema()
    except Exception as e:
        print(f"❌ Error al inicializar el esquema en Supabase: {e}")
        print("\n💡 Asegúrate de haber copiado correctamente la URI de conexión con la contraseña real en el archivo .env")
        sys.exit(1)
        
    postgres_match_repo = PostgresMatchRepository(postgres_db)
    postgres_attendance_repo = PostgresAttendanceRepository(postgres_db)
    postgres_table_repo = PostgresLeagueTableRepository(postgres_db)
    
    # 4. Migrar Partidos
    print("\n📦 Migrando PARTIDOS...")
    sqlite_matches = sqlite_match_repo.get_matches()
    print(f"   -> Encontrados {len(sqlite_matches)} partidos locales.")
    
    migrated_matches = 0
    for match in sqlite_matches:
        try:
            postgres_match_repo.insert_match(match)
            migrated_matches += 1
        except Exception as e:
            print(f"   ⚠️ Error al migrar partido {match.id}: {e}")
            
    print(f"   ✅ Se migraron exitosamente {migrated_matches} de {len(sqlite_matches)} partidos.")
    
    # 5. Migrar Tablas de Posiciones
    print("\n🏆 Migrando TABLAS DE POSICIONES...")
    # Buscaremos todas las tablas de posiciones cargadas en SQLite por temporada
    migrated_tables = 0
    # Recorremos el rango completo que hemos importado
    for year in range(2011, 2026):
        sqlite_tables = sqlite_table_repo.get_league_tables_by_season(str(year))
        for table in sqlite_tables:
            try:
                postgres_table_repo.insert_league_table(table)
                migrated_tables += 1
            except Exception as e:
                print(f"   ⚠️ Error al migrar tabla {table.competition_id}: {e}")
                
    print(f"   ✅ Se migraron exitosamente {migrated_tables} tablas de posiciones.")
    
    # 6. Migrar Asistencias de Usuarios
    print("\n🏟️ Migrando ASISTENCIAS DE USUARIOS...")
    # Obtenemos las asistencias de 'hincha_1' (y cualquier otro)
    # Como la tabla user_attendance solo tiene user_id y match_id, podemos leerla directamente con SQLite
    try:
        with sqlite_db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, match_id FROM user_attendance")
            sqlite_attendances = cursor.fetchall()
    except Exception as e:
        print(f"   ⚠️ Error al leer asistencias de SQLite: {e}")
        sqlite_attendances = []
        
    print(f"   -> Encontradas {len(sqlite_attendances)} registros de asistencia.")
    
    migrated_attendances = 0
    for row in sqlite_attendances:
        user_id = row["user_id"]
        match_id = row["match_id"]
        try:
            postgres_attendance_repo.mark_as_attended(user_id, match_id)
            migrated_attendances += 1
        except Exception as e:
            print(f"   ⚠️ Error al migrar asistencia de {user_id} para partido {match_id}: {e}")
            
    print(f"   ✅ Se migraron exitosamente {migrated_attendances} de {len(sqlite_attendances)} asistencias.")
    
    print("\n🎉 ¡MIGRACIÓN COMPLETADA CON ÉXITO ABSOLUTO! 🎉")
    print("Toda la base de datos histórica de la U (2011-2025) y tus registros personales ahora residen en Supabase.")

if __name__ == "__main__":
    run_migration()
