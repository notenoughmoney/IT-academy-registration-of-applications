import requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# my imports
import utils
from states import *

bot = Bot(token='5017253189:AAHBmdF-jQmQc3IntAcwpDToTZQfSa3wjsE')
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler()
async def start(message: types.Message):
    # получаем роль пользователя по нику
    role = utils.getRoleByUsername(message.from_user.username)
    # отправляем пользователя на соответствующую ветку
    if role == 1 or role == 2:
        await Order.waiting_for_action_spec.set()
    elif role == 3:
        await Order.waiting_for_action_user.set()

# начало сценария для пользователя
@dp.message_handler(state=Order.waiting_for_action_user)
async def get_action(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Подать заявку", callback_data="1"))
    keyboard.add(types.InlineKeyboardButton(text="Посмотреть свои заявки", callback_data="2"))
    await message.answer("Выберите, что вы хотите сделать?", reply_markup=keyboard)




executor.start_polling(dp)