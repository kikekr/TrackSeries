# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

import requests
from series.APIseries import APIseries
import series.crontab as crontab
from lxml import objectify

class Serie(models.Model):
	id = models.AutoField(primary_key=True)
	theTvdbID = models.IntegerField()
	nombre = models.CharField(max_length=100)
	descripcion = models.CharField(max_length=500)
	imagen = models.CharField(max_length=100)
	genero = models.CharField(max_length=100)
	fechaEmision = models.CharField(max_length=100, default="Fecha de emision")
	estado = models.CharField(max_length=100)
	tiempoAnalisis = models.IntegerField()
	numeroTorrents = models.IntegerField()
	limiteSubida = models.IntegerField()
	limiteBajada = models.IntegerField()

	def __unicode__(self):
		return self.nombre

	def __update__(self):
		api = APIseries()

		# Actualizar serie
		data = api.getDictSerie(self.theTvdbID)
		self.nombre = data['title']
		self.descripcion = data['overview']
		self.imagen = data['banner']
		self.genero = data['genre']
		self.fechaEmision = data['Airs_DayOfWeek']
		self.estado = data['status']
		self.save()

		# Actualizar todos los capítulos de esta serie
		structuredEpisodes = api.getStructuredEpisodes(self.theTvdbID)
		for episodeId, title, season, number, airdate in structuredEpisodes:
			try:
				c = Capitulo.objects.get(theTvdbID=episodeId)
				param = {"titulo": title, "airdate": airdate}
				c.__update__(data=param)
			except Capitulo.DoesNotExist:
				c = Capitulo(serie=self, theTvdbID=episodeId, temporada=season, numero=number, titulo=title, estado=-1, airDate=airdate)
				c.save()
			crontab.setAnalysisSchedule(c)
		crontab.saveTempChanges(crontab.path)

class Capitulo(models.Model):
	theTvdbID = models.IntegerField()
	serie = models.ForeignKey(Serie)
	temporada = models.IntegerField()
	numero = models.IntegerField()
	titulo = models.CharField(max_length=100)
	airDate = models.IntegerField()
	"""
	El estado se usa para indicar en qué estado se encuentra la recolección de datos a través de la descarga
	   -1: No hay análisis disponible
	   -2: Análisis completo
	0-100: Progreso del análisis
	"""
	estado = models.IntegerField()

	def __unicode__(self):
		return self.titulo

	def __update__(self, data=None):
		if not data:
			api = APIseries()
			data = api.getDictEpisode(self.theTvdbID)
		self.titulo = data['titulo']
		self.airDate = data['airdate']
		self.save()


class IPDescarga(models.Model):
	capitulo = models.ForeignKey(Capitulo)
	ip = models.CharField(max_length=15)
	hora = models.IntegerField()

class CachedLocation(models.Model):
	ip = models.CharField(primary_key=True, max_length=15)
	location = models.CharField(max_length=15)

class UserSerie(models.Model):
	user = models.ForeignKey(User)
	serie = models.ForeignKey(Serie)

def dailyUpdate():
	url = "http://www.thetvdb.com/api/EB224CCBC0C8E52F/updates/updates_day.xml"
	resp = requests.get(url)

	updates = objectify.fromstring(resp.content)
	updatedSeries = [int(serie.id) for serie in updates.Series]
	updatedEpisodes = [int(episode.id) for episode in updates.Episode]

	localSeries = Serie.objects.all()
	for serie in localSeries:
		if serie.theTvdbID in updatedSeries:
			serie.__update__()

	localEpisodes = Capitulo.objects.all()
	for episode in localEpisodes:
		if episode.theTvdbID in updatedEpisodes:
			episode.__update__()
			crontab.setAnalysisSchedule(episode)

	crontab.saveTempChanges(crontab.path)
