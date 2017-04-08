#encoding:utf-8
from lowpricex_app.models import Plataforma, Juego, HistoricoJuego
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def index(request):
    # Devolver los juegos que más cambian, pongamos 5 o 10 por temática (venta, intercambio, compra)
    return render(request, 'index.html')


def buscar(request):

    page = request.GET.get('page')
    juego = request.GET.get('juego')
    plataforma = request.GET.get('plataforma')
    
    if juego == None:
        juego = ""

    if plataforma == None:
        plataforma = ""

    if plataforma != "":
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

    return render(request, 'buscar.html', {'juegos': juegos, 'searchString':juego, 'plataformSel':plataforma})

def detalles(request):
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

    return render(request, 'detalles.html', {'juego': juego, 'preciosVenta':preciosVenta, 'preciosCompra':preciosCompra, 'preciosIntercambio':preciosIntercambio, \
                                           'fechas':fechas})
