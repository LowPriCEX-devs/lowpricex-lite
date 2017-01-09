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

 
class Categoria(models.Model):
    idCategoria = models.IntegerField(primary_key=True)
    categoria = models.TextField()
    
    def __str__(self):
        return self.categoria
    
    class Meta:
        ordering = ('categoria', )
        
class Keyword(models.Model):
    idKeyword = models.IntegerField(primary_key=True)
    keyword = models.TextField()
    
    def __str__(self):
        return self.keyword
    
    class Meta:
        ordering = ('keyword', )
        
class Empresa(models.Model):
    idEmpresa = models.IntegerField(primary_key=True)
    empresa = models.TextField()
    
    def __str__(self):
        return self.empresa
    
    class Meta:
        ordering = ('empresa', )
        
class Genero(models.Model):
    idGenero = models.IntegerField(primary_key=True)
    genero = models.TextField()
    
    def __str__(self):
        return self.genero
    
    class Meta:
        ordering = ('genero', )

class Tema(models.Model):
    idTema = models.IntegerField(primary_key=True)
    tema = models.TextField()
    
    def __str__(self):
        return self.tema
    
    class Meta:
        ordering = ('tema', )
        

class Juego(models.Model):
    sku = models.BigIntegerField(primary_key=True)
    idIGDB = models.BigIntegerField(null=True)
    plataforma = models.ForeignKey(Plataforma)
    nombre = models.TextField()
    portada = models.URLField()
    precioVenta = models.FloatField()
    precioCompra = models.FloatField()
    precioIntercambio = models.FloatField()
    fechaSalida = models.DateField(null=True)
    actualizado = models.DateField()
    categoria = models.ForeignKey(Categoria)
    desarrolladores = models.ManyToManyField(Empresa, related_name="desarrolladores")
    publishers = models.ManyToManyField(Empresa, related_name="publishers")
    keywords = models.ManyToManyField(Keyword)
    generos = models.ManyToManyField(Genero)
    temas = models.ManyToManyField(Tema)
    
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
        
class JuegoDetalles(models.Model):
    juego = models.ForeignKey(Juego)
    detalle = models.TextField()


class ImagenJuego(models.Model):
    urlImagen = models.URLField()
    juego = models.ForeignKey(Juego)
    
    def __str__(self):
        return self.urlImagen
    
class VideoJuego(models.Model):
    urlVideo = models.URLField()
    juego = models.ForeignKey(Juego)
    
    def __str__(self):
        return self.urlVideo