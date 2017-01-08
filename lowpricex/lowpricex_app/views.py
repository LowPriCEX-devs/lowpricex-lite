#encoding:utf-8
from lowpricex_app.models import Plataforma, Juego, HistoricoJuego
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from django.db.models import ExpressionWrapper, FloatField, F,  Q
from itertools import chain
from operator import itemgetter
import datetime

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
    
def detalles(request):
    # Obtenemos las plataformas de búsqueda
    plataformas = Plataforma.objects.all()
    
    nintendo = plataformas.filter(nombre__contains='Nintendo')
    sony = plataformas.filter(nombre__contains='PlayStation')
    microsoft = plataformas.filter(nombre__contains='Xbox')
    pc = plataformas.filter(nombre='PC')
    
    juego = get_object_or_404(Juego, pk=request.GET.get('sku'))
    
    # Datos para la gráfica de precios
    hist = HistoricoJuego.objects.filter(juego=juego.sku)
    preciosVenta = []
    preciosCompra = []
    preciosIntercambio = []
    fechas=[] 
    for h in hist:
        preciosVenta.append(h.precioVenta)
        preciosCompra.append(h.precioCompra)
        preciosIntercambio.append(h.precioIntercambio)
        fechas.append(h.fecha.strftime('%d/%m/%Y'))
        
    preciosVenta = (', '.join('"' + str(item) + '"' for item in preciosVenta))
    preciosCompra = (', '.join('"' + str(item) + '"' for item in preciosCompra))
    preciosIntercambio = (', '.join('"' + str(item) + '"' for item in preciosIntercambio))
    fechas = (', '.join('"' + str(item) + '"' for item in fechas))

    # Sistema de recomendación
    desarrolladores = juego.desarrolladores.all().values_list('pk', flat=True)
    publishers = juego.publishers.all().values_list('pk', flat=True)
    keywords = juego.keywords.all().values_list('pk', flat=True)
    generos = juego.generos.all().values_list('pk', flat=True)
    temas = juego.temas.all().values_list('pk', flat=True)

    juegosDevRecomendados = Juego.objects.filter(~Q(pk=juego.sku), ~Q(nombre=juego.nombre), plataforma=juego.plataforma, desarrolladores__in=desarrolladores)
    juegosPublishersRecomendados = Juego.objects.filter(~Q(pk=juego.sku), ~Q(nombre=juego.nombre), plataforma=juego.plataforma, publishers__in=publishers)
    juegosKeywordsRecomendados = Juego.objects.filter(~Q(pk=juego.sku), ~Q(nombre=juego.nombre), plataforma=juego.plataforma, keywords__in=keywords)
    juegosGenerosRecomendados = Juego.objects.filter(~Q(pk=juego.sku), ~Q(nombre=juego.nombre), plataforma=juego.plataforma, generos__in=generos)
    juegosTemasRecomendados = Juego.objects.filter(~Q(pk=juego.sku), ~Q(nombre=juego.nombre), plataforma=juego.plataforma, temas__in=temas)
    
    result_list = list(chain(juegosDevRecomendados, juegosPublishersRecomendados, juegosKeywordsRecomendados, juegosGenerosRecomendados, juegosTemasRecomendados))
    juegosRecomendar = list(set(result_list))

    fitnessList=[]
    for juegoRec in juegosRecomendar:
        fitness=0.0
        fitness += len(set(desarrolladores).intersection(juegoRec.desarrolladores.all().values_list('pk', flat=True))) \
                    + len(set(publishers).intersection(juegoRec.publishers.all().values_list('pk', flat=True))) \
                    + len(set(keywords).intersection(juegoRec.keywords.all().values_list('pk', flat=True))) \
                    + len(set(generos).intersection(juegoRec.generos.all().values_list('pk', flat=True))) \
                    + len(set(temas).intersection(juegoRec.temas.all().values_list('pk', flat=True)))
        fitnessList.append({'juego':juegoRec, 'fitness':fitness})
        
    juegosRecomendados = sorted(fitnessList, key=itemgetter('fitness'), reverse=True)[:5]

    return render(request, 'detalles.html', {'plataformas':plataformas.order_by('nombre'), 'nintendo':nintendo, 'sony':sony, 'microsoft':microsoft, 'pc':pc, \
                                           'juego': juego, 'preciosVenta':preciosVenta, 'preciosCompra':preciosCompra, 'preciosIntercambio':preciosIntercambio, \
                                           'fechas':fechas, 'juegosRecomendados':juegosRecomendados})