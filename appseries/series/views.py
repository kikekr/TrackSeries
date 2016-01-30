# -*- coding: utf-8 -*-

from APIseries import APIseries
from APIfreegeoip import getLocationByList
from django.shortcuts import render, redirect
from series.models import Capitulo, IPDescarga, Serie, UserSerie
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
import pandas as pd
from django.contrib import auth
from django.core.management import call_command

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger("django")

def generateContext(request=None, title=None, series=None):
	context = {}
	if request:
		context['request'] = request
	if title:
		context['title'] = title
	if series:
		context['series'] = series
	return context

def getSeriesForUser(request):
	return [userSerie.serie for userSerie in UserSerie.objects.filter(user=auth.get_user(request))]

def addSerie(request, identifier):
	# Comprobar si el usuario esta autenticado
	if not request.user.is_authenticated():
		context = generateContext(request=request, title="Inicio")
		return render(request, 'series/index-noauth.html', context)

	# Comprobar si la serie ya está en la base de datos
	try:
		s = Serie.objects.get(theTvdbID=identifier)
		userSerie = UserSerie.objects.get(serie=s)

		# Si la serie ya existe para ese usuario devolver un error
		series = getSeriesForUser(request)
		context = generateContext(request=request, title="Error al añadir serie", series=series)
		return render(request, 'series/erroranadida.html', context)

	except Serie.DoesNotExist:
		# Si no está -> añadir a la base de datos y al usuario
		api = APIseries()
		data = api.getDictSerie(identifier)

		# Añadir serie a la base de datos
		s = Serie(theTvdbID = identifier, nombre = data['title'], descripcion = data['overview'], imagen = data['banner'], \
			genero = data['genre'], fechaEmision = data['Airs_DayOfWeek'], estado = data['status'], \
			tiempoAnalisis = 24, numeroTorrents = 5, limiteSubida = 64, limiteBajada = 1024)
		s.save()

		# Añadir capítulos a la base de datos
		episodeData = api.getStructuredEpisodes(identifier)
		for episodeId, title, season, number in episodeData:
			s.capitulo_set.create(theTvdbID=episodeId, temporada=season, numero=number, titulo=title, estado=0)

		# Añadir serie al usuario correspondiente
		userSerie = UserSerie(user=auth.get_user(request), serie=s)
		userSerie.save()

	except UserSerie.DoesNotExist:
		# La serie existe en la base de datos, pero no está asociada al usuario
		userSerie = UserSerie(user=auth.get_user(request), serie=s)
		userSerie.save()

	series = getSeriesForUser(request)
	context = generateContext(request=request, title="Serie añadida correctamente", series=series)
	return render(request, 'series/serieanadida.html', context)


def nuevaSerie(request):
	if request.user.is_authenticated():
		seriesByUser = UserSerie.objects.filter(user = auth.get_user(request))
		series = []
		for relation in seriesByUser:
			series.append(relation.serie)

		context = generateContext(title = "Añadir serie", series=series, request=request)
		api = APIseries()

		if request.POST.has_key('myS'):
				nameserie = request.POST['myS']
				tuple_list = api.getStructuredSeries(nameserie)

				if tuple_list and len(tuple_list) > 0:
					context["tuple_list"] = tuple_list

		return render(request, 'series/nuevaserie.html', context)

	else:
		context = generateContext(title = "Añadir serie", request=request)
		return render(request, 'series/index-noauth.html', context)


def actualizar(serie):

	api = APIseries()
	data = api.getDictSerie(str(serie.theTvdbID))

	serie.nombre = data['title']
	serie.fechaemision = data['Airs_DayOfWeek']
	serie.descripcion = data['overview']
	serie.imagen = data['banner']
	serie.genero = data['genre']
	serie.estado = data['status']

	serie.save()

	dataStructuredEpisodes = api.getStructuredEpisodes(str(serie.theTvdbID))
	for title, season, number in dataStructuredEpisodes:
		try:
			episode = Capitulo.objects.get(serie=serie.id, temporada=season, numero=number, titulo = title)

		except Capitulo.DoesNotExist:
			Serie.objects.get(theTvdbID = serie.theTvdbID).capitulo_set.create(temporada = season, numero = number, titulo = title, estado = 0)

	return


def serie(request, selectedId, season=0):
	seriesByUser = UserSerie.objects.filter(user = auth.get_user(request))
	series = []
	for relation in seriesByUser:
		series.append(relation.serie)

	if request.POST.get('butAnalizar') is not None:
		episodeNum = request.POST.get('episodeNum')
		episodeSea = request.POST.get('episodeSea')

		# Error de versiones
		# call_command('startanalysis', selectedId, episodeSea, episodeNum)

	try:
		show = Serie.objects.get(id=int(selectedId))

		if request.POST.get('butActualizar') is not None:
			actualizar(show)

		context = generateContext(request=request, title=show.nombre, series=series)
		context["show"] = show
		allEpisodes = Capitulo.objects.filter(serie=int(selectedId))
		seasonCount = max(allEpisodes, key=lambda x: x.temporada).temporada
		context["seasons"] = range(1, seasonCount+1)
		if season>0:
			context["episodes"] = allEpisodes.filter(temporada=season).order_by("numero")

	except Serie.DoesNotExist:
		context = generateContext(request=request, title="Not found", series=series)

	return render(request, 'series/serie.html', context)

def index(request):
	if request.user.is_authenticated():
		seriesByUser = UserSerie.objects.filter(user = auth.get_user(request))
		series = []
		for relation in seriesByUser:
			series.append(relation.serie)

		return render(request, 'series/index-auth.html', generateContext(request=request, title="Inicio", series=series))

	else:
		return render(request, 'series/index-noauth.html', generateContext(request=request, title="Inicio"))

def estadisticas(request, showId, seasonId, episodeId):
	if request.user.is_authenticated():
		seriesByUser = UserSerie.objects.filter(user = auth.get_user(request))
		series = []
		for relation in seriesByUser:
			series.append(relation.serie)

		try:
			show = Serie.objects.get(id=int(showId))
			episode = Capitulo.objects.get(serie=int(showId), temporada=int(seasonId), numero=int(episodeId))
			ips = IPDescarga.objects.filter(capitulo=episode.id)

			ipinfo = getLocationByList(ips)
			df = pd.DataFrame(ipinfo)
			cnt = df.groupby(by="country_name")['ip'].count()
			logger.info(df.to_string())

			context = generateContext(request=request, title=show.nombre, series=series)
			context["show"] = show
			context["episode"] = episode
			context["cnt_downloads"] = sorted(cnt.iteritems(), key=lambda x: x[1], reverse=True)

		except (Serie.DoesNotExist, Capitulo.DoesNotExist):
			context = generateContext(request=request, title="Not found", series=series)

		return render(request, 'series/estadisticas.html', context)

	else:
		context = {'title' : 'Inicio', 'request' : request}
		return render(request, 'series/index-noauth.html', context)


def edit(request, selectedId):
	if request.user.is_authenticated():
		seriesByUser = UserSerie.objects.filter(user = auth.get_user(request))
		series = []
		for relation in seriesByUser:
			series.append(relation.serie)

		try:
			s = Serie.objects.get(id = int(selectedId))
			context = {'title' : s.nombre, 'series': series, 'request' : request, 'selectedId': selectedId, 'nombre': s.nombre, 'tiempoAnalisis': s.tiempoAnalisis, 'numTorrents': s.numeroTorrents, 'limiteSubida': s.limiteSubida, 'limiteDescarga': s.limiteBajada}
			page = 'series/edit.html'

			if request.POST.get('butAceptarPreferencias') is not None:
				numTorrents = request.POST.get('Torrents')
				tiempoAnalisis = request.POST.get('Horas')
				limiteSubida = request.POST.get('limiteSubida')
				limiteBajada = request.POST.get('limiteDescarga')
				page = 'series/cambiosguardados.html'

				s.tiempoAnalisis = tiempoAnalisis
				s.numeroTorrents = numTorrents
				s.limiteSubida = limiteSubida
				s.limiteBajada = limiteBajada
				s.save()

		except Serie.DoesNotExist:
			context = generateContext(request=request, title="Not found", series=series)
		return render(request, page, context)

	else:
		context = {'title' : 'Inicio', 'request' : request}
		return render(request, 'series/index-noauth.html', context)

def eliminar(request, selectedId):
	if request.user.is_authenticated():
		seriesByUser = UserSerie.objects.filter(user = auth.get_user(request))
		series = []
		for relation in seriesByUser:
			series.append(relation.serie)

		try:
			show = UserSerie.objects.get(user = auth.get_user(request), serie = int(selectedId))

			if request.POST.has_key('butAceptar'):
				show.delete()

				return redirect('index')
			elif request.POST.has_key('butCancelar'):
				return redirect('index')
			else:
				page = 'series/eliminar.html'
				context = {'title' : show.serie, 'show' : show, 'series': series, 'request' : request}

		except Serie.DoesNotExist:
			page = 'series/serie.html'
			context = {'title' : "Not found", 'series': series, 'request' : request}

		return render(request, page, context)

	else:
		context = {'title' : 'Inicio', 'request' : request}
		return render(request, 'series/index-noauth.html', context)

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
