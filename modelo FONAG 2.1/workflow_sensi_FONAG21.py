#############################################################################
#                                                                           #
#  Script:      Modelo FONAG 2.1 by atuk                                    #
#  Description: Modelo Hidrologico FONAG actualizado                        #
#  Created By:  ATUK Consultoria Estrategica & Katarisoft                   #
#  Date:        21-May-2020                                                 #
#                                                                           #
#############################################################################

'''
Este script realiza el workflow de analisis de sensibilidad del modelo FONAG 2.1

MODELO Y AREA DE ESTUDIO

El modelo utilizado es el modelo FONAG 2.1 by ATUK (Ochoa-Tocachi et al., 2020).
Los inputs de calibracion son los coeficientes Kc y a,b,spt de las hidrozonas,
el output son indicadores de sensibilidad.

En caso de existir datos, se realiza tambien el analisis de sensibilidad para
los coeficientes de transporte de compuestos as, at de las hidrozonas.

INDICE

Pasos:
0. Inicializar el espacio de trabajo e importar modulos de python

(Cargar datos producidos por el modulo de calibracion)
1. Analisis de sensibilidad regional (RSA) para funciones seleccionadas
2. Analisis de sensibilidad regional (RSA) para funcion OF
3. Analisis de sensibilidad PAWN (Pianosi et al., 2015) para caudal medio
4. Analisis de sensibilidad PAWN (Pianosi et al., 2015) para funcion OF

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
import RSA_FONAG21 as Rt # modulo para realizar RSA con umbrales
import PAWN_FONAG21 as PAWN # modulo para realizar RSA con umbrales
import plot_functions_FONAG21 as pf  # modulo para visualizar resultados
import calibracionFONAG21 as cal  # modulo de funciones de calibracion
from util_FONAG21 import aggregate_boot  # function to aggregate the bootstrap results
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

def rsa(path, E_cond=[True, False, True, True, False, True], E_umbral=[0.5, 1, 0.7, 25, 0.5, 1], cont=False):
    print('ANALISIS DE SENSIBILIDAD REGIONAL PARA FUNCIONES OBJETIVO')
    start = time.time()

    print(' ')
    # %% Paso 1a: Cargar datos del proceso de calibracion
    print('Paso 1a: Cargar datos del proceso de calibracion')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Crear carpeta de salidas
    print('Crear carpeta de salidas')
    os.system('md modeloFONAG\\%s\\sensibilidad' % t_inputs[16])

    # Matriz de combinaciones de parametros
    if cont:
        XC = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',
                        skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    print('Lectura de combinaciones de parametros')
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    # Matriz de funciones objetivo
    if cont:
        E = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedEC.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    else:
        E = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedE.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    E[:, 0] = 1 - E[:, 0]
    E[:, 3] = abs(E[:, 3])
    E[:, 4] = 1 - E[:, 4]
    print('Lectura de funciones objetivo')

    print(' ')
    # %% Paso 1b: Analisis de sensibilidad regional
    print('Paso 1b: Analisis de sensibilidad regional')

    # Definir que indicadores se usan para RSA
    E_Labels = ['NSE', 'RMSE', 'RSR', 'PBIAS', 'KGE', 'OF']
    if len(E_cond) == 5:
        E_cond.append(False) # Funciones objetivo
    elif len(E_cond) == 6:
        E_cond[5] = False # Funciones objetivo
    elif len(E_cond) != 6:
        E_cond = [True, False, True, True, False, False]  # Funciones objetivo
    if len(E_umbral) == 5:
        E_umbral.append(1) # Funciones objetivo
    elif len(E_umbral) != 6:
        E_umbral = [0.5, 1, 0.7, 25, 0.5, 1]
    print('Definir umbrales de aceptacion')

    # Extraer funciones seleccionadas
    E_umbral_mod = [1-E_umbral[0], E_umbral[1], E_umbral[2], abs(E_umbral[3]), 1-E_umbral[4], E_umbral[5]]
    E_umbrales = []
    E_cond_index = []
    for cond_index in range(6):
        if E_cond[cond_index]:
            E_umbrales.append(E_umbral_mod[cond_index])
            E_cond_index.append(cond_index)
    E_mod = E[:, E_cond_index]
    print('Extraer funciones seleccionadas')

    # Aplicar Analisis de Sensibilidad Regional
    E_max = np.max(E_mod, axis=0) <= E_umbrales
    E_min = np.min(E_mod, axis=0) >= E_umbrales
    if E_max.all():
        print('Todas las simulaciones cumplen los umbrales')
    elif E_min.all():
        print('No existen simulaciones que cumplan los umbrales.')
    else:
        mvd, spread, irr, idxb = Rt.RSA_indices_thres(X, E_mod, E_umbrales)
        print('Aplicar Analisis de Sensibilidad Regional')
        np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\idxb_RSA.csv', idxb, delimiter=',',
                   header='',comments='', fmt='%s')
        # Plot CDFs de los parametros
        Rt.RSA_plot_thres(X, idxb, X_Labels=X_Labels, str_legend=['cumplen', 'no cumplen'])
        plt.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_RSA_cdf.png',
                    orientation='landscape', papertype='a4')
        print('Plot CDFs de los parametros')

        # Calcular intervalos de confianza de los indicadores de sensibilidad usando bootstrapping
        Nboot = 1000
        mvd, spread, irr, idxb = Rt.RSA_indices_thres(X, E_mod, E_umbrales, Nboot=Nboot)
        # mvd, spread e irr tienen tamano (Nboot, M)
        print('Calcular intervalos de confianza')

        # Calcular media e intervalos de confianza de MVD entre los remuestreos:
        mvd_m, mvd_lb, mvd_ub = aggregate_boot(mvd)  # shape (M,)

        np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\mvd_m_rsa.csv', mvd_m, delimiter=',',header='',comments='')
        np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\mvd_lb_rsa.csv', mvd_lb, delimiter=',',header='',comments='')
        np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\mvd_ub_rsa.csv', mvd_ub, delimiter=',',header='',comments='')
        
        # Plot resultados:
        fig = plt.figure()
        pf.boxplot1(mvd_m, X_Labels=X_Labels, Y_Label='Sensibilidad MVD', S_lb=mvd_lb, S_ub=mvd_ub)
        fig.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_MVD_boot.png',
                    orientation='landscape', papertype='a4')
        print('Plot de sensibilidad MVD con intervalos de confianza')

    elapsed_time = (time.time() - start) / 60
    print('El proceso de analisis de sensibilidad RSA tomo %s minutos.' % elapsed_time)
    print('FIN PASO 1')
    plt.show()
    
def rsa_OF(path, E_umbrales = 1, cont=False):
    print('CONVERGENCIA DEL ANALISIS DE SENSIBILIDAD REGIONAL PARA OF')
    start = time.time()

    print(' ')
    # %% Paso 2a: Cargar datos del proceso de calibracion
    print('Paso 2a: Cargar datos del proceso de calibracion')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Crear carpeta de salidas
    print('Crear carpeta de salidas')
    os.system('md modeloFONAG\\%s\\sensibilidad' % t_inputs[16])

    # Matriz de combinaciones de parametros
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',
                        skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    print('Lectura de combinaciones de parametros')
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    # Matriz de funciones objetivo
    if cont:
        E = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedEC.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    else:
        E = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedE.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    E = E[:, 5]
    print('Lectura de funciones objetivo')

    print(' ')
    # %% Paso 2b: Analisis de sensibilidad regional
    print('Paso 2b: Analisis de sensibilidad regional')

    # Usar OF para RSA
    # E_umbrales = 1
    print('Definir umbrales de aceptacion')

    # Aplicar Analisis de Sensibilidad Regional
    E_max = max(E)
    E_min = min(E)
    if E_max <= E_umbrales:
        print('Todas las simulaciones cumplen los umbrales')
    elif E_min >= E_umbrales:
        print('No existen simulaciones que cumplan los umbrales.')
    else:
        mvd, spread, irr, idxb = Rt.RSA_indices_thres(X, E, E_umbrales)
        print('Aplicar Analisis de Sensibilidad Regional')

        np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\idxb_RSA_OF.csv', idxb, delimiter=',',header='',comments='', fmt='%s')
        
        # Plot CDFs de los parametros
        Rt.RSA_plot_thres(X, idxb, X_Labels=X_Labels, str_legend=['cumplen', 'no cumplen'])
        plt.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_RSA_OF_cdf.png',
                    orientation='landscape', papertype='a4')
        print('Plot CDFs de los parametros')

        # Calcular intervalos de confianza de los indicadores de sensibilidad usando bootstrapping
        Nboot = 1000
        mvd, spread, irr, idxb = Rt.RSA_indices_thres(X, E, E_umbrales, Nboot=Nboot)
        # mvd, spread e irr tienen tamano (Nboot, M)
        print('Calcular intervalos de confianza')

        # Calcular media e intervalos de confianza de MVD entre los remuestreos:
        mvd_m, mvd_lb, mvd_ub = aggregate_boot(mvd)  # shape (M,)
        np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\mvd_m_RSA_OF.csv', mvd_m, delimiter=',',header='',comments='')
        np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\mvd_lb_RSA_OF.csv', mvd_lb, delimiter=',',header='',comments='')
        np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\mvd_ub_RSA_OF.csv', mvd_ub, delimiter=',',header='',comments='')
        # Plot results:
        fig = plt.figure()
        pf.boxplot1(mvd_m, X_Labels=X_Labels, Y_Label='Sensibilidad MVD', S_lb=mvd_lb, S_ub=mvd_ub)
        fig.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_MVD_OF_boot.png',
                    orientation='landscape', papertype='a4')
        print('Plot de sensibilidad MVD con intervalos de confianza')

    elapsed_time = (time.time() - start) / 60
    print('El proceso de analisis de sensibilidad RSA para OF tomo %s minutos.' % elapsed_time)
    print('FIN PASO 2')
    plt.show()

def pawn(path, cont=False):
    print('ANALISIS DE SENSIBILIDAD PAWN PARA CAUDAL O CONTAMINANTE PROMEDIO')
    start = time.time()

    print(' ')
    # %% Paso 3a: Cargar datos del proceso de calibracion
    print('Paso 3a: Cargar datos del proceso de calibracion')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Crear carpeta de salidas
    print('Crear carpeta de salidas')
    os.system('md modeloFONAG\\%s\\sensibilidad' % t_inputs[16])

    # Matriz de combinaciones de parametros
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',
                        skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    print('Lectura de combinaciones de parametros')
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    # Matriz de caudales o contaminantes simulados
    if cont:
        Y = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedYC.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    else:
        Y = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedY.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    print('Lectura de resultados del modelo')
    E = np.mean(Y, axis=1)

    print(' ')
    # %% Paso 3b: Analisis de sensibilidad PAWN
    print('Paso 3b: Analisis de sensibilidad PAWN')

    n = 10  # numero de intervalos condicionantes

    # Calcular y plotear CDFs condicionales y no condicionales:
    
    YF, FU, FC, xc = PAWN.pawn_plot_cdf(X, E, n, cbar=True, n_col=3, labelinput=X_Labels)
    plt.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_PAWN_cdf.png',
                orientation='landscape', papertype='a4')
    print('Plot de CDFs condicionales y no condicionales')

    # Usar bootstrapping para calcular intervalos de confianza:
    Nboot = 1000
    # Calcular indicadores de sensibilidad para Nboot remuestreos
    KS_median, KS_mean, KS_max = PAWN.pawn_indices(X, E, n, Nboot=Nboot)
    # KS_median, KS_mean y KS_max tienen tamano (Nboot, M)
    # Calcular media e intervalos de confianza entre los resultados de los remuestreos:
    KS_median_m, KS_median_lb, KS_median_ub = aggregate_boot(KS_median)  # shape (M,)
    KS_mean_m, KS_mean_lb, KS_mean_ub = aggregate_boot(KS_mean)  # shape (M,)
    KS_max_m, KS_max_lb, KS_max_ub = aggregate_boot(KS_max)  # shape (M,)

    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_median_m_PAWN.csv', KS_median_m, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_median_lb_PAWN.csv', KS_median_lb, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_median_ub_PAWN.csv', KS_median_ub, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_mean_m_PAWN.csv', KS_mean_m, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_mean_lb_PAWN.csv', KS_mean_lb, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_mean_ub_PAWN.csv', KS_mean_ub, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_max_m_PAWN.csv', KS_max_m, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_max_lb_PAWN.csv', KS_max_lb, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_max_ub_PAWN.csv', KS_max_ub, delimiter=',',header='',comments='')
    
    # Plot bootstrapping results:
    fig = plt.figure()
    plt.subplot(131)
    pf.boxplot1(KS_median_m, S_lb=KS_median_lb, S_ub=KS_median_ub,
                X_Labels=X_Labels, Y_Label='KS (median)')
    plt.subplot(132)
    pf.boxplot1(KS_mean_m, S_lb=KS_mean_lb, S_ub=KS_mean_ub,
                X_Labels=X_Labels, Y_Label='KS (mean)')
    plt.subplot(133)
    pf.boxplot1(KS_max_m, S_lb=KS_max_lb, S_ub=KS_max_ub,
                X_Labels=X_Labels, Y_Label='Ks (max)')
    fig.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_PAWN_boot.png',
                orientation='landscape', papertype='a4')
    print('Plot de sensibilidad PAWN con intervalos de confianza')

    print(' ')
    # %% Paso 3c: Analisis de sensibilidad PAWN para una variable dummy
    print('Paso 3c: Analisis de sensibilidad PAWN para una variable dummy')

    # Nombre de los parametros incluyendo el dummy:
    X_Labels_dummy = X_Labels
    X_Labels_dummy.append('dummy')

    # Indicadores de sensibilidad usando bootstrap y la variable dummy:
    # Usar bootstrapping para calcular intervalos de confianza:
    Nboot = 1000
    # Calcular los indicadores de sensibilidad usando los remuestreos.
    # Se analiza solamente KS_max (y no KS_median y KS_mean) para mostrar resultados solamente.
    _, _, KS_max, KS_dummy = PAWN.pawn_indices(X, E, n, Nboot=Nboot, dummy=True)
    # KS_max has shape (Nboot, M), KS_dummy has shape (Nboot, )

    # Cacular media e intervalos de confianza entre los remuestreos:
    KS_m, KS_lb, KS_ub = aggregate_boot(np.column_stack((KS_max, KS_dummy)))

    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_m_PAWN.csv', KS_m, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_lb_PAWN.csv', KS_lb, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_ub_PAWN.csv', KS_ub, delimiter=',',header='',comments='')
    
    # Plot resultados de boostrap
    fig = plt.figure()  # plot main and total separately
    pf.boxplot1(KS_m, S_lb=KS_lb, S_ub=KS_ub, X_Labels=X_Labels_dummy, Y_Label='KS')
    fig.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_PAWN_dummy.png',
                orientation='landscape', papertype='a4')
    print('Plot de sensibilidad PAWN con variable dummy')

    elapsed_time = (time.time() - start) / 60
    print('El proceso de analisis de sensibilidad PAWN tomo %s minutos.' % elapsed_time)
    print('FIN PASO 3')
    plt.show()

def pawn_OF(path, cont=False):
    print('ANALISIS DE SENSIBILIDAD PAWN PARA OF')
    start = time.time()

    print(' ')
    # %% Paso 4a: Cargar datos del proceso de calibracion
    print('Paso 4a: Cargar datos del proceso de calibracion')

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    # Crear carpeta de salidas
    print('Crear carpeta de salidas')
    os.system('md modeloFONAG\\%s\\sensibilidad' % t_inputs[16])

    # Matriz de combinaciones de parametros
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',
                        skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    print('Lectura de combinaciones de parametros')
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    # Matriz de funciones objetivo
    if cont:
        E = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedEC.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    else:
        E = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedE.csv' % (path, t_inputs[16]), delimiter=',', skip_header=1)
    E = E[:, 5]
    print('Lectura de funciones objetivo')

    print(' ')
    # %% Paso 4b: Analisis de sensibilidad PAWN
    print('Paso 4b: Analisis de sensibilidad PAWN')

    n = 10  # numero de intervalos condicionantes

    # Calcular y plotear CDFs condicionales y no condicionales:
    YF, FU, FC, xc = PAWN.pawn_plot_cdf(X, E, n, cbar=True, n_col=3, labelinput=X_Labels)
    plt.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_PAWN_OF_cdf.png',
                orientation='landscape', papertype='a4')
    print('Plot de CDFs condicionales y no condicionales')

    # Usar bootstrapping para calcular intervalos de confianza:
    Nboot = 1000
    # Calcular indicadores de sensibilidad para Nboot remuestreos
    KS_median, KS_mean, KS_max = PAWN.pawn_indices(X, E, n, Nboot=Nboot)
    # KS_median, KS_mean y KS_max tienen tamano (Nboot, M)
    # Calcular media e intervalos de confianza entre los resultados de los remuestreos:
    KS_median_m, KS_median_lb, KS_median_ub = aggregate_boot(KS_median)  # shape (M,)
    KS_mean_m, KS_mean_lb, KS_mean_ub = aggregate_boot(KS_mean)  # shape (M,)
    KS_max_m, KS_max_lb, KS_max_ub = aggregate_boot(KS_max)  # shape (M,)

    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_median_m_PAWN_OF.csv', KS_median_m, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_median_lb_PAWN_OF.csv', KS_median_lb, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_median_ub_PAWN_OF.csv', KS_median_ub, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_mean_m_PAWN_OF.csv', KS_mean_m, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_mean_lb_PAWN_OF.csv', KS_mean_lb, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_mean_ub_PAWN_OF.csv', KS_mean_ub, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_max_m_PAWN_OF.csv', KS_max_m, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_max_lb_PAWN_OF.csv', KS_max_lb, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_max_ub_PAWN_OF.csv', KS_max_ub, delimiter=',',header='',comments='')

    
    # Plot bootstrapping results:
    fig = plt.figure()
    plt.subplot(131)
    pf.boxplot1(KS_median_m, S_lb=KS_median_lb, S_ub=KS_median_ub,
                X_Labels=X_Labels, Y_Label='KS (median)')
    plt.subplot(132)
    pf.boxplot1(KS_mean_m, S_lb=KS_mean_lb, S_ub=KS_mean_ub,
                X_Labels=X_Labels, Y_Label='KS (mean)')
    plt.subplot(133)
    pf.boxplot1(KS_max_m, S_lb=KS_max_lb, S_ub=KS_max_ub,
                X_Labels=X_Labels, Y_Label='Ks (max)')
    fig.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_PAWN_OF_boot.png',
                orientation='landscape', papertype='a4')
    print('Plot de sensibilidad PAWN con intervalos de confianza')

    print(' ')
    # %% Paso 4c: Analisis de sensibilidad PAWN para una variable dummy
    print('Paso 4c: Analisis de sensibilidad PAWN para una variable dummy')

    # Nombre de los parametros incluyendo el dummy:
    X_Labels_dummy = X_Labels
    X_Labels_dummy.append('dummy')

    # Indicadores de sensibilidad usando bootstrap y la variable dummy:
    # Usar bootstrapping para calcular intervalos de confianza:
    Nboot = 1000
    # Calcular los indicadores de sensibilidad usando los remuestreos.
    # Se analiza solamente KS_max (y no KS_median y KS_mean) para mostrar resultados solamente.
    _, _, KS_max, KS_dummy = PAWN.pawn_indices(X, E, n, Nboot=Nboot, dummy=True)
    # KS_max has shape (Nboot, M), KS_dummy has shape (Nboot, )

    # Cacular media e intervalos de confianza entre los remuestreos:
    KS_m, KS_lb, KS_ub = aggregate_boot(np.column_stack((KS_max, KS_dummy)))


    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_m_PAWN_OF.csv', KS_m, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_lb_PAWN_OF.csv', KS_lb, delimiter=',',header='',comments='')
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\KS_ub_PAWN_OF.csv', KS_ub, delimiter=',',header='',comments='')
    
    # Plot resultados de boostrap
    fig = plt.figure()  # plot main and total separately
    pf.boxplot1(KS_m, S_lb=KS_lb, S_ub=KS_ub, X_Labels=X_Labels_dummy, Y_Label='KS')
    fig.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_PAWN_OF_dummy.png',
                orientation='landscape', papertype='a4')
    print('Plot de sensibilidad PAWN con variable dummy')

    elapsed_time = (time.time() - start) / 60
    print('El proceso de analisis de sensibilidad PAWN para OF tomo %s minutos.' % elapsed_time)
    print('FIN PASO 4')
    plt.show()
