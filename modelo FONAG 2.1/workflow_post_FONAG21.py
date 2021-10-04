# -*- coding: utf-8 -*-

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

import csv
import threading
import time
import numpy as np
import matplotlib.pyplot as plt 
import re
from numpy import genfromtxt
import os
import random
import unicodedata

def elimina_tildes(s):
    replacements = (
        ("á", "a"),
        ("é", "e"),
        ("í", "i"),
        ("ó", "o"),
        ("ú", "u"),
    )
    for a, b in replacements:
        s = s.replace(a, b).replace(a.upper(), b.upper())
    return s

def percentiles(path, tab):
    patron = "^(F)?[0-9]{4}_[0-9]{2}"
    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')
    os.system('md modeloFONAG\\%s\\postproceso' % t_inputs[16])
    for t in tab:
        name = []
        inputs = open(r'%s\modeloFONAG\%s\tables\t_out_data_%s.csv' % (path, t_inputs[16], t), 'r')
        dictpercent = csv.DictReader(inputs, delimiter=',')
        percent = {}
        listdict = []
        for per in dictpercent:
            percent = {}
            if per.get('NOMBRE'):
                nom = per['NOMBRE']
            elif per.get('Nombre'):
                nom = per['Nombre']
            else:
                nom = per['name']
            name.append(elimina_tildes(nom.strip()))
            for j in per:
                ip = re.compile(patron)
                if ip.search(j):
                    percent.update({j:per[j]})
            listdict.append(percent)
        with open(r'%s\modeloFONAG\%s\postproceso\series_%s.csv' %(path, t_inputs[16], t), 'wb') as myfile:
            wr = csv.writer(myfile)
            listpercent = sorted(listdict[0])
            listpercent.insert(0,'Nombre/Fecha')
            wr.writerow(listpercent)
            for series in listdict:
                listpercent = sorted(series)
                punto = []
                for i in listpercent:
                    punto.append(float(series[i].replace(',','.')))
                punto.insert(0,nom)
                wr.writerow(punto)
    with open(r'%s\modeloFONAG\%s\postproceso\point_labels.csv' %(path, t_inputs[16]), 'wb') as mylabel:
        wr = csv.writer(mylabel, quoting=csv.QUOTE_ALL)
        wr.writerow(name)
    for t in tab:
        punto = []
        series = genfromtxt('%s\modeloFONAG\%s\postproceso\series_%s.csv' %(path, t_inputs[16], t), delimiter=',')
        print("SERIES %s" %t)
        with open(r'%s\modeloFONAG\%s\postproceso\percentil_%s.csv' %(path, t_inputs[16], t), 'wb') as myfile:
            wr = csv.writer(myfile)
            for per in range(100):
                punto.append("Percentil %s"%str(per+1))
            punto.insert(0,'Nombre/Percentil')
            wr.writerow(punto)
            if len(series) > 2:
                lb = 0
                for s in series[1:]:
                    punto = sorted(s)
                    percent = []
                    for per in range(100):
                        percent.append(np.percentile(punto[1:], per+1))
                    percent.insert(0,name[lb])
                    lb += 1
                    #percent.insert(0, qds[32])
                    wr.writerow(percent)
            else:
                punto = sorted(series[1])
                percent = []
                for per in range(100):
                    percent.append(np.percentile(punto[1:], per+1))
                #percent.insert(0, qds[32])
                percent.insert(0,name[0])
                wr.writerow(percent)
    
    for t in tab:
        #lectura de csv con la información
        t_out_data = open(r'%s\modeloFONAG\%s\tables\t_out_data_%s.csv' % (path, t_inputs[16], t), 'r')
        nom = {}
        dictprom = csv.DictReader(t_out_data, delimiter=',')
        for prom in dictprom:
            mes = {'01':[],'02':[],'03':[],'04':[],'05':[],'06':[],'07':[],'08':[],'09':[],'10':[],'11':[],'12':[]}
            for j in prom:
                ip = re.compile(patron)
                if ip.search(j):
                    mes[j[j.find('_')+1:]].append(float(prom[j].replace(',','.')))
            if prom.get('NOMBRE'):
                nom[prom['NOMBRE']] = mes
            elif prom.get('Nombre'):
                nom[prom['Nombre']] = mes
            else:
                nom[prom['name']] = mes
        promes = []
        with open(r'%s\modeloFONAG\%s\postproceso\promedio_out_%s.csv' % (path, t_inputs[16], t), 'wb') as myfile:
            wr = csv.writer(myfile)
            wr.writerow(['NOMBRE/MES','ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE'])
            for n in nom:
                promes = []
                for l in nom[n]:
                    if l == 'Nombre' or l == 'name':
                        continue
                    promes.append(np.mean(nom[n][l]))
                promes.insert(0, n.strip())
                wr.writerow(promes)
                
    n = 0
    for i in range(2):
        if i == 0:
            val = 'percentil'
            title = 'PERCENTILES'
            percentiles = range(100)
        else:
            val = 'promedio_out'
            title = 'PROMEDIOS MENSUALES'
            percentiles = range(1,13)
        for t in tab:
            percentil = genfromtxt('%s\modeloFONAG\%s\postproceso\%s_%s.csv' %(path, t_inputs[16], val, t), delimiter=',')
            fig = plt.figure("%s %s"%(title,t))
            ax = fig.add_subplot(1, 1, 1)
            lb = -1
            if len(percentil) > 2:
                for percent in percentil[1:]:
                    if i == 0:
                        x = np.transpose(sorted(percent[1:], reverse=True))
                    else:
                        x = percent[1:]
                    color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                    lb += 1
                    try:
                        ax.plot(percentiles, x, color=color, label=name[lb], linewidth=5)
                        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                        ax.set_title('%s %s'%(title,t))
                        ax.set_ylabel('Valor')
                        ax.set_xlabel(title)
                        ax.set_yscale('log')
                    except:
                        continue
            else:
                if i == 0:
                    x = np.transpose(sorted(percentil[1][1:], reverse=True))
                else:
                    x = percent[1][1:]
                color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
                try:
                    ax.plot(percentiles, np.transpose(sorted(percentil[1][1:], reverse=True)), color=color, label=name[0], linewidth=5)
                    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                    ax.set_title('%t %s'%(title,t))
                    ax.set_ylabel('Valor')
                    ax.set_xlabel(title)
                    ax.set_yscale('log')
                except:
                    continue
            print('%s %s'%(title,t))

    inputs = open(r'%s\modeloFONAG\inputs\t_inputs.csv' % path, 'r')
    t_inputs = inputs.read().split('\n')[1].split('\r')[0].split(',')
    inputs.close()
    print('Lectura de inputs')

    ####ANTERIOR#####
    '''
    mes1 = ['MES','ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
    bar = []
    for t in tab:
        per = genfromtxt(r'%s\modeloFONAG\%s\postproceso\promedio_out_%s.csv' % (path, t_inputs[16], t), delimiter=',', skip_header=1)
        if type(per[0]) != np.ndarray:
            per = [per]
        width = 0.1
        for percent in per:
            width += 0.2
            color = "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])
            barWidth = 0.1
            fig = plt.figure("Promedios mensuales %s"%t)
            #ax = fig.add_subplot(1, 1, 1)
            meses = np.arange(len(percent[1 :]))
            bar.append(plt.bar(meses + width/2, percent[1 :], width=0.1, color = color, label= mes1[1:]))
            plt.xticks(meses,mes1[1:])
            #pltxticklabels(mes1)
            #plt.yscale('log')000
            plt.yticks(percent[1:])
    '''
    plt.show()
