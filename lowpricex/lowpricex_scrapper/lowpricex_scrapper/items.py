# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class JuegoCEX(scrapy.Item):
    titulo = scrapy.Field()
    sku = scrapy.Field()
    img_caratula = scrapy.Field()
    precio_venta = scrapy.Field()
    precio_compra = scrapy.Field()
    precio_intercambio = scrapy.Field()
    categoria_id = scrapy.Field()
    categoria_str = scrapy.Field()