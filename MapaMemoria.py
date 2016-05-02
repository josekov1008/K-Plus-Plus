#Mapa de memoria para el compilador KPP
#Desarrollado por Jose Kovacevich
#
#Proyecto de Diseno de Compiladores
#Noviembre 7, 2015

#Especificaciones de direcciones virtuales

#
#Dir Virtual       |   Tipo de Memoria
#------------------|---------------------
#0 - 5000          |   Vars. Locales
#10000 - 15000     |   Vars. Globales
#20000 - 25000     |   Temporales
#30000 - 35000     |   Constantes
#
#Cada memoria seguira sus tipos de datos para identificar y guardar
#cada uno de los tipos de dato

import sys

class MemoryMap:

    #Constructor del mapa, inicializa diccionarios en blanco que seran usados para guardar informacion
    def __init__(self):
        self.globales = {}
        self.locales = {}
        self.constantes = {}
        self.temporales = {}
        self.stackMemoria = []
        self.extras = {}

    #Se guarda la memoria actual... antes de invocar una funcion/metodo
    #Se guarda en el stackMemoria
    def saveCurrentMemory(self):
        self.stackMemoria.append(self.locales.copy())

    #Se limpia la memoria local... para el inicio de modulos y cosas asi
    #Se eliminan locales
    def newLocalMemory(self):
        self.locales.clear()

    #Se regresa la ultima memoria guardada en el stack
    def restoreLastMemory(self):
        self.locales = self.stackMemoria.pop()

    #Guarda un dato en la memoria del programa
    #Recibe una direccion y un dato y se guarda en el lugar apropiado
    def save(self, address, data):
        if isinstance(address, str):
            self.extras[address] = data
        else:
            if address <= 5000:
                self.locales[address] = data
            elif 10000 <= address <= 15000:
                self.globales[address] = data
            elif 20000 <= address <= 25000:
                self.temporales[address] = data
            elif 30000 <= address <= 35000:
                self.constantes[address] = data

    #Accesa a la memoria del programa
    #Recibe una direccion y se regresa el dato
    #En caso de no existir se truena la ejecucion
    def read(self, address):
        if isinstance(address, str):
            if self.extras.has_key(address):
                data = self.extras[address]

                #Si es string se quitan las comillas
                if isinstance(data, str) and '"' in data:
                    data = data.translate(None, '"')

                return data
            else:
                print "Error de retorno de", address
                sys.exit()
        elif address <= 5000:
            if self.locales.has_key(address):
                data = self.locales[address]

                #Si es string se quitan las comillas
                if isinstance(data, str) and '"' in data:
                    data = data.translate(None, '"')

                return data
            else:
                print "Error de acceso a memoria en direccion", address
                sys.exit()
        elif 10000 <= address <= 15000:
            if self.globales.has_key(address):
                data = self.globales[address]

                #Si es string se quitan las comillas
                if isinstance(data, str) and '"' in data:
                    data = data.translate(None, '"')

                return data
            else:
                print "Error de acceso a memoria en direccion", address
                sys.exit()
        elif 20000 <= address <= 25000:
            if self.temporales.has_key(address):
                data = self.temporales[address]

                #Si es string se quitan las comillas
                if isinstance(data, str) and '"' in data:
                    data = data.translate(None, '"')

                return data
            else:
                print "Error de acceso a memoria en direccion", address
                sys.exit()
        elif 30000 <= address <= 35000:
            if self.constantes.has_key(address):

                data = self.constantes[address]

                #Si es string se quitan las comillas
                if isinstance(data, str) and '"' in data:
                    data = data.translate(None, '"')

                return data
            else:
                print "Error de acceso a memoria en direccion", address
                sys.exit()
