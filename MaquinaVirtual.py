#Maquina virtual para la ejcucion de los programas en lenguaje KPP
#Desarrollado por Jose Kovacevich
#
#Proyecto de Diseno de Compiladores
#Noviembre 10, 2015
import sys
from MapaMemoria import MemoryMap

#Objeto de cuadruplo a utilizar al interpretar
cuadruploActual = []

#Inicializacion del mapa de memoria
memoria = MemoryMap()

#Para llevar registro del cuadruplo en ejecucion
programCounter = 0

#Para llevar registro del cuadruplo donde se salto a funcion
pilaSaltosRutinas = []

#Funcion en curso
bufferFunciones = []

#Suma de dos elementos
def suma():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = memoria.read(op2) + memoria.read(op1)

    #Operador 1 y 2 son dirs
    elif isinstance(op1, str) and op1[0] == "[" and op1[-1] == "]" and isinstance(op2, str) and op2[0] == "[" and op2[-1] == "]":
        op1 = int(op1.translate(None, "[]"))
        op2 = int(op2.translate(None, "[]"))
        tmp = op1 + op2

    #Operador 1 indirecto, 2 dir
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "[" and op2[-1] == "]":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        op2 = int(op2.translate(None, "[]"))
        tmp = memoria.read(op1) + op2
    #Operador 2 dir y 2 indirecto
    elif isinstance(op1, str) and op1[0] == "[" and op1[-1] == "]" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        op1 = int(op1.translate(None, "[]"))
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = op1 + memoria.read(op2)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        tmp = memoria.read(op1) + memoria.read(op2)

    #Si es una direccion a la que se llama
    elif isinstance(op1, str) and op1[0] == "[" and op1[-1] == "]":
        op1 = int(op1.translate(None, "[]"))
        tmp = op1 + memoria.read(op2)

    #Operador 2 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = memoria.read(op2) + memoria.read(op1)

    #Si es una direccion a la que se llama
    elif isinstance(op2, str) and op2[0] == "[" and op2[-1] == "]":
        op2 = int(op2.translate(None, "[]"))
        tmp = op2 + memoria.read(op1)

    #Caso normal
    else:
        tmp = memoria.read(op1) + memoria.read(op2)

    memoria.save(res, tmp)
    return programCounter + 1

#Resta de dos elementos
def resta():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = memoria.read(op2) - memoria.read(op1)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        tmp = memoria.read(op1) - memoria.read(op2)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = memoria.read(op2) - memoria.read(op1)

    #Caso normal
    else:
        tmp = memoria.read(op1) - memoria.read(op2)

    memoria.save(res, tmp)
    return programCounter + 1

#Multiplicacion de dos elementos
def multiplicacion():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = memoria.read(op2) * memoria.read(op1)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        tmp = memoria.read(op1) * memoria.read(op2)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = memoria.read(op2) * memoria.read(op1)

    #Caso normal
    else:
        tmp = memoria.read(op1) * memoria.read(op2)

    memoria.save(res, tmp)
    return programCounter + 1

#Division de dos elementos
def division():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = memoria.read(op2) / memoria.read(op1)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        tmp = memoria.read(op1) / memoria.read(op2)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)
        tmp = memoria.read(op2) / memoria.read(op1)

    #Caso normal
    else:
        tmp = memoria.read(op1) / memoria.read(op2)

    memoria.save(res, tmp)
    return programCounter + 1

#Se asigna una variable/constante/arreglo/etc.
def asignacion():

    tmp = cuadruploActual[1]
    dirFinal = cuadruploActual[2]

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    if isinstance(tmp, str) and tmp[0] == "(" and tmp[-1] == ")":
        indAddr = int(tmp.translate(None, "()"))
        tmp = memoria.read(indAddr)
        memoria.save(dirFinal, memoria.read(tmp))

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(dirFinal, str) and dirFinal[0] == "(" and dirFinal[-1] == ")":
        indAddr = int(dirFinal.translate(None, "()"))
        dirFinal = memoria.read(indAddr)
        tmp = memoria.read(tmp)
        memoria.save(dirFinal, tmp)

    #Caso normal
    else:
        data = memoria.read(tmp)
        memoria.save(dirFinal, data)

    return programCounter + 1

#Entrada de consola
def entrada():
    tipo = cuadruploActual[1]
    temp = cuadruploActual[2]

    if tipo == 1000:
        tipo = int
    elif tipo == 2000:
        tipo = float
    else:
        tipo = str

    data = raw_input("Entrada: ")

    memoria.save(temp, tipo(data))
    return programCounter + 1

#Operacion logica de >
def mayorQue():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    if memoria.read(op1) > memoria.read(op2):
        tmp = 1
    else:
        tmp = 0

    memoria.save(res, tmp)
    return programCounter + 1

#Operacion logica de <
def menorQue():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    if memoria.read(op1) < memoria.read(op2):
        tmp = 1
    else:
        tmp = 0

    memoria.save(res, tmp)
    return programCounter + 1

#Operacion logica de ==
def igualIgual():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    if memoria.read(op1) == memoria.read(op2):
        tmp = 1
    else:
        tmp = 0

    memoria.save(res, tmp)
    return programCounter + 1

#Print en consola
def imprime():
    #Deberia ser una direccion lo que hay.. se saca de la memoria
    direccion = cuadruploActual[1]

    if isinstance(direccion, str) and direccion[0] == "(" and direccion[-1] == ")":
        direccion = int(direccion.translate(None, "()"))
        dir2 = memoria.read(direccion)
        dato = memoria.read(dir2)
    else:
        dato = memoria.read(direccion)

    #Se imprime
    print dato

    #Solo 1 salto para esta instruccion
    return programCounter + 1

#Salto del goto normal
def saltoBasico():
    return cuadruploActual[1]

#Salto del goto en falso
def saltoFalso():
    condicion = cuadruploActual[1]

    if memoria.read(condicion) == 1:
        return programCounter + 1
    else:
        return cuadruploActual[2]

#Cuando se va a saltar a una rutina, se prepara la memoria
def inicioRutina():
    #Se guarda e instancia una nueva memoria local
    memoria.saveCurrentMemory()
    memoria.newLocalMemory()

    return programCounter + 1

#Salto a subrutina (funcion)
def saltoRutina():
    #Se guarda donde iba cuando salto + 1
    pilaSaltosRutinas.append(programCounter + 1)

    #Se guarda el nombre actual (para retornos)
    bufferFunciones.append(cuadruploActual[1])

    #Se regresa el nuevo apuntador a cuadruplo
    return cuadruploActual[2]

#Se guarda el valor que debera regresar la rutina
def retornoRutina():
    addrRet = cuadruploActual[1]

    dato = memoria.read(addrRet)

    memoria.save(bufferFunciones.pop(), dato)

    return programCounter + 1

#Se obtiene la ubicacion de donde se inicio la rutina y se continua a partir de ahi
def finRutina():
    #Se borra la memoria local actual y se reestablece la anterior
    memoria.newLocalMemory()
    memoria.restoreLastMemory()

    #Se regresa el cuadruplo en el que se iba antes
    return pilaSaltosRutinas.pop()

#Se cargan a memoria local los parametros de la llamada a uan funcion
def cargaParametro():
    #Se mantiene presente la ultima memoria por si un argumento viene de una temporal anterior
    lastMem = memoria.stackMemoria[-1].copy()

    tempMem = MemoryMap()

    tempMem.locales = lastMem
    tempMem.globales = memoria.globales
    tempMem.constantes = memoria.constantes
    tempMem.temporales = memoria.temporales

    #Se lee las direcciones y se asignan a locales en las direcciones de los parametros
    valor = cuadruploActual[1]
    dirLocal = cuadruploActual[2]
    dato = tempMem.read(valor)

    #Se guarda en la instancia local el dato
    memoria.save(dirLocal, dato)

    tempMem.newLocalMemory()

    return programCounter + 1

#Se verifican los limites de los arreglos
def verificaLimite():
    addr = cuadruploActual[1]
    limite = cuadruploActual[2]

    callSize = memoria.read(addr)

    if 0 <= callSize < limite:
        return programCounter + 1
    else:
        print "Error! Indice fuera de rango"
        sys.exit()

#Operacion de AND logico
def andLogico():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    if memoria.read(op1) != 0 and memoria.read(op2)!= 0:
        tmp = 1
    else:
        tmp = 0

    memoria.save(res, tmp)
    return programCounter + 1

#Operacion de OR logico
def orLogico():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    if memoria.read(op1) != 0 or memoria.read(op2) != 0:
        tmp = 1
    else:
        tmp = 0

    memoria.save(res, tmp)
    return programCounter + 1

#Operacion de != logico
def diffLogico():
    op1 = cuadruploActual[1]
    op2 = cuadruploActual[2]
    res = cuadruploActual[3]

    #Operador 1 y 2 son indirectos
    if isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")" and isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    #Operador 1 es especial
    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op1, str) and op1[0] == "(" and op1[-1] == ")":
        indAddr = int(op1.translate(None, "()"))
        op1 = memoria.read(indAddr)

    #Si es una direccion que tiene guardada otra direccion (indirecto)
    elif isinstance(op2, str) and op2[0] == "(" and op2[-1] == ")":
        indAddr = int(op2.translate(None, "()"))
        op2 = memoria.read(indAddr)

    if memoria.read(op1) != memoria.read(op2):
        tmp = 1
    else:
        tmp = 0

    memoria.save(res, tmp)
    return programCounter + 1

#Switch de todas las operaciones permitidas por el lenguaje
acciones = {
    "+" : suma,
    "-" : resta,
    "*" : multiplicacion,
    "/" : division,
    "=" : asignacion,
    ">" : mayorQue,
    "<" : menorQue,
    "==" : igualIgual,
    "&" : andLogico,
    "|" : orLogico,
    "<>" : diffLogico,
    "print" : imprime,
    "input" : entrada,
    "goto" : saltoBasico,
    "gotoF" : saltoFalso,
    "gosub" : saltoRutina,
    "param" : cargaParametro,
    "return" : retornoRutina,
    "RET" : finRutina,
    "era" : inicioRutina,
    "ver" : verificaLimite
}

class virtualMachine:

    def __init__(self, consts, prog):
            #Tablas con informacion de los metodos/constantes/variables
            self.constantes = consts

            #Cuadruplos del programa a ejecutar
            self.programa = prog

            #Se inicializa la memoria con las constantes
            memoria.constantes = self.constantes

    @staticmethod
    def ejecutaCuad(cuad):
        #Se guarda el cuadruplo que esta por ejecutarse para lo que puedan usarse
        global cuadruploActual
        cuadruploActual = cuad

        #Se obtiene la instruccion para el switch
        instruccion = cuad[0]

        #Se ejecuta el cuadruplo
        return acciones[instruccion]()

    def correPrograma(self):
        #El programCounter apunta al cuadruplo que se va a ejecutar
        global programCounter
        print "Ejecutando programa...\n"
        #Se ejecuta cada uno de los cuadruplos del programa
        while programCounter < len(self.programa):
            programCounter = self.ejecutaCuad(self.programa[programCounter])
