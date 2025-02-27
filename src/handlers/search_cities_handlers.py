import asyncio
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from geopy.distance import geodesic
from src.handlers.my_routes import my_routes_menu, show_bookmarked_cities, show_visited_cities
from src.db.get_data_my_routes import toggle_bookmarks_db, toggle_visited_db, get_bookmarked_cities, get_visited_cities, is_city_bookmarked, is_city_visited
from src.db.get_city_details import get_city_details
from src.db.search_cities import get_cities_nearby_with_preferences
from src.db.get_user_location import get_user_location
import src.modules.keyboards as kb
from config import search_img, city_info


router = Router()


# поиск городов
@router.message(F.text == "🔎 Искать маршруты")
async def find_cities_with_preferences(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    await state.update_data(current_menu_location="search_cities_menu")

    # Получаем последние координаты пользователя
    user_location = get_user_location(user_tg_id)
    if not user_location:
        await message.answer(
            "Для поиска локаций поделитесь своей геопозицией через кнопку 🟦 <b>'Меню'</b>.",
            parse_mode="HTML",
            reply_markup=kb.main_menu,
        )
        return

    user_latitude, user_longitude = user_location
    try:
        cities = get_cities_nearby_with_preferences(user_tg_id, user_longitude, user_latitude)

        if cities:
            await state.update_data(current_section="search", cities=cities, current_page=1)
            await message.answer_photo(
                photo=search_img,
                caption="Найденные локации:",
                reply_markup=kb.generate_cities_keyboard_with_status(cities, page=1),
            )
        else:
            await message.answer(
                text="Не найдено локаций, соответствующих вашим критериям. Попробуйте изменить <b>'📍 Радиус поиска'</b> или <b>'👨‍👩‍👦‍👦 Население'</b>.",
                parse_mode='HTML'
            )
    except ValueError as e:
        await message.answer(str(e))


# возврат к списку городов
@router.callback_query(F.data == "return_to_list")
async def return_to_cities_list(callback: CallbackQuery, state: FSMContext):

    user_tg_id = callback.from_user.id
    user_location = get_user_location(user_tg_id)
    user_latitude, user_longitude = user_location

    # Извлекаем данные из состояния
    data = await state.get_data()
    current_section = data.get("current_section", "search")  # По умолчанию общий поиск
    build_location = ''

    if current_section == 'search':
        cities = await asyncio.to_thread(get_cities_nearby_with_preferences, user_tg_id, user_longitude, user_latitude)
    elif current_section == 'visited':
        empty_list = 1
        cities = await asyncio.to_thread(get_visited_cities, user_tg_id, user_longitude, user_latitude)
        build_location = 'my_routes'
    elif current_section == 'bookmarked':
        empty_list = 2
        cities = await asyncio.to_thread(get_bookmarked_cities, user_tg_id, user_longitude, user_latitude)
        build_location = 'my_routes'
        '''
    elif current_section == 'hidden':
        empty_list = 3
        cities = await asyncio.to_thread(get_hidden_cities, user_tg_id, user_longitude, user_latitude)
        build_location = 'my_routes'
        '''    
    else:
        cities = data.get('cities', [])

    page = data.get("current_page", 1)

    if not cities and build_location == 'my_routes':
        if empty_list == 1:
            await callback.answer(text='Список посещенных локаций пуст', show_alert=True)
        if empty_list == 2:
            await callback.answer(text='Список отложенных локаций пуст', show_alert=True)
        '''
        if empty_list == 3:
            await callback.answer(text='Список скрытых локаций пуст', show_alert=True)
        '''
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=search_img,
                caption='<b>Мои маршруты:</b>',
                parse_mode='HTML'
            ),
            reply_markup=kb.my_routes
        )
        return

    # Генерируем текст заголовка для разделов
    section_headers = {
        "visited": "✅ <b>Посещенные локации:</b>",
        "bookmarked": "📌 <b>Сохраненные локации:</b>",
        #"hidden": "🚫 <b>Скрытые локации:</b>",
    }

    header_text = section_headers.get(current_section, "Найденные локации:")
        

    # Генерируем клавиатуру
    keyboard = kb.generate_cities_keyboard_with_status(cities, page=page, build_location=build_location)
    await callback.message.edit_media(
        media=InputMediaPhoto(
            media=search_img,
        caption=header_text,
        parse_mode="HTML"
        ),
        reply_markup=keyboard,
        
    )


@router.callback_query(F.data.startswith("city_"))
async def show_city_details(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик открытия карточки города.
    :param callback: CallbackQuery
    :param state: FSMContext
    """
    try:
        # Извлекаем данные из callback_data
        data_parts = callback.data.split("_")
        city_id = int(data_parts[1])  # ID города
        page = int(data_parts[3])  # Номер страницы, с которой перешли
        data = await state.get_data()
        current_section = data.get('current_section')


        # Сохраняем текущую страницу и ID города в состояние
        await state.update_data(return_page=page, current_city_id=city_id)

        # Получаем информацию о городе
        city_details = await asyncio.to_thread(get_city_details, city_id)
        if not city_details:
            await callback.answer("Информация о локации не найдена.")
            return

        city_name, latitude, longitude, population = city_details

        # Получаем координаты пользователя
        user_tg_id = callback.from_user.id
        user_location = await asyncio.to_thread(get_user_location, user_tg_id)
        if not user_location:
            await callback.answer("Координаты пользователя не найдены.")
            return

        user_latitude, user_longitude = user_location

        # Рассчитываем расстояние в километрах
        distance_km = geodesic((user_latitude, user_longitude), (latitude, longitude)).kilometers
        distance_km = round(distance_km, 1)

        # Определяем текущий статус города (посещён, сохранён, скрыт)
        city_status = {
            "visited": await asyncio.to_thread(is_city_visited, user_tg_id, city_id),
            "bookmarked": await asyncio.to_thread(is_city_bookmarked, user_tg_id, city_id),
            #"hidden": await asyncio.to_thread(is_city_hidden, user_tg_id, city_id),
        }

        # Сохраняем статус города и его координаты в состоянии
        await state.update_data(city_status=city_status, latitude=latitude, longitude=longitude)

        # Формируем ответное сообщение
        response = (
            f"🪧 <b>Название:</b> {city_name}\n"
            f"👥 <b>Население:</b> ~ {population}\n"
            f"📏 <b>Расстояние:</b> ~ {distance_km} км\n\n"
            "(расстояние указывается приблизительное, без учета особенностей рельефа и построения маршрута)"
        )

        # Обновляем сообщение с карточкой города
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=city_info,
            caption=response,
            parse_mode='HTML'
            ),
            reply_markup=kb.back_to_cities_list(latitude, longitude, city_status, current_section=current_section)
        )

    except Exception as e:
        # Логируем ошибку и уведомляем пользователя
        print(f"Ошибка в обработчике show_city_details: {e}")
        await callback.answer("Произошла ошибка при загрузке данных о локации. Попробуйте позже.", show_alert=True)



# обработка сохранения, посещения и скрытия города
@router.callback_query(F.data == "to_visited")
async def add_to_visited(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    data = await state.get_data()
    city_id = data.get("current_city_id")
    current_section = data.get('current_section')

    if not city_id:
        await callback.answer("Не удалось определить локацию.")
        return

    user_location = await asyncio.to_thread(get_user_location, user_tg_id)
    if not user_location:
        await callback.answer("Не удалось получить координаты пользователя.")
        return

    user_latitude, user_longitude = user_location

    # Переключаем статус в БД
    await asyncio.to_thread(toggle_visited_db, user_tg_id, city_id)
    is_visited = await asyncio.to_thread(is_city_visited, user_tg_id, city_id)
    visited_list = await asyncio.to_thread(get_visited_cities, user_tg_id, user_longitude, user_latitude)

    city_details = await asyncio.to_thread(get_city_details, city_id)
    if not city_details:
        await callback.answer("Информация о локации не найдена.")
        return
    
    city_name, latitude, longitude, population = city_details

    # Если город удаляется из посещенных и пользователь находится в разделе "Посещенные"
    if not is_visited and current_section == 'visited':

        if visited_list:
            await callback.answer(
                text="Локация удалена из списка посещенных",
                )
            await show_visited_cities(callback, state)
            return
        else:
            await callback.answer(
                text="Список посещенных локаций пуст.",
                show_alert=True
                )
            await my_routes_menu(callback.message)
            return
        
            
    # Сообщение пользователю
    await callback.answer(
        "Локация добавлена в список посещенных" if is_visited else "Локация удалена из списка посещенных"
    )

    # Обновляем статус города в состоянии
    city_status = data.get("city_status", {"visited": False, "bookmarked": False})  # "hidden": False
    city_status["visited"] = is_visited
    await state.update_data(city_status=city_status)

    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(
        reply_markup=kb.back_to_cities_list(
            latitude, longitude, city_status, current_section=current_section
        )
    )


@router.callback_query(F.data == "to_bookmarks")
async def add_to_bookmarks(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    data = await state.get_data()
    city_id = data.get("current_city_id")
    current_section = data.get('current_section')

    if not city_id:
        await callback.answer("Не удалось определить локацию.")
        return

    user_location = await asyncio.to_thread(get_user_location, user_tg_id)
    if not user_location:
        await callback.answer("Не удалось получить координаты пользователя.")
        return

    user_latitude, user_longitude = user_location

    city_details = await asyncio.to_thread(get_city_details, city_id)
    if not city_details:
        await callback.answer("Информация о локации не найдена.")
        return
    
    city_name, latitude, longitude, population = city_details

    # Переключаем статус в БД
    await asyncio.to_thread(toggle_bookmarks_db, user_tg_id, city_id)
    is_bookmarked = await asyncio.to_thread(is_city_bookmarked, user_tg_id, city_id)
    bookmarked_list = await asyncio.to_thread(get_bookmarked_cities, user_tg_id, user_longitude, user_latitude)

    # Если город удаляется из посещенных и пользователь находится в разделе "Посещенные"
    if not is_bookmarked and current_section == 'bookmarked':

        if bookmarked_list:
            await callback.answer(
                text="Локация удалена из закладок",
                )
            await show_bookmarked_cities(callback, state)
            return
        else:
            await callback.answer(
                text="Список сохраненных локаций пуст.",
                show_alert=True
                )
            await my_routes_menu(callback.message)
            return


    await callback.answer(
    "Локация добавлена в закладки" if is_bookmarked else "Локация удалена из закладок"
    )

    # Обновляем статус города в состоянии
    city_status = data.get("city_status", {"visited": False, "bookmarked": False}) #"hidden": False
    city_status["bookmarked"] = is_bookmarked
    await state.update_data(city_status=city_status)

    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(reply_markup=kb.back_to_cities_list(latitude, longitude, city_status, current_section=current_section))


'''
@router.callback_query(F.data == "to_hide")
async def add_to_hidden(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    data = await state.get_data()
    city_id = data.get("current_city_id")
    current_section = data.get('current_section')

    if not city_id:
        await callback.answer("Не удалось определить локацию.")
        return

    user_location = await asyncio.to_thread(get_user_location, user_tg_id)
    if not user_location:
        await callback.answer("Не удалось получить координаты пользователя.")
        return

    user_latitude, user_longitude = user_location

    # Переключаем статус в БД
    await asyncio.to_thread(toggle_hidden_db, user_tg_id, city_id)
    is_hidden = await asyncio.to_thread(is_city_hidden, user_tg_id, city_id)

    # Сообщение пользователю
    await callback.answer(
        "Локация скрыта из поиска!" if is_hidden else "Локация возвращена в поиск!"
    )

    # Обновляем статус города в состоянии
    city_status = data.get("city_status", {"visited": False, "bookmarked": False}) #"hidden": False
    city_status["hidden"] = is_hidden
    await state.update_data(city_status=city_status)

    # Обновляем клавиатуру
    await callback.message.edit_reply_markup(reply_markup=kb.back_to_cities_list(user_latitude, user_longitude, city_status, current_section=current_section))
'''


# ПАГИНАЦИЯ
@router.callback_query(F.data.startswith("page_"))
async def paginate_cities(callback_query: CallbackQuery, state: FSMContext):
    # Извлекаем номер страницы из callback_data
    page = int(callback_query.data.split("_")[1])
    data = await state.get_data()
    cities = data.get("cities", [])

    if not cities:
        await callback_query.answer("Ошибка: список городов не найден.")
        return

    # Сохраняем текущую страницу в состоянии
    await state.update_data(current_page=page)

    # Обновляем клавиатуру для новой страницы
    await callback_query.message.edit_reply_markup(reply_markup=kb.generate_cities_keyboard_with_status(cities, page=page))