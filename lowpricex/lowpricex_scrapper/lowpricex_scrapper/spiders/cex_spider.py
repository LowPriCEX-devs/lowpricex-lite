import scrapy
import re
from logging import debug, info, warning, error
from lowpricex_scrapper.items import JuegoCEX

categorias = [
    (1001, "PlayStation 4"),
    (977, "Nintendo 3DS"),
    (834, "Nintendo DS"),
    (830, "PC"),
    (821, "PlayStation 3"),
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
    download_delay = 2

    def parse(self, response):
        catId = re.search("catid=(\d*)", response.url).group(1)
        catStr = [x[1] for x in categorias if x[0] == int(catId)][0]
        page = re.search("page=(\d*)", response.url).group(1)

        debug(response.url)
        debug("Página %s categoría %s (%s)" % (page, catId, catStr))

        divs_juegos = response.css("div.searchRecord")

        if divs_juegos == [] or divs_juegos == None:
            return # Parar cuando lleguemos a la página sin resultados

        for juego in divs_juegos:
            data = JuegoCEX()

            data["categoria_id"] = catId
            data["categoria_str"] = catStr
            data["titulo"] = juego.css("div.desc > h1 > a::text").extract_first()

            enlace = juego.css("div.desc > h1 > a::attr(href)").extract_first()
            data["sku"] = re.search("sku=(\d*)", enlace).group(1)

            data["img_caratula"] = juego.css("div.thumb img::attr(src)").extract_first()

            div_precios = juego.css("div.prodPrice")

            try:
                data["precio_venta"] = div_precios.re(r"Vendemos.*?:.*?€(\d*\.\d*)")[0]
            except:
                data["precio_venta"] = -1

            try:
                data["precio_compra"] = div_precios.re(r"Compramos.*?:.*?€(\d*\.\d*)")[0]
            except:
                data["precio_compra"] = -1

            try:
                data["precio_intercambio"] = div_precios.re(r"Intercambiamos.*?:.*?€(\d*\.\d*)")[0]
            except:
                data["precio_intercambio"] = -1
            
            yield data

        yield scrapy.Request("https://es.webuy.com/search/index.php?catid=%s&page=%d&counter=%s" % (catId, int(page)+1, page), callback=self.parse)

