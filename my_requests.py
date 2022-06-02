import requests
import json


def getRoleByUsername(username):
    r = requests.get("https://req.tucana.org/api/auth", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    return temp.get("workgroup").get("role").get("id")


def getGlobalReasons(username):
    r = requests.get("https://req.tucana.org/api/reasons", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = []
    for item in temp.get("globalReasons"):
        toSend.append([item.get("name"), item.get("id")])
    return toSend


def getSubReasons(username, name):
    r = requests.get("https://req.tucana.org/api/reasons", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = []
    for item in temp.get("globalReasons"):
        if item.get("name") == name:
            for item1 in item.get("requestReasons"):
                toSend.append([item1.get("name"), item1.get("id")])
            break
    return toSend


def getMyRequests(username):
    r = requests.get("https://req.tucana.org/api/request/my", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    toSend.reverse()  # отсортировали по времени
    for index, req in enumerate(toSend, 1):
        req["tg_id"] = index
    return toSend

def getMyRequest(username, id):
    r = requests.get(f"https://req.tucana.org/api/request/{id}", headers={"telegram": username})
    temp = json.loads(r.content.decode("utf-8"))
    toSend = temp
    return toSend
