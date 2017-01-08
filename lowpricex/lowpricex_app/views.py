#encoding:utf-8
from lowpricex_app.models import Plataforma, Juego
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from django.db.models import ExpressionWrapper, FloatField, F

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
                        annotate(difCompra = ExpressionWrapper(F('precioCompra') - F('historicojuego__precioCompra'), output_field=FloatField())). \
                        annotate(difVenta = ExpressionWrapper(F('precioVenta') - F('historicojuego__precioVenta'), output_field=FloatField())). \
                        annotate(difIntercambio = ExpressionWrapper(F('precioIntercambio') - F('historicojuego__precioIntercambio'), output_field=FloatField())). \
                        annotate(precioCompraAyer = ExpressionWrapper(F('historicojuego__precioCompra'), output_field=FloatField())). \
                        annotate(precioVentaAyer = ExpressionWrapper(F('historicojuego__precioVenta'), output_field=FloatField())). \
                        annotate(precioIntercambioAyer = ExpressionWrapper(F('historicojuego__precioIntercambio'), output_field=FloatField()))
                        

    bajanVenta = juegosCambian.filter(precioVenta__gt=0.0, precioVentaAyer__gt=0.0).order_by('difVenta')[:5]
    subenCompra = juegosCambian.filter(precioCompra__gt=0.0, precioCompraAyer__gt=0.0).order_by('-difCompra')[:5]
    subenIntercambio = juegosCambian.filter(precioIntercambio__gt=0.0, precioIntercambioAyer__gt=0.0).order_by('-difIntercambio')[:5]
    
    return render(request, 'index.html', {'plataformas':plataformas.order_by('nombre'), 'nintendo':nintendo, 'sony':sony, 'microsoft':microsoft, 'pc':pc, \
                                          'subenCompra':subenCompra, 'bajanVenta':bajanVenta, 'subenIntercambio':subenIntercambio})
    
    
def buscar(request):
    # Obtenemos las plataformas de búsqueda
    plataformas = Plataforma.objects.all()
    
    nintendo = plataformas.filter(nombre__contains='Nintendo')
    sony = plataformas.filter(nombre__contains='PlayStation')
    microsoft = plataformas.filter(nombre__contains='Xbox')
    pc = plataformas.filter(nombre='PC')
    
    page = request.GET.get('page')
    juego = request.GET.get('juego')
    plataforma = request.GET.get('plataforma')
    
    if juego == None:
        juego = ""
        
    if plataforma != None and plataforma != "": 
        juegos = Juego.objects.filter(nombre__icontains=juego, plataforma=Plataforma.objects.get(pk=plataforma))
    else:
        juegos = Juego.objects.filter(nombre__icontains=juego)
        
    paginator = Paginator(juegos, 25)

    try:
        juegos = paginator.page(page)
    except PageNotAnInteger:
        juegos = paginator.page(1)
    except EmptyPage:
        juegos = paginator.page(paginator.num_pages)

    return render(request, 'buscar.html', {'plataformas':plataformas.order_by('nombre'), 'nintendo':nintendo, 'sony':sony, 'microsoft':microsoft, 'pc':pc, \
                                           'juegos': juegos, 'searchString':juego})