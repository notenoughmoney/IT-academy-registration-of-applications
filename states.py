from aiogram.dispatcher.filters.state import State, StatesGroup

class Order(StatesGroup):
    waiting_for_action_user = State()
    waiting_for_action_spec = State()
    waiting_for_purpose = State()
    waiting_for_1st_problem = State()
    waiting_for_2st_problem = State()
    rick_roll = State()