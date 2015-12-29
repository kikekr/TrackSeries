from django.conf.urls import patterns, url, include
from series import views
from django.conf.urls.static import static

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^(\d+)/$', views.serie, name='serie'),
	url(r'^estadisticas/', views.estadisticas, name='estadisticas'),
	url(r'^nueva/', views.nuevaSerie, name='nueva'),
	url(r'^nuevaserie/(?P<identifier>\d+)/$', views.addSerie, name='addSerie'),
	url(r'^register/', views.register, name='register'),
	url(r'^', include('django.contrib.auth.urls')),
]
