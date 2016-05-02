##
##Archivo que maneja el cubo de datos del KPP
##
##Funciona utilizando una "arreglo" de 3 dimensiones
##

from collections import defaultdict
dataMatches = defaultdict(lambda :defaultdict(lambda :defaultdict(int)))

##Indices del arreglo
##dataMatches[x][y][z] donde
##	x = operando 1
##	y = operando 2
##	z = operador

##Identificadores de los datos
##
##	Int: 1
##	Float: 2
##	Char: 3
##  String: 4

##Identificadores de los operadores
##
##	+,-: 1
##	*,/: 2
##	&,|: 3
##	<,>: 4
##	==, <>: 5
##  =: 6

## Error = -1

##Operadores + y -
dataMatches[1][1][1] = 1
dataMatches[1][2][1] = 1
dataMatches[2][1][1] = 1
dataMatches[2][2][1] = 2
dataMatches[3][1][1] = 1
dataMatches[1][3][1] = 1
dataMatches[3][2][1] = -1
dataMatches[2][3][1] = -1
dataMatches[3][3][1] = 1
dataMatches[1][4][1] = -1
dataMatches[4][1][1] = -1
dataMatches[2][4][1] = -1
dataMatches[4][2][1] = -1
dataMatches[3][4][1] = -1
dataMatches[4][3][1] = -1
dataMatches[4][4][1] = -1

##Operadores * y /
dataMatches[1][1][2] = 1
dataMatches[1][2][2] = 2
dataMatches[2][1][2] = 2
dataMatches[2][2][2] = 2
dataMatches[3][1][2] = -1
dataMatches[1][3][2] = -1
dataMatches[3][2][2] = -1
dataMatches[2][3][2] = -1
dataMatches[3][3][2] = -1
dataMatches[1][4][2] = -1
dataMatches[4][1][2] = -1
dataMatches[2][4][2] = -1
dataMatches[4][2][2] = -1
dataMatches[3][4][2] = -1
dataMatches[4][3][2] = -1
dataMatches[4][4][2] = -1

##Operadores & y |
dataMatches[1][1][3] = 1
dataMatches[1][2][3] = -1
dataMatches[2][1][3] = -1
dataMatches[2][2][3] = -1
dataMatches[3][1][3] = -1
dataMatches[1][3][3] = -1
dataMatches[3][2][3] = -1
dataMatches[2][3][3] = -1
dataMatches[3][3][3] = -1
dataMatches[1][4][3] = -1
dataMatches[4][1][3] = -1
dataMatches[2][4][3] = -1
dataMatches[4][2][3] = -1
dataMatches[3][4][3] = -1
dataMatches[4][3][3] = -1
dataMatches[4][4][3] = -1

##Operadores < y >
dataMatches[1][1][4] = 1
dataMatches[1][2][4] = 1
dataMatches[2][1][4] = 1
dataMatches[2][2][4] = 1
dataMatches[3][1][4] = -1
dataMatches[1][3][4] = -1
dataMatches[3][2][4] = -1
dataMatches[2][3][4] = -1
dataMatches[3][3][4] = -1
dataMatches[1][4][4] = -1
dataMatches[4][1][4] = -1
dataMatches[2][4][4] = -1
dataMatches[4][2][4] = -1
dataMatches[3][4][4] = -1
dataMatches[4][3][4] = -1
dataMatches[4][4][4] = -1

##Operador ==
dataMatches[1][1][5] = 1
dataMatches[1][2][5] = 1
dataMatches[2][1][5] = 1
dataMatches[2][2][5] = 1
dataMatches[3][1][5] = 1
dataMatches[1][3][5] = 1
dataMatches[3][2][5] = 1
dataMatches[2][3][5] = 1
dataMatches[3][3][5] = 1
dataMatches[1][4][5] = -1
dataMatches[4][1][5] = -1
dataMatches[2][4][5] = -1
dataMatches[4][2][5] = -1
dataMatches[3][4][5] = -1
dataMatches[4][3][5] = -1
dataMatches[4][4][5] = 4

##Operador =
dataMatches[1][1][6] = 1
dataMatches[1][2][6] = 1
dataMatches[2][1][6] = 1
dataMatches[2][2][6] = 1
dataMatches[3][1][6] = 1
dataMatches[1][3][6] = 1
dataMatches[3][2][6] = -1
dataMatches[2][3][6] = -1
dataMatches[3][3][6] = 1
dataMatches[1][4][6] = -1
dataMatches[4][1][6] = -1
dataMatches[2][4][6] = -1
dataMatches[4][2][6] = -1
dataMatches[3][4][6] = -1
dataMatches[4][3][6] = -1
dataMatches[4][4][6] = 1

#Funcion de consulta del cubo para definir el resultado de una operacion
#Recibe como argumento los operandos y el operador
#Regresa la consulta al cubo
def getResultType(op1, op2, operator):
	return dataMatches[op1][op2][operator]
