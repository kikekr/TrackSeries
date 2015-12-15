from django.conf.urls import patterns, url, include
from series import views	

urlpatterns = [
	url(r'^$', views.index, name='index'),
	url(r'^estadisticas/', views.index, name='estadisticas'),
	url(r'^register/', views.register, name='register'),
	url(r'^', include('django.contrib.auth.urls')),
]
