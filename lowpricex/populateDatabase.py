#encoding:utf-8

import csv

from datetime                       import datetime
from lowpricex_scrapper.items       import JuegoCEX
from lowpricex_scrapper.pipelines   import ProcesadorJuegos
from lowpricex_app.models           import Plataforma, Categoria, Juego
from scrapy.exceptions              import DropItem

path = "data"

def populatePlatforms():
    print("Loading platforms....")
    
    with open(path+"/platforms.csv", "rt") as csvfile:
        platformsReader = csv.reader(csvfile, delimiter=';')
        next(platformsReader, None)
        for row in platformsReader:
            Plataforma(idPlataforma=row[0], nombre=row[1], abreviatura=row[2], logo=row[3]).save()

    print("Platforms inserted: " + str(Plataforma.objects.count()))
    print("---------------------------------------------------------")

def populateCategories():
    print("Loading categories....")
    
    with open(path+"/categories.csv", "rt") as csvfile:
        categoriesReader = csv.reader(csvfile, delimiter=';')
        next(categoriesReader, None)
        for row in categoriesReader:
            Categoria(idCategoria=row[0], categoria=row[1]).save()

    print("Categories inserted: " + str(Categoria.objects.count()))
    print("---------------------------------------------------------")


def populateCrawlings(file):
    fecha = datetime.strptime(file.split(".")[0], '%Y-%m-%d').date()
    procesador = ProcesadorJuegos()
    
    with open(path+"/"+file, "rt") as csvfile:
        fileReader = csv.reader(csvfile, delimiter=",", quotechar='"')
        # Nos saltamos la fila de headers
        next(fileReader, None)

        for row in fileReader:
            if not row[6].isdigit():
                # Si el SKU no es numérico, nos lo saltamos
                continue

            juegocex = JuegoCEX(titulo=row[5], sku=row[6], img_caratula=row[7], precio_venta=row[1], precio_compra=row[4], precio_intercambio=row[3], categoria_id=row[0], categoria_str=row[2])
            
            print("Procesando: " + juegocex["titulo"])

            try:
                procesador.process_item(juegocex, None, fecha)
            except DropItem:
                print("El juego %s no se encontró en IGDB" % juegocex["titulo"])
            

    print("Games inserted: " + str(Juego.objects.count()))
    print("---------------------------------------------------------")

    
#Función que carga los datos
def populateDatabase():
    populatePlatforms()
    populateCategories()
    populateCrawlings('2016-12-22.csv')

    
    print("Finished database population")
    
if __name__ == '__main__':
    populateDatabase()