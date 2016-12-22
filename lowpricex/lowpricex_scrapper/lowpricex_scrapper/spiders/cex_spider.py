import scrapy
from logging import debug, info, warning, error

categorias = [
    (977, "Nintendo 3DS"),
    (834, "Nintendo DS"),
    (830, "PC"),
    (821, "PlayStation 3"),
    (1001, "PlayStation 4"),
    (990, "PlayStation Vita"),
    (862, "PSP"),
    (831, "Wii"),
    (996, "Wii U"),
    (827, "Xbox 360"),
    (1002, "Xbox One")
]

class CexSpider(scrapy.Spider):
    name = "CexSpider"
    start_urls = ["https://es.webuy.com/search/index.php?catid=%d&page=1&counter=0" % x[0] for x in categorias]

    def parse(self, response, page=0):
        debug("Consulta realizada a %s" % response.url)

