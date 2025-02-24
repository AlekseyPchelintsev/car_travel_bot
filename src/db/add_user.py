import psycopg2
from src.db.models import get_db_connection

# Функция добавления пользователя
def add_user(telegram_id, name):
    connection = get_db_connection()
    
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (user_tg_id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (user_tg_id) DO NOTHING;
                """, (telegram_id, name))

                # Вставка записи в таблицу user_preferences
                cursor.execute("""
                    INSERT INTO user_preferences (user_tg_id)
                    VALUES (%s)
                    ON CONFLICT (user_tg_id) DO NOTHING;
                """, (telegram_id,))
    finally:
        connection.close()