from xml.etree import ElementTree as ET
import requests
import sys

class APIfreegeoip:
        
	def getLocationByIP(self, IP):

		response = requests.get("https://freegeoip.net/xml/" + IP)

		if (response.status_code == 200):
			data = ET.fromstring(response.text.encode('utf-8'))
			return data
