# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import threading
from lxml import html
import requests
from requests.utils import quote

from series.models import Serie
from datetime import datetime, timedelta
from time import sleep

class Command(BaseCommand):
    help = u"Inicia el análisis para el capítulo de la serie indicada"

    def getTorrentsForEpisode(self, tvshow, season, episode, count):
        # Url de búsqueda en kat.cr
        url = "https://kat.cr/usearch/" + quote("%s S%02dE%02d" % (tvshow, season, episode), safe="")
        page = requests.get(url)
        root = html.fromstring(page.content)
        # La primera tabla de la clase data es la tabla correspondiente a la búsqueda
        table = root.find_class("data")[0]
        # Los enlaces al fichero .torrent tienen el atributo data-download en su elemento
        links = table.findall(".//a[@data-download]")
        # Devolvemos los enlaces
        return map(lambda x: x.attrib['href'], links[:count])

    def analyze(self, serieId, temporada, capitulo):
        try:
            serie = Serie.objects.get(id=int(serieId))
        except Serie.DoesNotExist:
            self.stdout.write(u"No existe serie con id %i\n" % (int(serie)))
            return

        # Set de urls siendo actualmente descargadas
        urls = set()
        # Lista de las transferencias activas
        activeTransfers = []
        # Momento de finalización
        deadline = datetime.now() + timedelta(0, 0, 0, 0, 0, serie.tiempoAnalisis)

        while (deadline - datetime.now()).total_seconds()>0:
            # Comprobar si hay más urls disponibles en caso de no disponer de suficientes
            if len(urls)<urlLimit:
                newUrls = set(self.getTorrentsForEpisode(serie.nombre, int(temporada), int(capitulo), serie.numeroTorrents)) - urls
                for u in newUrls:
                    # Iniciar descarga para cada url
                    urls.add(u)

            # Para cada descarga comprobar a que peers se encuentra conectado

            # Debug
            self.stdout.write(u"Segundos restantes: %i\n" % (tiempoFin - datetime.now()).total_seconds())

            # Dormir durante 10s hasta próxima actualización
            sleep(10)

        # Cerrar todas las conexiones activas

    def handle(self, *args, **options):
        if len(args)==3:
            t = threading.Thread(target=self.analyze, args=args)
            t.start()

        else:
            self.stdout.write(u"Número incorrecto de parámetros")
