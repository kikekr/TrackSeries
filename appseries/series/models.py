from django.db import models

class Serie(models.Model):
	nombre = models.CharField(max_length=100)
	descripcion = models.CharField(max_length=500)
	imagen = models.CharField(max_length=100)
	genero = models.CharField(max_length=100)
	fechaEmision = models.CharField(max_length=100)
	estado = models.CharField(max_length=100)

	def __unicode__(self):
		return self.nombre
		
class Capitulo(models.Model):
	serie = models.ForeignKey(Serie)
	temporada = models.IntegerField()
	numero = models.IntegerField()
	titulo = models.CharField(max_length=100)

	def __unicode__(self):
		return self.titulo
