import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from src.db.models import create_tables
# handlers
from src.handlers.start_point import router as command_start_router
from src.handlers.search_cities_handlers import router as search_cities_router
from src.handlers.search_settings import router as search_settings_router
from src.handlers.my_routes import router as my_routes_router


storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=storage)

async def main():
    
    # create db tables
    await asyncio.to_thread(create_tables)

    # handlers
    dp.include_router(command_start_router)
    dp.include_router(search_cities_router)
    dp.include_router(search_settings_router)
    dp.include_router(my_routes_router)

    try:
        await dp.start_polling(bot, timeout=50)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
