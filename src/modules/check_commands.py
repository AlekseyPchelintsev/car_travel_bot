async def check_menu_commands(command, message, state):

  from src.handlers.search_settings import population_for_search, range_for_search
  from src.handlers.search_cities_handlers import find_cities_with_preferences
  from src.handlers.my_routes import my_routes_menu

  await state.set_state(None)

  if command == '🔎 Искать маршруты':
    await find_cities_with_preferences(message, state)
  elif command == '🌐 Радиус поиска':
    await range_for_search(message)
  elif command == '👨‍👩‍👦‍👦 Население':
    await population_for_search(message)
  elif command == '🧭 Мои маршруты':
    await my_routes_menu(message)