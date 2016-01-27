# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from series.models import Serie

import threading
from lxml import html
import requests
from requests.utils import quote
from datetime import datetime, timedelta
from time import sleep
import os
import libtorrent as lt

class Command(BaseCommand):
    help = u"Inicia el análisis para el capítulo de la serie indicada"

    tempUrl = "/tmp/.appseries/"

    # Dormir durante 10s hasta próxima actualización
    sleepTime = 10

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

    def getTorrentFileAsString(self, url):
        # Necesario cambiar el User-Agent, sino el servidor cierra la conexión TCP
        headers = {"User-Agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"}
        if url.startswith("/"):
            url = "http:" + url
        return requests.get(url, headers=headers).content

    def analyze(self, serieId, temporada, capitulo):
        try:
            serie = Serie.objects.get(id=int(serieId))
        except Serie.DoesNotExist:
            self.stdout.write(u"No existe serie con id %i\n" % (int(serie)))
            return

        # Falta comprobar si el directorio temporal existe, y crearlo en caso negativo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # Set de urls siendo actualmente descargadas
        urls = set()
        # Momento de finalización
        deadline = datetime.now() + timedelta(0, 0, 0, 0, 0, serie.tiempoAnalisis)

        # Inicialización de la sesión de
        ses = lt.session()

        while (deadline - datetime.now()).total_seconds()>0:
            # Comprobar si hay más urls disponibles en caso de no disponer de suficientes
            if len(urls)<serie.numeroTorrents:
                newUrls = set(self.getTorrentsForEpisode(serie.nombre, int(temporada), int(capitulo), serie.numeroTorrents)) - urls
                for u in newUrls:
                    # Iniciar descarga para cada url
                    e = lt.bdecode(self.getTorrentFileAsString(u))
                    info = lt.torrent_info(e)
                    params = { "save_path": "/tmp/.appseries/", "storage_mode": lt.storage_mode_t.storage_mode_sparse, "ti": info }
                    ses.add_torrent(params)
                    # Tal vez establecer un limite de bajada y subida?

                    # Añadir la url de la descarga a la lista
                    urls.add(u)

            # Para cada descarga comprobar a que peers se encuentra conectado
            for h in ses.get_torrents():
                for peer in h.get_peer_info():
                    # Debug
                    ip, port = peer.ip
                    self.stdout.write(ip)

            sleep(sleepTime)

        # Cerrar todas las conexiones activas !!!!!!!!!!!!!!!!! Sin debugear si funciona
        for h in ses.get_torrents():
            ses.remove_torrent(h)

    def handle(self, *args, **options):
        if len(args)==3:
            t = threading.Thread(target=self.analyze, args=args)
            t.start()

        else:
            self.stdout.write(u"Número incorrecto de parámetros")
