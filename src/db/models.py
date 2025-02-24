import psycopg2
from psycopg2 import OperationalError
from config import user, password, database, host

# подключение к бд
def get_db_connection():
    try:
        conn = psycopg2.connect(
            user=user,
            password=password,
            database=database,
            host=host
        )
        return conn
    except OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None
    
    
# создание бд
def create_tables():
    connection = get_db_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                # Основная таблица пользователей
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        user_tg_id BIGINT UNIQUE NOT NULL,
                        name VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_location GEOGRAPHY(POINT, 4326) -- Широта и долгота в формате точки в системе координат WGS84
                    );
                    """
                )
                
                # Настройки поиска
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id SERIAL PRIMARY KEY,
                        user_tg_id BIGINT UNIQUE REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        search_radius_from INTEGER DEFAULT 0, -- Минимальный радиус поиска
                        search_radius_to INTEGER DEFAULT 100,  -- Максимальный радиус поиска
                        has_river BOOLEAN DEFAULT FALSE,
                        has_lake BOOLEAN DEFAULT FALSE,
                        has_railway_station BOOLEAN DEFAULT FALSE,
                        has_airport BOOLEAN DEFAULT FALSE,
                        has_hiking_routes BOOLEAN DEFAULT FALSE,
                        population_range VARCHAR(50) DEFAULT '15' -- Например, "до 5000", "5000-15000"
                    );
                    """
                )
                
                # Города
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS cities (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        latitude FLOAT NOT NULL,
                        longitude FLOAT NOT NULL,
                        geom GEOGRAPHY(POINT, 4326),
                        population INTEGER NOT NULL, -- Население
                        has_river BOOLEAN DEFAULT FALSE, -- Наличие реки
                        has_lake BOOLEAN DEFAULT FALSE, -- Наличие озера
                        has_railway_station BOOLEAN DEFAULT FALSE, -- Железнодорожный вокзал
                        has_airport BOOLEAN DEFAULT FALSE, -- Аэропорт
                        UNIQUE(name, latitude, longitude) -- Уникальность по ключу
                    );
                    """
                )
                
                # Посещенные города
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS visited_cities (
                        id SERIAL PRIMARY KEY,
                        user_tg_id BIGINT REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
                        visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE (user_tg_id, city_id)  -- Добавлено уникальное ограничение
                    );
                    """
                )

                # Закладки городов для посещения
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS bookmarks (
                        id SERIAL PRIMARY KEY,
                        user_tg_id BIGINT REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
                        UNIQUE (user_tg_id, city_id)  -- Добавлено уникальное ограничение
                    );
                    """
                )

                # Скрытые города
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS hidden_cities (
                        id SERIAL PRIMARY KEY,
                        user_tg_id BIGINT REFERENCES users(user_tg_id) ON DELETE CASCADE,
                        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
                        UNIQUE (user_tg_id, city_id)  -- Добавлено уникальное ограничение
                    );
                    """
                )

                
    finally:
        connection.close()
