from xml.etree import ElementTree as ET
from lxml import objectify
import requests


class APIseries:

	def __init__ (self):
		self.APIKEY = "EB224CCBC0C8E52F"

	def getTextValue(self, node):
		if node:
			return node.text
		else:
			return None

	def getStructuredSeries(self, name):
		resp = requests.get("http://www.thetvdb.com/api/GetSeries.php?seriesname="+name+"&language=en")
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

	def getDictSerie(self, ID):
		resp = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/series/"+ID+"/en.xml")
		if resp.status_code == 200:
			root = objectify.fromstring(resp.content)
			serieItem = root.Series
			serie = {}

			serie['title'] = self.getTextValue(serieItem.find("SeriesName"))
			banner = self.getTextValue(serieItem.find("banner"))
			if not banner:
				serie['banner'] = "https://i.imgur.com/VMLDXzQ.jpg" # Not available banner
			else:
				serie['banner'] = "https://thetvdb.com/banners/" + banner
			serie['overview'] = self.getTextValue(serieItem.find("Overview"))
			serie['apiId'] = ID

			airsday = self.getTextValue(serieItem.find("Airs_DayOfWeek"))
			if not airsday:
				serie['Airs_DayOfWeek'] = 'None'
			else:
				serie['Airs_DayOfWeek'] = airsday

			genres = self.getTextValue(serieItem.find("Genre")).split("|")
			if not genres:
				serie['genre'] = "None"
			else:
				temp = ""
				for g in genres:
					if g:
						temp = temp + g + ", "
				serie['genre'] = temp[:-2]

			serie['status'] = self.getTextValue(serieItem.find("Status"))

			return serie

		else:
			return None

	def getDictEpisode(self, id):
		resp = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/episodes/"+id+"/en.xml")
		if resp.status_code == 200:
			root = objectify.fromstring(resp.content)
			episodeItem = root.Episode
			episode = {}

			title = self.getTextValue(episodeItem.find("EpisodeName"))
			if not title:
				episode['titulo'] = "None"
			else:
				episode['titulo'] = title

		else:
			return None

	def getSeries(self, name):

		response = requests.get("http://www.thetvdb.com/api/GetSeries.php?seriesname="+name+"&language=en")

		if (response.status_code == 200):
			data = ET.fromstring(response.content)
			return data

	def getSeriesByRemoteID(self, ID):

		response = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/series/"+ID+"/en.xml")

		if (response.status_code == 200):
			data = ET.fromstring(response.content)
			return data

	def getEpisodes(self, ID):

		response = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/series/"+ID+"/all/en.xml")

		if (response.status_code == 200):
			data = ET.fromstring(response.content)
			return data

	def getStructuredEpisodes(self, ID):
		resp = requests.get("http://www.thetvdb.com/api/"+self.APIKEY+"/series/"+ID+"/all/en.xml")
		if resp.status_code == 200:
			episodes = []
			root = objectify.fromstring(resp.content)
			for e in root.iterchildren():
				title = self.getTextValue(e.find("EpisodeName"))
				season = self.getTextValue(e.find("SeasonNumber"))
				number = self.getTextValue(e.find("EpisodeNumber"))
				episodeId = self.getTextValue(e.find("id"))

				# Siempre hay capitulos que les falta alguno de los datos
				# Si un capitulo no tiene alguno de estos campos, se ignora!
				if not title or not season or not number:
					continue

				episodes.append((episodeId, title, season, number))
			return episodes

		else:
			return None


