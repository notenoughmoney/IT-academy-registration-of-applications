from aiogram.dispatcher.filters.state import State, StatesGroup


class Order(StatesGroup):
    start = State()
    waiting_for_action_user = State()
    waiting_for_action_spec = State()
    waiting_for_purpose = State()
    waiting_for_1st_reason = State()
    waiting_for_2nd_reason = State()
    waiting_for_description = State()
