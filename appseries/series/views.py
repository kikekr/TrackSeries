from xml.etree import ElementTree as ET
import requests
import sys
import APIseries as api
from django.shortcuts import render
from series.models import Serie
import json

	
def addSerie(request, identifier):
	context = {'title' : 'Inicio', 'ID': identifier}	
	return render(request, 'series/serieanadida.html', context)
	

def nuevaSerie(request):
	
	context = {'title' : 'Inicio'}	
	nameserie = ''
	
	if request.POST.has_key('myS'):
			nameserie = request.POST['myS']
			data = api.getSeries(nameserie)

			if len(data) > 0:
				context = {'title' : 'Inicio', 'data': data}

	if request.POST.has_key('add'):
		print "Nueva serie"	
		#s = Serie(nombre='Nombre de la serie', descripcion='Descripcion de la serie', imagen='', genero='Drama', fechaEmision='', estado='Emision')
		#s.save()

	return render(request, 'series/NuevaSerie.html', context)

def index(request):
    context = {'title' : 'Inicio', 'request' : request}
    if request.user.is_authenticated():
        return render(request, 'series/index-auth.html', context)
    else:
        return render(request, 'series/index-noauth.html', context)

def estadisticas(request):
    context = {'title' : 'Estadisticas'}
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
