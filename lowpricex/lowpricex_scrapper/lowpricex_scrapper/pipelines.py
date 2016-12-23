# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import requests
from urllib.parse import quote_plus # URL Encoding
from scrapy.exceptions import DropItem
from logging import debug, info, warning, error 
from api_keys import KEY_IGDB_API

class ProcesadorJuegos(object):

    def process_item(self, item, spider):
        #Si el juego ya está en la BD, devolverlo directamente y terminar

        data = obtenerInfoIGDB(item["titulo"])
        return item

def obtenerInfoIGDB(titulo):
    return {} #TODO
