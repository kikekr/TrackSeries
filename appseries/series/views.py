from xml.etree import ElementTree as ET
import requests
import sys
from APIseries import APIseries
from django.shortcuts import render
from series.models import Serie
import json


def addSerie(request, identifier):
	series_list = Serie.objects.all()
	api = APIseries()
	data = api.getSeriesByRemoteID(identifier)

	try :
		p = Serie.objects.get(nombre = data[0][16].text)
		context = {'title' : 'Inicio', 'ID': identifier, 'nombre': data[0][16].text, 'series_list': series_list, 'existe': 'true'}

	except Serie.DoesNotExist :
		context = {'title' : 'Inicio', 'ID': identifier, 'nombre': data[0][16].text, 'series_list': series_list}

		if data[0][2].text is None:
			s = Serie(nombre = data[0][16].text, descripcion = data[0][11].text, imagen = data[0][20].text, genero = data[0][6].text, fechaEmision = "", estado = data[0][17].text)
		else:
			s = Serie(nombre = data[0][16].text, descripcion = data[0][11].text, imagen = data[0][20].text, genero = data[0][6].text, fechaEmision = data[0][2].text, estado = data[0][17].text)

		s.save()

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

	query = Serie.objects.filter(id=int(selectedId))
	if len(query) > 0:
		context = {'title' : query[0].nombre, 'selectedSerie' : query[0], 'series': series, 'request' : request}
	else:
		context = {'title' : "Not found", 'series': series, 'request' : request}

	return render(request, 'series/serie.html', context)

def index(request):

	series = Serie.objects.all()
	context = {'title' : 'Inicio', 'request' : request, 'series': series}

	if request.user.is_authenticated():
		return render(request, 'series/index-auth.html', context)
	else:
		return render(request, 'series/index-noauth.html', context)

def estadisticas(request):
	series = Serie.objects.all()
	context = {'title' : 'Estadisticas', 'series': series, 'request': request}
	return render(request, 'series/estadisticas.html', context)

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect

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
