from django.conf.urls import url, include
from series import views

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^(\d+)/$', views.serie, name='serie'),
    url(r'^(\d+)/(\d+)/$', views.serie, name='serie'),
    url(r'^(\d+)/delete/$', views.eliminar, name='eliminar'),
    url(r'^(\d+)/edit/$', views.edit, name='edit'),
	url(r'^(\d+)/(\d+)/(\d+)/$', views.estadisticas, name='estadisticas'),
    url(r'^(\d+)/(\d+)/(\d+)/analyze/$', views.analizar, name='analizar'),
	url(r'^add/$', views.nuevaSerie, name='nueva'),
	url(r'^submitnew/(?P<identifier>\d+)/$', views.addSerie, name='addSerie'),
	url(r'^register/$', views.register, name='register'),
	url(r'^', include('django.contrib.auth.urls')),
]
