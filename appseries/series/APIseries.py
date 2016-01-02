from xml.etree import ElementTree as ET
import requests
import sys

class APIseries:
	
	
	def __init__ (self):	
		self.APIKEY = "EB224CCBC0C8E52F"
        
	def getSeries(self, name):

		response = requests.get("http://www.thetvdb.com/api/GetSeries.php?seriesname="+name+"&language=es")

		if (response.status_code == 200):
			data = ET.fromstring(response.text.encode('utf-8'))
			return data
			
	def getSeriesByRemoteID(self, ID):
		
		response = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/series/"+ID+"/es.xml")
		
		if (response.status_code == 200):
			data = ET.fromstring(response.text.encode('utf-8'))
			return data
			
	def getEpisodes(self, ID):
		
		response = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/series/"+ID+"/all/es.xml")
		
		if (response.status_code == 200):
			data = ET.fromstring(response.text.encode('utf-8'))
			return data


