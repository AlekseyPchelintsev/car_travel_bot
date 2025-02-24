from src.db.models import get_db_connection

# Диапазоны населения в виде ключей и соответствующих значений
population_ranges = {
    '15': (1000, 4999),
    '515': (5000, 14999),
    '1530': (15000, 29999),
    '3050': (30000, 49999),
    '50': (50000, float('inf')),  # "более 50000"
}

def parse_population_range(population_range_key):
    # Если ключ не найден, возвращаем без ограничений
    if population_range_key is None or population_range_key == "":
        return 0, 10**9  # Без ограничений
    
    # Возвращаем числовые границы на основе ключа
    return population_ranges.get(population_range_key, (0, 10**9))  # По умолчанию без ограничений

# получение списка городов согласно настройкам поиска
def get_cities_nearby_with_preferences(user_tg_id, user_longitude, user_latitude):
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                # Получаем настройки пользователя
                cursor.execute("""
                    SELECT search_radius_from, 
                           search_radius_to, 
                           population_range
                    FROM user_preferences
                    WHERE user_tg_id = %s
                """, (user_tg_id,))
                preferences = cursor.fetchone()

                if not preferences:
                    raise ValueError("Настройки пользователя не найдены.")
                
                # Извлекаем радиус и ключ диапазона населения
                radius_from, radius_to, population_range_key = preferences

                # Преобразуем диапазон населения в числовые границы
                population_min, population_max = parse_population_range(population_range_key)

                # Формируем запрос для поиска городов с учётом скрытых
                query = """
                    SELECT c.id, c.name, c.population, c.latitude, c.longitude, 
                           ST_Distance(c.geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) / 1000 AS distance_km,
                           CASE WHEN vc.city_id IS NOT NULL THEN true ELSE false END AS is_visited,
                           CASE WHEN bm.city_id IS NOT NULL THEN true ELSE false END AS is_bookmarked
                    FROM cities c
                    LEFT JOIN visited_cities vc ON vc.city_id = c.id AND vc.user_tg_id = %s
                    LEFT JOIN bookmarks bm ON bm.city_id = c.id AND bm.user_tg_id = %s
                    --LEFT JOIN hidden_cities hc ON hc.city_id = c.id AND hc.user_tg_id = %s
                    WHERE ST_Distance(c.geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326)) BETWEEN %s AND %s
                          AND c.population BETWEEN %s AND %s
                          -- AND hc.city_id IS NULL -- Исключаем скрытые города
                    ORDER BY distance_km;
                """

                # Выполняем запрос
                cursor.execute(query, (
                    user_longitude, user_latitude,  # Координаты пользователя
                    user_tg_id,  # Для отметки посещённых
                    user_tg_id,  # Для отметки сохранённых
                    user_tg_id,  # Для исключения скрытых
                    user_longitude, user_latitude,  # Повтор для расчёта расстояния
                    radius_from or 0, radius_to or 50000,  # Радиус поиска
                    population_min, population_max  # Диапазон населения
                ))

                result = cursor.fetchall()

                # Возвращаем список городов
                return result
    finally:
        connection.close()