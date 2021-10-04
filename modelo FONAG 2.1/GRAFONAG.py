import numpy as np
import matplotlib.pyplot as plt
#from numpy.matlib import repmat
#import scipy.stats as st
#import os
#import time
import RSA_FONAG21 as Rt # modulo para realizar RSA con umbrales
import PAWN_FONAG21 as PAWN # modulo para realizar RSA con umbrales
import plot_functions_FONAG21 as pf  # modulo para visualizar resultados
#import calibracionFONAG21 as cal  # modulo de funciones de calibracion
#from util_FONAG21 import aggregate_boot  # function to aggregate the bootstrap results
import csv
from numpy import genfromtxt
#import arcpy
#from arcpy.sa import *
#from arcpy import env
import math
import random

def unirsensi(path):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    Sensi_label = ["MVD (5%)",
                   "MVD (medio)",
                   "MVD (95%)",
                   "MVD_OF (5%)",
                   "MVD_OF (medio)",
                   "MVD_OF (95%)",
                   "PAWN min (5%)",
                   "PAWN min (medio)",
                   "PAWN min (95%)",
                   "PAWN med (5%)",
                   "PAWN med (medio)",
                   "PAWN med (95%)",
                   "PAWN max (5%)",
                   "PAWN max (medio)",
                   "PAWN max (95%)",
                   "PAWN_OF min (5%)",
                   "PAWN_OF min (medio)",
                   "PAWN_OF min (95%)",
                   "PAWN_OF med (5%)",
                   "PAWN_OF med (medio)",
                   "PAWN_OF med (95%)",
                   "PAWN_OF max (5%)",
                   "PAWN_OF max (medio)",
                   "PAWN_OF max (95%)"]
    mvd_m = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_m_RSA.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_lb_RSA.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_ub_RSA.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_m_of = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_m_RSA_OF.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_lb_of = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_lb_RSA_OF.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_ub_of = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_ub_RSA_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_m_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_lb_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_ub_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_m_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_lb_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_ub_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_m_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_lb_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_ub_of = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')

    sensi = np.vstack((mvd_m , mvd_lb , mvd_ub , mvd_m_of , mvd_lb_of , mvd_ub_of , KS_median_m , KS_median_lb , KS_median_ub , KS_mean_m , KS_mean_lb , KS_mean_ub , KS_max_m , KS_max_lb , KS_max_ub , KS_median_m_of , KS_median_lb_of , KS_median_ub_of , KS_mean_m_of , KS_mean_lb_of , KS_mean_ub_of , KS_max_m_of , KS_max_lb_of , KS_max_ub_of)).T
    
    np.savetxt(r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\var_sensibilidad.csv', sensi, delimiter=',',header=','.join(Sensi_label),comments='')
    
def grafcdfrsa(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels) 
    idxb = genfromtxt('%s\modeloFONAG\%s\calibracion\idxb_RSA.csv' % (path, t_inputs[16]), delimiter=',', dtype=bool)
    Rt.RSA_plot_thres(X, idxb, X_Labels=X_Labels, str_legend=['cumplen', 'no cumplen'])
    plt.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_RSA_cdf.png',
                orientation='landscape', papertype='a4')
    plt.title("HOLA")
    plt.show()
    plt.close('all')

def grafsmvd(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)
    mvd_m = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_m_RSA.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_lb_RSA.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_ub_RSA.csv' % (path, t_inputs[16]), delimiter=',')
    fig = plt.figure("Sensibilidad MVD")
    pf.boxplot1(mvd_m, X_Labels=X_Labels, Y_Label='Sensibilidad MVD', S_lb=mvd_lb, S_ub=mvd_ub)
    print('Plot de sensibilidad MVD con intervalos de confianza')
    plt.show()

def grafcdfrsaof(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels) 
    idxb = genfromtxt('%s\modeloFONAG\%s\calibracion\idxb_RSA_OF.csv' % (path, t_inputs[16]), delimiter=',', dtype=bool)
    Rt.RSA_plot_thres(X, idxb, X_Labels=X_Labels, str_legend=['cumplen', 'no cumplen'])
    plt.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_RSA_OF_cdf.png',
                orientation='landscape', papertype='a4')
    plt.show()

def grafsmvdof(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)
    mvd_m = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_m_RSA_OF.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_lb_RSA_OF.csv' % (path, t_inputs[16]), delimiter=',')
    mvd_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\mvd_ub_RSA_OF.csv' % (path, t_inputs[16]), delimiter=',')
    fig = plt.figure("Seneibilidad MVD OF")
    pf.boxplot1(mvd_m, X_Labels=X_Labels, Y_Label='Sensibilidad MVD', S_lb=mvd_lb, S_ub=mvd_ub)
    print('Plot de sensibilidad MVD con intervalos de confianza')
    plt.show()

def grafcdfpawn(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
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
    n = 10 # numero de intervalos condicionantes
    
    YF, FU, FC, xc = PAWN.pawn_plot_cdf(X, E, n, cbar=True, n_col=3, labelinput=X_Labels)
    plt.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_PAWN_cdf.png',
                orientation='landscape', papertype='a4')
    print('Plot de CDFs condicionales y no condicionales')
    plt.show()

def grafspawn(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)
    
    KS_median_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')

    fig = plt.figure("Sensibilidad PAWN Qmedio")
    plt.subplot(131)
    pf.boxplot1(KS_median_m, S_lb=KS_median_lb, S_ub=KS_median_ub,
                X_Labels=X_Labels, Y_Label='KS (median)')
    plt.subplot(132)
    pf.boxplot1(KS_mean_m, S_lb=KS_mean_lb, S_ub=KS_mean_ub,
                X_Labels=X_Labels, Y_Label='KS (mean)')
    plt.subplot(133)
    pf.boxplot1(KS_max_m, S_lb=KS_max_lb, S_ub=KS_max_ub,
                X_Labels=X_Labels, Y_Label='Ks (max)')
    print('Plot de sensibilidad PAWN con intervalos de confianza')
    plt.show()

def grafdpawn(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    X_Labels_dummy = X_Labels
    X_Labels_dummy.append('dummy')
    
    KS_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_m_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_lb_PAWN.csv' % (path, t_inputs[16]), delimiter=',')
    KS_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_ub_PAWN.csv' % (path, t_inputs[16]), delimiter=',')

    fig = plt.figure("Dummy PAWN Qmedio")  # plot main and total separately
    pf.boxplot1(KS_m, S_lb=KS_lb, S_ub=KS_ub, X_Labels=X_Labels_dummy, Y_Label='KS')
    print('Plot de sensibilidad PAWN con variable dummy')
    plt.show("Dummy PAWN")


def grafcdfpawnof(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)
    # Matriz de caudales o contaminantes simulados
    if cont:
        E = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedEC.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    else:
        E = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedE.csv' % (path, t_inputs[16]), delimiter=',', skip_header=1)
    E = E[:, 5]

    n = 10 # numero de intervalos condicionantes
    
    YF, FU, FC, xc = PAWN.pawn_plot_cdf(X, E, n, cbar=True, n_col=3, labelinput=X_Labels)
    plt.savefig(r'%s\modeloFONAG\%s\sensibilidad' % (path, t_inputs[16]) + r'\p_PAWN_OF_cdf.png',
                orientation='landscape', papertype='a4')
    print('Plot de CDFs condicionales y no condicionales')
    plt.show()

def grafspawnof(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)
    
    KS_median_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_m_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_lb_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_median_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_median_ub_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_m_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_lb_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_mean_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_mean_ub_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_m_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_lb_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_max_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_max_ub_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')

    fig = plt.figure("Sensibilidad PAWN OF")
    plt.subplot(131)
    pf.boxplot1(KS_median_m, S_lb=KS_median_lb, S_ub=KS_median_ub,
                X_Labels=X_Labels, Y_Label='KS (median)')
    plt.subplot(132)
    pf.boxplot1(KS_mean_m, S_lb=KS_mean_lb, S_ub=KS_mean_ub,
                X_Labels=X_Labels, Y_Label='KS (mean)')
    plt.subplot(133)
    pf.boxplot1(KS_max_m, S_lb=KS_max_lb, S_ub=KS_max_ub,
                X_Labels=X_Labels, Y_Label='Ks (max)')
    print('Plot de sensibilidad PAWN con intervalos de confianza')
    plt.show()

def grafdpawnof(path, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    X_Labels_dummy = X_Labels
    X_Labels_dummy.append('dummy')
    
    KS_m = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_m_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_lb = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_lb_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')
    KS_ub = genfromtxt('%s\modeloFONAG\%s\calibracion\KS_ub_PAWN_OF.csv' % (path, t_inputs[16]), delimiter=',')

    fig = plt.figure("Sensibilidad Dummy PAWN OF")  # plot main and total separately
    pf.boxplot1(KS_m, S_lb=KS_lb, S_ub=KS_ub, X_Labels=X_Labels_dummy, Y_Label='KS')
    print('Plot de sensibilidad PAWN con variable dummy')
    plt.show()

def grafep(path,cont=False, N=1000):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    # Nombres de parametros
    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    muesconf_Z = open(r'%s/modeloFONAG/%s/' % (path, t_inputs[16]) + r'muescoef_Z.txt','r+')  
    Z = muesconf_Z.read().split('\n')
    muesconf_Z.close()
    
    fig = plt.figure("Ejes paralelos") 
    pf.parcoor(X, X_Labels=X_Labels)
    print('Plot de ejes paralelos')
    plt.show()

def grafst(path, cont=False, N=1000):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        Y = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedYC.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    else:
        Y = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedY.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)

    tipos = open(r'%s\modeloFONAG\%s\calibracion\tipos.csv' % (path, t_inputs[16]), 'r')
    tipos = tipos.read().split('\n')[0].split(',')
    tipos = map(int, tipos)
    Z = len(tipos)
        
    data = np.genfromtxt(r'%s\modeloFONAG\inputs\%s' % (path, t_inputs[19]), comments='%')
    y_obs = data[:, 1]
        
    fig = plt.figure("Series de tiempo")
    ax = fig.add_subplot(1, 1, 1)
    meses = range(len(y_obs))
    ax.plot(meses, np.transpose(Y[1, :]), color='grey', label='Caudales simulados')
    ax.plot(meses, np.transpose(Y), color='grey')
    ax.plot(meses, y_obs, color='blue', label='Caudal observado', linewidth=2)
    ax.legend()
    ax.set_title('Series de tiempo de caudal')
    ax.set_xlabel('meses')
    ax.set_ylabel('m3/s')
    print('Visualizar series de tiempo')
    plt.show()

def grafepc(path, cont=False,N=1000):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)

    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)

    E_mod = genfromtxt('%s\modeloFONAG\%s\calibracion\matrizE.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    orden = E_mod[:, 5].argsort()
    
    Nm = max(3, int(math.ceil(N * 0.01)))
    idxb = np.zeros(shape=(N, 1), dtype=bool)
    idxb[orden[range(Nm)]] = True
    
    # Plot de ejes paralelos seleccionados
    fig = plt.figure("Ejes paralelos seleccionados")
    pf.parcoor(X, X_Labels=X_Labels, idx=idxb)
    print('Plot de ejes paralelos seleccionados')
    plt.show()

def grafstc(path, cont=False,N=1000):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()

    if cont:
        Y = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedYC.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    else:
        Y = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedY.csv' % (path, t_inputs[16]), delimiter=',',
                       skip_header=1)
    
    data = np.genfromtxt(r'%s\modeloFONAG\inputs\%s' % (path, t_inputs[19]), comments='%')
    y_obs = data[:, 1]

    # Tipos de hidrozonas
    tipos = open(r'%s\modeloFONAG\%s\calibracion\tipos.csv' % (path, t_inputs[16]), 'r')
    tipos = tipos.read().split('\n')[0].split(',')
    tipos = map(int, tipos)
    Z = len(tipos)
    
    Nm = max(3, int(math.ceil(N * 0.01)))
    
    # Plot de series de tiempo
    fig = plt.figure("Series de tiempo seleccionados")
    ax = fig.add_subplot(1, 1, 1)
    meses = range(len(y_obs))

    E_mod = genfromtxt('%s\modeloFONAG\%s\calibracion\matrizE.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    orden = E_mod[:, 5].argsort()
    Y_sort = Y[orden]
    
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
    print('Visualizar series de tiempo seleccionados')
    plt.show()

def grafFunObj(path, E_cond_mod=[False,False,False,False,False,False],N=1000, cont=False):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()

    tipos = open(r'%s\modeloFONAG\%s\calibracion\tipos.csv' % (path, t_inputs[16]), 'r')
    tipos = tipos.read().split('\n')[0].split(',')
    tipos = map(int, tipos)
    Z = len(tipos)
    
    if cont:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedXC.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    else:
        X = genfromtxt('%s\modeloFONAG\%s\calibracion\sortedX.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)

    E_mod = genfromtxt('%s\modeloFONAG\%s\calibracion\matrizE.csv' % (path, t_inputs[16]), delimiter=',',skip_header=1)
    orden = E_mod[:, 5].argsort()
    E_Labels_mod = open(r'%s\modeloFONAG\%s\calibracion\E_Labels_mod.csv' % (path, t_inputs[16]), 'r')
    E_Labels_mod = E_Labels_mod.read().split('\n')[0].split(',')
    E_Labels_mod = map(str, E_Labels_mod) 

    X_Labels = open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'r')
    X_Labels = X_Labels.read().split('\n')[0].split(',')
    X_Labels = map(str, X_Labels)
    
    # Visualizar parametros en nubes de puntos
    Nm = max(3, int(math.ceil(N * 0.01)))
    idxb = np.zeros(shape=(N, 1), dtype=bool)
    idxb[orden[range(Nm)]] = True

    for cond_index in range(6):
        if E_cond_mod[cond_index]:
            fig = plt.figure(E_Labels_mod[cond_index])
            pf.scatter_plots(X, E_mod[:, cond_index], Y_Label=E_Labels_mod[cond_index], X_Labels=X_Labels, idx=idxb)

    print('Visualizar parametros en nubes de puntos')
    plt.show()

def grafser(path, t, output):
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    point_Labels = open(r'%s\modeloFONAG\%s\postproceso\point_labels.csv' % (path, t_inputs[16]), 'r')
    point_Labels = point_Labels.read().split('\n')[0].split(',')
    point_Labels = map(str, point_Labels)
    print(point_Labels)
    if output == "tables":
        percentil = genfromtxt('%s\modeloFONAG\%s\postproceso\series_%s.csv' %(path, t_inputs[16] ,t), delimiter=',')
        title = 'Series'
    elif output == "postproceso":
        percentil = genfromtxt('%s\modeloFONAG\%s\postproceso\percentil_%s.csv' %(path, t_inputs[16] ,t), delimiter=',')
        title = 'Percentil'
    else:
        percentil = genfromtxt('%s\modeloFONAG\%s\postproceso\promedio_out_%s.csv' %(path, t_inputs[16] ,t), delimiter=',')
        title = 'Promedios mensuales'
        
    fig = plt.figure("PERCENTILES %s"%t)
    ax = fig.add_subplot(1, 1, 1)
    lb = -1
    if len(percentil) > 2:
        for percent in percentil:
            if title == 'tables':
                x = sorted(np.transpose(percent), reverse=True)
            else:
                x = percent
            percentiles = range(len(percent))
            color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
            #ax.plot(meses, np.transpose(X[1 :]), color='grey', label='Caudales simulados')
            lb += 1
            try:
                ax.plot(percentiles, x, color=color, label=point_Labels[lb], linewidth=5)
                ax.legend()
                ax.set_title('%s %s'%(title,t))
                ax.set_ylabel('Valor')
                ax.set_xlabel(title)
                ax.set_yscale('log')
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                plt.grid(True)
                ax.set_axes()
            except:
                continue
    else:
        if title == 'tables':
            x = sorted(np.transpose(percentil[1][1:]), reverse=True)
        else:
            x = percentil[1][1:]
        percentiles = range(1,len(percentil[1][1:])+1)
        color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        #ax.plot(meses, np.transpose(X[1 :]), color='grey', label='Caudales simulados')
        lb += 1
        ax.plot(percentiles, x, color=color, label=point_Labels[lb], linewidth=5)
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        ax.set_title('%s %s'%(title,t))
        ax.set_ylabel('Valor')
        ax.set_xlabel(title)
        ax.set_yscale('log')
        print('Percentiles %s'%t)
    plt.show()

def grafmensual(path, t):
    mes1 = ['NOMBRE/MES','ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    per = genfromtxt(r'%s\modeloFONAG\%s\postproceso\promedio_out_%s.csv' % (path, t_inputs[16], t), delimiter=',', skip_header=1)
    if type(per[0]) != np.ndarray:
        per = [per]
    width = 0.1
    bar = []
    for percent in per:
        barWidth = 0.1
        color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
        width += 0.2
        fig = plt.figure("Promedios mensuales %s"%t)
        #ax = fig.add_subplot(1, 1, 1)
        meses = np.arange(1,len(percent[1 :])+1)
        bar.append(plt.bar(meses + width/2, percent[1 :], width=0.1, color = color, label= mes1[1:]))
        plt.xticks(meses,  mes1[1:])
    plt.show()
