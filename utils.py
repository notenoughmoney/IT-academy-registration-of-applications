import requests
import json

def column(matrix, i): return [row[i] for row in matrix]

def getRoleByUsername(username):
    r = requests.get("https://req.tucana.org/api/auth", headers={"telegram":username})
    temp = json.loads(r.content.decode("utf-8"))
    return temp.get("workgroup").get("role").get("id")

def getGlobalReasons(username):
    r = requests.get("https://req.tucana.org/api/reasons", headers={"telegram":username})
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

def getReasonId(array, text):
    for item in array:
        if item[0] == text:
            return item[1]