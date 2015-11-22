from django.conf.urls import patterns, url
from series import views	

urlpatterns = patterns('', url(r'^$', views.index, name='index'))
	
