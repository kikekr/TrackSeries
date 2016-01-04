from xml.etree import ElementTree as ET
import requests
import sys
from APIseries import APIseries
from APIfreegeoip import getLocationByIP
from django.shortcuts import render, redirect
from series.models import Capitulo, IPDescarga, Serie
from django import forms
from django.db.models import Max
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect


def novedades(request):

	#Obtenemos la lista de series suscritas
	series_list = Serie.objects.all()
	apiSeries = APIseries()

	#Para cada serie comprobamos la lista de capitulos en la BD y en TheTvdb
	for serie in series_list:
		dataEpisodes = apiSeries.getEpisodes(serie.theTvdbID).findall('Episode')
		dataBaseEpisodes = serie.capitulo_set.all()

		# print 'Episodios en TheTvdb: ' + str(len(dataEpisodes))
		# print 'Episodios en la base de datos: ' + str(len(dataBaseEpisodes))

		#Comprobamos el numero de episodios
		if len(dataEpisodes) == len(dataBaseEpisodes):
			print 'La serie ' + serie.nombre + ' esta actualizada'
		else:
			print 'La serie ' + serie.nombre + ' esta desactualizada'

			# Actualizar la base de datos
			# Descargar los ficheros torrent de los episodios nuevos

	return render(request, 'series/novedades.html')


def addSerie(request, identifier):
	series_list = Serie.objects.all()
	api = APIseries()

	data = api.getSeriesByRemoteID(identifier)
	dataEpisodes = api.getEpisodes(identifier)

	for serie in data.findall('Series'):
		name = serie.find('SeriesName').text
		airsday = serie.find('Airs_DayOfWeek').text
		description = serie.find('Overview').text
		image = serie.find('banner').text
		genre = serie.find('Genre').text
		status = serie.find('Status').text

		if name is None:
			name = 'None'
		if airsday is None:
			airsday = 'None'
		if description is None:
			description = 'None'
		if image is None:
			image = 'None'
		if genre is None:
			genre = 'None'
		if status is None:
			status = 'None'

	try :
		p = Serie.objects.get(nombre = data[0][16].text)
		context = {'title' : 'Inicio', 'ID': identifier, 'nombre': name, 'series_list': series_list, 'existe': 'true'}

	except Serie.DoesNotExist :

		context = {'title' : 'Inicio', 'ID': identifier, 'nombre': name, 'series_list': series_list}
		s = Serie(nombre = name, theTvdbID = identifier, descripcion = description, imagen = image, genero = genre, fechaEmision = airsday, estado = status)
		s.save()

		for episode in dataEpisodes.findall('Episode'):

			episodename = episode.find('EpisodeName').text
			episodenumber = episode.find('EpisodeNumber').text
			seasonnumber = episode.find('SeasonNumber').text

			if episodename is None:
					episodename = 'None'
			if episodenumber is None:
					episodenumber = 9999
			if seasonnumber is None:
					seasonnumber = 9999

			s.capitulo_set.create(temporada = seasonnumber, numero = episodenumber, titulo = episodename, estado = 0)

	return render(request, 'series/serieanadida.html', context)


def nuevaSerie(request):

	series = Serie.objects.all()
	context = {'title' : 'Inicio', 'series': series, 'request' : request}
	nameserie = ''
	api = APIseries()

	if request.POST.has_key('myS'):
			nameserie = request.POST['myS']
			data = api.getSeries(nameserie)

			if len(data) > 0:
				context = {'title' : 'Inicio', 'data': data, 'series': series, 'request' : request}

	return render(request, 'series/NuevaSerie.html', context)

def serie(request, selectedId):
	series = Serie.objects.all()

	try:
		show = Serie.objects.get(id=int(selectedId))
		countSeasons = Capitulo.objects.filter(serie=int(selectedId)).aggregate(count=Max('temporada'))['count']

		if countSeasons:
			seasons = {}
			for i in xrange(1, int(countSeasons)):
				seasons[i] = Capitulo.objects.filter(serie=int(selectedId), temporada=i)
			context = {'title' : show.nombre, 'show' : show, "seasons": seasons, 'series': series, 'request' : request}

		else:
			context = {'title' : show.nombre, 'show' : show, 'series': series, 'request' : request}

	except Serie.DoesNotExist:
		context = {'title' : "Not found", 'series': series, 'request' : request}

	return render(request, 'series/serie.html', context)

def index(request):
	series = Serie.objects.all()
	context = {'title' : 'Inicio', 'request' : request, 'series': series}

	if request.user.is_authenticated():
		return render(request, 'series/index-auth.html', context)
	else:
		return render(request, 'series/index-noauth.html', context)

def estadisticas(request, showId, seasonId, episodeId):
	series = Serie.objects.all()

	try:
		show = Serie.objects.get(id=int(showId))
		episode = Capitulo.objects.get(serie=int(showId), temporada=int(seasonId), numero=int(episodeId))
		ips = IPDescarga.objects.filter(capitulo=episode.id)

		ipinfo = []
		for ip in ips:
			ipinfo.append(getLocationByIP(ip.ip))

		context = {'title' : show.nombre, 'show' : show, 'episode': episode, 'ipinfo': ipinfo, 'series': series, 'request' : request}

	except Serie.DoesNotExist:
		context = {'title' : "Not found", 'series': series, 'request' : request}
	except Capitulo.DoesNotExist:
		context = {'title' : "Not found", 'series': series, 'request' : request}

	return render(request, 'series/estadisticas.html', context)

def eliminar(request, selectedId):
	series = Serie.objects.all()

	try:
		show = Serie.objects.get(id=int(selectedId))

		if request.POST.has_key('butAceptar'):
			show.delete()

			return redirect('index')
		elif request.POST.has_key('butCancelar'):
			return redirect('index')
		else:
			page = 'series/eliminar.html'
			context = {'title' : show.nombre, 'show' : show, 'series': series, 'request' : request}

	except Serie.DoesNotExist:
		page = 'series/serie.html'
		context = {'title' : "Not found", 'series': series, 'request' : request}

	return render(request, page, context)

def register(request):
    context = { 'form' : UserCreationForm() }

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/series/?newuser=" + new_user.username)
        else:
            context['error'] = form.error_messages

    return render(request, "registration/register.html", context)
