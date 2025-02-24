import asyncio
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.modules.check_commands import check_menu_commands
from src.db.search_user_settings import get_search_radius, get_user_preferences, radius_from, radius_to, update_population_range
import src.modules.keyboards as kb
from config import menu_commands, radius_search_img, population_search_img


router = Router()


from aiogram.fsm.state import StatesGroup, State

class RadiusSettings(StatesGroup):
    waiting_for_from = State()
    waiting_for_to = State()


# настройки радиуса поиска
@router.message(F.text == '🌐 Радиус поиска')
async def range_for_search(message: Message):
    user_tg_id = message.from_user.id

    # Получаем текущие настройки радиуса из БД
    radius = get_search_radius(user_tg_id)
    if radius:
        # Преобразуем радиусы из метров в километры
        search_radius_from_km = (radius[0] or 0) // 1000
        search_radius_to_km = (radius[1] or 100000) // 1000  # Используем 100 км по умолчанию

    else:
        text = "⚠️ Настройки радиуса поиска не найдены. Используются значения по умолчанию:\nот 0 км до 100 км"

    await message.answer_photo(
                         photo=radius_search_img,
                         caption=(f"<b>☉ Текущие настройки радиуса поиска:</b>\n\n"
                                      f"⟲ От: {search_radius_from_km} км\n"
                                      f"⟳ До: {search_radius_to_km} км"),
                         parse_mode='HTML',
                         reply_markup=kb.radius_search)


# обработчики кнопок настройка от и до
@router.callback_query(F.data == "set_radius_from")
async def set_radius_from(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите минимальный радиус поиска (км):")
    await state.set_state(RadiusSettings.waiting_for_from)


@router.callback_query(F.data == "set_radius_to")
async def set_radius_to(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите максимальный радиус поиска (км):")
    await state.set_state(RadiusSettings.waiting_for_to)


# обработка радиуса от пользователя
@router.message(RadiusSettings.waiting_for_from, F.text.isdigit())
async def process_radius_from(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    new_radius_from_km = int(message.text)
    new_radius_from_m = new_radius_from_km * 1000  # Преобразуем в метры

    # Проверяем, что минимальный радиус не превышает максимальный
    radius = get_search_radius(user_tg_id)
    if radius:
        _, search_radius_to = radius
        if search_radius_to is not None and new_radius_from_m > search_radius_to:
            await message.answer(
                text=f"⚠️ Ошибка: минимальный радиус не может быть больше максимального ({search_radius_to // 1000} км). Попробуйте снова.",
                reply_markup=kb.main_menu
            )
            return

    # Обновляем значение в БД
    await asyncio.to_thread(radius_from, user_tg_id, new_radius_from_m)

    await message.answer(
        text=f"✅ Минимальный радиус поиска успешно обновлён: {new_radius_from_km} км",
        reply_markup=kb.main_menu
    )
    await range_for_search(message)
    await state.clear()


@router.message(RadiusSettings.waiting_for_to, F.text.isdigit())
async def process_radius_to(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    new_radius_to_km = int(message.text)
    new_radius_to_m = new_radius_to_km * 1000  # Преобразуем в метры

    # Проверяем, что максимальный радиус больше минимального
    radius = get_search_radius(user_tg_id)
    if radius:
        search_radius_from, _ = radius
        if search_radius_from is not None and new_radius_to_m < search_radius_from:
            await message.answer(
                text=f"⚠️ Ошибка: максимальный радиус не может быть меньше минимального ({search_radius_from // 1000} км). Попробуйте снова.",
                reply_markup=kb.main_menu
            )
            return

    # Обновляем значение в БД
    await asyncio.to_thread(radius_to, user_tg_id, new_radius_to_m)

    await message.answer(
        text=f"✅ Максимальный радиус поиска успешно обновлён: {new_radius_to_km} км",
        reply_markup=kb.main_menu
    )
    await range_for_search(message)
    await state.clear()

  
# обработка если пользователь ввел не число
@router.message(RadiusSettings.waiting_for_from)
@router.message(RadiusSettings.waiting_for_to)
async def process_invalid_input(message: Message, state: FSMContext):

    if message.text in menu_commands:
        await check_menu_commands(message.text, message, state)
    else:
        await message.answer("Пожалуйста, введите числовое значение.")
        return


# настройки поиска населения
@router.message(F.text == '👨‍👩‍👦‍👦 Население')
async def population_for_search(message: Message):
    
    user_tg_id = message.from_user.id
    user_preferences = get_user_preferences(user_tg_id)
    selected_range = user_preferences.get('population_range', '1')
    
    await message.answer_photo(
        photo=population_search_img,
        caption='<b>Население</b>',
        parse_mode='HTML',
        reply_markup=kb.generate_population_keyboard(selected_range)
    )


# Статусы кнопок (🔘 — выбранная, ⚪️ — остальные)
population_ranges = {
    '15': '⚪️ 1000-5000',
    '515': '⚪️ 5000-15000',
    '1530': '⚪️ 15000-30000',
    '3050': '⚪️ 30000-50000',
    '50': '⚪️ от 50000',
}

@router.callback_query(F.data.in_(population_ranges.keys()))
async def handle_population_callback(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    selected_range = callback.data

    # Обновляем настройки пользователя в БД
    update_population_range(user_tg_id, selected_range)

    # Генерируем обновленную клавиатуру
    keyboard_builder = InlineKeyboardBuilder()
    for key, label in population_ranges.items():
        if key == selected_range:
            # Отмечаем выбранную кнопку
            keyboard_builder.button(
                text=label.replace('⚪️', '🔘'),
                callback_data=key
            )
        else:
            # Оставляем остальные кнопки
            keyboard_builder.button(
                text=label,
                callback_data=key
            )
    keyboard_builder.adjust(1)

    # Обновляем сообщение с новой клавиатурой
    await callback.message.edit_reply_markup(
        reply_markup=keyboard_builder.as_markup()
    )

    # Подтверждаем обработку колбэка
    await callback.answer("Настройки обновлены.")