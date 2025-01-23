from src.db.models import get_db_connection

# Функция обновления геопозиции пользователя в БД
def update_user_location(user_tg_id, latitude, longitude):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users
                    SET last_location = ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    WHERE user_tg_id = %s
                """, (longitude, latitude, user_tg_id))
    finally:
        connection.close()