#############################################################################
#                                                                           #
#  Script:      Modelo FONAG 2.1 by atuk                                    #
#  Description: Modelo Hidrologico FONAG actualizado                        #
#  Created By:  ATUK Consultoria Estrategica & Katarisoft                   #
#  Date:        30-Abr-2020                                                 #
#                                                                           #
#############################################################################

'''
Este script realiza el workflow de calibracion del modelo FONAG 2.1 iterativamente

MODELO Y AREA DE ESTUDIO

El modelo utilizado es el modelo FONAG 2.1 by ATUK (Ochoa-Tocachi et al., 2020).
Los inputs de calibracion son los coeficientes Kc y a,b,spt de las hidrozonas,
el output es el set de parametros que ofrece el mejor desempeno.

INDICE

Pasos:
0. Inicializar el espacio de trabajo e importar modulos de python
1. Configurar el modelo
2. Extraer datos climaticos
3a. Muestreo inicial de parametros
(Repetir iterativamente)
3b. Muestreo iterativo de parametros
4. Evaluar los resultados de caudal para elegir el mejor set
(Terminar bucle)
5. Correr el modelo FONAG 2.1 con caudal con dichos parametros

Este script fue desarrollado por ATUK Consultoria Estrategica, 2020
info@atuk.com.ec
'''

import time
import os
import math
import matplotlib.pyplot as plt
import scipy.stats as st
import time
import numpy as np
import plot_functions_FONAG21 as pf  # modulo para visualizar resultados
import calibracionFONAG21 as cal  # modulo de funciones de calibracion
import arcpy
from arcpy.sa import *
from arcpy import env

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension('Spatial')
# Check out the ArcGIS Geostatistical Analyst extension license
arcpy.CheckOutExtension('GeoStats')
# Permitir sobreescritura de archivos
env.overwriteOutput = True

rain = {}
evap = {}
temp = {}
y = 0
m = 0
factorh = []
ndias = []

def calibrar(path, N=1000, E_cond=[True, False, True, True, False], cont=False):
    start = time.time()
    # print N, E_cond, cont
    global rain
    global evap
    global temp
    global m
    global y
    global factorh
    global ndias

    print(' ')
        # %% Paso 1: Configurar el modelo FONAG 2.1
    print('Paso 1: Configurar el modelo FONAG 2.1')

    # Datos ingresados por el usuario (GUI)
    # N = 10000  #  Nummero de muestras, ingresado por el usuario
    # E_cond = [True, False, True, True, False] # Funciones objetivo
    # cont = False # Leer desde el usuario
    # Este es el equivalente a que el usuario cargue una configuracion diferente
    # inputs_usuario = raw_input('  Ingrese el nombre del archivo con la tabla de inputs: ')
    # Inputs fijos
    n = 0.4  # Factor exponencial para la escorrentia
    warmup = 12  # Periodo de calentamiento del modelo (meses)

    # Selecciona la ubicacion actual del directorio
    # path = os.getcwd()

    # Lectura de inputs
    inputs = open(r'%s/modeloFONAG/inputs/t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('  Lectura de inputs')

    # Crear carpeta de salidas
    # print '  Crear carpeta de salidas'
    # os.system('md modeloFONAG\\%s' % t_inputs[16])
    # os.system('md modeloFONAG\\%s\\calibracion' % t_inputs[16])

    # Analisis de terreno
    cal.terreno(path, t_inputs)
    print('  Analisis de terreno')

    # Usos de agua
    cal.usos_agua(path, t_inputs)
    print('  Usos de agua')

    # Usos de suelo
    cal.usos_suelo(path, t_inputs)
    print('Usos de suelo')

    # Leer datos de caudal para calibracion
    area_aporte, areas, demand_m3_s, hz_lista = cal.aforo_calibracion(path, t_inputs)
    data = np.genfromtxt(r'%s\modeloFONAG\inputs\%s' % (path, t_inputs[19]), comments='%')
    y_obs = data[:, 1]
    print('  Leer aforo de caudal para calibracion')

    print(' ')
    # %% Paso 2: Extraccion de datos climaticos
    print('Paso 2: Extraccion de datos climaticos')

    # Generar matrices de datos climaticos
    rain, evap, temp, y, m, factorh, ndias, date_Labels = cal.series_tiempo(path, t_inputs)
    # print '##VARIABLES'
    # print rain, evap, temp, y, m, factorh, ndias
    print('  Generar matrices de datos climaticos')

    print(' ')
    # %% Paso 3a: Muestreo del espacio parametrico
    print('Paso 3a: Muestreo del espacio parametrico')

    # Lectura de tabla de calibracion
    rangos = open(r'%s\modeloFONAG\inputs\%s' % (path, t_inputs[17]), 'r')
    t_rangos = rangos.read().split('\n')
    rangos.close()
    print('  Lectura de rangos de calibracion')

    # Generacion de matriz de parametros
    # M: Numero de parametros a calibrar
    # Z: Numero de hidrozonas a calibrar
    # tipos: Tipo de hidrozona (1: lineal, 2: no lineal, 3: glaciar)
    # xmin, xmax: Rangos de parametros a modelar
    # X_Labels: Nombres de parametros (para mostrar en los plots):
    M, Z, tipos, xmin, xmax, X_Labels, hz_lista = cal.tabla_calibracion(t_rangos, hz_lista, path=path,
                                                                        t_inputs=t_inputs)
    print('  Generacion de matriz de parametros')

    # Inicializar condiciones de bucle
    count = 0
    count_max = 10
    comparacion = 100
    tol = 100
    tol_max = 1E-6

    while count < count_max and tol > tol_max:
        print(' ')
        # %% Paso 3b: Muestreo del espacio parametrico
        print('Paso 3b: Muestreo del espacio parametrico')
        print('  Iteracion numero %s' % count)

        # Rangos de parametros
        print('  Rangos de parametros')
        print(X_Labels)
        print(xmin)
        print(xmax)

        # Distribuciones de los parametros
        distr_fun = st.uniform  # Distribucion uniforme
        # Los parametros de forma de la distribucion uniforme son el limite inferior
        # y la diferencia entre los limites superior e inferior
        distr_par = [np.nan] * M
        for i in range(M):
            distr_par[i] = [xmin[i], xmax[i] - xmin[i]]
        print('  Distribuciones de los parametros')

        # Muestreo hipercubo latino
        samp_strat = 'lhs'  # Latin Hypercube
        # N = 10000  #  Nummero de muestras, ingresado por el usuario
        X = cal.AAT_sampling(samp_strat, M, distr_fun, distr_par, N)
        print('  Muestreo hipercubo latino')

        print(' ')
        # %% Paso 4: Evaluar los resultados
        print('Paso 4: Evaluar los resultados')

        # Definir el modelo
        fun_eval = cal.evaluacion_modelo
        print('  Definir el modelo de evaluacion')

        E = cal.model_execution(fun_eval, X, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista,
                                m, y, factorh, ndias, y_obs, warmup)
        print('  Evaluar el modelo de FONAG 2.1')

        # Definir que indicadores se usan para OF
        E_Labels = ['NSE', 'RMSE', 'RSR', 'PBIAS', 'KGE']
        if len(E_cond) != 5:
            E_cond = [True, False, True, True, False]  # Funciones objetivo
        E_mod, E_cond_mod, E_Labels_mod = cal.funcionobjetivo(E, E_cond, E_Labels)
        print('  Calcular OF combinando indicadores')

        # Ordenar resultados de mejor a peor
        orden = E_mod[:, 5].argsort()
        X_sort = X[orden]
        print('  Ordenar resultados de mejor a peor')

        # Obtener nuevos rangos de parametros
        Nm = max(3, int(math.ceil(N * 0.01)))
        X_best = X_sort[range(Nm), :]
        xmin = np.nanpercentile(X_best, q=1, axis=0)
        xmax = np.nanpercentile(X_best, q=99, axis=0)

        # Grabar hz_lista, tipos, xmin y xmax en un csv

        tol = abs((xmax - xmin) / xmin)
        count += 1

    print(' ')
    # %% Paso 5: Correr el modelo FONAG 2.1
    print('Paso 5: Correr el modelo FONAG 2.1')

    # Definir el modelo
    fun_test = cal.modelo_iterativo
    print('  Definir el modelo de simulacion')

    Y = cal.model_execution(fun_test, X, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista,
                            m, y, factorh, ndias)
    print('  Correr el modelo FONAG 2.1')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizX.csv', X, delimiter=',',
               header=",".join(X_Labels), comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizY.csv', Y, delimiter=',',
               header=",".join(date_Labels),comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizE.csv', E_mod, delimiter=',',
               header=",".join(E_Labels_mod),comments='')
    print('  Grabar resultados')

    # Ordenar resultados de mejor a peor
    orden = E_mod[:, 5].argsort()
    X_sort = X[orden]
    Y_sort = Y[orden]
    E_sort = E_mod[orden]
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\sortedX.csv', X_sort, delimiter=',',
               header=",".join(X_Labels),comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\sortedY.csv', Y_sort, delimiter=',',
               header=",".join(date_Labels),comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\sortedE.csv', E_sort, delimiter=',',
               header=",".join(E_Labels_mod),comments='')
    print('  Grabar resultados ordenados de mejor a peor')

def paralelos():
    # Plot de ejes paralelos seleccionados
    idxb = np.zeros(shape=(N, 1), dtype=bool)
    idxb[orden[range(Nm)]] = True
    fig = plt.figure()
    pf.parcoor(X, X_Labels=X_Labels, idx=idxb)
    # plt.show()
    fig.savefig(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\p_%s_%shz_paralelcalib.png' % (N, Z))
    print('Plot de ejes paralelos seleccionados')

    for cond_index in range(6):
        if E_cond_mod[cond_index]:
            plt.figure()
            pf.scatter_plots(X, E_mod[:, cond_index], Y_Label=E_Labels_mod[cond_index], X_Labels=X_Labels, idx=idxb)
    # plt.show()
    print('Visualizar parametros en nubes de puntos')

    # Plot de series de tiempo
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    meses = range(len(y_obs))
    ax.plot(meses, np.transpose(Y_sort[1, :]), c='black', label='%s mejores simulaciones' % Nm)
    ax.plot(meses, np.transpose(Y_sort[range(2, Nm), :]), c='black')
    ax.plot(meses, np.transpose(Y_sort[0, :]), c='red', label='Mejor simulacion', linewidth=2)
    ax.plot(meses, y_obs, color='blue', label='Caudal observado', linewidth=2)
    ax.legend()
    ax.set_title('Series de tiempo de caudal')
    ax.set_xlabel('meses')
    ax.set_ylabel('m3/s')
    # plt.show()
    fig.savefig(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\p_%s_%shz_seriescalib.png' % (N, Z),
                orientation='landscape', papertype='a4')
    print('Visualizar series de tiempo')

    elapsed_time = (time.time() - start) / 60
    print('El proceso de calibracion para caudal tomo %s minutos.' % elapsed_time)
    plt.show()
