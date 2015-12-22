from xml.etree import ElementTree as ET
import requests
import sys
import APIseries as api

def nuevaSerie(request):
	if request.POST.has_key('myS'):
		nameserie = request.POST['myS']
		data = api.getSeries(nameserie)
		context = {'title' : 'Inicio', 'ID': data[0][0].text, 'idioma': data[0][1].text, 'nombre': data[0][2].text, 'descripcion': data[0][4].text}
	else:
		context = {'title' : 'Inicio'}
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
