from src.db.models import get_db_connection


def update_population_range(user_tg_id, population_range):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                # Обновляем настройки пользователя
                cursor.execute("""
                    UPDATE user_preferences
                    SET population_range = %s
                    WHERE user_tg_id = %s
                """, (population_range, user_tg_id))
    finally:
        connection.close()


# для отрисовки клавиатуры в настройках поиска (население)
def get_user_preferences(user_tg_id):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                # Извлекаем настройки пользователя
                cursor.execute("""
                    SELECT population_range
                    FROM user_preferences
                    WHERE user_tg_id = %s
                """, (user_tg_id,))
                result = cursor.fetchone()

                if result:
                    # Возвращаем настройки как словарь
                    return {'population_range': result[0]}
                else:
                    # Если настроек нет, возвращаем пустой словарь
                    return {}
    finally:
        connection.close()


# для настроек радиуса поиска
def get_search_radius(user_tg_id):
    """
    Получает текущие настройки радиуса поиска из таблицы user_preferences.
    """
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT search_radius_from, search_radius_to
                    FROM user_preferences
                    WHERE user_tg_id = %s
                """, (user_tg_id,))
                radius = cursor.fetchone()
                if radius:
                    return radius
                return None
    finally:
        connection.close()


# обновление радиусов от пользователя
def radius_from(user_tg_id, new_radius_from):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE user_preferences
                    SET search_radius_from = %s
                    WHERE user_tg_id = %s
                """, (new_radius_from, user_tg_id))
    finally:
        connection.close()


def radius_to(user_tg_id, new_radius_to):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE user_preferences
                    SET search_radius_to = %s
                    WHERE user_tg_id = %s
                """, (new_radius_to, user_tg_id))
    finally:
        connection.close()