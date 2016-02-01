# -*- coding: utf-8 -*-
from series.models import Serie, dailyUpdate
import series.crontab as crontab
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = u"Actualiza todas las series de la base de datos y establece una actualización automática a las 00:00 de cada día"

    def handle(self, *args, **options):
        if len(args)==1:
            param = str(args[0])

        else:
            self.stdout.write(u"Número incorrecto de parámetros")
            return

        if param == "all":
            # Actualizar todas las series
            seriesList = Serie.objects.all()
            for serie in seriesList:
                serie.__update__()

            # Establece la actualización automática
            crontab.setDailyUpdate(crontab.path)
            crontab.saveTempChanges(crontab.path)

        elif param == "daily":
            dailyUpdate()
