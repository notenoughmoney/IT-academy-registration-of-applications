import time
import requests
import io
import json
import math
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# my imports
import my_requests
import utils
from states import *

bot = Bot(token='5017253189:AAHBmdF-jQmQc3IntAcwpDToTZQfSa3wjsE')
dp = Dispatcher(bot, storage=MemoryStorage())

print("Bot started!")

BACK = u"\U00002B05 Назад"
HOME = u"\U0001F3E0 Главное меню"


# домашняя страничка
@dp.message_handler(commands=['start'])
@dp.message_handler(state=Order.start)
async def start(message: types.Message):
    # получаем роль пользователя по нику
    role = my_requests.getRoleByUsername(message.from_user.username)
    # отправляем пользователя на соответствующую ветку
    if role == 1 or role == 2:
        pass
    elif role == 3:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        purposes = ["Подать заявку", "Посмотреть мои заявки"]
        keyboard.add(*purposes)
        await message.answer("Выберите, что вы хотите сделать?", reply_markup=keyboard)
        await Order.waiting_for_purpose.set()


@dp.callback_query_handler(lambda c: c.data == 'left' or c.data == 'right', state=Order.waiting_for_purpose)
async def another_page(c: types.CallbackQuery, state: FSMContext):
    temp = await state.get_data()
    page = temp.get("page")
    pages = temp.get("pages")
    reqs = temp.get("reqs")

    btn_left = None
    btn_right = None
    toSend = None
    if c.data == 'left':
        await state.update_data(page=page - 1)
        toSend = utils.form_text(page - 1, pages, reqs)
        btn_left = InlineKeyboardButton("<", callback_data="left") if (page - 1 > 1) else None
        btn_right = InlineKeyboardButton(">", callback_data="right") if (page - 1 < pages) else None
    elif c.data == 'right':
        await state.update_data(page=page + 1)
        toSend = utils.form_text(page + 1, pages, reqs)
        btn_left = InlineKeyboardButton("<", callback_data="left") if (page + 1 > 1) else None
        btn_right = InlineKeyboardButton(">", callback_data="right") if (page + 1 < pages) else None

    # формируем клавиатуру
    keyboard = InlineKeyboardMarkup()
    if btn_left is not None and btn_right is not None:
        keyboard.row(btn_left, btn_right)
    elif btn_left is not None:
        keyboard.row(btn_left)
    elif btn_right is not None:
        keyboard.row(btn_right)

    await bot.edit_message_text(toSend,
                                message_id=c.message.message_id,
                                inline_message_id=c.message.message_id,
                                chat_id=c.message.chat.id,
                                reply_markup=keyboard)


@dp.message_handler(state=Order.waiting_for_purpose)
async def get_purpose(message: types.Message, state: FSMContext):
    if message.text == "Подать заявку":
        globalReasons = my_requests.getGlobalReasons(message.from_user.username)
        await state.update_data(availableGlobalReasons=globalReasons)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for globalReason in globalReasons:
            keyboard.add(globalReason[0])
        keyboard.add(BACK)
        await message.answer("Что у вас случилось?", reply_markup=keyboard)
        await Order.waiting_for_1st_reason.set()
    if message.text == "Посмотреть мои заявки":
        reqs = my_requests.getMyRequests(message.from_user.username)

        length = len(reqs)
        pages = math.ceil(length / 5)  # округляем в большую сторону
        page = 1

        # заносим в state данные
        await state.update_data(page=1)      # о текущей странице
        await state.update_data(pages=pages) # о количстве страниц
        await state.update_data(reqs=reqs)   # о заявках

        # формируем клавиатуру
        keyboard = InlineKeyboardMarkup()
        btn_right = InlineKeyboardButton(">", callback_data="right") if (page < pages) else None
        if btn_right is not None:
            keyboard.row(btn_right)

        toSend = utils.form_text(page, pages, reqs)
        await message.answer(toSend, reply_markup=keyboard)


@dp.message_handler(state=Order.waiting_for_1st_reason)
async def get_global_reason(message: types.Message, state: FSMContext):
    # проверка на назад
    if message.text == BACK:
        await Order.start.set()
        await start(message)
        return

    # проверка на наличие проблемы в списке предложенных
    availableGlobalReasons = await state.get_data()
    if message.text not in utils.column(availableGlobalReasons.get("availableGlobalReasons"), 0):
        await message.answer("Пожалуйста, используйте только клавиатуру ниже.")
        return

    # заносим в state ID причины 1-го уровня
    temp = await state.get_data()
    await state.update_data(globalReason=utils.getReasonId(temp.get("availableGlobalReasons"), message.text))

    # предлагаем пользователю выбрать подпричину
    subReasons = my_requests.getSubReasons(message.from_user.username, message.text)
    await state.update_data(availableSubReasons=subReasons)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for subReason in subReasons:
        keyboard.add(subReason[0])
    keyboard.row(BACK, HOME)
    await message.answer("Что конкретно у вас случилось?", reply_markup=keyboard)
    await Order.waiting_for_2nd_reason.set()


@dp.message_handler(state=Order.waiting_for_2nd_reason)
async def get_sub_reason(message: types.Message, state: FSMContext):
    # проверка на назад
    if message.text == BACK:
        await Order.waiting_for_purpose.set()
        message.text = "Подать заявку"
        await get_purpose(message, state)
        return

    # проверка на домой
    if message.text == HOME:
        await Order.start.set()
        await start(message)
        return

    # делаем проверку сообщения
    availableSubReasons = await state.get_data()
    if message.text not in utils.column(availableSubReasons.get("availableSubReasons"), 0):
        await message.answer("Пожалуйста, используйте только клавиатуру ниже.")
        return

    # заносим в state ID причины 2-го уровня
    temp = await state.get_data()
    await state.update_data(subReason=utils.getReasonId(temp.get("availableSubReasons"), message.text))

    # чекаем state в терминале
    # temp = await state.get_data()
    # temp = json.dumps(temp, ensure_ascii=False, indent=2)
    # print(temp)

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(BACK, HOME)
    # предлагаем пользователю внести описание проблемы
    await message.answer(
        "Пожалуйста, опишите свою проблему более детально.\nМожете прикрепить изображение (не обязательно).",
        reply_markup=keyboard)
    await Order.waiting_for_description.set()


@dp.message_handler(state=Order.waiting_for_description, content_types=["photo", "text"])
async def get_description(message: types.Message, state: FSMContext):
    # обрабатываем кнопки
    if message.text == BACK:
        await Order.waiting_for_1st_reason.set()
        temp = await state.get_data()
        array = temp.get("availableGlobalReasons")
        num = temp.get("globalReason")
        message.text = utils.getReasonText(array, num)
        await get_global_reason(message, state)
        return

    if message.text == HOME:
        await Order.start.set()
        await start(message)
        return

    # пробуем получить картинку, переводим её в байт-код
    try:
        file = await bot.get_file(message.photo[-1].file_id)
        file_byte: io.BytesIO = await bot.download_file(file.file_path)
        files = {"image": file_byte.getvalue()}
    except:
        files = {"image": None}

    # получаем reason из state
    temp = await state.get_data()
    reason = temp.get("subReason")

    # формируем description
    description = message.caption if message.caption is not None else message.text
    if (description == None):
        await message.answer("Пожалуйста, добавьте текстовое описание.")
        return

    # всё остальное
    url = "https://req.tucana.org/api/request"
    headers = {"telegram": message.from_user.username}

    # без ключа картинки запрос проходит
    # с ключом, но без картинки запрос тоже проходит
    # description - обязателен - строка

    r = requests.post(url, data={"description": description, "reason": reason}, headers=headers, files=files)

    if r.ok:
        await message.answer(
            "Ваша заявка успешно зарегистрирована. Ожидайте помощи специалиста.",
            reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(
            "Упс...\nПохоже, что-то пошло не так.\nПопробуйте оставить заявку позже или воспользуйтесь сайтом.",
            reply_markup=types.ReplyKeyboardRemove())

    # перекидываем домой
    time.sleep(2)  # чтобы пользователь успел прочитать результат
    await Order.start.set()
    await start(message)
    return


executor.start_polling(dp)
