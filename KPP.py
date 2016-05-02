#Compilador para el lenguaje de entrada visual KPP
#Desarrollado por Jose Kovacevich
#
#Proyecto de Diseno de Compiladores
#Septiembre 30, 2015

import sys
import ply.lex as lex
import ply.yacc as yacc
import dataMatches
from MaquinaVirtual import virtualMachine

#############################################################################################
#Definicion del lexico del lenguaje
#############################################################################################

#Lista de tokens posibles
reserved = {
   'if' : 'IF',
   'else' : 'ELSE',
   'while' : 'WHILE',
   'return' : 'RETURN',
   'print' : 'PRINT',
   'input' : 'INPUT',
   'int' : 'TIPO_INT',
   'float' : 'TIPO_FLOAT',
   'char' : 'TIPO_CHAR',
   'string' : 'TIPO_STRING',
   'void' : 'TIPO_VOID',
   'main' : 'MAIN'
}

tokens = ['INT', 'STRING', 'CHAR', 'FLOAT', 'DELIMITADOR_CUADRADO', 'DELIMITADOR_CUADRADO_CERRAR',
          'DELIMITADOR_ABRIR', 'DELIMITADOR_CERRAR', 'SEPARADOR', 'OPERADOR_MD', 'OPERADOR_SR',
          'OPERADOR_LOGICO', 'OPERADOR_ANDOR', 'IDENTIFICADOR',
          'OPERADOR_ASIGNACION', 'FIN_LINEA', 'DELIMITADOR_LLAVES'] + list(reserved.values()) ##Checar que hacer con MAIN D:

#Caracteres a ignorar
t_ignore = ' \t\n'

#Identificadores y palabras reservadas
def t_IDENTIFICADOR(token):
    r'[a-zA-Z][a-zA-Z0-9]*'
    token.type = reserved.get(token.value,'IDENTIFICADOR')    # Se checa por palabras reservadas en la lista inicial
    return token

#Constantes
#Flotantes (punto decimal)
def t_FLOAT(token):
    r'[0-9]*\.[0-9]+'
    token.value = float(token.value)
    return token
#Enteras
def t_INT(token):
    r'[0-9]+'
    token.value = int(token.value)
    return token
#Characteres ASCII
def t_CHAR(token):
    r'\'[a-zA-Z0-9]\''
    return token
#Cadenas de caracteres
def t_STRING(token):
    r'"[A-Za-z0-9 ]+"'
    return token

#Operadores agrupados por prioridades
#Suma/Resta
def t_OPERADOR_SR(token):
    r'\+|\-'
    return token
#Multiplicacion/Division
def t_OPERADOR_MD(token):
    r'\*|/'
    return token
#Operadores logicos mayor/menor/igual/diferente que
def t_OPERADOR_LOGICO(token):
    r'<>|==|<|>'
    return token
#Operadores AND/OR
def t_OPERADOR_ANDOR(token):
    r'&|\|'
    return token
#Operador de asignacion =
def t_OPERADOR_ASIGNACION(token):
    r'='
    return token

#Otros simbolos
#Delimitadores de arreglos
def t_DELIMITADOR_CUADRADO(token):
    r'\['
    return token

def t_DELIMITADOR_CUADRADO_CERRAR(token):
    r'\]'
    return token
#Parentesis
def t_DELIMITADOR_ABRIR(token):
    r'\('
    return token

def t_DELIMITADOR_CERRAR(token):
    r'\)'
    return token
#Llaves
def t_DELIMITADOR_LLAVES(token):
    r'\{|\}'
    return token
#Punto y coma al final de los estatutos
def t_FIN_LINEA(token):
    r'\;'
    return token
#Coma para separar argumentos
def t_SEPARADOR(token):
    r'\,'
    return token

#Para segmentos de codigo hay que hacer una funcion
def t_error(t):
    print 'Error de sintaxis en entrada: Caracter Invalido ', t.value[0]
    sys.exit()

#############################################################################################
#Funciones auxiliares para la gramatica
#############################################################################################
#Contadores de direcciones virtuales
#Locales
dirInt = 0
dirFloat = 1000
dirChar = 2000
dirString = 3000
#Globales
dirGlobalInt = 10000
dirGlobalFloat = 11000
dirGlobalChar = 12000
dirGlobalString = 13000
#Temporales
dirTempInt = 20000
dirTempFloat = 21000
dirTempChar = 22000
dirTempString = 23000
#Constantes
dirCteInt = 30000
dirCteFloat = 31000
dirCteChar = 32000
dirCteString = 33000

#Tablas de constantes, variables y procs, tamanos para mantener track de los arreglos
procedures = { }
variables = { }
constantes = { }
variableSizes = { }

#Usados para identificacion de declaraciones y de tipos
calledVars = []
calledProcs = { }
orderParamsBuffer = []

#Usaro para identificacion de variables no declaradas en metodos
undeclaredVars = []
undeclaredProcs = []

#Generacion de cuadruplos
bufferCuadruplos = []
cuadruplos = [['goto', -1]] #Cuadruplo inicial va a ser el salto al main

contTemp = 1 #Para llevar un conteo de cuantos temporales seran necesarios

#Bufers utilizados para mantener control de los operandos de cada una de las operaciones posibles
bufferMD = []
bufferSR = []
bufferLogico = []
bufferANDOR = []

#Contadores utilizados para los cuadruplos
cuadruploActual = 1 #El 0 es el salto al main
cuadMain = 0
numParam = 0

#Pila de saltos... para los saltos (goto, gotoF, etc.)
pSaltos = []

#Generacion de cuadruplos para funciones
pilaCuadInicio = []
pilaTamsFuncion = []

#Encapsula el proceso de verificar si existe la variable en el scope
#Checa en el scope local dado y en el scope global
#Recibe como argumento una variable o cadena de operaciones y el scope de la funcion en donde se llama
def isDeclared(var, scope):
    if var[0] in variables[scope]:
        type1 = getTypeVariable(variables[scope][var[0]])
        type2 = opsToType(var[1], scope)

        if isCompatible(type1 / 1000, type2 / 1000, 6, "asignacion"):
            return True

    elif 'global' in variables.keys():
        if var[0] in variables['global']:
            type1 = getTypeVariable(variables['global'][var[0]])
            type2 = opsToType(var[1], 'global')

            if isCompatible(type1 / 1000, type2 / 1000, 6, "asignacion"):
                return True
        else:
            return False
    else:
        return False

#Obtiene el tipo de una variable en base a un nombre dado
#Busca en el scope y en las globales para ver si existe
#Recibe como argumento una variable y el scope donde esta ha sido llamada
def getTypeVariableName(var, scope):
    if var[0] in variables[scope]:
        return getTypeVariable(variables[scope][var[0]])

    elif 'global' in variables.keys():
        if var[0] in variables['global']:
            return getTypeVariable(variables['global'][var[0]])

#Funcion para consultar el cubo de tipos
#Regresa el resultado correspondiente de acuerdo a lo establecido en el cubo de datos
#Recibe como argumentos los dos operandos, el tipo de operador y un mensaje para mostrar
#en caso de que los operandos no sean compatibles entre si
#Regresa el tipo de dato resultante en caso de ser compatibles
def isCompatible(op1, op2, operator, message):
    #Ver si hay una manera de guardar valores, una pila tal vez? seria ejecutar?
    if dataMatches.getResultType(op1, op2, operator) == -1:
        print "Error! Tipos no compatibles en operacion de", message
        sys.exit()
    else:
        return dataMatches.getResultType(op1, op2, operator) * 1000

#Funcion para asignar una direccion local en base al tipo de asignacion
#Actualiza los contadores apropiados segun se requiera
#Recibe como argumentos el tipo de variable y un tamano, regresa una direccion valida
def assignAddress(tipo, tam):
    if tipo == 'int':
        global dirInt
        dirInt += tam
        return dirInt - tam
    elif tipo == 'float':
        global dirFloat
        dirFloat += tam
        return dirFloat - tam
    elif tipo == 'char':
        global dirChar
        dirChar += tam
        return dirChar - tam
    else:
        global dirString
        dirString += tam
        return dirString - tam

#Funcion para asignar una direccion global en base al tipo de asignacion
#Actualiza los contadores apropiados segun se requiera
#Recibe como argumentos el tipo de variable y un tamano, regresa una direccion valida
def assignGlobalAddress(tipo, tam):
    if tipo == 'int':
        global dirGlobalInt
        dirGlobalInt += tam
        return dirGlobalInt - tam
    elif tipo == 'float':
        global dirGlobalFloat
        dirGlobalFloat += tam
        return dirGlobalFloat - tam
    elif tipo == 'char':
        global dirGlobalChar
        dirGlobalChar += tam
        return dirGlobalChar - tam
    else:
        global dirGlobalString
        dirGlobalString += tam
        return dirGlobalString - tam

#Funcion para asignar una direccion temporal en base al tipo de asignacion
#Actualiza los contadores apropiados segun se requiera
#Recibe como argumentos el tipo de variable, regresa una direccion valida
def assignTempAddress(tipo):
    if tipo == 'int':
        global dirTempInt
        dirTempInt += 1
        return dirTempInt - 1
    elif tipo == 'float':
        global dirTempFloat
        dirTempFloat += 1
        return dirTempFloat - 1
    elif tipo == 'char':
        global dirTempChar
        dirTempChar += 1
        return dirTempChar - 1
    else:
        global dirTempString
        dirTempString += 1
        return dirTempString - 1

#Funcion para asignar una direccion para las constantes en base a su tipo
#Actualiza los contadores apropiados segun se requiera
#Recibe como argumentos el tipo de variable, regresa una direccion valida
def assignConstantAddress(tipo):
    if tipo == 'int':
        global dirCteInt
        dirCteInt += 1
        return dirCteInt - 1
    elif tipo == 'float':
        global dirCteFloat
        dirCteFloat += 1
        return dirCteFloat - 1
    elif tipo == 'char':
        global dirCteChar
        dirCteChar += 1
        return dirCteChar - 1
    else:
        global dirCteString
        dirCteString += 1
        return dirCteString - 1

#Obtiene el identificador de tipo (numerico) a base de la direccion
#Recibe como parametro la direccion de una variables
#Regresa el tipo de la variable
def getTypeVariable(address):
    if address < 1000 or 10000 <= address < 11000 or 20000 <= address < 21000 or 30000 <= address < 31000:
        return 1000
    elif 1000 <= address < 2000 or 11000 <= address < 12000 or 21000 <= address < 22000 or 31000 <= address < 32000:
        return 2000
    elif 2000 <= address < 3000 or 12000 <= address < 13000 or 22000 <= address < 23000 or 32000 <= address < 33000:
        return 3000
    else:
        return 4000

#Se obtiene el tipo a base del nombre de una variable
#Recibe como parametro el nombre de la variable
#Regresa el identificador de tipo
def getTypeName(tipoId):
    if tipoId == 1000:
        return 'int'
    elif tipoId == 2000:
        return 'float'
    elif tipoId == 3000:
        return 'char'
    elif tipoId == 4000:
        return 'string'
    else:
        return 'void'

#Se obtienen las claves para cada tipo de dato posible
#Recibe como parametro el tipo
#Regresa la clave del tipo
def getTypeId(tipo):
    if tipo == 'int':
        return 1000
    elif tipo == 'float':
        return 2000
    elif tipo == 'char':
        return 3000
    elif tipo == 'string':
        return 4000
    elif tipo == 'void':
        return 5000

#Interpretar las cadenas de operaciones almacenadas en diccionarios para determinar el tipo
#en el que resultara la operacion realizada
#Recibe como parametro una cadena de operaciones y un scope de donde fue realizada
#Regresa el tipo que debera tener el resultado
def opsToType(d, scope):
    #Si ya es un tipo
    if isinstance(d, int):
        return d
    #Si es una lista de operaciones
    elif isinstance(d, list):
        print d
    #Si hay otra variable de por medio
    elif isinstance(d, dict):
        var1 = d.keys()[0]

        #Esto puede fallar si es que existiera una variable que tuviera un nombre igual a una funcion y/o parametro
        #Se busca la variable en las declaraciones
        if var1 in variables[scope].keys():
            type1 = getTypeVariable(variables[scope][var1])
            return opsToTypeAux(d[var1], type1, scope)

        #Es funcion si tiene el 9999 en la llamada
        elif (var1 in procedures.keys() and d[var1].has_key(9999)) or (var1 == -1 and d[var1].has_key(9999)):
            #Se verifican los argumentos con los llamados
            if d[var1][9999] is not None:
                argsCalled = d[var1][9999]
                funcArgs = list(procedures[var1]['params'].values())

                #Si los argumentos dados no son el mismo numero de los esperados
                if len(argsCalled) != len(funcArgs):
                    print "Error! cantidad de argumentos en funcion", var1
                    sys.exit()

                for arg in argsCalled:
                    #Si el arg es una variable, checar que este declarada
                    if isinstance(arg, dict):
                        if isDeclared((arg.keys()[0], arg), scope):
                            arg = getTypeVariableName(arg.keys()[0], scope)
                        else:
                            print "Error! Argumento no declarado", arg.keys()[0]
                            sys.exit()

                    #Se verifica compatibilidad entre los argumentos esperados y los dados
                    for param in funcArgs:
                        if isCompatible(arg / 1000, getTypeVariable(param) / 1000, 6, "asignacion"):
                            funcArgs.remove(param)
                            break

                #Si se "consumieron" todos los argumentos
                if len(funcArgs) == 0:
                    return procedures[var1]['type']
                else:
                    print "Error! Inconsistencia de argumentos en funcion", var1
                    sys.exit()
            else:
                #Checar que no se esperen argumentos y estos no vengan en la llamada
                if len(procedures[var1]['params'].keys()) == 0:
                    return procedures[var1]['type']
                else:
                    print "Error! Argumentos esperados para funcion",  var1
                    sys.exit()
        #Se busca en los argumentos del scope si no es main
        elif scope != "main" and procedures[scope].has_key('params'):
            if var1 in procedures[scope]['params']:
                type1 = getTypeVariable(procedures[scope]['params'][var1])
                return opsToTypeAux(d[var1], type1, scope)
        else:
            print "Error! variable/funcion no declarada", var1
            sys.exit()

#Se analiza la lista de tuplas que contiene operaciones que utilizan variables y/o arreglos
#Recibe como parametro una lista de operaciones, un tipo inicial (de la variable/funcion) y
#el scope de la llamada
#Regresa el tipo resultante de la lista de operaciones
def opsToTypeAux(listaOps, tipoInicial, scope):
    tipo1 = tipoInicial

    for op in listaOps:
        operacion = op[0]

        if isinstance(op[1], dict):
            tipo2 = opsToType(op[1], scope)
        else:
            tipo2 = op[1]

        tipo1 = isCompatible(tipo1 / 1000, tipo2 / 1000, operacion, "asignacion")

    return tipo1

#Se crean el cuadruplo para la operacion especificada
#Recibe como argumento una lista que contiene el signo, o alguna otra informacion necesaria
#para crear el cuadruplo
#Agrega un cuadruplo a la lista de cuadruplos, cada cuadruplo es una lista
def makeCuadruple(signo):
    global bufferCuadruplos
    global contTemp
    global cuadruploActual

    opr = signo.pop()

    #Solo en el goto clasico, no hay que sacar nada de la pila de operaciones
    if opr == "goto":
        cuad = [opr, -1]
        pSaltos.append(cuadruploActual)
        cuadruplos.append(cuad)
        cuadruploActual += 1
    #Si la operacion es un ERA
    elif opr == "era":
        pilaTamsFuncion.append(cuadruploActual)
        cuad = [opr, signo.pop()]
        cuadruplos.append(cuad)
        cuadruploActual += 1
    #Saltos a subrutinas
    elif opr == "gosub":
        cuad = [opr, signo.pop(), -1]
        cuadruplos.append(cuad)
        cuadruploActual += 1
    #Parametros en llamadas a funcion
    elif opr == "param":
        global numParam
        param = bufferCuadruplos.pop()
        numPar = signo.pop() + str(numParam)
        cuad = [opr, param, numPar]
        cuadruplos.append(cuad)
        numParam -= 1
        cuadruploActual += 1
    #Verificacion de limites en arreglos
    elif opr == "ver":
        varName = signo.pop()
        offset = signo.pop()
        cuad = [opr, offset, varName]
        cuadruplos.append(cuad)
        cuadruploActual += 1
    #Si no fue ninguna de las anteriores (especiales) es una simple operacion
    #Se ve si hay cosas en le buffer de cuads
    elif len(bufferCuadruplos) > 0:
        op1 = bufferCuadruplos.pop()

        temp = "-0TMP" + str(contTemp) #Se crea el "identificador" del temporal

        #A la hora de asignar un cuad, validar si tiene resultado, y asignar temporal para guardarlo
        #Asignaciones
        if opr == "=":
            if len(bufferCuadruplos) > 0:
                op2 = bufferCuadruplos.pop()
                cuad = [opr, op2, op1]
        #Estatutos de impresion
        elif opr == "print":
            cuad = [opr, op1]
        #Estatutos de entrada
        elif opr == "input":
            cuad = [opr, getTypeId(op1), temp]
            bufferCuadruplos.append(temp)
            contTemp += 1
        #Salto en falso
        elif opr == "gotoF":
            cuad = [opr, op1, -1] #-1 denota que no ha sido completado el cuad
            pSaltos.append(cuadruploActual)
        #Default: Operaciones matematicas
        else:
            if len(bufferCuadruplos) > 0:
                op2 = bufferCuadruplos.pop()
                cuad = [opr, op2, op1, temp]
                bufferCuadruplos.append(temp)
                contTemp += 1

        cuadruplos.append(cuad)
        cuadruploActual += 1

##Funciones de postprocesamiento de los cuadruplos generados, agregan informacion faltantes

#Se agrega a los cuads de ERA el tamano de la funcion que estan creando
#Modifica el cuadruplo y lo actualiza en la lista de cuadruplos
def completaTamanosFuncs():
     while len(pilaTamsFuncion) > 0:
         salto = pilaTamsFuncion.pop()
         cuad = cuadruplos[salto]
         funcion = cuad[-1]
         if isinstance(funcion, basestring):
             tam = procedures[funcion]['size']
             cuad[-1] = tam
             cuadruplos[salto] = cuad

#Se completa el salto al main del inicio
#Modifica el cuadruplo y lo actualiza en la lista de cuadruplos
def completarSaltoMain(inicio):
    cuadInicial = cuadruplos[0]
    if cuadInicial[-1] == -1:
        cuadInicial[-1] = inicio
        cuadruplos[0] = cuadInicial

#Se agregan los saltos a subrutinas faltantes
#Modifica el cuadruplo y lo actualiza en la lista de cuadruplos
def completaSaltosFuncion():
    for cuad in cuadruplos:
        if cuad[0] == "gosub" and cuad[-1] == -1:
            funcion = cuad[1]
            dirInicio = procedures[funcion]['start']
            cuad[-1] = dirInicio
            idx = cuadruplos.index(cuad)
            cuadruplos[idx] = cuad

#Se obtiene el id de cada operador
#Se recibe como parametro un operador
#Se regresa la clave del operador compatible con el cubo de datos
def getOperator(opr):
    if opr == "+" or opr == "-":
        return 1
    elif opr == "*" or opr == "/":
        return 2
    elif opr == "&" or opr == "|":
        return 3
    elif opr == "<" or opr == ">":
        return 4
    elif opr == "==" or opr == "<>":
        return 5
    elif opr == "=":
        return 6

#Se asignan direcciones virtuales a los cuads que las requieran para los temps
#Modifica los cuadruplos necesarios y lo actualiza en la lista de cuadruplos
def generaTemps():
    tmpsAsignados = {}
    for cuad in list(cuadruplos):
        i = 1
        while i < len(cuad):
            tmp = cuad[i]
            #Se checa que tenga la etiqueta de temporal
            if isinstance(tmp, str) and "-0TMP" in tmp:
                limPar = False
                limCuad = False
                #Si son arreglos/apuntadores, se respetan los parentesis
                if tmp[0] == "(" and tmp[-1] == ")":
                    limPar = True
                    tmp = tmp.translate(None, "()")

                if tmp[0] == "[" and tmp[-1] == "]":
                    limCuad = True
                    tmp = tmp.translate(None, "[]")

                #Si ya se asigno ese temp, simplemente se obtiene la direccion previamente asignada
                if tmpsAsignados.has_key(tmp):
                    tmp = tmpsAsignados[tmp]
                else:
                    #Se obtiene el tipo esperado para reservar la direccion correcta
                    res = dataMatches.getResultType(getTypeVariable(cuad[1]), getTypeVariable(cuad[2]), getOperator(cuad[0]))
                    tmpAdr = assignTempAddress(res * 1000)
                    tmpsAsignados[tmp] = tmpAdr
                    tmp = tmpAdr
                idx = cuadruplos.index(cuad)

                if limPar:
                    cuad[i] = "(" + str(tmp) + ")"
                elif limCuad:
                    cuad[i] = "[" + str(tmp) + "]"
                else:
                    cuad[i] = tmp

                cuadruplos[idx] = cuad
            i += 1

#Obtiene el address de una variable en base a su numero de cuadruplo
#Recibe como parametro el nombre de la variable y el numero de cuadruplo en el que esta
#Regresa la direccion de una variable
def getVarAddr(var, numCuad):
    near = 999999999
    mainStart = cuadruplos[0][1]
    scopeVar = ""
    #Se busca cual es la funcion mas "cercana"
    for scope in variables.keys():
        if scope is not "main" and scope is not "global":
            start = procedures[scope]['start']
            if start <= numCuad and numCuad - start < near:
                scopeVar = scope
                near = numCuad - start

    #Se verifica si es posible que pertenezca al scope main
    if near == 999999999 or (numCuad >= mainStart and numCuad - mainStart < near):
        scopeVar = 'main'

    #Si son arreglos/apuntadores, se respetan los parentesis
    array = False
    delCuad = False
    if var[0] == "(" and var[-1] == ")":
        array = True
        var = var.translate(None, "[]")

    if var[0] == "[" and var[-1] == "]":
        array = True
        delCuad = True
        var = var.translate(None, "[]")

    if scopeVar is not "main" and scopeVar is not "global" and var in procedures[scopeVar]['params'].keys():
        #Si son arreglos/apuntadores, se respetan los parentesis
        if array:
            if delCuad:
                return "[" + str(procedures[scopeVar]['params'][var]) + "]"
            else:
                return "(" + str(procedures[scopeVar]['params'][var]) + ")"
        else:
            return procedures[scopeVar]['params'][var]
    elif scopeVar in variables.keys():
        if var in variables[scopeVar].keys():
            #Si son arreglos/apuntadores, se respetan los parentesis
            if array:
                if delCuad:
                    return "[" + str(variables[scopeVar][var]) + "]"
                else:
                    return "(" + str(variables[scopeVar][var]) + ")"
            else:
                return variables[scopeVar][var]
        else:
            if variables.has_key('global') and var in variables['global'].keys():
                #Si son arreglos/apuntadores, se respetan los parentesis
                if array:
                    if delCuad:
                        return "[" + str(variables['global'][var]) + "]"
                    else:
                        return "(" + str(variables['global'][var]) + ")"
                else:
                    return variables['global'][var]
            else:
                #Si son arreglos/apuntadores, se respetan los parentesis
                if array:
                    if delCuad:
                        return "[" + var + "]"
                    else:
                        return "(" + var + ")"
                else:
                    if var in procedures.keys() or "-" in var:
                        return var #Parche para funciones reemplazar por direccion de retorno o a ver que
                    else:
                        print "Error! Identificador no declarado", var
                        sys.exit()

#Se obtiene el tamano de la variable... para arreglos
#Obtiene el tamano de una variable en base a su cuadruplo/scope
#Recibe como parametro el identificador de la variable y el numero de cuadruplo en el que esta
#Regrsa el tamano de la variable/arreglo
def getVarSize(var, numCuad):
    near = 999999999
    mainStart = cuadruplos[0][1]
    scopeVar = ""

    for scope in variables.keys():
        if scope is not "main" and scope is not "global":
            start = procedures[scope]['start']
            if start <= numCuad and numCuad - start < near:
                scopeVar = scope
                near = numCuad - start

    if near == 999999999 or (numCuad >= mainStart and numCuad - mainStart < near):
        scopeVar = 'main'

    if variableSizes.has_key(scopeVar):
        if variableSizes[scopeVar].has_key(var):
            return variableSizes[scopeVar][var]

#Se cambian los identificadores de las variables por sus respectivas direcciones
#Se modifica cada cuadruplo y se actualiza en la lista global
def putAddrCuads():
    i = 0
    for cuad in cuadruplos:
        j = 1
        while j < len(cuad):
            if isinstance(cuad[j], str) and "-0TMP" not in cuad[j] and cuad[0] is not "gosub" and cuad[j] is not "param" and cuad[0] is not "ver":
                cuad[j] = getVarAddr(cuad[j], i)
            j += 1

        cuadruplos[i] = cuad
        i += 1

#Se completan los cuadruplos de ver para arreglos
#Se modifican los cuadruplos necesarios y se actualizan en la lista global
def verCuads():
    i = 0
    for cuad in cuadruplos:
        if cuad[0] == "ver":
            #Se identifican si son strings y se obtienen las direcciones
            if isinstance(cuad[2], str):
                cuad[2] = getVarSize(cuad[2], i)

            if isinstance(cuad[1], str):
                cuad[1] = getVarAddr(cuad[1], i)

        cuadruplos[i] = cuad
        i += 1

#Asigna los parametros en las llamadas a funcion utilizando una lista que determina
#el orden en el que son esperados por la funcion
#Modifica los cuadruplos param necesarios y actualiza en la lista global
def funcAnalysis():
    i = 0
    for cuad in cuadruplos:
        if cuad[0] == "param":

            keys = cuad[2].split("-")
            funcName = keys[0]
            paramNo = int(keys[1])
            paramName = procedures[funcName]['orderParams']
            paramName = paramName[paramNo]
            paramAdd = procedures[funcName]['params'][paramName]
            cuad[2] = paramAdd
            cuadruplos[i] = cuad
        i += 1

#############################################################################################
#Definicion de las reglas de la gramatica
#############################################################################################

#Programa
def p_programa(p):
    '''programa : programaX inicioMain DELIMITADOR_LLAVES bloqueCodigo DELIMITADOR_LLAVES'''

    #Se obtienen las variables declaradas
    mainVars = { }
    mainSizes = { }
    if p[4] is not None and p[4].has_key('tempVars'):
        localVars = p[4]['tempVars'].copy()
        del p[4]['tempVars']

        for varName in localVars.keys():
            code = localVars[varName]
            atts = code.split("-")
            addr = int(atts[0])
            varSize = int(atts[1])
            mainVars.update({varName : addr})
            mainSizes.update({varName : varSize})

    variables['main'] = mainVars
    variableSizes['main'] = mainSizes

    #Variables llamadas en el scope
    scope = 'main'
    if p[4] is not None and p[4].has_key('call'):
        #Si existe el scope, se busca ahi y en lo global
        if scope in variables.keys():
            for key in list(p[4]['call']):
                if isDeclared(key, scope):
                    p[4]['call'].remove(key)

        #Se verifica si son funciones de tipo void
        for key in list(p[4]['call']):
            if key[0] == -1:
                if opsToType(key[1], 'main'):
                    p[4]['call'].remove(key)

        #Si sobro alguna esta de mas
        if len(p[4]['call']) > 0:
            print "Error! Variable no declarada", p[4]['call'][0][0], "en el scope", scope
            sys.exit()


    for key in list(calledProcs.keys()):
        if key in procedures.keys() and procedures[key]['type'] == calledProcs[key]:
            del calledProcs[key]
        else:
            print "Error! Funcion no declarada:", key, "de tipo:", getTypeName(calledProcs[key])
            sys.exit()


    #Completar saltos a funcion
    completaTamanosFuncs()

    #Agregar salto inicial al main
    completarSaltoMain(p[2])

    #Se agregan las direcciones de las funciones
    completaSaltosFuncion()

    #Se completan los cuads de verificacion para arreglos
    verCuads()

    #Se agregan direcciones faltantes a los cuads
    putAddrCuads()

    #Se agregan direcciones de los temps
    generaTemps()

    #Se agregan las direcciones que se usaran para cada parametro
    funcAnalysis()

    print "Compilacion Exitosa!\n"

#Inicio del main para usarse al llenar su respectivo salto
def p_inicioMain(p):
    '''inicioMain : MAIN'''
    p[0] = cuadruploActual

#Variables globales y funciones
def p_programaX(p):
    '''programaX : tipo IDENTIFICADOR programaY programaX
                 | ''' #Epsilon
    global cuadMain
    cuadMain = cuadruploActual
    if len(p) > 3:
        if p[3] is not None:
            #Si es una declaracion de una variable global
            if p[3].has_key('var'):
                if p[3]['var'] == 'var':
                    size = 1
                else:
                    size = p[3]['var']

                del p[3]['var']

                dirDato = assignGlobalAddress(p[1], size)

                for key in p[3]:
                    if p[3][key] == 'var':
                        size = 1
                    else:
                        size = p[3][key]
                    p[3][key] = assignGlobalAddress(p[1], size)

                tempVars = {p[2] : dirDato}
                tempVars.update(p[3])

                #Se checa si hay un scope global
                if variables.has_key('global'):
                    globales = variables['global']
                    globales.update(tempVars)
                    variables['global'] = globales
                else:
                    variables['global'] = tempVars

            #Si es funcion
            else:
                size = 0
                thisElement = { }
                thisElement['type'] = getTypeId(p[1])

                if p[3].has_key('localVars'):
                    variables[p[2]] = {}
                    variableSizes[p[2]] = {}

                    if p[3]['localVars'] is not None:
                        localVars = p[3]['localVars'].copy()
                        del p[3]['localVars']

                        for varName in localVars.keys():
                            code = localVars[varName]
                            atts = code.split("-")
                            addr = int(atts[0])
                            varSize = int(atts[1])
                            variables[p[2]].update({varName : addr, 'size' : varSize})
                            variableSizes[p[2]].update({varName : varSize})
                            size += varSize

                    else:
                        localVars = { }
                        variables[p[2]] = localVars

                if p[3].has_key('params'):
                    thisElement['orderParams'] = p[3]['params']['orderParams']
                    del p[3]['params']['orderParams']
                    thisElement['params'] = p[3]['params']

                    size += len(p[3]['params'])
                else:
                    thisElement['params'] = { }

                thisElement['size'] = size

                thisElement['start'] = pilaCuadInicio.pop()

                procedures[p[2]] = thisElement

                scope = p[2]

                #Variables llamadas en el scope
                if p[3].has_key('calledVars'):
                    #Si existe el scope, se busca ahi y en lo global
                    if scope in variables.keys():
                        for key in list(p[3]['calledVars']):
                            if isDeclared(key, scope):
                                p[3]['calledVars'].remove(key)

                    #Se busca ahora en los parametros
                    if thisElement.has_key('params'):
                        if len(thisElement['params']) > 0:
                            for key in list(p[3]['calledVars']):
                                if key[0] in thisElement['params'].keys() and isCompatible(opsToType(key[1], scope) / 1000, getTypeVariable(p[3]['params'][key[0]]) / 1000, 6, "asignacion"):
                                    p[3]['calledVars'].remove(key)

                    #Se verifica si son funciones de tipo void
                    for key in list(p[3]['calledVars']):
                        if key[0] == -1:
                            if opsToType(key[1], scope):
                                p[3]['calledVars'].remove(key)

                    #Si sobro alguna esta de mas
                    if len(p[3]['calledVars']) > 0:
                        print "Error! Variable no declarada", p[3]['calledVars'][0][0], "en el scope", scope
                        sys.exit()

def p_programaY(p):
    '''programaY : var
                 | funcion'''
    p[0] = p[1]

#Bloque Codigo
def p_bloqueCodigo(p):
    '''bloqueCodigo : estatuto bloqueCodigo
                    | ''' #Epsilon

    if len(p) > 2:
        if p[1] is not None:
            tempBloque = p[1]
            #Si hubo llamadas a varialbes/funciones se crea o actualiza la lista total
            if p[2] is not None:
               if tempBloque.has_key('call') and p[2].has_key('call'):
                   listaTemp = tempBloque['call']
                   for call in p[2]['call']:
                       if call not in tempBloque['call']:
                           listaTemp.append(call)
                   tempBloque['call'] = listaTemp
                   del p[2]['call']
               else:
                   if p[2].has_key('call'):
                       tempBloque['call'] = p[2]['call']

               if tempBloque.has_key('tempVars') and p[2].has_key('tempVars'):
                   tempv1 = tempBloque['tempVars']
                   tempv2 = p[2]['tempVars']
                   tempv1.update(tempv2)
                   tempBloque['tempVars'] = tempv1
               else:
                   if p[2].has_key('tempVars'):
                       tempBloque['tempVars'] = p[2]['tempVars']

            p[0] = tempBloque
        else:
            if p[2] is not None:
                p[0] = p[2]

#Estatuto
def p_estatuto(p):
    '''estatuto : escritura
                | IDENTIFICADOR estatutoX
                | if
                | while
                | tipo IDENTIFICADOR var'''


    if len(p) > 3 and p[1] is not 'return':
        #Declaraciones de variables
        if p[3] is not None:
            if p[3].has_key('var'):

                if p[3]['var'] == 'var':
                    size = 1
                else:
                    size = p[3]['var']

                del p[3]['var']

                tempVars = {p[2] : str(assignAddress(p[1], size)) + "-" + str(size)}

                for key in p[3].copy():
                    if p[3][key] == 'var':
                        size = 1
                    else:
                        size = p[3][key]

                    p[3][key] = str(assignAddress(p[1], size)) + "-" + str(size)

                tempVars.update(p[3])

                p[0] = {'tempVars' : tempVars}
    #Asignacion y llamada a funcion
    elif len(p) > 2:
        if p[2].has_key(103):
            #Si es tupla es que es un array con offset
            if isinstance(p[2][103], tuple):
                offset = p[2][103][0]
                makeCuadruple([offset, p[1], 'ver'])
                bufferCuadruplos.append(offset)
                bufferCuadruplos.append("[" + p[1] + "]")
                makeCuadruple(['+'])
                tmp = bufferCuadruplos.pop()
                bufferCuadruplos.append("(" + str(tmp) + ")")
                makeCuadruple(['='])

            else:
                #Si no es una llamada normal
                res = p[2][103]

                bufferCuadruplos.append(p[1])
                makeCuadruple(["="])

                p[0] = {'call':[(p[1], res)]}
        elif p[2].has_key(105):

            if p[1] not in calledProcs.keys():
                calledProcs[p[1]] = p[2][105]

            #Se genera el cuadruplo ERA
            makeCuadruple([p[1], "era"])

            args = {}

            if p[2].has_key('args'):
                args = p[2]['args']
                params = args[9999]
                cantParams = len(params)
                i = 0
                global numParam
                numParam = cantParams - 1

                while i < cantParams:
                    makeCuadruple([p[1]+"-", "param"])
                    i += 1
            else:
                args[9999] = []

            #Se hace el cuadruplo del goto a la funcion
            makeCuadruple([p[1], "gosub"])

            #Se forma la llamada, el -1 denota que es una funcion de tipo void
            #Asi se sobrepasa el chequeo de tipos de retorno para las no-void
            p[0] = {'call' : [(-1, {p[1] : args})]}

    #Cualquiera de los otros estatutos, ya deberia venir bien formado
    elif len(p) > 1 and p[1] is not None:
        p[0] = p[1]


#Temporales, no deberia quedarse asi (la primera regla esta mal, debuggear)... parece que ya quedo :D
def p_estatutoX(p):
    '''estatutoX : DELIMITADOR_ABRIR constanteY DELIMITADOR_CERRAR FIN_LINEA
                 | asignacionX OPERADOR_ASIGNACION estatutoY'''
    #Si es asignacion
    if p[1] != '(':
        if p[1] is not None:
            p[0] = {103 : (p[1]['arr'], p[3])}
        else:
            p[0] = {103 : p[3]} #Codigo de asignacion
    else:
        if p[2] is not None:
            p[0] = {105 : 5000, 'args' : {9999 : p[2]}}
        else:
            p[0] = {105 : 5000} #Codigo de llamada a funcion, solo podrian ser voids


def p_estatutoY(p):
    '''estatutoY : input
                 | asignacionY FIN_LINEA'''

    p[0] = p[1]

#Funcion
def p_funcion(p):
    '''funcion : idFuncion inicioFuncion bloqueCodigo accionRetorno DELIMITADOR_LLAVES'''
    tempFunc = { }
    if p[1] is not None:
        tempFunc['params'] = p[1]
    if tempFunc is not None and p[3] is not None:
        if p[3].has_key('tempVars'):
            tempFunc['localVars'] = p[3]['tempVars']

        if p[3].has_key('call'):
            tempFunc['calledVars'] = p[3]['call']

    p[0] = tempFunc

def p_idFuncion(p):
    '''idFuncion : DELIMITADOR_ABRIR idFuncionX DELIMITADOR_CERRAR'''
    p[0] = p[2]

def p_idFuncionX(p):
    '''idFuncionX : tipo nomParametro idFuncionZ idFuncionY
                  | ''' #Epsilon
    if len(p) > 2:
        temp = {p[2] : assignAddress(p[1], 1)}
        temp.update(p[4])

        if not temp.has_key('orderParams'):
            temp['orderParams'] = list(orderParamsBuffer)

        p[0] = temp

def p_nomParametro(p):
    '''nomParametro : IDENTIFICADOR'''
    orderParamsBuffer.append(p[1])
    p[0] = p[1]

def p_idFuncionY(p):
    '''idFuncionY : nextParam idFuncionX
                  | ''' #Epsilon
    if len(p) > 2:
        p[0] = p[2]
    else:
        p[0] = { }

def p_nextParam(p):
    '''nextParam : SEPARADOR'''

def p_idFuncionZ(p):
    '''idFuncionZ : DELIMITADOR_CUADRADO exp DELIMITADOR_CUADRADO_CERRAR
                  | ''' #Epsilon

def p_inicioFuncion(p):
    '''inicioFuncion : DELIMITADOR_LLAVES'''
    pilaCuadInicio.append(cuadruploActual)

def p_accionRetorno(p):
    '''accionRetorno : RETURN accionRetornoX FIN_LINEA'''

def p_accionRetornoX(p):
    '''accionRetornoX : constante
                      | '''
    #Aqui se insertara el cuad del return (pendiente)
    global cuadruploActual
    if len(p) > 1 and p[1] is not None:
        retorno = bufferCuadruplos.pop()
        cuadruplos.append(["return", retorno])
        cuadruploActual += 1

    cuadruplos.append(["RET"])
    cuadruploActual += 1
    del orderParamsBuffer[:]

#Variables
def p_var(p):
    '''var : varX FIN_LINEA'''
    p[0] = p[1]

def p_varX(p):
    '''varX : varY varZ'''
    varsDict = { 'var' : 'var'}

    if p[1] is not None:
        varsDict['var'] = p[1]

    varsDict.update(p[2])
    p[0] = varsDict

def p_varY(p):
    '''varY : DELIMITADOR_CUADRADO exp DELIMITADOR_CUADRADO_CERRAR
            | ''' #Epsilon
    if len(p) > 1:
        sizeAddr = bufferCuadruplos.pop()
        if sizeAddr >= 30000:
            sizeArr = constantes[sizeAddr]
            p[0] = sizeArr
        else:
            p[0] = p[2]

def p_varZ(p):
    '''varZ : SEPARADOR IDENTIFICADOR varX
            | ''' #Epsilon
    if len(p) > 3:
        tmpDir = { p[2] : 'var' }

        if p[3] is not None:
            if p[3].has_key('var'):
                tmpDir[p[2]] = p[3]['var']
                del p[3]['var']
                tmpDir.update(p[3])

        p[0] = tmpDir
    else:
        p[0] = { }

#Operacion
def p_operacion(p):
    '''operacion : expresion operacionX'''
    if len(p) > 2:
        #Si son dos o mas operandos, se verifica que sean compatibles
        if p[2] is not None:
            #Si es dict es porque es variable, se trata diferente
            if isinstance(p[1], dict):
                idVar = p[1].keys()[0]
                ops = p[1].values()[0]

                if isinstance(ops, dict) and ops.has_key(9999):
                    makeCuadruple(bufferANDOR)
                    p[0] = p[1]
                else:
                    ops.append( (3, p[2]) )
                    makeCuadruple(bufferANDOR)
                    p[0] = {idVar : ops}

            elif isinstance(p[2], dict):
                idVar = p[2].keys()[0]
                ops = p[2].values()[0]

                if isinstance(ops, dict) and ops.has_key(9999):
                    p[0] = p[2]
                else:
                    ops.append( (3, p[1]) )
                    makeCuadruple(bufferANDOR)
                    p[0] = {idVar : ops}

            else:
                makeCuadruple(bufferANDOR)
                op2 = p[2] / 1000
                signo = 3
                op1 = p[1] / 1000

                p[0] = isCompatible(op1, op2, signo, "logica")
        else:
            p[0] = p[1]

def p_operacionX(p):
    '''operacionX : OPERADOR_ANDOR operacion
                  | ''' #Epsilon
    if len(p) > 2 and p[2] is not None:
        bufferANDOR.append(p[1])
        p[0] = p[2]

#Expresion
def p_expresion(p):
    '''expresion : exp expresionX'''
    if len(p) > 2:
        #Si son dos o mas operandos, se verifica que sean compatibles
        if p[2] is not None:
            #Si es dict es porque es variable, se trata diferente
            if isinstance(p[1], dict):
                idVar = p[1].keys()[0]
                ops = p[1].values()[0]

                if isinstance(ops, dict) and ops.has_key(9999):
                    makeCuadruple(bufferLogico)
                    p[0] = p[1]
                else:
                    if '>' in p[2].keys():
                        ops.append( (4, p[2]['>']) )
                    elif '<' in p[2].keys():
                        ops.append( (4, p[2]['<']) )
                    elif '==' in p[2].keys():
                        ops.append( (5, p[2]['==']) )

                    makeCuadruple(bufferLogico)
                    p[0] = {idVar : ops}

            else:
                makeCuadruple(bufferLogico)

                if '>' in p[2].keys():
                    signo = 4
                    op2 = p[2]['>'] / 1000
                elif '<' in p[2].keys():
                    signo = 4
                    op2 = p[2]['<'] / 1000
                elif '==' in p[2].keys():
                    signo = 5
                    op2 = p[2]['=='] / 1000

                op1 = p[1] / 1000

                p[0] = isCompatible(op1, op2, signo, "comparacion de valores")
        else:
            p[0] = p[1]

def p_expresionX(p):
    '''expresionX : OPERADOR_LOGICO exp
                  | ''' #Epsilon
    if len(p) > 2 and p[2] is not None:
        bufferLogico.append(p[1])
        p[0] = {p[1] : p[2]}

#Factor
def p_factor(p):
    '''factor : DELIMITADOR_ABRIR expresion DELIMITADOR_CERRAR
              | constante
              | OPERADOR_SR constante'''
    if len(p) > 3:
        p[0] = p[2]
    elif len(p) > 2:
        if p[2] != 4000:

            #Se guarda el 0 como una constantes (para negativos se hace una resta de 0
            if 0 in constantes.values():
                dirCero = constantes.keys()[constantes.values().index(0)]
            else:
                dirCero = assignConstantAddress("int")
                constantes[dirCero] = 0

            #Generacion de cuadruplos
            global bufferCuadruplos
            bufferCuadruplos.insert(len(bufferCuadruplos) - 1, dirCero)
            makeCuadruple(["-"])

            p[0] = p[2]
        else:
            print "Error! Strings no soportados en signos"
            sys.exit()
    elif len(p) > 1:
        p[0] = p[1]

#Escritura
def p_escritura(p):
    '''escritura : PRINT DELIMITADOR_ABRIR operacion DELIMITADOR_CERRAR FIN_LINEA'''
    makeCuadruple(["print"])

    if isinstance(p[3], dict):
        ret = {}
        calls = []
        for key in p[3].keys():
            calls.append( (key, {key : list(p[3][key])}) )
        ret['call'] = calls

        p[0] = ret

#Asignacion
def p_asignacionX(p):
    '''asignacionX : DELIMITADOR_CUADRADO exp DELIMITADOR_CUADRADO_CERRAR
                   | ''' #Epsilon
    if len(p) > 1 and p[1] == '[':
            idxArray = bufferCuadruplos.pop()
            p[0] = {'arr' : idxArray}

def p_asignacionY(p):
    '''asignacionY : operacion'''
    p[0] = p[1]

#Exp
def p_exp(p):
    '''exp : termino expX'''
    if len(p) > 2:
        #Si son dos o mas operandos, se verifica que sean compatibles
        if p[2] is not None:
            #Si es dict es porque es variable, se trata diferente
            if isinstance(p[1], dict):
                idVar = p[1].keys()[0]
                ops = p[1].values()[0]

                if isinstance(ops, dict) and ops.has_key(9999):
                    makeCuadruple(bufferSR)
                    p[0] = p[1]
                else:
                    ops.append( (1, p[2]) )
                    makeCuadruple(bufferSR)
                    p[0] = {idVar : ops}

            elif isinstance(p[2], dict):
                idVar = p[2].keys()[0]
                ops = p[2].values()[0]

                if isinstance(ops, dict) and ops.has_key(9999):
                    p[0] = p[2]
                else:
                    ops.append( (1, p[1]) )
                    makeCuadruple(bufferSR)
                    p[0] = {idVar : ops}

            else:
                makeCuadruple(bufferSR)

                op2 = p[2] / 1000
                signo = 1
                op1 = p[1] / 1000

                p[0] = isCompatible(op1, op2, signo, "suma/resta")
        else:
            p[0] = p[1]

def p_expX(p):
    '''expX : OPERADOR_SR exp
            | ''' #Epsilon
    if len(p) > 2 and p[2] is not None:
        bufferSR.append(p[1])
        p[0] = p[2]

#Termino
def p_termino(p):
    '''termino : factor terminoX'''
    if len(p) > 2:
        #Si son dos o mas operandos, se verifica que sean compatibles
        if p[2] is not None:
            #Si es dict es porque es variable, se trata diferente
            if isinstance(p[1], dict):
                idVar = p[1].keys()[0]
                ops = p[1].values()[0]

                if isinstance(ops, dict) and ops.has_key(9999):
                    makeCuadruple(bufferMD)
                    p[0] = p[1]
                else:
                    ops.append( (2, p[2]) )
                    makeCuadruple(bufferMD)
                    p[0] = {idVar : ops}

            elif isinstance(p[2], dict):
                idVar = p[2].keys()[0]
                ops = p[2].values()[0]

                if isinstance(ops, dict) and ops.has_key(9999):
                    p[0] = p[2]
                else:
                    ops.append( (2, p[1]) )
                    makeCuadruple(bufferMD)
                    p[0] = {idVar : ops}

            else:
                makeCuadruple(bufferMD)

                op2 = p[2] / 1000
                signo = 2
                op1 = p[1] / 1000

                p[0] = isCompatible(op1, op2, signo, "multiplicacion/division")
        else:
            p[0] = p[1]

def p_terminoX(p):
    '''terminoX : OPERADOR_MD termino
                | ''' #Epsilon
    if len(p) > 2 and p[2] is not None:
        bufferMD.append(p[1])

        p[0] = p[2]

#While
def p_while(p):
    '''while : WHILE DELIMITADOR_ABRIR operacion inicioWhile DELIMITADOR_LLAVES bloqueCodigo finWhile'''
    ret = p[6]

    if ret is not None:
        if isinstance(p[3], dict):
            if ret.has_key('call'):
                calls = ret['call']
                for key in p[3].keys():
                    calls.append( (key, {key : list(p[3][key])}) )
                ret['call'] = calls
            else:
                calls = []
                for key in p[3].keys():
                    calls.append( (key, {key : list(p[3][key])}) )
                ret['call'] = calls

        p[0] = ret


#If
def p_if(p):
    '''if : IF DELIMITADOR_ABRIR operacion inicioIf DELIMITADOR_LLAVES bloqueCodigo DELIMITADOR_LLAVES ifX'''
    #Cuando se reduzca por completo el if se rellena el ultimo salto registrado
    ultimoSalto = pSaltos.pop()
    cuadSalto = cuadruplos[ultimoSalto]
    if cuadSalto[-1] == -1:
        cuadSalto[-1] = cuadruploActual
        cuadruplos[ultimoSalto] = cuadSalto

    ret = p[6]

    if ret is not None:
        if isinstance(p[3], dict):
            if ret.has_key('call'):
                calls = ret['call']
                for key in p[3].keys():
                    calls.append( (key, {key : list(p[3][key])}) )
                ret['call'] = calls
            else:
                calls = []
                for key in p[3].keys():
                    calls.append( (key, {key : list(p[3][key])}) )
                ret['call'] = calls
        p[0] = ret

def p_ifX(p):
    '''ifX : else DELIMITADOR_LLAVES bloqueCodigo DELIMITADOR_LLAVES
           | ''' #Epsilon

#Input
def p_input(p):
    '''input : INPUT DELIMITADOR_ABRIR tipo DELIMITADOR_CERRAR FIN_LINEA'''
    bufferCuadruplos.append(p[3])
    makeCuadruple(["input"])
    p[0] = getTypeId(p[3])

#Constante
def p_constante(p):
    '''constante : cteString
                 | cteChar
                 | cteInt
                 | cteFloat
                 | cteId'''
    if len(p) > 1 and p[1] is not None:
        p[0] = p[1]

def p_cteInt(p):
    '''cteInt : INT'''
    #Se checa si es que esta constante ya existe en la tabla para obtener la misma direccion
    if p[1] in constantes.values():
        dirCte = constantes.keys()[constantes.values().index(p[1])]
    else:
        dirCte = assignConstantAddress("int")
        constantes[dirCte] = p[1]

    bufferCuadruplos.append(dirCte)
    p[0] = 1000

def p_cteChar(p):
    '''cteChar : CHAR'''
    #Se checa si es que esta constante ya existe en la tabla para obtener la misma direccion
    if p[1] in constantes.values():
        dirCte = constantes.keys()[constantes.values().index(p[1])]
    else:
        dirCte = assignConstantAddress("char")
        constantes[dirCte] = p[1]

    bufferCuadruplos.append(dirCte)
    p[0] = 3000

def p_cteString(p):
    '''cteString : STRING'''
    #Se checa si es que esta constante ya existe en la tabla para obtener la misma direccion
    if p[1] in constantes.values():
        dirCte = constantes.keys()[constantes.values().index(p[1])]
    else:
        dirCte = assignConstantAddress("string")
        constantes[dirCte] = p[1]

    bufferCuadruplos.append(dirCte)
    p[0] = 4000

def p_cteFloat(p):
    '''cteFloat : FLOAT'''
    #Se checa si es que esta constante ya existe en la tabla para obtener la misma direccion
    if p[1] in constantes.values():
        dirCte = constantes.keys()[constantes.values().index(p[1])]
    else:
        dirCte = assignConstantAddress("float")
        constantes[dirCte] = p[1]

    bufferCuadruplos.append(dirCte)
    p[0] = 2000

def p_cteId(p):
    '''cteId : IDENTIFICADOR constanteX'''
    #Checar si esta declarada y el tipo, regresar acorde
    if len(p) > 2:
        bufferCuadruplos.append(p[1])
        if p[2] is not None:
            if p[2].has_key('func'):

                dato = p[2]['func']

                #Se genera el cuadruplo ERA
                makeCuadruple([p[1], "era"])

                #Aqui debera ir lo de los parametros
                cantParams = len(dato)
                i = 0
                nameFunc = bufferCuadruplos.pop()

                global numParam
                numParam = cantParams - 1

                #Para cada parametro se hace un cuadruplo
                while i < cantParams:
                    makeCuadruple([p[1]+"-", "param"])
                    i += 1

                #Se hace el cuadruplo del goto a la funcion
                makeCuadruple([p[1], "gosub"])

                bufferCuadruplos.append(nameFunc)

                p[0] = { p[1] : {9999  : dato} }
            elif p[2].has_key('arr'):
                bufferCuadruplos.pop()
                offset = p[2]['arr']
                makeCuadruple([offset, p[1], 'ver'])
                bufferCuadruplos.append(offset)
                bufferCuadruplos.append("[" + p[1] + "]")
                makeCuadruple(['+'])
                res = bufferCuadruplos.pop()
                bufferCuadruplos.append("(" + res + ")")

                p[0] = {p[1] : []}
        else:
            p[0] = {p[1] : []}

def p_constanteX(p):
    '''constanteX : DELIMITADOR_CUADRADO exp DELIMITADOR_CUADRADO_CERRAR
                  | DELIMITADOR_ABRIR constanteY DELIMITADOR_CERRAR
                  | ''' #Epsilon
    if len(p) > 2:
        if p[1] == '(':
            p[0] = { 'func':p[2] }
        elif p[1] == '[':
            p[0] = {'arr' : bufferCuadruplos.pop()}

def p_constanteY(p):
    '''constanteY : constante constanteZ
                  | ''' #Epsilon
    if len(p) > 2:
        args = [p[1]]
        if p[2] is not None:
            args = args + p[2]

        p[0] = args

def p_constanteZ(p):
    '''constanteZ : SEPARADOR constanteY
                  | ''' #Epsilon
    if len(p) > 2:
        p[0] = p[2]

#Tipo
def p_tipo(p):
    '''tipo : TIPO_STRING
            | TIPO_CHAR
            | TIPO_INT
            | TIPO_FLOAT
            | TIPO_VOID'''
    p[0] = p[1]

#Terminales para cada uno de los identificadores de los ciclos
#Utilizados para saber donde insertar los saltos en la ejecucion
#Donde inicia el if, ya esta el cuadruplo de operacion
def p_inicioWhile(p):
    '''inicioWhile : DELIMITADOR_CERRAR'''
    pSaltos.append(cuadruploActual)
    makeCuadruple(["gotoF"])

def p_finWhile(p):
    '''finWhile : DELIMITADOR_LLAVES'''
    #Se rellena el cuad del salto en falos de la comparacion
    ultimoSalto = pSaltos.pop()
    cuadSalto = cuadruplos[ultimoSalto]
    if cuadSalto[-1] == -1:
        cuadSalto[-1] = cuadruploActual + 1
        cuadruplos[ultimoSalto] = cuadSalto

    #Se hace cuadruplo del goto para volver a la comparacion
    makeCuadruple(["goto"])

    #Se rellena el goto que se acaba de hacer
    ultimoSalto = pSaltos.pop()
    cuadSalto = cuadruplos[ultimoSalto]
    if cuadSalto[-1] == -1:
        cuadSalto[-1] = pSaltos.pop() - 1 #-1 para volver a la comparacion
        cuadruplos[ultimoSalto] = cuadSalto

def p_inicioIf(p):
    '''inicioIf : DELIMITADOR_CERRAR'''
    makeCuadruple(["gotoF"])

#Else para el if
#Se completa el ultimo salto (obviamente del if que lo requiere
def p_else(p):
    '''else : ELSE'''
    #Se rellena el if que contiene el else
    ultimoSalto = pSaltos.pop()
    cuadSalto = cuadruplos[ultimoSalto]
    if cuadSalto[-1] == -1:
        cuadSalto[-1] = cuadruploActual + 1
        cuadruplos[ultimoSalto] = cuadSalto

    #Se hace cuadruplo del goto para el if positivo
    makeCuadruple(["goto"])

#Funcion de error para el parser
def p_error(p):
    print "Error al parsear el programa. Mensaje: ", p
    sys.exit()

#Inicializacion del Lexer
lex.lex()

#Inicializacion del Parser
yacc.yacc()

nombreArchivo = raw_input("Nombre del Archivo: ")

archivo = open(nombreArchivo, 'r')

datos = archivo.read()

yacc.parse(datos)

#Se declara la maquina virtual y se manda llamar inmediatamente despues de la compilacion
maquinaVirtual = virtualMachine(constantes, cuadruplos)

#Se ejecuta el programa
maquinaVirtual.correPrograma()
