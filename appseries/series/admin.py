from django.contrib import admin
from series.models import Serie, Capitulo, IPDescarga, CachedLocation, UserSerie

admin.site.register(Serie)
admin.site.register(Capitulo)
admin.site.register(IPDescarga)
admin.site.register(CachedLocation)
admin.site.register(UserSerie)
