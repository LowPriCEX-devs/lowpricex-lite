# encoding:utf-8

import csv

from datetime                       import datetime
from lowpricex_scrapper.items       import JuegoCEX
from lowpricex_scrapper.pipelines   import ProcesadorJuegos
from lowpricex_app.models           import Plataforma, Categoria, Juego, Tema, Keyword, Genero, Empresa, JuegoDetalles
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

def populateThemes():
    print("Loading themes....")
    
    with open(path+"/themes.csv", "rt") as csvfile:
        categoriesReader = csv.reader(csvfile, delimiter=';')
        next(categoriesReader, None)
        for row in categoriesReader:
            Tema(idTema=row[0], tema=row[1]).save()

    print("Themes inserted: " + str(Tema.objects.count()))
    print("---------------------------------------------------------")

def populateGenres():
    print("Loading genres....")
    
    with open(path+"/genres.csv", "rt") as csvfile:
        categoriesReader = csv.reader(csvfile, delimiter=';')
        next(categoriesReader, None)
        for row in categoriesReader:
            Genero(idGenero=row[0], genero=row[1]).save()

    print("Themes inserted: " + str(Genero.objects.count()))
    print("---------------------------------------------------------")

def populateKeywords():
    print("Loading keywords....")
    
    with open(path+"/keywords.csv", "rt") as csvfile:
        categoriesReader = csv.reader(csvfile, delimiter=';')
        next(categoriesReader, None)
        for row in categoriesReader:
            Keyword(idKeyword=row[0], keyword=row[1]).save()

    print("Keywords inserted: " + str(Keyword.objects.count()))
    print("---------------------------------------------------------")

def populateCompanies():
    print("Loading companies....")
    
    with open(path+"/companies.csv", "rt") as csvfile:
        categoriesReader = csv.reader(csvfile, delimiter=';')
        next(categoriesReader, None)
        for row in categoriesReader:
            Empresa(idEmpresa=row[0], empresa=row[1]).save()

    print("Companies inserted: " + str(Empresa.objects.count()))
    print("---------------------------------------------------------")


def populateCrawlings(file):
    fecha = datetime.strptime(file.split(".")[0], '%Y-%m-%d').date()
    procesador = ProcesadorJuegos()
    
    with open(path+"/"+file, "rt") as csvfile:
        fileReader = csv.reader(csvfile, delimiter=",", quotechar='"')
        # Nos saltamos la fila de headers
        headers = next(fileReader, None)

        i = 0
        for row in fileReader:
            if not row[6].isdigit():
                # Si el SKU no es numérico, nos lo saltamos
                continue

            juegocex = JuegoCEX(titulo=row[headers.index("titulo")], sku=row[headers.index("sku")], img_caratula=row[headers.index("img_caratula")], 
                                            precio_venta=row[headers.index("precio_venta")], precio_compra=row[headers.index("precio_compra")], 
                                            precio_intercambio=row[headers.index("precio_intercambio")], categoria_id=row[headers.index("categoria_id")], 
                                            categoria_str=row[headers.index("categoria_str")])
            
            print("Procesando: " + juegocex["titulo"])

            try:
                procesador.process_item(juegocex, None, fecha)
            except DropItem:
                print("El juego %s no se encontró en IGDB" % juegocex["titulo"])
            except:
                print("Excepción no controlada")

            i += 1
            if i % 100 == 0:
                print("-------------------------------")
                print("    Consultados %d juegos" % i)
                print("-------------------------------")
            

    print("Games inserted: " + str(Juego.objects.count()))
    print("---------------------------------------------------------")

def populateDetails():
    print("Loading details....")
    
    with open(path+"/detalles.csv", "rt") as csvfile:
        detailsReader = csv.reader(csvfile, delimiter=',',  quotechar='"')
        next(detailsReader, None)
        for row in detailsReader:
            if Juego.objects.filter(pk=row[0]).exists():
                JuegoDetalles(juego=Juego.objects.get(pk=row[0]), detalle=row[1]).save()

    print("Details inserted: " + str(JuegoDetalles.objects.count()))
    print("---------------------------------------------------------")
    
    
#Función que carga los datos
def populateDatabase():
    populatePlatforms()
    populateCategories()
    populateGenres()
    populateThemes()
    populateKeywords()
    populateCompanies()
    populateCrawlings('2016-12-22.csv')

    
    print("Finished database population")
    
if __name__ == '__main__':
    populateDatabase()