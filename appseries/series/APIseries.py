from xml.etree import ElementTree as ET
from lxml import objectify
import requests
import sys

class APIseries:


	def __init__ (self):
		self.APIKEY = "EB224CCBC0C8E52F"

	def getTextValue(self, node):
		if node:
			return node.text
		else:
			return None

	def getStructuredSeries(self, name):
		resp = requests.get("http://www.thetvdb.com/api/GetSeries.php?seriesname="+name+"&language=es")
		if resp.status_code == 200:
			series = []
			root = objectify.fromstring(resp.content)
			for s in root.iterchildren():
				title = self.getTextValue(s.find("SeriesName"))
				banner = self.getTextValue(s.find("banner"))
				if not banner:
					banner = "https://i.imgur.com/VMLDXzQ.jpg" # Not available banner
				else:
					banner = "https://thetvdb.com/banners/" + banner
				overview = self.getTextValue(s.find("Overview"))
				apiId = self.getTextValue(s.find("seriesid"))
				series.append((title, banner, overview, apiId))
			return series

		else:
			return None

	def getSeries(self, name):

		response = requests.get("http://www.thetvdb.com/api/GetSeries.php?seriesname="+name+"&language=es")

		if (response.status_code == 200):
			data = ET.fromstring(response.content)
			return data

	def getSeriesByRemoteID(self, ID):

		response = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/series/"+ID+"/es.xml")

		if (response.status_code == 200):
			data = ET.fromstring(response.content)
			return data

	def getEpisodes(self, ID):

		response = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/series/"+ID+"/all/es.xml")

		if (response.status_code == 200):
			data = ET.fromstring(response.content)
			return data


