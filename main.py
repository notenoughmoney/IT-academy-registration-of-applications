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
    # 1 - Администратор
    # 2 - Специалист
    # 3 - Пользователь
    if role == 1 or role == 2:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        purposes1 = ["Подать заявку", "Посмотреть мои поданные заявки"]
        purposes2 = ["Биржа заявок", "Посмотреть мои выполняемые заявки"]
        keyboard.row(*purposes1)
        keyboard.row(*purposes2)
        await message.answer("Выберите, что вы хотите сделать?", reply_markup=keyboard)
        await Order.waiting_for_purpose.set()
    elif role == 3:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        purposes = ["Подать заявку", "Посмотреть мои заявки"]
        keyboard.add(*purposes)
        await message.answer("Выберите, что вы хотите сделать?", reply_markup=keyboard)
        await Order.waiting_for_purpose.set()


@dp.message_handler(state=Order.waiting_for_purpose)
async def get_purpose(message: types.Message, state: FSMContext):
    # проверка на дурака
    if message.text not in ["Подать заявку",
                            "Посмотреть мои поданные заявки", "Посмотреть мои заявки",
                            "Биржа заявок",
                            "Посмотреть мои выполняемые заявки"]:
        await message.answer("Пожалуйста, используйте клавиатуру.\nЧто я могу сделать?")
        return

    # для норм пользователей
    if message.text == "Подать заявку":
        globalReasons = my_requests.getGlobalReasons(message.from_user.username)
        await state.update_data(availableGlobalReasons=globalReasons)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for globalReason in globalReasons:
            keyboard.add(globalReason[0])
        keyboard.add(BACK)
        await message.answer("Что у вас случилось?", reply_markup=keyboard)
        await Order.waiting_for_1st_reason.set()
    if message.text == "Посмотреть мои заявки" or message.text == "Посмотреть мои поданные заявки":
        reqs = my_requests.getMyRequests(message.from_user.username)

        length = len(reqs)
        pages = math.ceil(length / 5)  # округляем в большую сторону
        page = 1
        wlist = "my"

        # заносим в state данные
        await state.update_data(page=1)  # о текущей странице
        await state.update_data(pages=pages)  # о количстве страниц
        await state.update_data(reqs=reqs)  # о заявках
        await state.update_data(wlist=wlist)  # какой именно список

        keyboard = utils.form_keyboard(page, pages, length, None)
        toSend = utils.form_text_list(page, pages, reqs, "my")
        await message.answer(toSend, reply_markup=keyboard)
    if message.text == "Биржа заявок":
        reqs = my_requests.getExchange(message.from_user.username)

        length = len(reqs)
        pages = math.ceil(length / 5)  # округляем в большую сторону
        page = 1
        wlist = "exchange"

        # заносим в state данные
        await state.update_data(page=1)  # о текущей странице
        await state.update_data(pages=pages)  # о количестве страниц
        await state.update_data(reqs=reqs)  # о заявках
        await state.update_data(wlist=wlist)  # какой именно список

        keyboard = utils.form_keyboard(page, pages, length, None)
        toSend = utils.form_text_list(page, pages, reqs, "exchange")
        await message.answer(toSend, reply_markup=keyboard)
    if message.text == "Посмотреть мои выполняемые заявки":
        reqs = my_requests.getReqsToDo(message.from_user.username)

        length = len(reqs)
        pages = math.ceil(length / 5)  # округляем в большую сторону
        page = 1
        wlist = "todo"

        # заносим в state данные
        await state.update_data(page=1)  # о текущей странице
        await state.update_data(pages=pages)  # о количестве страниц
        await state.update_data(reqs=reqs)  # о заявках
        await state.update_data(wlist=wlist)  # какой именно список

        keyboard = utils.form_keyboard(page, pages, length, None)
        toSend = utils.form_text_list(page, pages, reqs, "todo")
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
        "Пожалуйста, опишите свою проблему более детально.\nМожете прикрепить ужатое изображение (не обязательно).",
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
    headers = {"telegram": message.from_user.username}

    # без ключа картинки запрос проходит
    # с ключом, но без картинки запрос тоже проходит
    # description - обязателен - строка

    r = requests.post(my_requests.url + "request",
                      data={"description": description, "reason": reason},
                      headers=headers,
                      files=files)

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


# обрабатываем прилетающие callback'и

# перелистывание списка заявок
@dp.callback_query_handler(lambda c: c.data == 'left' or c.data == 'right', state=Order.waiting_for_purpose)
async def another_page(c: types.CallbackQuery, state: FSMContext):
    temp = await state.get_data()
    page = temp.get("page")
    pages = temp.get("pages")
    reqs = temp.get("reqs")
    wlist = temp.get("wlist")
    length = len(reqs)

    toSend = None
    if c.data == 'left':
        await state.update_data(page=page - 1)
        toSend = utils.form_text_list(page - 1, pages, reqs, wlist)
    elif c.data == 'right':
        await state.update_data(page=page + 1)
        toSend = utils.form_text_list(page + 1, pages, reqs, wlist)

    keyboard = utils.form_keyboard(page, pages, length, c)

    await bot.edit_message_text(text=toSend,
                                message_id=c.message.message_id,
                                inline_message_id=c.message.message_id,
                                chat_id=c.message.chat.id,
                                reply_markup=keyboard)
    # отвечаем на callback, чтобы часики перестали тикать
    await bot.answer_callback_query(callback_query_id=c.id)


# показ конкретной заявки
@dp.callback_query_handler(lambda c: c.data.startswith('show'), state=Order.waiting_for_purpose)
async def show_more(c: types.CallbackQuery, state: FSMContext):
    # первое, что нужно знать - tg_id
    tg_id = c.data.split("_")[1]
    # получаем инфу с state
    temp = await state.get_data()
    reqs = temp.get("reqs")
    wlist = temp.get("wlist")
    # получаем оригинальный id
    orig_id = utils.getIdByTgId(reqs, tg_id)
    # делаем запрос с этим id
    info = my_requests.getRequest(c.from_user.username, orig_id)
    # формируем текст сообщения
    caption, image = utils.form_text_req(info, tg_id)
    # формируем кнопки
    keyboard = utils.form_req_keyboard(wlist, tg_id)

    # отправляем сообщение
    if image is None:
        await bot.send_message(c.message.chat.id, caption, reply_markup=keyboard)
    else:
        await bot.send_photo(c.message.chat.id, image, caption, reply_markup=keyboard)
    await bot.answer_callback_query(callback_query_id=c.id)


# 5 обработчиков для callback'ов

# omg im so sorry i have many same functions
# im so lazy to fix it

@dp.callback_query_handler(lambda c: c.data.startswith('appoint'), state=Order.waiting_for_purpose)
async def appoint(c: types.CallbackQuery, state: FSMContext):
    # получаем tg_id заявки, которую хотим принять
    tg_id = c.data.split("_")[1]
    # получаем инфу с state для получеия оригинального id
    temp = await state.get_data()
    reqs = temp.get("reqs")
    # получаем оригинальный id
    orig_id = utils.getIdByTgId(reqs, tg_id)
    # получаем подробную инфу о пользователе, которому хотим назначить заявку (т.е. себе)
    toUser = my_requests.getMe(c.from_user.username)
    # делаем запрос на принятие заявки
    response = my_requests.appoint(c.from_user.username, orig_id, toUser)
    # если запрос прошёл успешно, то перерисовываем сообщение
    if response.ok:
        # нужно сформировать новый текст сообщения, в котором будет обновлённый статус
        info = my_requests.getRequest(c.from_user.username, orig_id)
        caption, image = utils.form_text_req(info, tg_id)
        # редактируем сообщение
        if image is None:
            await bot.edit_message_text(text=caption,
                                        message_id=c.message.message_id,
                                        inline_message_id=c.message.message_id,
                                        chat_id=c.message.chat.id,
                                        reply_markup=None)
        else:
            await bot.edit_message_caption(caption=caption,
                                           message_id=c.message.message_id,
                                           inline_message_id=c.message.message_id,
                                           chat_id=c.message.chat.id,
                                           reply_markup=None)
        await bot.send_message(c.message.chat.id, "Заявка перенесена в раздел выполняемых")
    else:
        print("???")

    await bot.answer_callback_query(callback_query_id=c.id)


@dp.callback_query_handler(lambda c: c.data.startswith('perform'), state=Order.waiting_for_purpose)
async def perform(c: types.CallbackQuery, state: FSMContext):
    # получаем tg_id заявки, которую хотим пометить выполненной
    tg_id = c.data.split("_")[1]
    # получаем инфу с state для получеия оригинального id
    temp = await state.get_data()
    reqs = temp.get("reqs")
    # получаем оригинальный id
    orig_id = utils.getIdByTgId(reqs, tg_id)
    # делаем запрос на отметку
    response = my_requests.perform(c.from_user.username, orig_id)
    # если запрос прошёл успешно, то перерисовываем сообщение
    if response.ok:
        # нужно сформировать новый текст сообщения, в котором будет обновлённый статус
        info = my_requests.getRequest(c.from_user.username, orig_id)
        caption, image = utils.form_text_req(info, tg_id)
        # редактируем сообщение
        if image is None:
            await bot.edit_message_text(text=caption,
                                        message_id=c.message.message_id,
                                        inline_message_id=c.message.message_id,
                                        chat_id=c.message.chat.id,
                                        reply_markup=None)
        else:
            await bot.edit_message_caption(caption=caption,
                                           message_id=c.message.message_id,
                                           inline_message_id=c.message.message_id,
                                           chat_id=c.message.chat.id,
                                           reply_markup=None)
        await bot.send_message(c.message.chat.id, "Заявка помечена выполненной")
    else:
        print("???")

    await bot.answer_callback_query(callback_query_id=c.id)


@dp.callback_query_handler(lambda c: c.data.startswith('approve'), state=Order.waiting_for_purpose)
async def approve(c: types.CallbackQuery, state: FSMContext):
    # получаем tg_id заявки, которую хотим закрыть
    tg_id = c.data.split("_")[1]
    # получаем инфу с state для получеия оригинального id
    temp = await state.get_data()
    reqs = temp.get("reqs")
    # получаем оригинальный id
    orig_id = utils.getIdByTgId(reqs, tg_id)
    # делаем запрос на завершение
    response = my_requests.approve(c.from_user.username, orig_id)
    # если запрос прошёл успешно, то перерисовываем сообщение
    if response.ok:
        # нужно сформировать новый текст сообщения, в котором будет обновлённый статус
        info = my_requests.getRequest(c.from_user.username, orig_id)
        caption, image = utils.form_text_req(info, tg_id)
        # редактируем сообщение
        if image is None:
            await bot.edit_message_text(text=caption,
                                        message_id=c.message.message_id,
                                        inline_message_id=c.message.message_id,
                                        chat_id=c.message.chat.id,
                                        reply_markup=None)
        else:
            await bot.edit_message_caption(caption=caption,
                                           message_id=c.message.message_id,
                                           inline_message_id=c.message.message_id,
                                           chat_id=c.message.chat.id,
                                           reply_markup=None)
        await bot.send_message(c.message.chat.id, "Заявка успешно закрыта")
    else:
        print(response)

    await bot.answer_callback_query(callback_query_id=c.id)


@dp.callback_query_handler(lambda c: c.data.startswith('refuse'), state=Order.waiting_for_purpose)
async def refuse(c: types.CallbackQuery, state: FSMContext):
    # получаем tg_id заявки, от которой хотим отказаться
    tg_id = c.data.split("_")[1]
    # получаем инфу с state для получеия оригинального id
    temp = await state.get_data()
    reqs = temp.get("reqs")
    # получаем оригинальный id
    orig_id = utils.getIdByTgId(reqs, tg_id)
    # делаем запрос на отказ
    response = my_requests.refuse(c.from_user.username, orig_id)
    # если запрос прошёл успешно, то перерисовываем сообщение
    if response.ok:
        # нужно сформировать новый текст сообщения, в котором будет обновлённый статус
        info = my_requests.getRequest(c.from_user.username, orig_id)
        caption, image = utils.form_text_req(info, tg_id)
        # редактируем сообщение
        if image is None:
            await bot.edit_message_text(text=caption,
                                        message_id=c.message.message_id,
                                        inline_message_id=c.message.message_id,
                                        chat_id=c.message.chat.id,
                                        reply_markup=None)
        else:
            await bot.edit_message_caption(caption=caption,
                                           message_id=c.message.message_id,
                                           inline_message_id=c.message.message_id,
                                           chat_id=c.message.chat.id,
                                           reply_markup=None)
        await bot.send_message(c.message.chat.id, "Вы отказались от заявки.\nЗаявка перенесена обратно в биржу.")
    else:
        print(response)

    await bot.answer_callback_query(callback_query_id=c.id)


@dp.callback_query_handler(lambda c: c.data.startswith('rollback'), state=Order.waiting_for_purpose)
async def rollback(c: types.CallbackQuery, state: FSMContext):
    # получаем tg_id заявки, которую хотим откатить
    tg_id = c.data.split("_")[1]
    # получаем инфу с state для получеия оригинального id
    temp = await state.get_data()
    reqs = temp.get("reqs")
    # получаем оригинальный id
    orig_id = utils.getIdByTgId(reqs, tg_id)
    # делаем запрос на откат
    response = my_requests.rollback(c.from_user.username, orig_id)
    # если запрос прошёл успешно, то перерисовываем сообщение
    if response.ok:
        # нужно сформировать новый текст сообщения, в котором будет обновлённый статус
        info = my_requests.getRequest(c.from_user.username, orig_id)
        caption, image = utils.form_text_req(info, tg_id)
        # редактируем сообщение
        if image is None:
            await bot.edit_message_text(text=caption,
                                        message_id=c.message.message_id,
                                        inline_message_id=c.message.message_id,
                                        chat_id=c.message.chat.id,
                                        reply_markup=None)
        else:
            await bot.edit_message_caption(caption=caption,
                                           message_id=c.message.message_id,
                                           inline_message_id=c.message.message_id,
                                           chat_id=c.message.chat.id,
                                           reply_markup=None)
        await bot.send_message(c.message.chat.id, "Вы откатили заявку.")
    else:
        print(response)

    await bot.answer_callback_query(callback_query_id=c.id)

executor.start_polling(dp)
