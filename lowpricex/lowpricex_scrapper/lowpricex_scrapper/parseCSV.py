from pipelines         import ProcesadorJuegos
from items             import JuegoCEX
from scrapy.exceptions import DropItem

import csv

ruta_csv = "/home/usuario/Escritorio/2016-12-25.csv"
procesador = ProcesadorJuegos()

with open(ruta_csv, "r") as csvfile:
    i = 0
    data = csv.reader(csvfile.readlines())
    for line in data:

        if i == 0:
            headers = line
        else:
            juego = JuegoCEX()
            for k in range(0, len(line)):
                juego[headers[k]] = line[k]
            
            try:
                procesador.process_item(juego, None)
            except DropItem:
                pass
        i += 1

        if i % 1000 == 0:
            print("Procesados %d juegos" % i)
        

    print("Procesamiento terminado")
