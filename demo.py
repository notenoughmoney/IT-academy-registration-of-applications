import my_requests
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import message
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

# my imports
import utils
from states import *

bot = Bot(token='5017253189:AAHBmdF-jQmQc3IntAcwpDToTZQfSa3wjsE')
dp = Dispatcher(bot, storage=MemoryStorage())

print("Bot started!")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    purposes = ["Подать заявку", "Посмотреть мои заявки"]
    keyboard.add(*purposes)
    await message.answer("Выберите, что вы хотите сделать?", reply_markup=keyboard)

@dp.message_handler(regexp='Подать заявку')
async def step1(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    purposes = ["Проблема с программой", "Проблема с рабочим местом"]
    keyboard.add(*purposes)
    await message.answer("Что у вас случилось?", reply_markup=keyboard)

@dp.message_handler(regexp='Проблема с рабочим местом')
async def step1(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    purposes = ["Не работает периферия", "Не работает компьютер", "Не работает Интернет", "Другое"]
    keyboard.add(*purposes)
    await message.answer("Что конкретно произошло?", reply_markup=keyboard)

@dp.message_handler(regexp='Не работает Интернет')
async def step1(message: types.Message):
    await message.answer("Опишите свою проблему более детально.\nМожете прикрепить изображение (не обязательно).",
        reply_markup=types.ReplyKeyboardRemove())


#У меня не грузит Интернет, хотя у коллег всё хорошо. Кабель подключен. Думаю, проблема в настройках DNS.

@dp.message_handler(regexp='У меня не грузит Интернет, хотя у коллег всё хорошо. Кабель подключен. Думаю, проблема в настройках DNS.')
async def step1(message: types.Message):
    await message.answer("Ваша заявка успешно зарегистрирована. Ожидайте специалиста.",
        reply_markup=types.ReplyKeyboardRemove())


executor.start_polling(dp)

