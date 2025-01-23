from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardMarkup,
                           KeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder



geoposition = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📍 Поделиться геопозицией 🌏', request_location=True)]
    ],
    resize_keyboard=True
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Искать маршруты", request_location=True)],
        [KeyboardButton(text="🎛 Настройки поиска")]
    ],
    resize_keyboard=True
)


# формирование клавиатуры с названиями городов при поиске
def generate_cities_keyboard(cities):
    """
    Создает инлайн-клавиатуру с кнопками для каждого города.
    :param cities: список городов (результат функции get_cities_nearby_with_preferences)
    :return: объект InlineKeyboardMarkup
    """
    keyboard = InlineKeyboardMarkup(row_width=1)  # Одна кнопка в строке

    for city in cities:
        city_id = city[0]  # ID города
        city_name = city[1]  # Название города
        city_region = city[2]  # Регион города

        # Кнопка с названием города и его ID в callback_data
        keyboard.add(
            InlineKeyboardButton(
                text=f"{city_name} ({city_region})",
                callback_data=f"city_{city_id}"  # Уникальный идентификатор для кнопки
            )
        )
    
    return keyboard


# возврат к списку городов
back_to_cities_list = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton("Назад к списку", callback_data="back_to_list")]]
        )