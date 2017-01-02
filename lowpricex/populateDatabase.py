#encoding:utf-8
from lowpricex_app.models import Plataforma, Juego, HistoricoJuego
import csv
from datetime import datetime

path = "data"


def populatePlatforms():
    print("Loading platforms....")
    
    with open(path+"/platforms.csv", "rt") as csvfile:
        platformsReader = csv.reader(csvfile, delimiter=';')
        next(platformsReader, None)
        for row in platformsReader:
            Plataforma(idPlataforma=row[0], nombre=row[1], abreviatura=row[2], logo=row[3]).save()

    print("Platform inserted: " + str(Plataforma.objects.count()))
    print("---------------------------------------------------------")



def insertarHistorico(fecha, precioVenta, precioIntercambio, precioCompra, juego):
    HistoricoJuego(juego=juego, fecha=fecha, precioVenta=precioVenta, precioIntercambio=precioIntercambio, precioCompra=precioCompra).save()
    juego.precioVenta = precioVenta
    juego.precioIntercambio = precioIntercambio
    juego.precioCompra = precioCompra
    juego.actualizado = fecha
    juego.save()

def populateCrawlings(file):
    fecha = datetime.strptime(file.split(".")[0], '%Y-%m-%d').date()
    
    with open(path+"/"+file, "rt") as csvfile:
        fileReader = csv.reader(csvfile, delimiter=",", quotechar='"')
        next(fileReader, None)
        for row in fileReader:
            if not row[6].isdigit():
                continue
            
            print(row[5])
            
            plataforma = Plataforma.objects.get(pk=row[0])
            precioVenta = float(row[1])
            precioIntercambio = float(row[3])
            precioCompra = float(row[4])
            nombre = row[5]
            sku = int(row[6])
            imagenCaratula = "https://es.webuy.com" + row[7]
            
            #Si no existe el juego en la base de datos, lo damos de alta.            
            if not Juego.objects.filter(pk=sku).exists():
                Juego(sku=sku, plataforma=plataforma, nombre=nombre, portada=imagenCaratula, precioVenta=precioVenta, precioCompra=precioCompra, precioIntercambio=precioIntercambio, actualizado=fecha).save()
            
            #Obtenemos el juego que estamos tratando
            juego = Juego.objects.get(pk=sku)
            
            try:
                # Si hay histórico obtenemos el más reciente
                hJuego = HistoricoJuego.objects.filter(juego=sku).order_by('-fecha')[:1].get()

                # Si el más reciente tiene ALGO diferente, lo metemos en el histórico y actualizamos el registro
                if hJuego.juego.actualizado > fecha and (hJuego.precioCompra != precioCompra or hJuego.precioIntercambio != precioIntercambio or hJuego.precioVenta != precioVenta):
                    insertarHistorico(fecha, precioVenta, precioIntercambio, precioCompra, juego)
                     
            except:
                insertarHistorico(fecha, precioVenta, precioIntercambio, precioCompra, juego)

    print("Games inserted: " + str(Juego.objects.count()))
    print("---------------------------------------------------------")

    
    #Función que carga los datos
def populateDatabase():
    populatePlatforms()
    #populateCrawlings('2016-12-31.csv')

    
    print("Finished database population")
    
if __name__ == '__main__':
    populateDatabase()