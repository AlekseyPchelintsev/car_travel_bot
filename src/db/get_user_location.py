from psycopg2.extras import RealDictCursor
from src.db.models import get_db_connection

def get_user_location(user_tg_id):
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        ST_X(ST_AsText(last_location)) AS longitude, -- Долгота
                        ST_Y(ST_AsText(last_location)) AS latitude  -- Широта
                    FROM users
                    WHERE user_tg_id = %s
                """, (user_tg_id,))
                result = cursor.fetchone()

                if result:
                    return result['latitude'], result['longitude']
                else:
                    return None
    finally:
        conn.close()

