import django
django.setup()

import requests
import re

from datetime               import datetime
from scrapy.exceptions      import DropItem
from logging                import debug, info, warning, error 
from difflib                import SequenceMatcher
from lowpricex_app.models   import *

try:
    from api_keys       import KEY_IGDB_API, KEY_YANDEX_TRANSLATOR
except:
    from .api_keys      import KEY_IGDB_API, KEY_YANDEX_TRANSLATOR

SEMEJANZA_MINIMA_TITULO = 0.5

class ProcesadorJuegos(object):

    def process_item(self, item, spider, curDate=datetime.now()): # El parámetro curDate es necesario por si estamos insertando datos antiguos con el populate

        if not item["sku"].isdigit():
            raise DropItem("El juego %s no tiene un SKU válido" % item["titulo"])

        # Si el juego ya está en la BD
        if Juego.objects.filter(pk=item["sku"]).exists():
            juegoGuardado = Juego.objects.get(pk=item["sku"])

            pVenta = float(item["precio_venta"])
            pCompra = float(item["precio_compra"])
            pIntercambio = float(item["precio_intercambio"])

            # Comprobamos si los precios son diferentes
            if juegoGuardado.precioVenta != pVenta or juegoGuardado.precioCompra != pCompra or juegoGuardado.precioIntercambio != pIntercambio:
                # Si alguno de los precios ha cambiado, actualizamos el juego e insertamos un histórico
                insertarHistorico(curDate, pVenta, pIntercambio, pCompra, juegoGuardado)
                info("Actualizado precio para %s (SKU: %s)" % (item["titulo"], item["sku"]))

        # Si el juego no está en la BD
        else:
            # Traer la info de IGDB
            igdbInfo = obtenerInfoIGDB(item["titulo"])

            # Si no hay info de IGDB, lanzar excepción para el log y sacar el juego de la pipeline
            if igdbInfo is None:
                raise DropItem("No se ha encontrado en IGDB el juego %s (SKU: %s)" % (item["titulo"], item["sku"]))

            insertarJuegoBD(item, igdbInfo, curDate)

        return item

# Devuelve la información de IGDB de un juego cuyo título se parezca al
# introducido como parámetro en SEMEJANZA_MINIMA_TITULO o más
# Intenta primero con el título original. Si falla, elimina paréntesis. Si vuelve a fallar, traduce al inglés.
def obtenerInfoIGDB(titulo):
    data = consultaJuegoIGDB(titulo)
    if data != None:
        return data

    if "(" in titulo and ")" in titulo:
        titulo = re.sub("(\(.*?\))", "", titulo)
        data = consultaJuegoIGDB(titulo)
        if data != None:
            return data

    tituloTraducido = traducirTitulo(titulo)
    return consultaJuegoIGDB(tituloTraducido)

# Realiza la petición a IGDB y devuelve el primer objeto cuyo título se parezca al
# introducido como parámetro en SEMEJANZA_MINIMA_TITULO o más
# Devuelve None si no se ha encontrado ninguno con esas características
def consultaJuegoIGDB(titulo):
    params = {
        "search": titulo,
        "limit": 50,
        "fields": "name,developers,publishers,category,keywords,themes,genres,screenshots,videos,cover,first_release_date"
    }

    for juego in peticionIGDB("games", params):
        if indiceSemejanza(titulo, juego["name"]) >= SEMEJANZA_MINIMA_TITULO:
            return normalizarJuegoIGDB(juego)

    return None

def peticionIGDB(endpoint, params, id=""):
    url = "https://igdbcom-internet-game-database-v1.p.mashape.com/%s/%s" % (endpoint,id)

    headers = {
        "X-Mashape-Key": KEY_IGDB_API,
        "Accept": "application/json"
    }

    return requests.get(url, headers=headers, params=params).json()

# Traduce una cadena de español a inglés usando la API del traductor de Yandex
def traducirTitulo(titulo):
    url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    params = {
        "key": KEY_YANDEX_TRANSLATOR,
        "lang": "es-en",
        "text": titulo
    }

    req = requests.get(url, params=params)
    return req.json()["text"][0]

def indiceSemejanza(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()

def normalizarJuegoIGDB(data):
    if "developers" not in data:
        data["developers"] = []
    if "publishers" not in data:
        data["publishers"] = []
    if "category" not in data:
        data["category"] = 0
    if "keywords" not in data:
        data["keywords"] = []
    if "themes" not in data:
        data["themes"] = []
    if "genres" not in data:
        data["genres"] = []
    if "screenshots" not in data:
        data["screenshots"] = []
    if "videos" not in data:
        data["videos"] = []
    if "cover" not in data:
        data["cover"] = None
    if "first_release_date" not in data:
        data["first_release_date"] = None
    return data

def insertarHistorico(fecha, precioVenta, precioIntercambio, precioCompra, juego):
    HistoricoJuego(juego=juego, fecha=fecha, precioVenta=precioVenta, precioIntercambio=precioIntercambio, precioCompra=precioCompra).save()
    juego.precioVenta = precioVenta
    juego.precioIntercambio = precioIntercambio
    juego.precioCompra = precioCompra
    juego.actualizado = fecha
    juego.save()

def insertarJuegoBD(juegoCex, infoIgdb, curDate):
    juego = Juego()

    # Crear y guardar el objeto Juego
    juego.sku = int(juegoCex["sku"])
    juego.idIGDB = infoIgdb["id"]
    juego.plataforma = Plataforma.objects.get(pk=juegoCex["categoria_id"])
    juego.nombre = infoIgdb["name"]

    if infoIgdb["cover"] is not None:
        juego.portada = "https://images.igdb.com/igdb/image/upload/%s.png" % infoIgdb["cover"]["cloudinary_id"]
    else:
        juego.portada = "https://es.webuy.com" + juegoCex["img_caratula"]

    pVenta = float(juegoCex["precio_venta"])
    pCompra = float(juegoCex["precio_compra"])
    pIntercambio = float(juegoCex["precio_intercambio"])

    juego.precioVenta = pVenta
    juego.precioCompra = pCompra
    juego.precioIntercambio = pIntercambio
    juego.actualizado = curDate

    if infoIgdb["first_release_date"] is not None:
        juego.fechaSalida = datetime.fromtimestamp(infoIgdb["first_release_date"] / 1000)
    else:
        juego.fechaSalida = None

    juego.categoria = Categoria.objects.get(pk=infoIgdb["category"])

    juego.save()

    # Crear y guardar el primer registro histórico de precios
    HistoricoJuego(juego=juego, fecha=curDate, precioVenta=pVenta, precioCompra=pCompra, precioIntercambio=pIntercambio).save()

    # Crear y guardar las imágenes y vídeos del juego
    for screenshot in infoIgdb["screenshots"]:
        ImagenJuego(juego=juego, urlImagen=("https://images.igdb.com/igdb/image/upload/%s.png" % screenshot["cloudinary_id"])).save()

    for video in infoIgdb["videos"]:
        VideoJuego(juego=juego, urlVideo=("https://www.youtube.com/watch?v=%s" % video["video_id"])).save()

    # Establecer el resto de relaciones many-to-many
    for dev_id in infoIgdb["developers"]:
        juego.desarrolladores.add(obtenerEmpresa(dev_id))

    for publisher_id in infoIgdb["publishers"]:
        juego.publishers.add(obtenerEmpresa(publisher_id))

    for keyword_id in infoIgdb["keywords"]:
        juego.keywords.add(obtenerKeyword(keyword_id))

    for genero_id in infoIgdb["genres"]:
        juego.generos.add(obtenerGenero(genero_id))

    for tema_id in infoIgdb["themes"]:
        juego.temas.add(obtenerTema(tema_id))

    info("Añadido nuevo juego: %s (SKU: %s)" % (juego.nombre, juego.sku))

def obtenerEmpresa(id_obj):
    if not Empresa.objects.filter(pk=id_obj).exists():
        data = peticionIGDB("companies", {"fields": "name", "limit":1}, str(id_obj))
        name = data[0]["name"]
        Empresa(idEmpresa=id_obj, empresa=name).save()
        info("Guardada nueva empresa: %s" % name)

    return Empresa.objects.get(pk=id_obj)

def obtenerKeyword(id_obj):
    if not Keyword.objects.filter(pk=id_obj).exists():
        data = peticionIGDB("keywords", {"fields": "name", "limit":1}, str(id_obj))
        name = data[0]["name"]
        Keyword(idKeyword=id_obj, keyword=name).save()
        info("Guardada nueva keyword: %s" % name)

    return Keyword.objects.get(pk=id_obj)

def obtenerGenero(id_obj):
    if not Genero.objects.filter(pk=id_obj).exists():
        data = peticionIGDB("genres", {"fields": "name", "limit":1}, str(id_obj))
        name = data[0]["name"]
        Genero(idGenero=id_obj, genero=name).save()
        info("Guardado nuevo género: %s" % name)

    return Genero.objects.get(pk=id_obj)

def obtenerTema(id_obj):
    if not Tema.objects.filter(pk=id_obj).exists():
        data = peticionIGDB("themes", {"fields": "name", "limit":1}, str(id_obj))
        name = data[0]["name"]
        Tema(idTema=id_obj, tema=name).save()
        info("Guardado nuevo tema: %s" % name)

    return Tema.objects.get(pk=id_obj)