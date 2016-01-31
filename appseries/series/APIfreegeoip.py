import json
import threading
import requests

from series.models import CachedLocation

def requestGeoIp(IP):
    response = requests.get("https://freegeoip.net/json/" + IP)

    if (response.status_code == 200):
        data = json.loads(response.text.encode('utf-8'))
        return data
    else:
        return None

def resolveLocation(ipAddress):
    try:
        query = CachedLocation.objects.get(ip=ipAddress)
        return json.loads(query.location)
    except CachedLocation.DoesNotExist:
        jsResult = requestGeoIp(ipAddress)
        cachedLoc = CachedLocation(ip=ipAddress, location=json.dumps(jsResult))
        cachedLoc.save()
        return jsResult

def getLocationByList(IPList):
    numThreads = 4
    ipPerThread = len(IPList)/numThreads
    threadList = []
    IPInfo = []

    def runOnThread(smallIpList, resultList):
        temp = []

        for ip in smallIpList:
            info = resolveLocation(ip)
            temp.append(info)

        resultList.extend(temp)

    for i in xrange(1, numThreads):
        splitIpList = map(lambda ip: ip.ip, IPList[(i-1)*ipPerThread:i*ipPerThread])
        t = threading.Thread(target=runOnThread, args=(splitIpList, IPInfo))
        t.start()
        threadList.append(t)

    for t in threadList:
        t.join()

    return filter(lambda x: x is not None, IPInfo)
