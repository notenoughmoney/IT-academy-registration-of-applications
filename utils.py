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


def form_text(page, pages, reqs):
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


