import requests
import json

url = "http://tucana.org:3100/api/"


# получаем роль пользователя
def getRoleByUsername(username):
    r = requests.get(f"{url}auth", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    return temp.get("workgroup").get("role").get("id")


# получить глобальные причины
def getGlobalReasons(username):
    r = requests.get(f"{url}reasons", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = []
    for item in temp.get("globalReasons"):
        toSend.append([item.get("name"), item.get("id")])
    return toSend


# получить подпричины
def getSubReasons(username, name):
    r = requests.get(f"{url}reasons", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = []
    for item in temp.get("globalReasons"):
        if item.get("name") == name:
            for item1 in item.get("requestReasons"):
                toSend.append([item1.get("name"), item1.get("id")])
            break
    return toSend


# получить конкретную завку
def getRequest(username, id):
    r = requests.get(f"{url}request/{id}", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    return toSend


# получить все заявки пользователя
def getMyRequests(username):
    r = requests.get(f"{url}request/my", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    for index, req in enumerate(toSend, 1):
        req["tg_id"] = index
    toSend.reverse()  # отсортировали по времени
    return toSend


# получить все доступные заявки с биржи
def getExchange(username):
    r = requests.get(f"{url}request/exchange", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    for index, req in enumerate(toSend, 1):
        req["tg_id"] = index
    toSend.reverse()  # отсортировали по времени
    return toSend


# получить все заявки к выполнению
def getReqsToDo(username):
    r = requests.get(f"{url}request/myWork", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    for index, req in enumerate(toSend, 1):
        req["tg_id"] = index
    toSend.reverse()  # отсортировали по времени
    return toSend


def getMe(username):
    r = requests.get(f"{url}auth", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    # урезаем данные
    temp.pop("email")
    temp.pop("workgroup")
    toSend = {'user': temp}
    return toSend


# 1 - Закрытие заявки пользователем
def approve(username, id):
    r = requests.patch(f"{url}request/{id}/approve", headers={"telegram": username})
    return r

# 2 - Откат заявки пользователем
def rollback(username, id):
    r = requests.patch(f"{url}request/{id}/rollback", headers={"telegram": username})
    return r

# 3 - назначить заявку специалисту
def appoint(username, id, toUser):
    r = requests.patch(f"{url}request/{id}/appoint", json=toUser, headers={"telegram": username})
    return r

# 4 - Выполнение заявки специалистом
def perform(username, id):
    r = requests.patch(f"{url}request/{id}/perform", headers={"telegram": username})
    return r

# 5 - Отказ специалиста от заявки
def refuse(username, id):
    r = requests.patch(f"{url}request/{id}/refuse", headers={"telegram": username})
    return r