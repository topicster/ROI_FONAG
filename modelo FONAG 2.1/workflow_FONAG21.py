#############################################################################
#                                                                           #
#  Script:      Modelo FONAG 2.1 by atuk                                    #
#  Description: Modelo Hidrologico FONAG actualizado                        #
#  Created By:  ATUK Consultoria Estrategica & Katarisoft                   #
#  Date:        30-Abr-2020                                                 #
#                                                                           #
#############################################################################

"""
Este script realiza el workflow de calibracion del modelo FONAG 2.1

MODELO Y AREA DE ESTUDIO

El modelo utilizado esta basado en el modelo FONAG 2.1 by ATUK (Ochoa-Tocachi et al., 2019).
Los inputs de calibracion son los coeficientes Kc y a,b,spt de las hidrozonas,
el output es el set de parametros que ofrece el mejor desempeno.

En caso de existir datos, se realiza tambien la calibracion de coeficientes de
transporte de compuestos as, at de las hidrozonas.

INDICE

Pasos:
0a. Inicializar el espacio de trabajo e importar modulos de python
0b. Cargar datos y configurar el modelo FONAG 2.1

1. Terreno
2. Usos de agua
3. Usos de suelo
4. Coeficientes de hidrozonas
5. Balance hidrico
6. Estres hidrico

Este script fue desarrollado por ATUK Consultoria Estrategica, 2020
info@atuk.com.ec
"""

print """
############################################################
#                                                          #
#   Modelo Hidrologico FONAG 2.1 by atuk                   #
#   Creado por: ATUK Consultoria Estrategica & Katarisoft  #
#                                                          #
############################################################
"""

print " "
print "INICIO"


print " "
#%% Paso 0a: importar modulos de python
print("Importar modulos de python")

import math
import numpy as np
import matplotlib.pyplot as plt
from numpy.matlib import repmat
import scipy.stats as st
import os
import time
import plot_functions_FONAG21 as pf # module to visualize the results
# import calibracionFONAG2
import modeloFONAG21

start = time.time()

print " "
#%% Paso 0b: Configurar el modelo FONAG 2.1
print "Configurar el modelo FONAG 2.1"

# Selecciona la ubicacion actual del directorio
path = os.getcwd()
# Lectura de inputs
# Este es el equivalente a que el usuario cargue una configuracion diferente
inputs_usuario = raw_input('Ingrese el nombre del archivo con la tabla de inputs: ')
inputs = open(r"%s\modeloFONAG\inputs\%s" % (path, inputs_usuario), "r")
t_inputs = inputs.read().split("\n")[1].split("\r")[0].split(",")
inputs.close()
print("Lectura de inputs")

modeloFONAG_1 = modeloFONAG21.modelinit(path, t_inputs)

# print("Paso 1: Analisis de terreno")
# Analisis de terreno
modeloFONAG_1.terreno(path)

# print("Paso 2: Usos de agua")
# Usos de agua
modeloFONAG_1.usos_agua(path)

# print("Paso 3: Usos de suelo")
# Usos de suelo
modeloFONAG_1.usos_suelo(path)

# print("Paso 4: Coeficientes de hidrozonas")
# Usos de suelo
modeloFONAG_1.coeficientes(path)

# print("Paso 5: Balance hidrico")
# Usos de suelo
modeloFONAG_1.balance(path)

# print("Paso 6: Estres hidrico")
# Usos de suelo
modeloFONAG_1.estres(path)

elapsed_time = (time.time() - start) / 60
print("La corrida del modelo tomo %s minutos." % elapsed_time)
