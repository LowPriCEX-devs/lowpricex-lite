#encoding:utf-8
from lowpricex_app.models import Plataforma, Juego
from django.shortcuts import render

from datetime import timedelta
from django.db.models import ExpressionWrapper, DecimalField, F

def index(request):
    # Obtenemos las plataformas de búsqueda
    plataformas = Plataforma.objects.all()
    
    nintendo = plataformas.filter(nombre__contains='Nintendo')
    sony = plataformas.filter(nombre__contains='PlayStation')
    microsoft = plataformas.filter(nombre__contains='Xbox')
    pc = plataformas.filter(nombre='PC')
    
    # Obtenemos la fecha última de ejecución
    fecha = Juego.objects.latest('actualizado').actualizado
    
    # Le restamos uno para obtener el día anterior
    fechaAyer = fecha - timedelta(days=1)
    
    # Buscamos juegos cuya última fecha de actualización sea la fecha, y la fecha de histórico sea la de ayer, y ordenamos por diferencia
    juegosCambian = Juego.objects.filter(actualizado = fecha, historicojuego__fecha = fechaAyer). \
                        annotate(difCompra = ExpressionWrapper(F('precioCompra') - F('historicojuego__precioCompra'), output_field=DecimalField())). \
                        annotate(difVenta = ExpressionWrapper(F('precioVenta') - F('historicojuego__precioVenta'), output_field=DecimalField())). \
                        annotate(difCompra = ExpressionWrapper(F('precioIntercambio') - F('historicojuego__precioIntercambio'), output_field=DecimalField()))

    bajanCompra = juegosCambian.order_by('difCompra')[:5]
    subenVenta = juegosCambian.order_by('-difVenta')[:5]
    subenIntercambio = juegosCambian.order_by('-difIntercambio')[:5]
    
    return render(request, 'index.html', {'plataformas':plataformas.order_by('nombre'), 'nintendo':nintendo, 'sony':sony, 'microsoft':microsoft, 'pc':pc, \
                                          'bajanCompra':bajanCompra, 'subenVenta':subenVenta, 'subenIntercambio':subenIntercambio})