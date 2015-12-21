from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    context = {'title' : 'Inicio'}
    return render(request, 'series/index.html', context)

def estadisticas(request):
    context = {'title' : 'Estadísticas'}
	return render(request, 'series/estadisticas.html', context)

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect("/reviews/")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })
