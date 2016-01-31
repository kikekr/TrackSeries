# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = u"Inicia el análisis para el capítulo de la serie indicada"

    def handle(self, *args, **options):
        if len(args)==3:
            return
