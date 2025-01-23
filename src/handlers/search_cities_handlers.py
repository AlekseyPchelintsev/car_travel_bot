import asyncio
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.db.add_user import add_user
from src.db.get_city_details import get_city_details
from src.db.search_cities import get_cities_nearby_with_preferences
from src.db.update_user_location import update_user_location
from src.db.get_user_location import get_user_location
import src.modules.keyboards as kb


router = Router()


# поиск городов
@router.message(F.text == "🔎 Искать маршруты")
async def find_cities_with_preferences(message: Message):
    user_tg_id = message.from_user.id

    # Проверяем, отправил ли пользователь свою геопозицию
    if message.location:
        user_latitude = message.location.latitude
        user_longitude = message.location.longitude

        # Обновляем геопозицию пользователя в БД
        await asyncio.to_thread(update_user_location, user_tg_id, user_latitude, user_longitude)
    else:
        # Получаем последние координаты пользователя из БД
        user_location = get_user_location(user_tg_id)

        if not user_location:
            await message.answer(
                "Для поиска маршрутов поделитесь своей геопозицией. Нажмите <b>'🔎 Искать маршруты'</b> ещё раз, чтобы отправить локацию.",
                parse_mode='HTML',
                reply_markup=kb.main_menu
            )
            return

        user_latitude, user_longitude = user_location

    try:
        # Ищем города с учетом предпочтений
        cities = get_cities_nearby_with_preferences(user_tg_id, user_longitude, user_latitude)

        if cities:
            await message.answer(
                "Вот города, найденные поблизости:",
                reply_markup=kb.generate_cities_keyboard(cities)
            )
        else:
            await message.answer(text=(
                "Не найдено городов, соответствующих вашим критериям."
                "\nПопробуйте изменить '🎛 Настройки поиска'"))
    except ValueError as e:
        await message.answer(str(e))
                

# возврат к списку городов
@router.callback_query(F.data == "back_to_list")
async def back_to_city_list(callback: CallbackQuery):
    user_tg_id = callback.from_user.id

    # Получаем последние координаты пользователя
    user_location = get_user_location(user_tg_id)

    if not user_location:
        await callback.message.edit_text("Не удалось определить вашу геопозицию. Пожалуйста, поделитесь своей локацией.")
        return

    user_latitude, user_longitude = user_location

    try:
        # Выполняем поиск городов с учетом предпочтений пользователя
        cities = get_cities_nearby_with_preferences(user_tg_id, user_longitude, user_latitude)

        if cities:
            await callback.message.edit_text("Вот города, найденные поблизости:", 
                                 reply_markup=kb.generate_cities_keyboard(cities))
        else:
            await callback.message.edit_text("Не найдено городов, соответствующих вашим критериям.")
    except ValueError as e:
        await callback.message.edit_text(str(e))
        

# просмотр данных о городе
@router.callback_query(F.data.startswith("city_"))
async def show_city_details(callback: CallbackQuery):
    city_id = int(callback.data.split("_")[1])  # Извлекаем ID города из callback_data

    # Получаем информацию о городе из БД
    city_details = await asyncio.to_thread(get_city_details, city_id)

    if city_details:
        city_name, city_region, latitude, longitude, population = city_details
        response = (
            f"📍 Город: {city_name}\n"
            f"🌍 Регион: {city_region}\n"
            f"👥 Население: {population}\n"
            f"🌐 Координаты: {latitude}, {longitude}\n"
        )
        # Кнопка для возврата к списку городов
        
        await callback.message.edit_text(response, reply_markup=kb.back_to_cities_list)
    else:
        await callback.answer("Информация о городе не найдена.", show_alert=True)