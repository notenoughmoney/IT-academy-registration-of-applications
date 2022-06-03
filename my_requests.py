import requests
import json

url = "http://tucana.org:3100/api/"

# получпем роль пользователя
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

# получить все заявки ПОЛЬЗОВАТЕЛЯ
def getMyRequests(username):
    r = requests.get(f"{url}request/my", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    for index, req in enumerate(toSend, 1):
        req["tg_id"] = index
    toSend.reverse()  # отсортировали по времени
    return toSend

# получить конкретную завку ПОЛЬЗОВАТЕЛЯ
def getMyRequest(username, id):
    r = requests.get(f"{url}request/{id}", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    return toSend

"""""""""""""""""""""""""""""
ДОСТУПНЫ ТОЛЬКО СПЕЦИАЛИСТАМ
"""""""""""""""""""""""""""""

# получить доступные заявки с биржи
def getExchange(username):
    r = requests.get(f"{url}request/exchange", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    for index, req in enumerate(toSend, 1):
        req["tg_id"] = index
    toSend.reverse()  # отсортировали по времени
    return toSend