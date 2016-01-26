# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import threading

class Command(BaseCommand):
    help = u"Inicia el análisis para el capítulo de la serie indicada"

    def analyze(self, serie, capitulo):
        self.stdout.write(u"Serie: %i, capítulo: %i\n" % (int(serie), int(capitulo)))

    def handle(self, *args, **options):
        if len(args)==2:
            t = threading.Thread(target=self.analyze, args=args)
            t.start()

        else:
            self.stdout.write(u"Número incorrecto de parámetros")
