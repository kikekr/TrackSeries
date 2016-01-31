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

def setContextSuccess(context, message):
	context['success'] = message

def setContextInfo(context, message):
	context['info'] = message

def setContextWarning(context, message):
	context['warning'] = message

def setContextError(context, message):
	context['error'] = message

def addSerie(request, identifier):
	# Comprobar si el usuario esta autenticado
	if not request.user.is_authenticated():
		return redirect('index')

	# Comprobar si la serie ya está en la base de datos
	try:
		s = Serie.objects.get(theTvdbID=identifier)
		userSerie = UserSerie.objects.get(serie=s)

		# Si la serie ya existe para ese usuario devolver un warning
		series = getSeriesForUser(request)
		context = generateContext(request=request, title="Control panel", series=series)
		setContextWarning(context, "You already have that show")
		return render(request, 'series/index-message.html', context)

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
			s.capitulo_set.create(theTvdbID=episodeId, temporada=season, numero=number, titulo=title, estado=-1)

		# Añadir serie al usuario correspondiente
		userSerie = UserSerie(user=auth.get_user(request), serie=s)
		userSerie.save()

	except UserSerie.DoesNotExist:
		# La serie existe en la base de datos, pero no está asociada al usuario
		userSerie = UserSerie(user=auth.get_user(request), serie=s)
		userSerie.save()

	series = getSeriesForUser(request)
	context = generateContext(request=request, title="Control panel", series=series)
	setContextSuccess(context, "Show was added to your account")
	return render(request, 'series/index-message.html', context)


def nuevaSerie(request):
	# Comprobar si el usuario esta autenticado
	if not request.user.is_authenticated():
		return redirect('index')

	series = getSeriesForUser(request)

	context = generateContext(title = "Añadir serie", series=series, request=request)
	api = APIseries()

	if request.POST.has_key('myS'):
			nameserie = request.POST['myS']
			tuple_list = api.getStructuredSeries(nameserie)

			if tuple_list and len(tuple_list) > 0:
				context["tuple_list"] = tuple_list

	return render(request, 'series/nuevaserie.html', context)


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
	# Comprobar si el usuario esta autenticado
	if not request.user.is_authenticated():
		return redirect('index')

	series = getSeriesForUser(request)

	try:
		show = Serie.objects.get(id=int(selectedId))

		if request.POST.get('butActualizar') is not None:
			actualizar(show)

		context = generateContext(request=request, title=show.nombre, series=series)
		context["show"] = show
		allEpisodes = Capitulo.objects.filter(serie=int(selectedId))
		if len(allEpisodes)>0:
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
	# Comprobar si el usuario esta autenticado
	if not request.user.is_authenticated():
		return redirect('index')

	series = getSeriesForUser(request)

	try:
		show = Serie.objects.get(id=int(showId))
		episode = Capitulo.objects.get(serie=int(showId), temporada=int(seasonId), numero=int(episodeId))
		ips = IPDescarga.objects.filter(capitulo=episode.id)

		context = generateContext(request=request, title=show.nombre, series=series)
		context["show"] = show
		context["episode"] = episode

		if len(ips)>0:
			ipinfo = getLocationByList(ips)
			df = pd.DataFrame(ipinfo)
			cnt = df.groupby(by="country_name")['ip'].count()
			logger.info(df.to_string())

			context["cnt_downloads"] = sorted(cnt.iteritems(), key=lambda x: x[1], reverse=True)

		else:
			context["no_data"] = 1

		return render(request, 'series/estadisticas.html', context)

	except (Serie.DoesNotExist, Capitulo.DoesNotExist):
		context = generateContext(request=request, title="Not found", series=series)
		setContextError(context, "Couldn't find the episode for the selected serie")
		return render(request, 'series/index-message.html', context)


def analizar(request, showId, seasonId, episodeId):
	# Comprobar si el usuario esta autenticado
	if not request.user.is_authenticated():
		return redirect('index')

	call_command('startanalysis', showId, seasonId, episodeId)

	series = getSeriesForUser(request)
	context = generateContext(request=request, title="Control panel", series=series)
	setContextInfo(context, "Analysis started")
	return render(request, 'series/index-message.html', context)

def edit(request, selectedId):
	# Comprobar si el usuario esta autenticado
	if not request.user.is_authenticated():
		return redirect('index')

	series = getSeriesForUser(request)
	try:
		s = Serie.objects.get(id=selectedId)
		# Comprobar si el usuaruo tiene acceso a esa serie
		UserSerie.objects.get(user=auth.get_user(request), serie=s)

		if request.POST.get('butAceptarPreferencias') is None:
			context = generateContext(request=request, title=s.nombre, series=series)
			context["selectedId"] = s.id
			context['tiempoAnalisis'] = s.tiempoAnalisis
			context['numTorrents'] = s.numeroTorrents
			context['limiteSubida'] = s.limiteSubida
			context['limiteDescarga'] = s.limiteBajada
			return render(request, "series/edit.html", context)

		else:
			s.tiempoAnalisis = request.POST.get('Horas')
			s.numeroTorrents = request.POST.get('Torrents')
			s.limiteSubida = request.POST.get('limiteSubida')
			s.limiteBajada = request.POST.get('limiteDescarga')
			s.save()

			context = generateContext(request=request, title="Control panel", series=series)
			setContextSuccess(context, "Preferences updated for " + s.nombre)
			return render(request, "series/index-message.html", context)

	except (Serie.DoesNotExist, UserSerie.DoesNotExist):
		context = generateContext(request=request, title="Control panel", series=series)
		setContextError(context, "Show not found")
		return render(request, "series/index-message.html", context)


def eliminar(request, selectedId):
	# Comprobar si el usuario esta autenticado
	if not request.user.is_authenticated():
		return redirect('index')

	series = getSeriesForUser(request)

	try:
		show = UserSerie.objects.get(user = auth.get_user(request), serie = int(selectedId))

		if request.POST.has_key('butAceptar'):
			show.delete()

			return redirect('index')
		elif request.POST.has_key('butCancelar'):
			return redirect('index')
		else:
			page = 'series/eliminar.html'
			context = generateContext(request=request, title=show.serie, series=series)
			context['show'] = show

	except Serie.DoesNotExist:
		page = 'series/index-message.html'
		context = generateContext(request=request, title="Control panel", series=series)
		setContextError(context, "Show not found")

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
