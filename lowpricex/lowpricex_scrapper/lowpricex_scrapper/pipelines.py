import django
django.setup()

import requests
import re

import datetime
from logging                import debug, info, warning, error
from lowpricex_app.models   import *

try:
    from api_keys       import KEY_IGDB_API
except:
    from .api_keys      import KEY_IGDB_API

from scrapy.exceptions import DropItem


class ProcesadorJuegos(object):

    def process_item(self, item, spider, curDate=datetime.date.today()): # El parámetro curDate es necesario por si estamos insertando datos antiguos con el populate

        # Si el juego ya está en la BD
        if Juego.objects.filter(pk=item["sku"]).exists():
            juegoGuardado = Juego.objects.get(pk=item["sku"])
            juegoGuardado.portadaCEX = getImagenCEX(item["img_caratula"])
            juegoGuardado.save()

            if not juegoGuardado.actualizado < curDate:
                return item
                # Si en esta pasada ya se ha actualizado, saltar este juego (SKU repetido en CEX, no debería pasar...)

            pVenta = float(item["precio_venta"])
            pCompra = float(item["precio_compra"])
            pIntercambio = float(item["precio_intercambio"])

            # Comprobamos si los precios son diferentes
            if juegoGuardado.precioVenta != pVenta or juegoGuardado.precioCompra != pCompra or juegoGuardado.precioIntercambio != pIntercambio:
                insertarHistorico(curDate, pVenta, pIntercambio, pCompra, juegoGuardado)
                info("Actualizado precio para %s (SKU: %s)" % (item["titulo"], item["sku"]))

        else:
            igdbInfo = obtenerInfoIGDB(item["titulo"])
            insertarJuegoBD(item, igdbInfo, curDate)

        return item

# Devuelve la información de IGDB de un juego cuyo título se parezca al
# introducido como parámetro en SEMEJANZA_MINIMA_TITULO o más
# Intenta primero con el título original. Si falla, elimina paréntesis. Si vuelve a fallar, traduce al inglés.
def obtenerInfoIGDB(titulo):
    data = consultaJuegoIGDB(titulo)

    if data == None and ("(" in titulo and ")" in titulo):
        titulo = re.sub("(\(.*?\))", "", titulo)
        data = consultaJuegoIGDB(titulo)

    return data

# Realiza la petición a IGDB y devuelve el primer objeto cuyo título se parezca al
# introducido como parámetro en SEMEJANZA_MINIMA_TITULO o más
# Devuelve None si no se ha encontrado ninguno con esas características
def consultaJuegoIGDB(titulo):
    params = {
        "search": titulo,
        "limit": 1,
        "fields": "cover"
    }

    for juego in peticionIGDB("games", params):
        return juego

    return None

def peticionIGDB(endpoint, params, id=""):
    url = "https://igdbcom-internet-game-database-v1.p.mashape.com/%s/%s" % (endpoint,id)

    headers = {
        "X-Mashape-Key": KEY_IGDB_API,
        "Accept": "application/json"
    }

    return requests.get(url, headers=headers, params=params).json()

def insertarHistorico(fecha, precioVenta, precioIntercambio, precioCompra, juego):
    HistoricoJuego(juego=juego, fecha=fecha, precioVenta=precioVenta, precioIntercambio=precioIntercambio, precioCompra=precioCompra).save()
    juego.precioVenta = precioVenta
    juego.precioIntercambio = precioIntercambio
    juego.precioCompra = precioCompra
    juego.actualizado = fecha
    juego.save()

def insertarJuegoBD(juegoCex, infoIgdb, curDate):
    juego = Juego()

    juego.sku = juegoCex["sku"]

    if juego.sku == "":
        raise DropItem

    juego.plataforma = Plataforma.objects.get(pk=juegoCex["categoria_id"])
    juego.nombre = juegoCex["titulo"]
    juego.portadaCEX = getImagenCEX(juegoCex["img_caratula"])

    if infoIgdb != None and "cover" in infoIgdb and infoIgdb["cover"] is not None:
        juego.portada = "https://images.igdb.com/igdb/image/upload/%s.png" % infoIgdb["cover"]["cloudinary_id"]

    pVenta = float(juegoCex["precio_venta"])
    pCompra = float(juegoCex["precio_compra"])
    pIntercambio = float(juegoCex["precio_intercambio"])

    juego.precioVenta = pVenta
    juego.precioCompra = pCompra
    juego.precioIntercambio = pIntercambio
    juego.actualizado = curDate
    juego.save()

    # Crear y guardar el primer registro histórico de precios
    HistoricoJuego(juego=juego, fecha=curDate, precioVenta=pVenta, precioCompra=pCompra, precioIntercambio=pIntercambio).save()

    info("Añadido nuevo juego: %s (SKU: %s)" % (juego.nombre, juego.sku))

def getImagenCEX(scrapped):
    return "https://es.webuy.com" + scrapped[:-5] + "l" + scrapped[-4:]
