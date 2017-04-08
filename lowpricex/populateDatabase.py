# encoding:utf-8

import csv

from datetime                       import datetime
from lowpricex_scrapper.items       import JuegoCEX
from lowpricex_scrapper.pipelines   import ProcesadorJuegos
from lowpricex_app.models           import Plataforma
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

#Función que carga los datos
def populateDatabase():
    populatePlatforms()
    print("Finished database population")

if __name__ == '__main__':
    populateDatabase()
