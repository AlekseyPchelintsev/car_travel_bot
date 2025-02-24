
from src.db.models import get_db_connection
import csv
import io


from src.db.models import get_db_connection
import csv

def import_csv_to_cities(csv_file_path):
    """
    Импортирует данные из CSV-файла в таблицу cities.
    :param csv_file_path: Путь к CSV-файлу.
    """
    connection = get_db_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                # Читаем CSV-файл
                with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
                    reader = csv.DictReader(file, delimiter=';')
                    print(f"Заголовки: {reader.fieldnames}")  # Проверяем, какие заголовки считались
                    for row in reader:
                        print(f"Считанная строка: {row}")  # Проверяем, что содержится в строках
                        
                        # Преобразуем координаты в тип geography
                        latitude = float(row['latitude'])
                        longitude = float(row['longitude'])
                        
                        # Создание географической точки с использованием PostGIS
                        geography_point = f"SRID=4326;POINT({longitude} {latitude})"  # Географическая точка (долгота, широта)

                        # Вставка данных в таблицу
                        cursor.execute("""
                            INSERT INTO cities (name, population, latitude, longitude, geom)
                            VALUES (%s, %s, %s, %s, ST_GeogFromText(%s))
                        """, (row['name'], int(row['population']), latitude, longitude, geography_point))
        print("Данные успешно импортированы.")
    finally:
        connection.close()

# Путь к вашему CSV-файлу
csv_file_path = 'CITIES_DATA.csv'

# Импортируем данные
import_csv_to_cities(csv_file_path)