from aiogram.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           ReplyKeyboardMarkup,
                           KeyboardButton)

from aiogram.utils.keyboard import InlineKeyboardBuilder
import urllib.parse


geoposition = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📍 Поделиться геопозицией 🌏', request_location=True)]
    ],
    resize_keyboard=True
)


update_geoposition = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📍 Обновить геопозицию 🌏', request_location=True)]
    ],
    resize_keyboard=True
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Искать маршруты")],
        [KeyboardButton(text="🧭 Мои маршруты")],
        [KeyboardButton(text="🌐 Радиус поиска"),
        KeyboardButton(text="👨‍👩‍👦‍👦 Население")],
        [KeyboardButton(text="📍 Обновить геопозицию", request_location=True)]
    ],
    resize_keyboard=True
)


# формирование клавиатуры с названиями городов при поиске
def generate_cities_keyboard_with_status(cities, page=1, items_per_page=10, build_location=''):
    """
    Создает инлайн-клавиатуру с пагинацией для списка городов с учетом статусов.
    :param cities: список городов
    :param page: текущая страница
    :param items_per_page: количество городов на странице
    :return: объект InlineKeyboardMarkup
    """
    # Определяем границы текущей страницы
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Формируем кнопки для городов текущей страницы
    current_cities = cities[start_idx:end_idx]
    buttons = []
    for city in current_cities:
        city_id = city[0]
        city_name = city[1]
        city_distance = city[5]  # Расстояние до города
        is_visited = city[6]
        is_bookmarked = city[7]
        '''
        is_hidden = False
        try:
            is_hidden = city[8]
        except:
            pass
        '''
        # Формируем текст кнопки с учётом статусов
        status = ""
        if is_visited:
            status += "✅ "
        if is_bookmarked:
            status += "📌 "
        '''    
        if is_hidden:
            status += "🚫 "
        '''
        button_text = f"{status}{city_name} ({city_distance:.1f} км)"
        callback_data = f"city_{city_id}_page_{page}"
        buttons.append(InlineKeyboardButton(text=button_text, callback_data=callback_data))

    # Проверяем, что список кнопок не пустой
    if not buttons:
        raise ValueError("Список городов для генерации клавиатуры пуст.")

    # Создаем клавиатуру
    inline_keyboard = [[button] for button in buttons]

    # Добавляем кнопки пагинации
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}"))
    if end_idx < len(cities):
        pagination_buttons.append(InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"page_{page + 1}"))
    if build_location == 'my_routes':
        pagination_buttons.append(InlineKeyboardButton(text="↩️ К моим маршрутам", callback_data="back_to_my_routes"))
    if pagination_buttons:
        inline_keyboard.append(pagination_buttons)

    # Возвращаем клавиатуру
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


# возврат к списку городов
def back_to_cities_list(latitude, longitude, city_status, return_callback="return_to_list", current_section=""):
    """
    Генерирует клавиатуру для карточки города с динамическими кнопками.
    :param latitude: Широта города
    :param longitude: Долгота города
    :param city_status: Статус города {'visited': bool, 'bookmarked': bool, 'hidden': bool}
    :param return_callback: Callback для кнопки возврата
    :return: InlineKeyboardMarkup
    """

    if current_section == 'visited':

        if not city_status.get("visited"):
            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="🚘 Открыть в Яндекс.Картах",
                    url=f"https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
                )],
                [InlineKeyboardButton(text="↩️ К списку городов", callback_data=return_callback)]
            ]
        )
        else:

            text = f"Посмотри маршрут: https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
            encoded_text = urllib.parse.quote(text, safe='')

            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🚘 Открыть в Яндекс.Картах",
                        url=f"https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
                    )],
                    [InlineKeyboardButton(
                        text="📤 Поделиться",
                        url=f"tg://resolve?domain=share&text={encoded_text}"
                    )],
                    [InlineKeyboardButton(text='Убрать из посещенных', callback_data='to_visited')],
                    [InlineKeyboardButton(text="↩️ К списку городов", callback_data=return_callback)]
                ]
            )


    elif current_section == 'bookmarked':

        text = f"Посмотри маршрут: https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
        encoded_text = urllib.parse.quote(text, safe='')

        if not city_status.get("bookmarked"):            

            keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="🚘 Открыть в Яндекс.Картах",
                    url=f"https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
                )],
                [InlineKeyboardButton(text="↩️ К списку городов", callback_data=return_callback)]
            ]
        )
        else:
        
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🚘 Открыть в Яндекс.Картах",
                        url=f"https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
                    )],
                    [InlineKeyboardButton(
                        text="📤 Поделиться",
                        url=f"tg://resolve?domain=share&text={encoded_text}"
                    )],
                    [InlineKeyboardButton(text='Убрать из отложенных', callback_data='to_bookmarks')],
                    [InlineKeyboardButton(text="↩️ К списку городов", callback_data=return_callback)]
                ]
            )

    else:

        text = f"Посмотри маршрут: https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
        encoded_text = urllib.parse.quote(text, safe='')

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="🚘 Открыть в Яндекс.Картах",
                    url=f"https://yandex.ru/maps/?rtext=~{latitude},{longitude}&rtt=auto"
                )],
                [InlineKeyboardButton(
                    text="📤 Поделиться",
                    url=f"tg://resolve?domain=share&text={encoded_text}"
                )],
                [InlineKeyboardButton(
                    text="✅ Посещено" if city_status.get("visited") else "● Посещено",
                    callback_data="to_visited"
                )],
                [InlineKeyboardButton(
                    text="📌 В закладках" if city_status.get("bookmarked") else "● В закладки",
                    callback_data="to_bookmarks"
                )],
                
                [InlineKeyboardButton(text="↩️ К списку городов", callback_data=return_callback)],
            ]
        )
    return keyboard


my_routes = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Посещенные", callback_data="visited")],
                [InlineKeyboardButton(text="📌 Сохраненные", callback_data="bookmarks")],
                #[InlineKeyboardButton(text="🚫 Скрытые", callback_data="hide")]
                             ]
        )


# возврат в главное меню
'''back_to_main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="↩️ В главное меню")]
    ],
    resize_keyboard=True
)


# возврат в настройки поиска
back_to_search_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="↩️ К настройкам")]
    ],
    resize_keyboard=True
)'''



# население
def generate_population_keyboard(selected_range):
    population_ranges = {
        '15': '⚪️ 1000-5000',
        '515': '⚪️ 5000-15000',
        '1530': '⚪️ 15000-30000',
        '3050': '⚪️ 30000-50000',
        '50': '⚪️ более 50000',
    }
    keyboard_builder = InlineKeyboardBuilder()
    for key, label in population_ranges.items():
        if key == selected_range:
            keyboard_builder.button(
                text=label.replace('⚪️', '🔘'),
                callback_data=key
            )
        else:
            keyboard_builder.button(
                text=label,
                callback_data=key
            )
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


# радиус поиска
radius_search = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="От", callback_data="set_radius_from"),
                InlineKeyboardButton(text="До", callback_data="set_radius_to")
            ]
        ]
    )