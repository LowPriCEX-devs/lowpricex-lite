# encoding:utf-8
from django.db import models

class Plataforma(models.Model):
    idPlataforma = models.IntegerField(primary_key=True)
    nombre = models.TextField()
    abreviatura = models.TextField()
    logo = models.URLField()

    def __str__(self):
        return self.abreviatura

    class Meta:
        ordering = ('abreviatura', )

class Juego(models.Model):
    sku = models.TextField(primary_key=True)
    idIGDB = models.BigIntegerField(null=True)
    plataforma = models.ForeignKey(Plataforma)
    nombre = models.TextField()
    portada = models.URLField()
    portadaCEX = models.URLField(null=True)
    precioVenta = models.FloatField()
    precioCompra = models.FloatField()
    precioIntercambio = models.FloatField()
    actualizado = models.DateField()

    def __str__(self):
        return self.sku

    class Meta:
        ordering = ('nombre', )

class HistoricoJuego(models.Model):
    juego = models.ForeignKey(Juego)
    fecha = models.DateField()
    precioVenta = models.FloatField()
    precioCompra = models.FloatField()
    precioIntercambio = models.FloatField()

    class Meta:
        ordering = ('fecha', )
