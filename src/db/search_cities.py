from src.db.models import get_db_connection


# преобразование диапазона населения в числовые границы
def parse_population_range(population_range):
    if population_range is None or population_range == "":
        return 0, 10**9  # Без ограничений

    if "до" in population_range:
        max_population = int(population_range.split("до")[1].strip())
        return 0, max_population

    if "более" in population_range:
        min_population = int(population_range.split("более")[1].strip())
        return min_population, 10**9

    if "-" in population_range:
        min_population, max_population = map(int, population_range.split("-"))
        return min_population, max_population

    return 0, 10**9  # На случай некорректного значения


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
                           has_river, 
                           has_lake, 
                           has_railway_station, 
                           has_airport, 
                           has_hiking_routes, 
                           population_range
                    FROM user_preferences
                    WHERE user_tg_id = %s
                """, (user_tg_id,))
                preferences = cursor.fetchone()
                
                if not preferences:
                    raise ValueError("Настройки пользователя не найдены.")
                
                radius_from, radius_to, has_river, has_lake, has_railway_station, has_airport, has_hiking_routes, population_range = preferences

                # Преобразуем диапазон населения в числовые границы
                population_min, population_max = parse_population_range(population_range)

                # Формируем запрос на выборку городов с учетом фильтров
                query = """
                    SELECT *, 
                           ST_DistanceSphere(
                               ST_MakePoint(longitude, latitude),
                               ST_MakePoint(%s, %s)
                           ) AS distance
                    FROM cities
                    WHERE ST_DistanceSphere(
                              ST_MakePoint(longitude, latitude),
                              ST_MakePoint(%s, %s)
                          ) BETWEEN %s AND %s
                          AND (%s IS NULL OR has_river = %s)
                          AND (%s IS NULL OR has_lake = %s)
                          AND (%s IS NULL OR has_railway_station = %s)
                          AND (%s IS NULL OR has_airport = %s)
                          AND (%s IS NULL OR has_hiking_routes = %s)
                          AND population BETWEEN %s AND %s
                    ORDER BY distance;
                """
                cursor.execute(query, (
                    user_longitude, user_latitude,  # Координаты пользователя
                    user_longitude, user_latitude,  # Координаты пользователя (повтор для вычисления расстояния)
                    radius_from, radius_to,         # Радиус поиска
                    has_river, has_river,           # Фильтр по реке
                    has_lake, has_lake,             # Фильтр по озеру
                    has_railway_station, has_railway_station,  # Фильтр по вокзалу
                    has_airport, has_airport,       # Фильтр по аэропорту
                    has_hiking_routes, has_hiking_routes,  # Пешие маршруты
                    population_min, population_max  # Диапазон населения
                ))

                return cursor.fetchall()
    finally:
        connection.close()