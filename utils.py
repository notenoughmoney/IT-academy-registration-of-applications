from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def column(matrix, i): return [row[i] for row in matrix]

def getReasonId(array, text):
    for item in array:
        if item[0] == text:
            return item[1]

def getReasonText(array, id):
    for item in array:
        if item[1] == id:
            return item[0]

def getRequestByTgId(array, id):
    for item in array:
        if item["tg_id"] == id:
            return item

def getIdByTgId(array, tg_id):
    for item in array:
        if item.get("tg_id") == int(tg_id):
            return item.get("id")


def form_text_req(info, tg_id):
    text = f"ID: {tg_id}\n"
    text += f"Заявка: {info.get('specific_name')}\n"
    text += f"Описание: {info.get('messages')[0].get('text')}\n"
    text += f"Дата: {info.get('date')[0:10]} {info.get('date')[11:16]} \n"
    text += f"Статус: {info.get('stage').get('name')}\n"
    return text


def form_text_list(page, pages, reqs):
    text = "Ваши заявки:\n\n"
    text += f"Страница {page} из {pages}\n\n"
    i = (page - 1) * 5 + 1
    while i < page * 5 + 1:
        req = getRequestByTgId(reqs, i)
        if req is None:
             break
        else:
            text += f"{i}.\n" \
                    f"Заявка: {req.get('specific_name')}\n" \
                    f"Дата: {req.get('date')[0:10]} {req.get('date')[11:16]} \n" \
                    f"Статус: {req.get('stage').get('name')} \n\n"
        i += 1
    return text


def form_keyboard(c, page, pages, length):
    btnArray = [None] * 5
    btn_left = None
    btn_right = None

    if c is None:
        # сначала кнопки, привязанные к заявкам
        for i in range(5):
            btnArray[i] = InlineKeyboardButton(f"{i + 1}", callback_data=f"show_{i + 1}") if (length >= i + 1) else None
        # потом кнопку вправо
        btn_right = InlineKeyboardButton(">", callback_data="right") if (page < pages) else None
    elif c.data == 'left':
        btn_left = InlineKeyboardButton("<", callback_data="left") if (page - 1 > 1) else None
        btn_right = InlineKeyboardButton(">", callback_data="right") if (page - 1 < pages) else None
        # сколько заявок доступно на текущей странице
        onPage = 5 if ((page - 1) * 5 <= length) else length % 5
        for i in range(onPage):
            btnArray[i] = InlineKeyboardButton(f"{(page - 2) * 5 + i + 1}", callback_data=f"show_{(page - 2) * 5 + i + 1}")
    elif c.data == 'right':
        btn_left = InlineKeyboardButton("<", callback_data="left") if (page + 1 > 1) else None
        btn_right = InlineKeyboardButton(">", callback_data="right") if (page + 1 < pages) else None
        # сколько заявок доступно на текущей странице
        onPage = 5 if ((page + 1) * 5 <= length) else length % 5
        for i in range(onPage):
            btnArray[i] = InlineKeyboardButton(f"{page * 5 + i + 1}", callback_data=f"show_{page * 5 + i + 1}")

    # формируем клавиатуру
    keyboard = InlineKeyboardMarkup()
    # кнопки назад и вперёд уже сформированы
    # формириуем массив кнопок, которые отправятсся пользователю
    buttonsToSend = []
    # если кнопка равна None, то не заносим её в массив
    for btn in [btn_left, *btnArray, btn_right]:
        if btn is not None:
            buttonsToSend.append(btn)
    keyboard.row(*buttonsToSend)
    return keyboard

