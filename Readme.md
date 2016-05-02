# K Plus Plus

K Plus Plus (KPP) es un lenguaje de programación básico que soporta programas creados en su interfaz visual, así como en el código del lenguaje. Creado utilizando Python 2.7 y la biblioteca [PLY](http://www.dabeaz.com/ply/) (Python Lex-Yacc) desarrollada por David Beazley. La interfaz visual fue creada utilizando la libreria [Blockly](https://developers.google.com/blockly/) de Google.

Desarrollado como proyecto final para la clase de Diseño de Compiladores.

Características del lenguaje y el compilador incluyen:

  - Entrada visual a través del editor
  - Soporte para programas escritos en código fuente KPP
  - Recursividad simple
  - Operaciones aritmeticas con enteros y flotantes
  - Entrada y salida de consola
  - Ciclos simples y anidados
  - Estatutos condicionales simples y anidados

### Versión
1.0.0

### Instalación

Para instalar KPP solo hay que descargar este repositorio y contar con Python 2.7 instalado.

### Usando KPP

Usar KPP consiste en dos partes:
* Crear un programa (código fuente o interfaz visual)
* Correr el programa

Para crear un programa en la interfaz visual es necesario abrir el editor en:

```sh
index.html
```
y guardar el archivo del programa utilizando el botón de la parte superior derecha.

Para correr un programa es necesario ejecutar utilizando la consola de Python el archivo:

```sh
KPP.py
```

### Ejemplos
En la carpeta Ejemplos hay algunos programas que utilizan varias de las caracteristicas que ofrece KPP.

### Problemas y Caracteristicas Pendientes

 - Varias llamadas recursivas en una sola línea
 - Integración del editor visual con el compilador sin un paso extra
 - Pruebas de funcionamiento en todos los casos posibles
 - Soporte para operaciones con strings