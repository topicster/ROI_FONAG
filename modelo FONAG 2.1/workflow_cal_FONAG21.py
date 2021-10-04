#############################################################################
#                                                                           #
#  Script:      Modelo FONAG 2.1 by atuk                                    #
#  Description: Modelo Hidrologico FONAG actualizado                        #
#  Created By:  ATUK Consultoria Estrategica & Katarisoft                   #
#  Date:        30-Abr-2020                                                 #
#                                                                           #
#############################################################################

'''
Este script realiza el workflow de calibracion del modelo FONAG 2.1

MODELO Y AREA DE ESTUDIO

El modelo utilizado es el modelo FONAG 2.1 by ATUK (Ochoa-Tocachi et al., 2020).
Los inputs de calibracion son los coeficientes Kc y a,b,spt de las hidrozonas,
el output es el set de parametros que ofrece el mejor desempeno.

En caso de existir datos, se realiza tambien la calibracion de coeficientes de
transporte de compuestos as, at de las hidrozonas.

INDICE

Pasos:
0. Inicializar el espacio de trabajo e importar modulos de python

1. Cargar datos y configurar el modelo FONAG 2.1
2. Extraer datos climaticos

3. Muestreo de parametros
4a. Correr el modelo FONAG 2.1 con caudal con dichos parametros
4b. Evaluar los resultados de caudal para elegir el mejor set

(En caso de que haya contaminantes para calibrar)
5. Muestreo de parametros de transporte de contaminantes
6a. Correr el modelo FONAG 2.1 para transporte de compuestos
6b. Evaluar los resultados de compuestos para elegir el mejor set

Este script fue desarrollado por ATUK Consultoria Estrategica, 2020
info@atuk.com.ec
'''

print('''
############################################################
#                                                          #
#   Modelo Hidrologico FONAG 2.1 by atuk                   #
#   Creado por: ATUK Consultoria Estrategica & Katarisoft  #
#                                                          #
############################################################
''')

print(' ')
print('INICIO')

print(' ')
# %% Paso 0: importar modulos de python
print('Paso 0: importar modulos de python')

import math
import numpy as np
import matplotlib.pyplot as plt
from numpy.matlib import repmat
import scipy.stats as st
import os
import time
import plot_functions_FONAG21 as pf  # modulo para visualizar resultados
import calibracionFONAG21 as cal  # modulo de funciones de calibracion
import csv
from numpy import genfromtxt
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

def configuracion(path, N=1000, E_cond=[True, False, True, True, False], cont=False):
    print(' ')
    # %% Paso 1: Configurar el modelo FONAG 2.1
    print('Paso 1: Configurar el modelo FONAG 2.1')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Datos ingresados por el usuario (GUI)
    # N = 10000  #  Nummero de muestras, ingresado por el usuario
    # E_cond = [True, False, True, True, False] # Funciones objetivo
    # cont = False # Leer desde el usuario
    # Este es el equivalente a que el usuario cargue una configuracion diferente
    # inputs_usuario = raw_input('Ingrese el nombre del archivo con la tabla de inputs: ')

    # Selecciona la ubicacion actual del directorio
    # path = os.getcwd()

    # Lectura de inputs
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Crear carpeta de salidas
    print('Crear carpeta de salidas')
    os.system('md modeloFONAG\\%s' % t_inputs[16])
    os.system('md modeloFONAG\\%s\\calibracion' % t_inputs[16])

    # Analisis de terreno
    cal.terreno(path, t_inputs)
    print('Analisis de terreno')

    # Usos de agua
    cal.usos_agua(path, t_inputs)
    print('Usos de agua')

    # Usos de suelo
    cal.usos_suelo(path, t_inputs)
    print('Usos de suelo')

    # Leer datos de caudal para calibracion
    area_aporte, areas, demand_m3_s, hz_lista = cal.aforo_calibracion(path, t_inputs)
    print('Leer aforo de caudal para calibracion')

    print('FIN PASO 1')


def clima(path, N=1000, E_cond=[True, False, True, True, False], cont=False):
    global rain
    global evap
    global temp
    global m
    global y
    global factorh
    global ndias

    print(' ')
    # %% Paso 2: Extraccion de datos climaticos
    print('Paso 2: Extraccion de datos climaticos')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Generar matrices de datos climaticos
    rain, evap, temp, y, m, factorh, ndias, date_Labels = cal.series_tiempo(path, t_inputs)
    print('Generar matrices de datos climaticos')
    print('FIN PASO 2')


def muescoef(path, N=1000, E_cond=[True, False, True, True, False], cont=False):
    # start = time.time()
    print(' ')
    # %% Paso 3: Muestreo del espacio parametrico
    print('Paso 3: Muestreo del espacio parametrico')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Lectura de tabla de calibracion
    rangos = open(r'%s\modeloFONAG\inputs\%s' % (path, t_inputs[17]), 'r')
    t_rangos = rangos.read().split('\n')
    rangos.close()
    print('Lectura de rangos de calibracion')

    # Generacion de matriz de parametros
    # M: Numero de parametros a calibrar
    # Z: Numero de hidrozonas a calibrar
    # tipos: Tipo de hidrozona (1: lineal, 2: no lineal, 3: glaciar)
    # xmin, xmax: Rangos de parametros a modelar
    # X_Labels: Nombres de parametros (para mostrar en los plots):
    hz_lista = open('%s\modeloFONAG\%s\calibracion\hz_lista.csv' % (path, t_inputs[16]), 'r')
    hz_lista = hz_lista.read().split('\n')[0].split(',')
    hz_lista = map(int, hz_lista)
    
    M, Z, tipos, xmin, xmax, X_Labels, hz_lista = cal.tabla_calibracion(t_rangos, hz_lista, path=path,t_inputs=t_inputs)
    print(Z)

    file1 = open(r'%s/modeloFONAG/%s/' %(path, t_inputs[16]) + r'muescoef_Z.txt','w')
    file1.write(str(Z))
    file1.close()
    
    print('Generacion de matriz de parametros')
    # Distribuciones de los parametros
    distr_fun = st.uniform  # Distribucion uniforme
    # Los parametros de forma de la distribucion uniforme son el limite inferior
    # y la diferencia entre los limites superior e inferior
    distr_par = [np.nan] * M
    for i in range(M):
        distr_par[i] = [xmin[i], xmax[i] - xmin[i]]
    print('Distribuciones de los parametros')

    # Muestreo hipercubo latino
    samp_strat = 'lhs'  # Latin Hypercube
    # N = 10000  #  Nummero de muestras, ingresado por el usuario
    X = cal.AAT_sampling(samp_strat, M, distr_fun, distr_par, N)
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizX.csv', X, delimiter=',',
               header=",".join(X_Labels),comments='')
    print('Muestreo hipercubo latino')

    # Plot de ejes paralelos
    fig = plt.figure()
    pf.parcoor(X, X_Labels=X_Labels)
    fig.savefig(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\p_%s_%shz_paralel.png' % (N, Z))
    print('Plot de ejes paralelos')
    print('FIN PASO 3')
    plt.show()


def modcaud(path, N=1000, E_cond=[True, False, True, True, False], cont=False):
    start = time.time()
    global rain
    global evap
    global temp
    global m
    global y
    global factorh
    global ndias

    print(' ')
    # %% Paso 4a: Correr el modelo FONAG 2.1
    print('Paso 4a: Correr el modelo FONAG 2.1')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')
    X = genfromtxt('%s\modeloFONAG\%s\calibracion\matrizX.csv' % (path, t_inputs[16]), delimiter=',', skip_header=1)
    # Definir el modelo
    fun_test = cal.modelo_iterativo
    print('Definir el modelo de simulacion')

    # Area de aporte
    area_aporte = open(r'%s\modeloFONAG\%s\calibracion\area_aporte.csv' % (path, t_inputs[16]), 'r')
    area_aporte = area_aporte.read().split('\n')[0].split(',')
    area_aporte = map(float, area_aporte)
    area_aporte = area_aporte[0]

    # Areas de contribucion
    areasf = open(r'%s\modeloFONAG\%s\calibracion\areas.csv' % (path, t_inputs[16]), 'r')
    areasf = areasf.read().split('\n')
    # areas = map(int, areas)
    areas = {}
    for i in areasf:
        if len(i) > 0:
            areasi = i.split(',')
            for j in areasi[1:]:
                # print j
                areas[int(areasi[0])] = float(j)
    # print areas

    # Demanda de agua
    demand_m3_s = open(r'%s\modeloFONAG\%s\calibracion\demand_m3_s.csv' % (path, t_inputs[16]), 'r')
    demand_m3_s = demand_m3_s.read().split('\n')[0].split(',')
    demand_m3_s = map(float, demand_m3_s)

    # Lista de hidrozonas
    hz_lista = open(r'%s\modeloFONAG\%s\calibracion\hz_lista.csv' % (path, t_inputs[16]), 'r')
    hz_lista = hz_lista.read().split('\n')[0].split(',')
    hz_lista = map(int, hz_lista)

    # Tipos de hidrozonas
    tipos = open(r'%s\modeloFONAG\%s\calibracion\tipos.csv' % (path, t_inputs[16]), 'r')
    tipos = tipos.read().split('\n')[0].split(',')
    tipos = map(int, tipos)
    Z = len(tipos)

    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    # Etiquetas de fechas
    date_Labels = open(r'%s\modeloFONAG\%s\calibracion\date_Labels.csv' % (path, t_inputs[16]), 'r')
    date_Labels = date_Labels.read().split('\n')[0].split(',')
    date_Labels = map(str, date_Labels)

    Y = cal.model_execution(fun_test, X, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista, m, y,
                            factorh, ndias)
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizY.csv', Y, delimiter=',',
               header=",".join(date_Labels),comments='')
    print('Correr el modelo FONAG 2.1')

    # Leer datos de caudal para calibracion
    data = np.genfromtxt(r'%s\modeloFONAG\inputs\%s' % (path, t_inputs[19]), comments='%')
    y_obs = data[:, 1]
    warmup = 12  # Periodo de calentamiento del modelo (meses)
    print('Leer aforo de caudal para calibracion')

    # Plot de series de tiempo
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    meses = range(len(y_obs))
    ax.plot(meses, np.transpose(Y[1, :]), color='grey', label='Caudales simulados')
    ax.plot(meses, np.transpose(Y), color='grey')
    ax.plot(meses, y_obs, color='blue', label='Caudal observado', linewidth=2)
    ax.legend()
    ax.set_title('Series de tiempo de caudal')
    ax.set_xlabel('meses')
    ax.set_ylabel('m3/s')
    fig.savefig(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\p_%s_%shz_seriestotal.png' % (N, Z),
                orientation='landscape', papertype='a4')
    print('Visualizar series de tiempo')

    print(' ')
    # %% Paso 4b: Evaluar los resultados
    print('Paso 4b: Evaluar los resultados')
 
    # Definir el modelo
    fun_eval = cal.evaluacion_modelo
    print('Definir el modelo de evaluacion')

    E = cal.model_execution(fun_eval, X, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista,
                            m, y, factorh, ndias, y_obs, warmup)
    print('Evaluar el modelo FONAG 2.1')

    # Definir que indicadores se usan para OF
    E_Labels = ['NSE', 'RMSE', 'RSR', 'PBIAS', 'KGE']
    if len(E_cond) != 5:
        E_cond = [True, False, True, True, False]  # Funciones objetivo
    E_mod, E_cond_mod, E_Labels_mod = cal.funcionobjetivo(E, E_cond, E_Labels)
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizE.csv', E_mod, delimiter=',',
               header=",".join(E_Labels_mod),comments='')

    with open(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\E_Labels_mod.csv','wb') as file:
        wr = csv.writer(file, quoting=csv.QUOTE_ALL)
        wr.writerow(E_Labels_mod)
    
    #np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\E_Labels_mod.csv', E_Labels_mod, delimiter=',',header="",comments='')
    print('Calcular OF combinando indicadores')

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
    print('Ordenar resultados de mejor a peor')

    '''
    # Indicar umbrales de aceptacion
    nse_umbral = 0.50 # umbral para NSE
    rsr_umbral = 0.70 # umbral para RSR
    pbias_umbral = 25 # umbral para PBIAS
    kge_umbral = 0.50 # umbral para KGE
    print('Indicar umbrales de aceptacion')

    # Encontrar funciones que cumplan los umbrales
    umbrales = [1 - nse_umbral, rsr_umbral, abs(pbias_umbral)]
    print('Encontrar funciones que cumplan los umbrales')
    '''

    # Visualizar parametros en nubes de puntos
    Nm = max(3, int(math.ceil(N * 0.01)))
    idxb = np.zeros(shape=(N, 1), dtype=bool)
    idxb[orden[range(Nm)]] = True

    for cond_index in range(6):
        if E_cond_mod[cond_index]:
            fig = plt.figure()
            pf.scatter_plots(X, E_mod[:, cond_index], Y_Label=E_Labels_mod[cond_index], X_Labels=X_Labels, idx=idxb)
            # plt.show()
            fig.savefig(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\p_%s_%shz_scatter%s.png' % (
            N, Z, E_Labels_mod[cond_index]))

    print('Visualizar parametros en nubes de puntos')

    # Plot de ejes paralelos seleccionados
    fig = plt.figure()
    pf.parcoor(X, X_Labels=X_Labels, idx=idxb)
    fig.savefig(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\p_%s_%shz_paralelcalib.png' % (N, Z))
    print('Plot de ejes paralelos seleccionados')

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
    fig.savefig(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\p_%s_%shz_seriescalib.png' % (N, Z),
                orientation='landscape', papertype='a4')
    print('Visualizar series de tiempo')

    elapsed_time = (time.time() - start) / 60
    print('El proceso de calibracion para caudal tomo %s minutos.' % elapsed_time)

    '''
    EN CASO DE QUE EXISTAN DATOS SE PUEDE PROCEDER CON LA CALIBRACION DE CONTAMINANTES
    '''
    print('FIN PASO 4')
    plt.show()


def muescont(path, N=1000, E_cond=[True, False, True, True, False], cont=False):
    # start = time.time()
    print(' ')
    # %% Paso 5: Muestreo de parametros de transporte
    print('Paso 5: Muestreo de parametros de transporte')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Leer datos de contaminante para calibracion
    hz_lista = open('%s\modeloFONAG\%s\calibracion\hz_lista.csv' % (path, t_inputs[16]), 'r')
    hz_lista = hz_lista.read().split('\n')[0].split(',')
    hz_lista = map(int, hz_lista)
    rangos = open(r'%s\modeloFONAG\inputs\%s' % (path, t_inputs[17]), 'r')
    t_rangos = rangos.read().split('\n')
    rangos.close()

    # Generacion de matriz de parametros
    # M: Numero de parametros a calibrar
    # Z: Numero de hidrozonas a calibrar
    # tipos: Tipo de hidrozona (1: lineal, 2: no lineal, 3: glaciar)
    # xmin, xmax: Rangos de parametros a modelar
    # X_Labels: Nombres de parametros (para mostrar en los plots):
    MC, ZC, tiposC, xCmin, xCmax, XC_Labels, hz_lista = cal.tabla_calibracion(t_rangos, hz_lista, cont, path=path,
                                                                              t_inputs=t_inputs)
    print('Generacion de matriz de parametros')

    # Distribuciones de los parametros
    distr_fun = st.uniform  # Distribucion uniforme
    # Los parametros de forma de la distribucion uniforme son el limite inferior
    # y la diferencia entre los limites superior e inferior
    distr_parC = [np.nan] * MC
    for i in range(MC):
        distr_parC[i] = [xCmin[i], xCmax[i] - xCmin[i]]
    print('Distribuciones de los parametros')

    # Muestreo hipercubo latino
    samp_strat = 'lhs'  # Latin Hypercube
    # N = 10000  # Numero de muestras igual al anterior
    XC = cal.AAT_sampling(samp_strat, MC, distr_fun, distr_parC, N)
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizXC.csv', XC, delimiter=',',
               header=",".join(X_Labels),comments='')
    print('Muestreo hipercubo latino')

    # Plot de ejes paralelos
    plt.figure()
    pf.parcoor(XC, X_Labels=XC_Labels)
    print('Plot de ejes paralelos')
    print('FIN PASO 5')
    plt.show()


def modcont(path, N=1000, E_cond=[True, False, True, True, False], cont=False):
    start = time.time()
    global rain
    global evap
    global temp
    global m
    global y
    global factorh
    global ndias

    print(' ')
    # %% Paso 6a: Correr el modelo FONAG 2.1 para transporte de compuestos
    print('Paso 6a: Correr el modelo FONAG 2.1 para transporte de compuestos')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    #XC = open('%s\modeloFONAG\%s\calibracion\matrizXC.csv' % (path, t_inputs[16]), 'r')
    #XC = XC.read().split('\n')
    XC = genfromtxt('%s\modeloFONAG\%s\calibracion\matrizXC.csv' % (path, t_inputs[16]), delimiter=',', skip_header=1)
    print('Lectura de inputs')
    # Definir el modelo
    fun_test = cal.modelo_iterativo
    print('Definir el modelo de simulacion')

    # Area de aporte
    area_aporte = open(r'%s\modeloFONAG\%s\calibracion\area_aporte.csv' % (path, t_inputs[16]), 'r')
    area_aporte = area_aporte.read().split('\n')[0].split(',')
    area_aporte = map(float, area_aporte)
    area_aporte = area_aporte[0]

    # Areas de contribucion
    areasf = open(r'%s\modeloFONAG\%s\calibracion\areas.csv' % (path, t_inputs[16]), 'r')
    areasf = areasf.read().split('\n')
    # areas = map(int, areas)
    areas = {}
    for i in areasf:
        if len(i) > 0:
            areasi = i.split(',')
            for j in areasi[1:]:
                # print j
                areas[int(areasi[0])] = float(j)
    # print areas

    # Demanda de agua
    demand_m3_s = open(r'%s\modeloFONAG\%s\calibracion\demand_m3_s.csv' % (path, t_inputs[16]), 'r')
    demand_m3_s = demand_m3_s.read().split('\n')[0].split(',')
    demand_m3_s = map(float, demand_m3_s)

    # Lista de hidrozonas
    hz_lista = open(r'%s\modeloFONAG\%s\calibracion\hz_lista.csv' % (path, t_inputs[16]), 'r')
    hz_lista = hz_lista.read().split('\n')[0].split(',')
    hz_lista = map(int, hz_lista)

    # Tipos de hidrozonas
    tipos = open(r'%s\modeloFONAG\%s\calibracion\tipos.csv' % (path, t_inputs[16]), 'r')
    tipos = tipos.read().split('\n')[0].split(',')
    tipos = map(int, tipos)
    Z = len(tipos)

    # Nombres de parametros
    XC_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    XC_Labels = XC_Labels.read().split('\n')[0].split(',')
    XC_Labels = map(str, XC_Labels)

    # Nombres de parametros
    date_Labels = open(r'%s\modeloFONAG\%s\calibracion\date_Labels.csv' % (path, t_inputs[16]), 'r')
    date_Labels = date_Labels.read().split('\n')[0].split(',')
    date_Labels = map(str, date_Labels)

    n = 0.4  # Factor exponencial para la escorrentia

    YC = cal.model_execution(fun_test, XC, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista, m, y,
                             factorh, ndias, n, cont)
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizYC.csv', YC, delimiter=',',
               header=",".join(date_Labels),comments='')
    print('Correr el modelo FONAG 2.1 para contaminantes')

    # Leer datos de contaminantes para calibracion
    data = np.genfromtxt(r'%s\modeloFONAG\inputs\%s' % (path, t_inputs[19]), comments='%')
    c_obs = data[:, 2]
    warmup = 12  # Periodo de calentamiento del modelo (meses)
    print('Leer observaciones de contaminante para calibracion')

    # Plot de series de tiempo
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    meses = range(len(c_obs))
    ax.plot(meses, np.transpose(YC[1, :]), color='grey', label='Concentraciones simuladas')
    ax.plot(meses, np.transpose(YC), color='grey')
    ax.plot(meses, c_obs, color='blue', label='Concentracion observada', linewidth=2)
    ax.legend()
    ax.set_title('Series de tiempo de concentraciones de compuesto')
    ax.set_xlabel('meses')
    ax.set_ylabel('g/m3')
    plt.savefig(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\p_%s_%shz_seriestotal.png' % (N, Z),
                orientation='landscape', papertype='a4')
    print('Visualizar series de tiempo')

    print(' ')
    # %% Paso 6b: Evaluar los resultados de compuestos
    print('Paso 6b: Evaluar los resultados de compuestos')

    # Definir el modelo
    fun_eval = cal.evaluacion_modelo
    print('Definir el modelo de evaluacion')

    EC = cal.model_execution(fun_eval, XC, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos,
                             hz_lista, m, y, factorh, ndias, c_obs, warmup, n, cont)
    print('Evaluar el modelo FONAG 2.1 para contaminantes')

    # Definir que indicadores se usan para OF
    E_Labels = ['NSE', 'RMSE', 'RSR', 'PBIAS', 'KGE']
    if len(E_cond) != 5:
        E_cond = [True, False, True, True, False]  # Funciones objetivo
    EC_mod, EC_cond_mod, EC_Labels_mod = cal.funcionobjetivo(EC, E_cond, E_Labels)
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\matrizEC.csv', EC_mod, delimiter=',',
               header=",".join(EC_Labels_mod),comments='')
    print('Calcular OF combinando indicadores')

    # Ordenar resultados de mejor a peor
    ordenC = EC_mod[:, 5].argsort()
    XC_sort = XC[ordenC]
    YC_sort = YC[ordenC]
    EC_sort = EC_mod[ordenC]
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\sortedXC.csv', XC_sort, delimiter=',',
               header=",".join(XC_Labels),comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\sortedYC.csv', YC_sort, delimiter=',',
               header=",".join(date_Labels),comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\sortedEC.csv', EC_sort, delimiter=',',
               header=",".join(EC_Labels_mod),comments='')
    print('Ordenar resultados de mejor a peor')

    '''
    # Indicar umbrales de aceptacion
    nse_umbral = 0.50 # umbral para NSE
    rsr_umbral = 0.70 # umbral para RSR
    pbias_umbral = 50 # umbral para PBIAS
    kge_umbral = 0.50 # umbral para KGE
    print('Indicar umbrales de aceptacion')

    # Encontrar funciones que cumplan los umbrales
    umbrales = [1 - nse_umbral, rsr_umbral, abs(pbias_umbral)]
    print('Encontrar funciones que cumplan los umbrales')
    '''

    # Visualizar parametros en nubes de puntos
    Nm = max(3, int(math.ceil(N * 0.01)))
    idxc = np.zeros(shape=(N, 1), dtype=bool)
    idxc[ordenC[range(Nm)]] = True

    for cond_index in range(6):
        if EC_cond_mod[cond_index]:
            plt.figure()
            pf.scatter_plots(XC, EC_mod[:, cond_index], Y_Label=EC_Labels_mod[cond_index], X_Labels=XC_Labels, idx=idxc)
            # plt.show()
    print('Visualizar parametros en nubes de puntos')

    # Plot de ejes paralelos seleccionados
    plt.figure()
    pf.parcoor(XC, X_Labels=XC_Labels, idx=idxc)
    # plt.show()
    print('Plot de ejes paralelos seleccionados')

    # Plot de series de tiempo
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    meses = range(len(c_obs))
    ax.plot(meses, np.transpose(YC_sort[1, :]), c='black', label='%s mejores simulaciones' % Nm)
    ax.plot(meses, np.transpose(YC_sort[range(2, Nm), :]), c='black')
    ax.plot(meses, np.transpose(YC_sort[0, :]), c='red', label='Mejor simulacion')
    ax.plot(meses, c_obs, label='Contaminante observado')
    ax.legend()
    ax.set_title('Series de tiempo de caudal')
    ax.set_xlabel('meses')
    ax.set_ylabel('g/m3')
    # plt.show()
    print('Visualizar series de tiempo')

    elapsed_time = (time.time() - start) / 60
    print('El proceso de calibracion de contaminantes tomo %s minutos.' % elapsed_time)
    print('FIN PASO 6')
    plt.show()
