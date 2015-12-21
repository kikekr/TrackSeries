from xml.etree import ElementTree as ET
import requests
import sys

def getSeries(name):

	response = requests.get("http://www.thetvdb.com/api/GetSeries.php?seriesname="+name+"&language=es")

	if (response.status_code == 200):
		data = ET.fromstring(response.text.encode('utf-8'))
		return data

from django.shortcuts import render
from django.http import HttpResponse

def index(request):
	data = getSeries("The Walking Dead")
	context = {'ID': data[0][0].text, 'idioma': data[0][1].text, 'nombre': data[0][2].text, 'descripcion': data[0][4].text}
	return render(request, 'series/NuevaSerie.html', context)

def estadisticas(request):
	return render(request, 'series/estadisticas.html')

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect

def register(request):
    if request.method == 'POST': 	
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/profile/")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })
