import asyncio
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from geopy.distance import geodesic
from src.db.get_data_my_routes import get_bookmarked_cities, get_visited_cities
from src.db.get_city_details import get_city_details
from src.db.search_cities import get_cities_nearby_with_preferences
from src.db.get_user_location import get_user_location
import src.modules.keyboards as kb
from config import my_routes_img


router = Router()


@router.message(F.text == '🧭 Мои маршруты')
async def my_routes_menu(message: Message):

  try:
    await message.edit_caption(
        caption='<b>Мои маршруты:</b>',
        parse_mode='HTML',
        reply_markup=kb.my_routes
    )
  except:
    await message.answer_photo(
        photo= my_routes_img,
        caption='<b>Мои маршруты:</b>',
        parse_mode='HTML',
        reply_markup=kb.my_routes
    )


@router.callback_query(F.data == 'back_to_my_routes')
async def back_to_my_routes(callback: CallbackQuery):
    
    try:
        await callback.message.edit_caption(
            caption='<b>Мои маршруты:</b>',
            parse_mode='HTML',
            reply_markup=kb.my_routes
            )
    except:
        await callback.answer_photo(
            photo=my_routes_img,
            caption='<b>Мои маршруты:</b>',
            parse_mode='HTML',
            reply_markup=kb.my_routes
        )


@router.callback_query(F.data == "visited")
async def show_visited_cities(callback: CallbackQuery, state: FSMContext):
    
    user_tg_id = callback.from_user.id

    # Получаем последние координаты пользователя
    user_location = get_user_location(user_tg_id)
    if not user_location:
        await callback.message.answer(
            "Для поиска локаций поделитесь своей геопозицией через кнопку 🟦 <b>'Меню'</b>.",
            parse_mode="HTML",
            reply_markup=kb.main_menu,
        )
        return

    user_latitude, user_longitude = user_location

    cities = await asyncio.to_thread(get_visited_cities, user_tg_id, user_longitude, user_latitude)

    if cities:
        await state.update_data(current_section='visited', cities=cities, current_page=1)
        await callback.message.edit_caption(
            caption="✅ <b>Посещенные локации:</b>",
            parse_mode="HTML",
            reply_markup=kb.generate_cities_keyboard_with_status(cities=cities, build_location='my_routes')
        )
    else:
        await callback.answer(
            text="Список посещенных локаций пуст.",
            show_alert=True
        )

@router.callback_query(F.data == "bookmarks")
async def show_bookmarked_cities(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    
    # Получаем последние координаты пользователя
    user_location = get_user_location(user_tg_id)
    if not user_location:
        await callback.message.answer(
            "Для поиска локаций поделитесь своей геопозицией через кнопку 🟦 <b>'Меню'</b>.",
            parse_mode="HTML",
            reply_markup=kb.main_menu,
        )
        return

    user_latitude, user_longitude = user_location

    cities = await asyncio.to_thread(get_bookmarked_cities, user_tg_id, user_longitude, user_latitude)

    if cities:
        await state.update_data(current_section='bookmarked', cities=cities, current_page=1)
        await callback.message.edit_caption(
            caption="📌 <b>Сохраненные локации:</b>",
            parse_mode="HTML",
            reply_markup=kb.generate_cities_keyboard_with_status(cities=cities, build_location='my_routes')
        )
    else:
        await callback.answer(
            text="Список сохраненных локаций пуст.",
            show_alert=True
        )


'''
@router.callback_query(F.data == "hide")
async def show_hidden_cities(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    
    # Получаем последние координаты пользователя
    user_location = get_user_location(user_tg_id)
    if not user_location:
        await callback.message.answer(
            "Для поиска локаций поделитесь своей геопозицией через кнопку 🟦 <b>'Меню'</b>.",
            parse_mode="HTML",
            reply_markup=kb.main_menu,
        )
        return

    user_latitude, user_longitude = user_location

    cities = await asyncio.to_thread(get_hidden_cities, user_tg_id, user_longitude, user_latitude)
    print(cities)
    if cities:
        await state.update_data(current_section='hidden', cities=cities, current_page=1)
        await callback.message.edit_caption(
            caption="🚫 <b>Скрытые локации:</b>",
            parse_mode="HTML",
            reply_markup=kb.generate_cities_keyboard_with_status(cities=cities, build_location='my_routes')
        )
    else:
        await callback.answer(
            text="Список скрытых локаций пуст.",
            show_alert=True
        )
'''