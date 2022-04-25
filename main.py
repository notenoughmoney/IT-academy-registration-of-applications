import requests
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


@dp.message_handler(commands=['start'])
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
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    purposes = ["Подать заявку", "Посмотреть мои заявки"]
    keyboard.add(*purposes)
    await message.answer("Выберите, что вы хотите сделать?", reply_markup=keyboard)
    await Order.waiting_for_purpose.set()


@dp.message_handler(state=Order.waiting_for_purpose)
async def get_global_reason(message: types.Message, state: FSMContext):
    if message.text == "Подать заявку":
        globalReasons = utils.getGlobalReasons(message.from_user.username)
        await state.update_data(availableGlobalReasons=globalReasons)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for globalReason in globalReasons:
            keyboard.add(globalReason[0])
        await message.answer("Что у вас случилось?", reply_markup=keyboard)
        await Order.waiting_for_1st_reason.set()


@dp.message_handler(state=Order.waiting_for_1st_reason)
async def get_sub_reasons(message: types.Message, state: FSMContext):
    # делаем проверку сообщения
    availableGlobalReasons = await state.get_data()
    if message.text not in utils.column(availableGlobalReasons.get("availableGlobalReasons"), 0):
        await message.answer("Пожалуйста, используйте только клавиатуру ниже.")
        return

    # заносим в state ID причины 1-го уровня
    temp = await state.get_data()
    await state.update_data(globalReason=utils.getReasonId(temp.get("availableGlobalReasons"), message.text))

    # предлагаеи пользователю выбрать подпричину
    subReasons = utils.getSubReasons(message.from_user.username, message.text)
    await state.update_data(availableSubReasons=subReasons)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subReason in subReasons:
        keyboard.add(subReason[0])
    await message.answer("Что конкретно у вас случилось?", reply_markup=keyboard)
    await Order.waiting_for_2nd_reason.set()


@dp.message_handler(state=Order.waiting_for_2nd_reason)
async def get_sub_reasons(message: types.Message, state: FSMContext):
    # делаем проверку сообщения
    availableSubReasons = await state.get_data()
    if message.text not in utils.column(availableSubReasons.get("availableSubReasons"), 0):
        await message.answer("Пожалуйста, используйте только клавиатуру ниже.")
        return

    # заносим в state ID причины 2-го уровня
    temp = await state.get_data()
    await state.update_data(subReason=utils.getReasonId(temp.get("availableSubReasons"), message.text))

    # чекаем в терминале
    temp = await state.get_data()
    print(temp)

    # предлагаем пользователю внести описание проблемы
    await message.answer(
        "Пожалуйста, опишите свою проблему более детально.\nМожете прикрепить изображение (не обязательно).",
        reply_markup=types.ReplyKeyboardRemove())
    await Order.waiting_for_description.set()


@dp.message_handler(state=Order.waiting_for_description, content_types=["photo", "text"])
async def get_description(message: types.Message, state: FSMContext):
    print("it works")
    description = message.text
    print(message.photo)


executor.start_polling(dp)
