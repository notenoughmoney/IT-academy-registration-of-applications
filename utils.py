import requests
import json

def getRoleByUsername(username):
    r = requests.get("https://req.tucana.org/api/auth", headers={"telegram":username})
    temp = json.loads(r.content.decode("utf-8"))
    return temp.get("workgroup").get("role").get("id")