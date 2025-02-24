import asyncio
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from src.db.add_user import add_user
from src.db.update_user_location import update_user_location
import src.modules.keyboards as kb


router = Router()


class Registration(StatesGroup):
    start_info = State()


# КОММАНДА /START
@router.message(CommandStart())
async def start(message: Message, state: FSMContext, bot: Bot):

    # получение id пользователя
    user_tg_id = message.from_user.id
    user_name = message.from_user.full_name
    
    await asyncio.to_thread(add_user, user_tg_id, user_name)
    
    await bot.send_message(chat_id=user_tg_id, 
                           text='Чтобы воспользоваться сервисом подбора маршрутов для автопутешествий, необходимо дать доступ к вашей геопозиции.', 
                           reply_markup=kb.geoposition)
    

# обновление геопозиции
@router.message(Command("update_geo"))
async def update_geoposition(message: Message, bot: Bot):

    user_tg_id = message.from_user.id

    await bot.send_message(
        chat_id=user_tg_id,
        text='Подтвердите обновление геопозиции',
        reply_markup=kb.update_geoposition
    )


@router.message(Command('help'))
async def help_menu(message: Message, bot: Bot, state: State):

    await message.answer(
        text=(
            'Раздел "помощь"'
            '\n(в процессе заполнения)'
        ),
        parse_mode='HTML',
        reply_markup=kb.main_menu
    )


@router.message(F.text == '↩️ В главное меню')
async def back_to_main_menu(message: Message, bot: Bot, state: State):

    await message.answer(
            text='<b>Главное меню:</b>',
            parse_mode='HTML',
            reply_markup=kb.main_menu
            )
    

@router.message(F.location)
async def handle_location(message: Message, bot: Bot, state: FSMContext):
    
    user_tg_id = message.from_user.id
    latitude = message.location.latitude
    longitude = message.location.longitude

    await asyncio.to_thread(update_user_location, user_tg_id, latitude, longitude)
    
    await bot.send_message(
        chat_id=user_tg_id,
        text='Геопозиция обновлена!',
        reply_markup=kb.main_menu
    )


# ПОЛУЧЕНИЕ id ИЗОБРАЖЕНИЙ
'''
@router.message(F.photo)
async def get_photo_id(message: Message):
    # Получаем ID фото
    photo_id = message.photo[-1].file_id  # Получаем ID самого высокого качества
    await message.answer(text=f'ID фото: {photo_id}')
'''