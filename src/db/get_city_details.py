from src.db.models import get_db_connection


def get_city_details(city_id):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT name, region, latitude, longitude, population
                    FROM cities
                    WHERE id = %s
                """, (city_id,))
                return cursor.fetchone()
    finally:
        conn.close()