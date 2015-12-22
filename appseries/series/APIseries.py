from xml.etree import ElementTree as ET
import requests
import sys

def getSeries(name):

    response = requests.get("http://www.thetvdb.com/api/GetSeries.php?seriesname="+name+"&language=es")

    if (response.status_code == 200):
        data = ET.fromstring(response.text.encode('utf-8'))
        return data

