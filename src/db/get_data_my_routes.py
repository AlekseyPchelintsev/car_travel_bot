from src.db.models import get_db_connection

# Получение посещенных городов
def get_visited_cities(user_tg_id, user_longitude, user_latitude):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT c.id, c.name, c.population, c.latitude, c.longitude,
                      ST_Distance(c.geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) / 1000 AS distance_km, -- Расчет расстояния
                      true AS is_visited,
                      false AS is_bookmarked,
                      false AS is_hidden
                FROM visited_cities vc
                JOIN cities c ON vc.city_id = c.id
                WHERE vc.user_tg_id = %s
                ORDER BY c.name;
            """

            # Выполняем запрос
            cursor.execute(query, (user_longitude, user_latitude, user_tg_id))
            return cursor.fetchall()  # [(id, name, population, latitude, longitude, distance_km, is_visited, is_bookmarked, is_hidden), ...]
    finally:
        connection.close()

# Получение сохраненных городов
def get_bookmarked_cities(user_tg_id, user_longitude, user_latitude):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT c.id, c.name, c.population, c.latitude, c.longitude,
                       ST_Distance(c.geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) / 1000 AS distance_km, -- Расчет расстояния
                       false AS is_visited,
                       true AS is_bookmarked,
                       false AS is_hidden
                FROM bookmarks b
                JOIN cities c ON b.city_id = c.id
                WHERE b.user_tg_id = %s
                ORDER BY c.name;
            """
            cursor.execute(query, (user_longitude, user_latitude, user_tg_id))
            return cursor.fetchall()  # [(id, name, population, latitude, longitude, distance_km, is_visited, is_bookmarked, is_hidden), ...]
    finally:
        connection.close()


# Получение скрытых городов
'''
def get_hidden_cities(user_tg_id, user_longitude, user_latitude):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT c.id, c.name, c.population, c.latitude, c.longitude,
                       ST_Distance(c.geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) / 1000 AS distance_km, -- Расчет расстояния
                       false AS is_visited,
                       false AS is_bookmarked,
                       true AS is_hidden
                FROM hidden_cities hc
                JOIN cities c ON hc.city_id = c.id
                WHERE hc.user_tg_id = %s
                ORDER BY c.name;
            """
            cursor.execute(query, (user_longitude, user_latitude, user_tg_id))
            return cursor.fetchall()  # [(id, name, population, latitude, longitude, distance_km, is_visited, is_bookmarked, is_hidden), ...]
    finally:
        connection.close()
'''


# добавление/удаление в бд посещенных, скрытых и отложенных городов
def toggle_bookmarks_db(user_tg_id, city_id):
    """Добавить или удалить город из закладок."""
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                # Проверяем наличие записи в закладках
                cursor.execute("""
                    SELECT 1 FROM bookmarks WHERE user_tg_id = %s AND city_id = %s
                """, (user_tg_id, city_id))
                if cursor.fetchone():
                    # Если запись есть, удаляем её
                    cursor.execute("""
                        DELETE FROM bookmarks WHERE user_tg_id = %s AND city_id = %s
                    """, (user_tg_id, city_id))
                    return False  # Удалено
                else:
                    # Если запись отсутствует, добавляем её
                    cursor.execute("""
                        INSERT INTO bookmarks (user_tg_id, city_id) VALUES (%s, %s)
                    """, (user_tg_id, city_id))

                    # Удаляем город из скрытых, если он там есть
                    cursor.execute("""
                        DELETE FROM hidden_cities WHERE user_tg_id = %s AND city_id = %s
                    """, (user_tg_id, city_id))
                    
                    return True  # Добавлено
    finally:
        connection.close()


def toggle_visited_db(user_tg_id, city_id):
    """Добавить или удалить город из посещённых."""
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                # Проверяем наличие записи в посещённых
                cursor.execute("""
                    SELECT 1 FROM visited_cities WHERE user_tg_id = %s AND city_id = %s
                """, (user_tg_id, city_id))
                if cursor.fetchone():
                    # Если запись есть, удаляем её
                    cursor.execute("""
                        DELETE FROM visited_cities WHERE user_tg_id = %s AND city_id = %s
                    """, (user_tg_id, city_id))
                    return False  # Удалено
                else:
                    # Если записи нет, добавляем её
                    cursor.execute("""
                        INSERT INTO visited_cities (user_tg_id, city_id) VALUES (%s, %s)
                    """, (user_tg_id, city_id))

                    # Удаляем город из скрытых, если он там есть
                    cursor.execute("""
                        DELETE FROM hidden_cities WHERE user_tg_id = %s AND city_id = %s
                    """, (user_tg_id, city_id))
                    
                    return True  # Добавлено
    finally:
        connection.close()

'''
def toggle_hidden_db(user_tg_id, city_id):
    """Добавить или удалить город из скрытых."""
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 1 FROM hidden_cities WHERE user_tg_id = %s AND city_id = %s
                """, (user_tg_id, city_id))
                if cursor.fetchone():
                    cursor.execute("""
                        DELETE FROM hidden_cities WHERE user_tg_id = %s AND city_id = %s
                    """, (user_tg_id, city_id))
                    return False
                else:
                    cursor.execute("""
                        INSERT INTO hidden_cities (user_tg_id, city_id) VALUES (%s, %s)
                    """, (user_tg_id, city_id))
                    cursor.execute("""
                        DELETE FROM visited_cities WHERE user_tg_id = %s AND city_id = %s
                    """, (user_tg_id, city_id))
                    cursor.execute("""
                        DELETE FROM bookmarks WHERE user_tg_id = %s AND city_id = %s
                    """, (user_tg_id, city_id))
                    return True
    finally:
        connection.close()
'''

# проверка посещен ли конкретный город для отрисовки клавиатуры
def is_city_visited(user_tg_id, city_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM visited_cities
                    WHERE user_tg_id = %s AND city_id = %s
                )
            """, (user_tg_id, city_id))
            return cursor.fetchone()[0]  # Возвращает True или False
    finally:
        connection.close()


# Проверка, находится ли город в закладках
def is_city_bookmarked(user_tg_id, city_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM bookmarks
                    WHERE user_tg_id = %s AND city_id = %s
                )
            """, (user_tg_id, city_id))
            return cursor.fetchone()[0]  # Возвращает True или False
    finally:
        connection.close()


# Проверка, является ли город скрытым
def is_city_hidden(user_tg_id, city_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1
                    FROM hidden_cities
                    WHERE user_tg_id = %s AND city_id = %s
                )
            """, (user_tg_id, city_id))
            return cursor.fetchone()[0]  # Возвращает True или False
    finally:
        connection.close()