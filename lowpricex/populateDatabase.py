# encoding:utf-8

import csv
import os

from datetime                       import datetime
from lowpricex_scrapper.items       import JuegoCEX
from lowpricex_scrapper.pipelines   import ProcesadorJuegos
from lowpricex_app.models           import Plataforma
from scrapy.exceptions              import DropItem
from lowpricex.settings             import BASE_DIR

path = os.path.join(BASE_DIR, "data")

def populatePlatforms():
    print("Loading platforms....")

    with open(path+"/platforms.csv", "rt") as csvfile:
        platformsReader = csv.reader(csvfile, delimiter=';')
        next(platformsReader, None)
        for row in platformsReader:
            Plataforma(idPlataforma=row[0], nombre=row[1], abreviatura=row[2], logo=row[3]).save()

    print("Platforms inserted: " + str(Plataforma.objects.count()))
    print("---------------------------------------------------------")

def populateCsvs():
    print("Loading csv's....")

    csvs_path = os.path.join(path, "csv")
    files = sorted(os.listdir(csvs_path))
    
    for f in files:
        filepath = os.path.join(csvs_path, f)

        fecha = datetime.strptime(f.split(".")[0], '%Y-%m-%d').date()
        procesador = ProcesadorJuegos()

        with open(filepath, "rt") as csvfile:
            fileReader = csv.reader(csvfile, delimiter=",", quotechar='"')
            # Guardamos la fila de headers
            headers = next(fileReader, None)

            i = 0
            for row in fileReader:
                juegocex = JuegoCEX(titulo=row[headers.index("titulo")], sku=row[headers.index("sku")], img_caratula=row[headers.index("img_caratula")], 
                                                precio_venta=row[headers.index("precio_venta")], precio_compra=row[headers.index("precio_compra")], 
                                                precio_intercambio=row[headers.index("precio_intercambio")], categoria_id=row[headers.index("categoria_id")], 
                                                categoria_str=row[headers.index("categoria_str")])

                try:
                    procesador.process_item(juegocex, None, fecha)
                except DropItem:
                    print("El juego %s no tiene SKU" % juegocex["titulo"])
                except Exception as e:
                    print("Excepción no controlada:")
                    print(e)

                i += 1
                if i % 100 == 0:
                    print("%s | Procesados %d juegos" % (str(fecha), i))
            

    print("Games inserted: " + str(Juego.objects.count()))
    print("---------------------------------------------------------")

#Función que carga los datos
def populateDatabase():
    populatePlatforms()
    print("Finished database population")

if __name__ == '__main__':
    populateDatabase()
