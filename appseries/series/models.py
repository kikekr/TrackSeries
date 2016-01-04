# -*- coding: utf-8 -*-

from django.db import models

class Serie(models.Model):
	id = models.AutoField(primary_key=True)
	theTvdbID = models.CharField(max_length=100)
	nombre = models.CharField(max_length=100)
	descripcion = models.CharField(max_length=500)
	imagen = models.CharField(max_length=100)
	genero = models.CharField(max_length=100)
	fechaEmision = models.CharField(max_length=100, default="Fecha de emision")
	estado = models.CharField(max_length=100)

	def __unicode__(self):
		return self.nombre

class Capitulo(models.Model):
	serie = models.ForeignKey(Serie)
	temporada = models.IntegerField()
	numero = models.IntegerField()
	titulo = models.CharField(max_length=100)
	"""
	El estado se usa para indicar en qué estado se encuentra la recolección de datos a través de la descarga
	0: No hay información disponible
	1: En proceso de descarga
	2: Información
	"""
	estado = models.IntegerField()

	def __unicode__(self):
		return self.titulo

class IPDescarga(models.Model):
	capitulo = models.ForeignKey(Capitulo)
	ip = models.CharField(max_length=15)
	hora = models.IntegerField()
