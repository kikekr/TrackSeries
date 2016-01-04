import json
import requests

def getLocationByIP(IP):
    response = requests.get("https://freegeoip.net/json/" + IP)

    if (response.status_code == 200):
        data = json.loads(response.text.encode('utf-8'))
        return data
    else:
        return None
