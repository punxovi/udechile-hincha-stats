import sqlite3
import os
import sys

# Asegurar importes del proyecto
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from infrastructure.persistence.sqlite_store import SqliteDatabase
from infrastructure.data_loaders.chuncho_scraper import scrape_year_config

def run_recovery_and_cleanup():
    db_path = os.path.join(script_dir, "udechile_stats.db")
    if not os.path.exists(db_path):
        print(f"[ERROR] No se encontro la base de datos local '{db_path}'")
        sys.exit(1)
        
    print("[Fase 1/3] Iniciando Re-Scrapeo completo (2011-2025) para recuperar partidos perdidos...")
    # Ejecutamos el scraper para cada año desde 2011 a 2025 de forma limpia.
    # Como ya tenemos la caché en data/cache, el scraper leerá desde el disco local
    # evitando peticiones masivas al sitio y ejecutando la restauración en segundos.
    
    # Nos movemos temporalmente a script_dir para que el scraper encuentre sus carpetas data/cache locales
    original_cwd = os.getcwd()
    os.chdir(script_dir)
    
    for year in range(2011, 2026):
        try:
            print(f"-> Procesando ano {year}...")
            # clear=False para no borrar lo que ya tenemos, force=False para usar la caché local
            scrape_year_config(year, clear=False, force=False)
        except Exception as e:
            print(f"[WARN] Error al raspar ano {year}: {e}")
            
    os.chdir(original_cwd)

    print("\n[Fase 2/3] Mapeando y migrando asistencias asociadas a IDs manuales...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Mapeo explícito de los partidos manuales del seed a sus homólogos del scraper
    migration_map = {
        "match_2011_sud_final": "chuncho_20111214_763c",
        "match_2011_cl_uc": "chuncho_20110612_7b0f",
        "match_2012_cl_cc": "chuncho_20120429_c5ed",
        "match_2023_ue": "chuncho_20230717_93a3",
        "match_2023_ohi": "chuncho_20230219_eaf4",
        "match_2024_cl_cc": "chuncho_20240310_7662"
    }

    migrated_attendances = 0
    deleted_duplicates = 0

    for manual_id, scraper_id in migration_map.items():
        # Verificar si hay asistencias para el ID manual
        cursor.execute("SELECT user_id FROM user_attendance WHERE match_id = ?", (manual_id,))
        users = [r["user_id"] for r in cursor.fetchall()]
        
        if users:
            print(f"-> Encontradas asistencias de {len(users)} usuario(s) para el partido manual '{manual_id}'")
            for user_id in users:
                # Comprobar si el usuario ya tiene marcada la asistencia para el partido del scraper
                cursor.execute("""
                    SELECT 1 FROM user_attendance 
                    WHERE user_id = ? AND match_id = ?
                """, (user_id, scraper_id))
                exists = cursor.fetchone()
                
                if exists:
                    # Si ya tiene marcada la asistencia en el scraper_id, solo borramos la asistencia del manual_id
                    cursor.execute("""
                        DELETE FROM user_attendance 
                        WHERE user_id = ? AND match_id = ?
                    """, (user_id, manual_id))
                    deleted_duplicates += 1
                else:
                    # Si no existe, actualizamos el match_id
                    cursor.execute("""
                        UPDATE user_attendance 
                        SET match_id = ? 
                        WHERE user_id = ? AND match_id = ?
                    """, (scraper_id, user_id, manual_id))
                    migrated_attendances += 1
            print(f"   [OK] Asistencias actualizadas/consolidadas hacia '{scraper_id}'")

    conn.commit()

    print("\n[Fase 3/3] Eliminando partidos duplicados inyectados manualmente...")
    removed_matches = 0
    for manual_id in migration_map.keys():
        cursor.execute("SELECT id FROM matches WHERE id = ?", (manual_id,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("DELETE FROM matches WHERE id = ?", (manual_id,))
            removed_matches += 1
            print(f"   [DEL] Eliminado partido manual duplicado: {manual_id}")
            
    conn.commit()
    conn.close()

    print(f"\n*** PROCESO FINALIZADO CON EXITO ***")
    print(f"  - Partidos re-importados/verificados: Temporadas 2011 a 2025.")
    print(f"  - Asistencias migradas al partido real del scraper: {migrated_attendances}")
    print(f"  - Asistencias duplicadas simplificadas: {deleted_duplicates}")
    print(f"  - Partidos manuales duplicados eliminados de la BD: {removed_matches}")

if __name__ == "__main__":
    run_recovery_and_cleanup()
