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

                # основная таблица пользователей
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
                
                # настройки поиска
                cursor.execute(
                    """
                        CREATE TABLE IF NOT EXISTS user_preferences (
                        id SERIAL PRIMARY KEY,
                        user_tg_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        search_radius_from INTEGER DEFAULT 0, -- Минимальный радиус поиска
                        search_radius_to INTEGER DEFAULT 200  -- Максимальный радиус поиска
                        has_river BOOLEAN DEFAULT NULL,
                        has_lake BOOLEAN DEFAULT NULL,
                        has_railway_station BOOLEAN DEFAULT NULL,
                        has_airport BOOLEAN DEFAULT NULL,
                        has_hiking_routes BOOLEAN DEFAULT NULL,
                        population_range VARCHAR(50) DEFAULT NULL -- Например, "до 5000", "5000-15000"
                    );
                    """
                )
                
                #города
                cursor.execute(
                    """
                        CREATE TABLE IF NOT EXISTS cities (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        type VARCHAR(255),
                        latitude FLOAT NOT NULL,
                        longitude FLOAT NOT NULL,
                        population INTEGER NOT NULL, -- Население
                        has_river BOOLEAN DEFAULT NULL, -- Наличие реки
                        has_lake BOOLEAN DEFAULT NULL, -- Наличие озера
                        has_railway_station BOOLEAN DEFAULT NULL, -- Железнодорожный вокзал
                        has_airport BOOLEAN DEFAULT NULL, -- Аэропорт
                        UNIQUE(name, region, latitude, longitude) -- Уникальность по ключу
                    );
                    """
                )
                
                # посещеные города
                cursor.execute(
                    """
                        CREATE TABLE IF NOT EXISTS visited_cities (
                        id SERIAL PRIMARY KEY,
                        user_tg_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
                        visited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    """
                )
                
                # закладки городов для посещения
                cursor.execute(
                    """
                        CREATE TABLE IF NOT EXISTS visited_cities (
                        id SERIAL PRIMARY KEY,
                        user_tg_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        city_id INTEGER REFERENCES cities(id) ON DELETE CASCADE,
                    );
                    """
                )
                
    finally:
        connection.close()