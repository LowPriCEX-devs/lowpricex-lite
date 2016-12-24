# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
from scrapy.exceptions  import DropItem
from logging            import debug, info, warning, error 
from difflib            import SequenceMatcher

try:
    from api_keys       import KEY_IGDB_API, KEY_YANDEX_TRANSLATOR
except:
    from .api_keys      import KEY_IGDB_API, KEY_YANDEX_TRANSLATOR

SEMEJANZA_MINIMA_TITULO = 0.65

class ProcesadorJuegos(object):

    def process_item(self, item, spider):

        # Si el juego ya está en la BD
            # Comprobar si los precios han cambiado
            # Si han cambiado
                # Actualizar precios
            # return item
        # Si no está en la BD
            # Intentar traer información de IGDB
            # Si tenemos información
                # Meter juego en la BD
                # return item
            # Si no lo hemos encontrado
                # raise DropItem     

        return item

# Devuelve la información de IGDB de un juego cuyo título se parezca al
# introducido como parámetro en SEMEJANZA_MINIMA_TITULO o más
# Intenta traducir el título al inglés si la consulta falla. Si también falla tras traducir, devuelve None
def obtenerInfoIGDB(titulo):
    data = consultaIGDB(titulo)
    if data != None:
        return data
    else:
        tituloTraducido = traducirTitulo(titulo)
        return consultaIGDB(tituloTraducido)

# Realiza la petición a IGDB y devuelve el primer objeto cuyo título se parezca al
# introducido como parámetro en SEMEJANZA_MINIMA_TITULO o más
# Devuelve None si no se ha encontrado ninguno con esas características
def consultaIGDB(titulo):
    url = "https://igdbcom-internet-game-database-v1.p.mashape.com/games/"

    headers = {
        "X-Mashape-Key": KEY_IGDB_API,
        "Accept": "application/json"
    }

    params = {
        "search": titulo,
        "limit": 50,
        "fields": "name"
    }

    req = requests.get(url, headers=headers, params=params)

    for juego in req.json():
        if indiceSemejanza(titulo, juego["name"]) >= SEMEJANZA_MINIMA_TITULO:
            return juego

    return None

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