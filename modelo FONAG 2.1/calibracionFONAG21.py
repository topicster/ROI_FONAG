#############################################################################
#                                                                           #
#  Script:      Modelo FONAG 2.1 by atuk                                    #
#  Description: Modelo Hidrologico FONAG actualizado                        #
#  Created By:  ATUK Consultoria Estrategica & Katarisoft                   #
#  Date:        30-Abr-2020                                                 #
#                                                                           #
#############################################################################

# Import system modules
import os
import csv
import math
import numpy as np
from numpy.matlib import repmat
import scipy.stats as st
from scipy.spatial.distance import pdist
import dbfread

import arcpy
from arcpy.sa import *
from arcpy import env

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension('Spatial')
# Check out the ArcGIS Geostatistical Analyst extension license
arcpy.CheckOutExtension('GeoStats')
# Permitir sobreescritura de archivos
env.overwriteOutput = True

def modelo_iterativo(param, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista, m, y, factorh, ndias, n=0.4, cont=False):

    '''Esta funcion simula la version simplificada del modelo hidrologico FONAG 2.1 (Ochoa-Tocachi et al., 2020).

    Uso:
        Q_sim = modelo_iterativo(param, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista,
                                 m, y, factorh, ndias, n, cont)

    Input:
      param = vector de parametros del modelo                   - numpy.ndarray(2*H, )
              1 hasta H:      Kc    = Coeficientes de cultivo para ept [-]
              H+1 hasta 2*H: coef   = a, b, spt [-]
      rain  = serie de tiempo de precipitacion                  - numpy.ndarray(T, )
      evap  = serie de tiempo de evapotranspiracion potencial   - numpy.ndarray(T, )
      temp  = serie de tiempo de temperatura                    - numpy.ndarray(T, )
      demand_m3_s = acumulacion de usos de agua [m3/s]          - scalar
      area_aporte = area de aporte al punto de aforo [km2]      - scalar
      areas = % de areas de la cuenca para cada hidrozona       - dict{H}
              H: numero de hidrozonas
      tipos = tipos de regulacion hidrologica de cada hidrozona - numpy.ndarray(H, 1)
      hz_lista  = Hidrozonas relevantes para la cuenca de aforo
      m         = mes inicial para la simulacion
      y         = anio inicial para la simulacion
      factorh   = factor H de lavado de suelos (0:ene, 11:dic)  - list: 12
      ndias     = numero de dias de cada mes   (0:ene, 11:dic)  - list: 12
      n         = factor exponencial de escorrentia (def.: 0.4) - scalar
      cont      = True: Se modelan contaminantes,               - boolean
                  False: No se modelan contaminantes

    Output:
      Q_sim     = serie de tiempo de caudal simulado (in mm)    - numpy.ndarray(T, )

    '''

    dicthz = coeficientes(param, tipos, hz_lista, cont)
    Q_sim = balance(dicthz, rain, evap, temp, demand_m3_s, area_aporte, areas, hz_lista, m, y, factorh, ndias, n, cont)

    return Q_sim

def f2r_c(in_features, field, out_raster, inMaskData):
    # FeatureToRaster_conversion
    arcpy.PointToRaster_conversion(in_features, field, out_raster, 'SUM', field)
    out_rastser_zeros = Con(IsNull(out_raster), 0, out_raster)
    out_raster_mask = ExtractByMask(out_rastser_zeros, inMaskData)
    return out_raster_mask

def asignacion(lista, raster, col1, col2):
    # Asignacion de tabla a raster (float)
    print('Asignacion de tabla a raster')
    rasterlist = []
    sumraster = 0
    for i in lista[1:]:
        i = i.split(',')
        if len(i) <= 1:
            continue
        rasterlist.append(Con(raster == float(i[col1]), float(i[col2]), 0))
    for j in rasterlist:
        sumraster += j
    return sumraster

def asignacion_int(lista, raster, col1, col2):
    # Asignacion de tabla a raster (enteros)
    print('Asignacion de tabla a raster (enteros)')
    rasterlist = []
    sumraster = 0
    for i in lista[1:]:
        i = i.split(',')
        if len(i) <= 1:
            continue
        rasterlist.append(Con(raster == int(i[col1]), int(i[col2]), 0))
    for j in rasterlist:
        sumraster += j
    return sumraster

def angleAccum(flowdir, angle):
    # Acumulacion de numeros positivos y negativos
    pos_angle = Con(angle > 0, angle, 0)
    neg_angle = Abs(Con(angle < 0, angle, 0))
    pos_accum = FlowAccumulation(flowdir, pos_angle, 'FLOAT')
    neg_accum = FlowAccumulation(flowdir, neg_angle, 'FLOAT')
    diff_accum = pos_accum - neg_accum
    return diff_accum

def terreno(path, t_inputs):
    # TERRENO: DEM, DIRECCION DE FLUJO, ACUMULACION, LONGITUD
    print('TERRENO: DEM, DIRECCION DE FLUJO, ACUMULACION, LONGITUD')

    # Crear carpeta de salidas
    print('Crear carpeta de salidas')
    os.system('md modeloFONAG\\%s' % t_inputs[16])
    # os.system('md modeloFONAG\\%s\\tables' % t_inputs[16])
    env.workspace = '%s/modeloFONAG/%s' % (path, t_inputs[16])

    # Lectura de DEM y relleno de vacios
    r_DEM = arcpy.Raster('%s/modeloFONAG/inputs/%s' % (path, t_inputs[0]))
    print('Lectura DEM')
    print('%s/modeloFONAG/inputs/%s' % (path, t_inputs[0]))

    # Leer Mascara
    inMaskData = '%s/modeloFONAG/inputs/%s/%s' % (path, t_inputs[1], t_inputs[2])
    print('Lectura Mascara')
    print(inMaskData)

    # Extraer por mascara
    r_DEM_mask = ExtractByMask(r_DEM, inMaskData)
    r_DEM_mask.save('%s/modeloFONAG/%s/r_DEM_mask.tif'%(path, t_inputs[16]))
    print('Extraer por mascara')

    # Relleno de vacios
    r_SurfaceRaster = Fill(r_DEM_mask)
    r_SurfaceRaster.save('%s/modeloFONAG/%s/r_DEM_fill.tif'%(path, t_inputs[16]))
    print('Relleno de vacios')

    #Variables de entorno
    env.cellSize = '%s/modeloFONAG/%s/r_DEM_fill.tif'%(path, t_inputs[16])
    env.extent = '%s/modeloFONAG/%s/r_DEM_fill.tif'%(path, t_inputs[16])
    print('Variables de entorno')

    # Generar hillshade
    r_Hillshade = '%s/modeloFONAG/%s/r_DEM_shd.tif'%(path,t_inputs[16])
    arcpy.HillShade_3d(r_SurfaceRaster, r_Hillshade, z_factor=3)
    print('Generar hillshade')

    # Direccion de flujo
    r_FlowDirection = FlowDirection(r_SurfaceRaster, 'NORMAL')
    r_FlowDirection.save('%s/modeloFONAG/%s/r_DEM_dir.tif'%(path,t_inputs[16]))
    print('Direccion de flujo')

    # Acumulacion de flujo
    inWeightRaster = ''
    r_FlowAccumulation = FlowAccumulation(r_FlowDirection, inWeightRaster) + 1
    r_FlowAccumulation.save('%s/modeloFONAG/%s/r_DEM_acc.tif'%(path,t_inputs[16]))
    print('Acumulacion de flujo')

    # Area de aporte
    cellXResult = arcpy.GetRasterProperties_management(r_DEM_mask, 'CELLSIZEX')
    cellYResult = arcpy.GetRasterProperties_management(r_DEM_mask, 'CELLSIZEY')
    cellX = float(cellXResult.getOutput(0))
    cellY = float(cellYResult.getOutput(0))
    cellArea = cellX * cellY
    r_area = r_FlowAccumulation * cellArea
    r_area.save('%s/modeloFONAG/%s/r_DEM_area.tif' % (path, t_inputs[16]))
    print('Area de aporte')

    # Longitud de flujo
    r_FlowLength = FlowLength(r_FlowDirection, 'UPSTREAM', inWeightRaster)
    r_FlowLength.save('%s/modeloFONAG/%s/r_DEM_length.tif' % (path, t_inputs[16]))
    print('Longitud de flujo')
    r_LengthAccumulation = FlowAccumulation(r_FlowDirection, r_FlowLength)
    r_Length_mean = r_LengthAccumulation / r_FlowAccumulation
    r_Length_norm = (r_FlowLength + 1) / (r_Length_mean + 1)
    c_factordist = Exp(-1 * r_Length_norm)
    c_factordist.save('%s/modeloFONAG/%s/r_factordist.tif' % (path, t_inputs[16]))
    print('Factor de ponderacion por distancia')

def usos_agua(path, t_inputs):
    # USOS DE AGUA: ABSTRACCIONES Y RETORNOS
    print('USOS DE AGUA: ABSTRACCIONES Y RETORNOS')

    # Variables de entorno
    env.cellSize = '%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16])
    env.extent = '%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16])
    print('Variables de entorno')

    # Leer Raster de entrada
    inMaskData = arcpy.Raster('%s/modeloFONAG/%s/r_DEM_fill.tif' % (path,t_inputs[16]))
    r_area = arcpy.Raster('%s/modeloFONAG/%s/r_DEM_area.tif' % (path,t_inputs[16]))
    r_FlowDirection = arcpy.Raster('%s/modeloFONAG/%s/r_DEM_dir.tif' % (path,t_inputs[16]))
    r_FlowAccumulation = arcpy.Raster('%s/modeloFONAG/%s/r_DEM_acc.tif' % (path, t_inputs[16]))

    # Generar raster de ceros y de unos para ciertos procesos
    r_SurfaceRaster = arcpy.Raster('%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16]))
    r_DEM_ceros = r_SurfaceRaster * 0
    # r_DEM_unos = r_SurfaceRaster / r_SurfaceRaster

    # Lectura de tabla de abstracciones y retornos
    f_coefret = open('%s/modeloFONAG/inputs/%s' % (path, t_inputs[4]), 'r')
    lines_coefret = f_coefret.read().split('\n')
    f_coefret.close()

    dicwd = {}
    dicrf = {}
    dicsum = {}
    print('Lectura de tabla abstracciones')
    print(lines_coefret)

    if (len(lines_coefret) <= 1) or (len(lines_coefret[1]) == 0):
        # No existen usos de agua para modelar
        cont = False
        print('No existen usos de agua para modelar')
    else:
        # Creacion de rasters de abstracciones y retornos
        print('Inicio bucle de creacion de rasters de abstracciones')

        for i in lines_coefret[1:]:
            i = i.split(',')

            # Abstracciones de agua
            print('%s/modeloFONAG/inputs/%s/%s' % (path, t_inputs[3], i[0]))
            if len(i) <= 1:
                continue
            if i[0][0] == 'v':
                print('Transformar abstraccion a raster')
                dicwd[i[0]] = f2r_c('%s/modeloFONAG/inputs/%s/%s' % (path, t_inputs[3], i[0]), i[3],
                                    '%s/modeloFONAG/%s/r%s.tif' % (path, t_inputs[16], i[0][1:]), inMaskData)
            elif i[0][0] == 'r':
                print('Lectura de abstraccion raster')
                dicwd[i[0]] = arcpy.Raster('%s/modeloFONAG/inputs/%s/%s' % (path, t_inputs[3], i[0]))
                dicwd[i[0]] = Con(IsNull(dicwd[i[0]]), 0, dicwd[i[0]])
                dicwd[i[0]] = ExtractByMask(dicwd[i[0]], inMaskData)
            elif not i[0][0]:
                print('Abstraccion vacia')
                dicwd[i[0]] = r_DEM_ceros
            else:
                print('Abstraccion inexistente')
                dicwd[i[0]] = r_DEM_ceros

            # Retornos de agua
            print('%s/modeloFONAG/inputs/%s/%s' % (path, t_inputs[3], i[1]))
            if i[1][0] == 'v':
                print('Transformar retorno a raster')
                dicrf[i[1]] = f2r_c('%s/modeloFONAG/inputs/%s/%s' % (path, t_inputs[3], i[1]), i[3],
                                    '%s/modeloFONAG/%s/r%s.tif' % (path, t_inputs[16], i[1][1:]), inMaskData)
            elif i[1][0] == 'r':
                print('Lectura de retorno raster')
                dicrf[i[1]] = arcpy.Raster('%s/modeloFONAG/inputs/%s/%s' % (path, t_inputs[3], i[1]))
                dicrf[i[1]] = Con(IsNull(dicrf[i[1]]), 0, dicrf[i[1]])
                dicrf[i[1]] = ExtractByMask(dicrf[i[1]], inMaskData)
            elif i[1][0] == 'd':
                print('Retorno aguas abajo del punto de abstraccion')
                dicrf[i[1]] = arcpy.SnapPourPoint('%s/modeloFONAG/inputs/%s/%s' % (path, t_inputs[3], i[0]),
                                                  r_FlowAccumulation, float(i[1][2:]), i[3])
            elif not i[1][0]:
                print('Retorno vacio')
                dicrf[i[1]] = r_DEM_ceros
            else:
                print('Retorno inexistente')
                dicrf[i[1]] = r_DEM_ceros

            # Suma de retorno de agua con el coeficiente de retorno y resta de la abstraccion de agua
            dicsum[i[0]] = (dicrf[i[1]] * float(i[2])) - dicwd[i[0]]
        print('Fin bucle')

    # Suma de todos los usos de agua
    r_demand_m3s = r_DEM_ceros
    for i in dicsum:
        r_demand_m3s += dicsum[i]
    r_demand_m3s.save('%s/modeloFONAG/%s/r_demand_m3s.tif' % (path, t_inputs[16]))
    # Acumulacion de demanda de agua
    r_demand_m3s_acc = angleAccum(r_FlowDirection, r_demand_m3s)
    r_demand_m3s_acc.save('%s/modeloFONAG/%s/r_demand_m3s_acc.tif' % (path, t_inputs[16]))
    print('Combinacion de abstracciones y retornos de agua')

    # Transformacion de unidades de usos de agua (queda pendiente el numero de dias al mes)
    r_demand_mmdia = r_demand_m3s * 60 * 60 * 24 * 1000 / r_area
    r_demand_mmdia.save('%s/modeloFONAG/%s/r_demand_mmdia.tif' % (path, t_inputs[16]))
    print('Transformacion de unidades de usos de agua')

    # Acumulacion de usos de agua para estres hidrico
    r_wateruse_m3s = r_DEM_ceros
    for i in dicwd:
        r_wateruse_m3s += dicwd[i]
    r_UsosAccumulation = angleAccum(r_FlowDirection, r_wateruse_m3s)
    r_UsosAccumulation.save('%s/modeloFONAG/%s/r_wateruse_acc.tif' % (path, t_inputs[16]))
    print('Acumulacion de usos de agua para estres hidrico')

def usos_suelo(path, t_inputs):
    # USOS DE SUELO: ASIGNACION DE USOS DE HIDROZONAS
    print('USOS DE SUELO: ASIGNACION DE USOS DE HIDROZONAS')

    # Variables de entorno
    env.cellSize = '%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16])
    env.extent = '%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16])
    print('Variables de entorno')

    # Leer Raster de entrada
    inMaskData = arcpy.Raster('%s/modeloFONAG/%s/r_DEM_fill.tif' % (path,t_inputs[16]))

    # Lectura de la tabla de usos de suelo e hidrozonas
    f_landuse = open('%s/modeloFONAG/inputs/%s' % (path, t_inputs[6]), 'r')
    lines_landuse = f_landuse.read().split('\n')
    print('Lectura de tabla de usos')

    # Lectura del raster de usos de suelo
    r_landuse = arcpy.Raster('%s/modeloFONAG/inputs/%s' % (path, t_inputs[5]))
    r_landuse_mask = ExtractByMask(r_landuse, inMaskData)
    print('Lectura raster usos suelo')

    # Asignacion de hidrozonas a usos de suelo
    r_hidrozonas = asignacion_int(lines_landuse, r_landuse_mask, 0, 1)
    r_hidrozonas.save('%s/modeloFONAG/%s/r_hidrozonas.tif' % (path, t_inputs[16]))
    print( 'Asignacion de hidrozonas a usos de suelo')

def aforo_calibracion(path, t_inputs):
    # DETERMINAR PUNTO DE AFORO Y AREAS DE APORTE
    print('DETERMINAR PUNTO DE AFORO Y AREAS DE APORTE')

    # Crear carpeta de salidas
    print('Crear carpeta de salidas')
    os.system('md modeloFONAG\\%s\\calibracion' % t_inputs[16])

    # Variables de entorno
    env.cellSize = '%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16])
    env.extent = '%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16])
    print('Variables de entorno')

    # Leer Raster de entrada
    r_FlowDirection = arcpy.Raster('%s/modeloFONAG/%s/r_DEM_dir.tif' % (path,t_inputs[16]))
    r_hidrozonas = arcpy.Raster('%s/modeloFONAG/%s/r_hidrozonas.tif' % (path, t_inputs[16]))
    r_demand_m3s_acc = arcpy.Raster('%s/modeloFONAG/%s/r_demand_m3s_acc.tif' % (path, t_inputs[16]))
    r_area = arcpy.Raster ('%s/modeloFONAG/%s/r_DEM_area.tif' % (path, t_inputs[16]))

    # Leer punto de aforo para la calibracion
    v_aforo = '%s/modeloFONAG/inputs/%s' % (path, t_inputs[18])
    print('Lectura de coordenadas de puntos de aforo')

    # Determinar el area de la cuenca de aporte
    r_outWatershed = Watershed(r_FlowDirection, v_aforo)
    r_outWatershed.save('%s/modeloFONAG/%s/calibracion/r_outWatershed.tif' % (path, t_inputs[16]))
    print('Determinar el area de la cuenca de aporte')

    # Extraer hidrozonas por mascara de cuenca de aforo
    r_hidrozonas_mask = ExtractByMask(r_hidrozonas, r_outWatershed)
    r_hidrozonas_mask.save('%s/modeloFONAG/%s/calibracion/r_hidrozonas_mask.tif' % (path, t_inputs[16]))
    print('Extraer hidrozonas por mascara de cuenca de aforo')

    # Crear tablas de estadisticas (calcular el area de cada hidrozona)
    areas_OutTable = r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\t_tab_areas.dbf'
    TabulateArea(r_hidrozonas_mask, 'Value', r_outWatershed, 'Value', areas_OutTable, 1)

    # Guardar datos en el diccionario respectivo
    areas = {}
    areas_sum = 0
    hz_lista = []
    areas_table = dbfread.DBF(areas_OutTable, load=True)
    for s in areas_table.records:
        areas[int(s[str(areas_table.field_names[0])])] = float(s[str(areas_table.field_names[1])])
        areas_sum += float(s[str(areas_table.field_names[1])])
        hz_lista.append(int(s[str(areas_table.field_names[0])]))

    # Extraer porcentajes de areas de hidrozonas
    for area in areas:
        areas[area] = areas[area]/areas_sum
    print('Extraer porcentajes de areas de hidrozonas')

    # Transformacion de unidades de usos de agua (queda pendiente el numero de dias al mes)
    # r_demand_mm_mes = r_UsosAccumulation * 60 * 60 * 24 * 1000 * 30 / r_area

    # Crear tablas de estadisticas (calcular el valor en el punto de aforo)
    area_OutTable = r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\t_tab_area.dbf'
    demand_OutTable = r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\t_tab_demand.dbf'

    arcpy.ExtractValuesToTable_ga(v_aforo, r_area, area_OutTable, '', '')
    arcpy.ExtractValuesToTable_ga(v_aforo, r_demand_m3s_acc, demand_OutTable, '', '')
    # arcpy.ExtractValuesToTable_ga(v_aforo, r_demand_mm_mes, demand_OutTable, '', '')

    # Guardar datos en la variable respectiva
    area_table = dbfread.DBF(area_OutTable, load=True)
    demand_table = dbfread.DBF(demand_OutTable, load=True)

    # Determinar demanda de agua total en el punto de aforo
    area_aporte = float(area_table.records[0][str(area_table.field_names[0])]) / 1000000 # km2
    demand_m3_s = float(demand_table.records[0][str(demand_table.field_names[0])]) # m3/s
    # demand_mm_mes = float(demand_table.records['Value_0']) # mm/mes
    # print area_aporte, areas, demand_m3_s, hz_lista

    with open(r'%s\modeloFONAG\%s\calibracion\area_aporte.csv' % (path, t_inputs[16]), 'wb') as datos:
        writefile = csv.writer(datos)
        writefile.writerow([area_aporte])

    with open(r'%s\modeloFONAG\%s\calibracion\areas.csv' % (path, t_inputs[16]), 'wb') as datos:
        #writefile = csv.writer(datos)
        for key in areas.keys():
            datos.write('%s,%s\n'%(key,areas[key]))
            #writefile.writerow([areas])

    with open(r'%s\modeloFONAG\%s\calibracion\demand_m3_s.csv' % (path, t_inputs[16]), 'wb') as datos:
        writefile = csv.writer(datos)
        writefile.writerow([demand_m3_s])

    with open(r'%s\modeloFONAG\%s\calibracion\hz_lista.csv' % (path, t_inputs[16]), 'wb') as datos:
        writefile = csv.writer(datos)
        writefile.writerow(hz_lista)

    return area_aporte, areas, demand_m3_s, hz_lista

def series_tiempo(path, t_inputs):
    # CREAR SERIES DE TIEMPO DE LLUVIA, ETO, TEMPERATURA
    print('CREAR SERIES DE TIEMPO DE LLUVIA, ETO, TEMPERATURA')

    # Variables de entorno
    env.cellSize = '%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16])
    env.extent = '%s/modeloFONAG/%s/r_DEM_fill.tif' % (path, t_inputs[16])
    print('Variables de entorno')

    # Lectura de la tabla de fechas de inicio y fin de modelacion
    f_fechas = open('%s/modeloFONAG/inputs/%s' % (path, t_inputs[11]), 'r')
    lista_fechas = f_fechas.read().split('\n')
    f_fechas.close()
    print('Lectura de la tabla de fechas de inicio y fin de modelacion')

    # Factor H de lavado de suelos
    f_factorh = open('%s/modeloFONAG/inputs/%s' % (path, t_inputs[8]), 'r')
    c_factorh = f_factorh.read().split('\n')
    factorh = c_factorh[1].split(',')
    ndias = c_factorh[2].split(',')
    f_factorh.close()

    # Lectura del raster de hidrozonas
    r_hidrozonas_mask = arcpy.Raster('%s/modeloFONAG/%s/calibracion/r_hidrozonas_mask.tif' % (path, t_inputs[16]))
    print('Lectura del raster de hidrozonas en el punto de aforo')

    # Inicializar las matrices (o diccionarios)
    rain = {}
    evap = {}
    temp = {}

    # Determina el numero de iteraciones en base a las fechas indicadas
    iterdata = lista_fechas[1].split(',')
    iter = ((int(iterdata[2]) - int(iterdata[0])) * 12) + (int(iterdata[3]) - int(iterdata[1])) + 1
    print('Determina el numero de iteraciones en base a las fechas indicadas')

    # Definir el anio inicial
    y = int(iterdata[0])

    # Determinar el mes inicial
    m = int(iterdata[1])

    # Inicializar la etiqueta de fecha
    date_Labels = []

    for i in range(iter):
        # Completar el numero de mes a dos digitos
        if m < 10:
            m = '0%s' % m
        print('PROCESANDO ANIO %s MES %s' % (y, m))

        # Leer datos climaticos mensuales
        r_prc = arcpy.Raster('%s/modeloFONAG/inputs/%s/r_prc_%s_%s.tif' % (path, t_inputs[12], y, m))
        r_eto = arcpy.Raster('%s/modeloFONAG/inputs/%s/r_eto_%s_%s.tif' % (path, t_inputs[14], y, m))
        # Usar temperatura minima:
        # r_tmp = arcpy.Raster('%s/modeloFONAG/inputs/%s/r_tmpmin_%s_%s.tif' % (path, t_inputs[13], y, m))
        # Si no se tiene temperatura minima, usar la temperatura promedio escalada:
        r_tmpavg = arcpy.Raster('%s/modeloFONAG/inputs/%s/r_tmp_%s_%s.tif' % (path, t_inputs[13], y, m))
        r_tmp = r_tmpavg / 3 - 1  # Esta relacion deberia ser calibrada
        # print('  Leer datos climaticos')

        # Crear tablas de estadisticas (calcular el promedio de cada variable)
        prc_OutTable = r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\t_tab_prc.dbf'
        tmp_OutTable = r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\t_tab_tmp.dbf'
        eto_OutTable = r'%s\modeloFONAG\%s\calibracion' % (path, t_inputs[16]) + r'\t_tab_eto.dbf'
        ZonalStatisticsAsTable(r_hidrozonas_mask, 'Value', r_prc, prc_OutTable, 'DATA', 'MEAN')
        ZonalStatisticsAsTable(r_hidrozonas_mask, 'Value', r_tmp, tmp_OutTable, 'DATA', 'MEAN')
        ZonalStatisticsAsTable(r_hidrozonas_mask, 'Value', r_eto, eto_OutTable, 'DATA', 'MEAN')
        print('  Extraer datos climaticos por hidrozona')

        rain_table = dbfread.DBF(prc_OutTable, load=True)
        temp_table = dbfread.DBF(tmp_OutTable, load=True)
        evap_table = dbfread.DBF(eto_OutTable, load=True)

        for s in rain_table.records:
            if int(s[str(rain_table.field_names[0])]) not in rain:
                rain[int(s[str(rain_table.field_names[0])])] = np.zeros((iter, ))
            rain[int(s[str(rain_table.field_names[0])])][i, ] = float(s['MEAN'])
        for s in temp_table.records:
            if int(s[str(temp_table.field_names[0])]) not in temp:
                temp[int(s[str(temp_table.field_names[0])])] = np.zeros((iter,))
            temp[int(s[str(temp_table.field_names[0])])][i, ] = float(s['MEAN'])
        for s in evap_table.records:
            if int(s[str(evap_table.field_names[0])]) not in evap:
                evap[int(s[str(evap_table.field_names[0])])] = np.zeros((iter,))
            evap[int(s[str(evap_table.field_names[0])])][i, ] = float(s['MEAN'])
        # print('  Guardar datos climaticos por hidrozona')

        # Guardar las etiquetas de fecha
        date_Labels.append(str(m) + '/' + str(y))

        # Determinar el valor de anio y mes de la siguiente iteracion
        if int(m) == 12:
            m = 0
            y += 1
        m = int(m) + 1

    # Definir el anio inicial
    y = int(iterdata[0])
    # Determinar el mes inicial
    m = int(iterdata[1])

    with open(r'%s\modeloFONAG\%s\calibracion\date_Labels.csv' % (path, t_inputs[16]), 'wb') as lista:
        writefile = csv.writer(lista)
        writefile.writerow(date_Labels)

    return rain, evap, temp, y, m, factorh, ndias, date_Labels

def tabla_calibracion_completa(t_rangos, cont=False):
    # CREAR VECTORES CON INFORMACION DE CALIBRACION
    print('CREAR VECTORES CON INFORMACION DE CALIBRACION')

    # Inicializar variables
    M = 0
    tipos = []
    xmin = []
    xmax = []
    X_Labels = []

    # Coeficientes de rendimiento
    for hz in t_rangos[1:]:
        hz = hz.split(',')
        xmin.append(float(hz[2]))
        xmax.append(float(hz[3]))
        X_Labels.append('Kc%s' % hz[0])
        M += 1

    # Coeficientes de regulacion
    for hz in t_rangos[1:]:
        hz = hz.split(',')
        tipos.append(int(hz[1]))
        xmin.append(float(hz[4]))
        xmax.append(float(hz[5]))
        if hz[1] == '3':
            X_Labels.append('SPT%s' % hz[0])
        elif hz[1] == '2':
            X_Labels.append('b%s' % hz[0])
        else:
            X_Labels.append('a%s' % hz[0])
        M += 1

    # Coeficientes de transporte de contaminantes
    if cont and len(t_rangos[0].split(',')) >= 10:
        for hz in t_rangos[1:]:
            hz = hz.split(',')
            xmin.append(float(hz[6]))
            xmax.append(float(hz[7]))
            X_Labels.append('as%s' % hz[0])
            M += 1
        for hz in t_rangos[1:]:
            hz = hz.split(',')
            xmin.append(float(hz[8]))
            xmax.append(float(hz[9]))
            X_Labels.append('at%s' % hz[0])
            M += 1

    Z = len(tipos)

    return M, Z, tipos, xmin, xmax, X_Labels

def filtrar_parametros(hz_lista, tipos, xmin, xmax, X_Labels):
    # FILTRAR VECTORES CON INFORMACION DE CALIBRACION
    print('FILTRAR VECTORES CON INFORMACION DE CALIBRACION')

    if len(tipos) > len(hz_lista):

        # Inicializar variables
        xmin2 = []
        xmax2 = []
        X_Labels2 = []
        Z = len(tipos)
        M = len(xmin)

        # Extraer solamente datos de hz_lista
        for i in range(0, M, Z):
            tipos2 = []
            for hz in hz_lista:
                tipos2.append(tipos[hz - 1])
                xmin2.append(xmin[hz + i - 1])
                xmax2.append(xmax[hz + i - 1])
                X_Labels2.append(X_Labels[hz + i - 1])

        Z2 = len(tipos2)
        M2 = len(xmin2)

        return M2, Z2, tipos2, xmin2, xmax2, X_Labels2

    else:
        Z = len(tipos)
        M = len(xmin)

        return M, Z, tipos, xmin, xmax, X_Labels

def tabla_calibracion(t_rangos, hz_lista, cont=False, path='/', t_inputs=False):
    # CREAR VECTORES CON INFORMACION DE CALIBRACION
    print('CREAR VECTORES CON INFORMACION DE CALIBRACION')

    # Inicializar variables
    M = 0
    tipos = []
    xmin = []
    xmax = []
    X_Labels = []
    hz_lista_completa = []

    # Coeficientes de rendimiento
    for hz in t_rangos[1:]:
        hz = hz.split(',')
        hz_lista_completa.append(int(hz[0]))
        if int(hz[0]) in hz_lista:
            xmin.append(float(hz[2]))
            xmax.append(float(hz[3]))
            X_Labels.append('Kc%s' % hz[0])
            M += 1

    # Coeficientes de regulacion
    for hz in t_rangos[1:]:
        hz = hz.split(',')
        if int(hz[0]) in hz_lista:
            tipos.append(int(hz[1]))
            xmin.append(float(hz[4]))
            xmax.append(float(hz[5]))
            if hz[1] == '3':
                X_Labels.append('SPT%s' % hz[0])
            elif hz[1] == '2':
                X_Labels.append('b%s' % hz[0])
            else:
                X_Labels.append('a%s' % hz[0])
            M += 1

    # Coeficientes de transporte de contaminantes
    if cont and len(t_rangos[0].split(',')) >= 10:
        for hz in t_rangos[1:]:
            hz = hz.split(',')
            if int(hz[0]) in hz_lista:
                xmin.append(float(hz[6]))
                xmax.append(float(hz[7]))
                X_Labels.append('as%s' % hz[0])
                M += 1
        for hz in t_rangos[1:]:
            hz = hz.split(',')
            if int(hz[0]) in hz_lista:
                xmin.append(float(hz[8]))
                xmax.append(float(hz[9]))
                X_Labels.append('at%s' % hz[0])
                M += 1

    Z = len(tipos)

    hz_lista = [x for x in hz_lista if x in hz_lista_completa]
    if t_inputs:
        with open(r'%s\modeloFONAG\%s\calibracion\hz_lista.csv' % (path, t_inputs[16]), 'wb') as lista:
            writefile = csv.writer(lista)
            writefile.writerow(hz_lista)
        with open(r'%s\modeloFONAG\%s\calibracion\tipos.csv' % (path, t_inputs[16]), 'wb') as lista:
            writefile = csv.writer(lista)
            writefile.writerow(tipos)
        with open(r'%s\modeloFONAG\%s\calibracion\X_Labels.csv' % (path, t_inputs[16]), 'wb') as lista:
            writefile = csv.writer(lista)
            writefile.writerow(X_Labels)

    return M, Z, tipos, xmin, xmax, X_Labels, hz_lista

def coeficientes(param, tipos, hz_lista, cont=False):
    # COEFICIENTES DE REGULACION HIDRLOGICA

    # Numero de hidrozonas
    Z = len(hz_lista)
    dicthz = {}

    # Determinacion de coeficientes mensuales
    for hz in range(Z):
        if tipos[hz] == 1:
            # Caso de hidrozona con comportamiento lineal
            yl = np.zeros(shape=(13, ))
            m = np.zeros(shape=(12, ))
            yl[0] = -1 * (float(param[Z + hz])) * 0 + (2 * float(param[Z + hz])) ** 0.5
            for j in range(1, 13):
                yl[j] = -1 * (float(param[Z + hz])) * j + (2 * float(param[Z + hz]))**0.5
                m[j - 1] = (yl[j] + yl[j-1]) / 2
            # Eliminar coeficientes negativos y escalarlos
            m[m < 0] = 0
            M = sum(m)
            m = m / M
            dicthz[hz_lista[hz]] = {'tipo': tipos[hz],
                                    'kc': param[hz],
                                    'coef': param[Z + hz],
                                    'spt': -999}
            for j in range(1,13):
                dicthz[hz_lista[hz]]['m%s' % j] = m[j - 1]
            if cont:
                # Existen parametros de transporte contaminantes
                dicthz[hz_lista[hz]]['as'] = param[2*Z + hz]
                dicthz[hz_lista[hz]]['at'] = param[3*Z + hz]
        elif tipos[hz] == 2:
            # Caso de hidrozona con comportamiento no lineal
            yl = np.zeros(shape=(13,))
            m = np.zeros(shape=(12,))
            yl[0] = float(param[Z + hz]) * math.exp((-1 * float(param[Z + hz])) * 0)
            for j in range(1, 13):
                yl[j] = float(param[Z + hz]) * math.exp((-1 * float(param[Z + hz])) * j)
                m[j - 1] = (yl[j] + yl[j - 1]) / 2
            # Eliminar coeficientes negativos y escalarlos
            m[m < 0] = 0
            M = sum(m)
            m = m / M
            dicthz[hz_lista[hz]] = {'tipo': tipos[hz],
                                    'kc': param[hz],
                                    'coef': param[Z + hz],
                                    'spt': -999}
            for j in range(1, 13):
                dicthz[hz_lista[hz]]['m%s' % j] = m[j - 1]
            if cont:
                # Existen parametros de transporte contaminantes
                dicthz[hz_lista[hz]]['as'] = param[2 * Z + hz]
                dicthz[hz_lista[hz]]['at'] = param[3 * Z + hz]
        elif tipos[hz] == 3:
            # Caso de hidrozona glaciar
            dicthz[hz_lista[hz]] = {'tipo': tipos[hz],
                                    'kc': param[hz],
                                    'coef': 0.0,
                                    'spt': param[Z + hz],
                                    'm1': 0.000001}
            for j in range(2, 13):
                dicthz[hz_lista[hz]]['m%s' % j] = 0.0 # 1./12.
            if cont:
                # Existen parametros de transporte contaminantes
                dicthz[hz_lista[hz]]['as'] = param[2 * Z + hz]
                dicthz[hz_lista[hz]]['at'] = param[3 * Z + hz]

    return dicthz

def balance(dicthz, rain, evap, temp, demand_m3_s, area_aporte, areas, hz_lista, m, y, factorh, ndias, n=0.4, cont=False):
    # MODELO HIDROLOGICO: BALANCE HIDRICO MENSUAL

    # Numero de datos mensuales
    # print 'LISTA'
    # print hz_lista
    # print rain
    iter = len(rain[hz_lista[0]])

    # Inicializar variables
    Qn = np.zeros((iter, ))
    cnt = np.zeros((iter, ))

    # Calcular flujos en cada hidrozona
    gla = {}
    eta = {}
    erf = {}
    q = {}
    for hz in hz_lista:
        q[hz] = {}
        # Calcular deshielo glaciar del mes actual
        if dicthz[hz]['spt'] == -999:
            gla[hz] = temp[hz] * 0
        else:
            gla[hz] = temp[hz] * (1.52 + 0.54 * dicthz[hz]['spt'])

        # Calcular evapotranspiracion real
        eta[hz] = (dicthz[hz]['kc'] * evap[hz])

        # Calcular la lluvia efectiva del mes actual
        erf[hz] = (rain[hz] - eta[hz])
        erf[hz][erf[hz] < 0] = 0

        # Inicializar escorrentia mensual
        for j in range(1, 13):
            q[hz]['q%s' % j] = 0.0

        for i in range(iter):

            # Reasignar los caudales arrastrados de meses anteriores
            for j in range(12, 1, -1):
                q[hz]['q%s' % j] = q[hz]['q%s' % (j - 1)]
            q[hz]['q1'] = erf[hz][i]

            # Calcular el caudal natural del mes actual
            Sum = gla[hz][i]
            for j in range(1, 13):
                Sum += dicthz[hz]['m%s' % j] * q[hz]['q%s' % j]
            Qn[i] += Sum /60 /60 /24 / float(ndias[m]) * areas[hz] * area_aporte * 1000

            # Calcular carga de contaminantes
            if cont:
                # Identificar el mes actual
                qr = dicthz[hz]['m1'] * q[hz]['q1'] /60 /60 /24 / float(ndias[m]) * areas[hz] * area_aporte * 1000
                cnt[i] += (dicthz[hz]['as'] + float(factorh[m]) * (dicthz[hz]['at'])) * pow(qr, 1 + n)

            # Determinar el valor de anio y mes de la siguiente iteracion
            if m == 12:
                m = 0
                y = y + 1
            m += 1

    # Calcular el caudal disponible del mes actual
    Q_sim = Qn + demand_m3_s
    Q_sim[Q_sim <= 0] = 0.0001

    if cont:
        C_sim = cnt / Q_sim
        return C_sim
    else:
        return Q_sim

def evaluacion_modelo(param, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista,
                      m, y, factorh, ndias, y_obs, warmup=12, n=0.4, cont=False):

    '''Esta funcion determina los indicadores de desempeno de los resultados
        del modelo FONAG 2.1 (Ochoa-Tocachi et al., 2020).

        Uso:
        f = evaluacion_modelo(param, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista,
                              m, y, factorh, ndias, y_obs, warmup, n, cont)

      Input:
          param = vector de parametros del modelo                   - numpy.ndarray(2*H, )
                  1 hasta H:      Kc    = Coeficientes de cultivo para ept [-]
                  H+1 hasta 2*H: coef   = a, b, spt [-]
          rain  = serie de tiempo de precipitacion                  - numpy.ndarray(T, )
          evap  = serie de tiempo de evapotranspiracion potencial   - numpy.ndarray(T, )
          temp  = serie de tiempo de temperatura                    - numpy.ndarray(T, )
          demand_m3_s = acumulacion de usos de agua [m3/s]          - scalar
          area_aporte = area de aporte a la cuenca [km2]            - scalar
          areas = % de areas de la cuenca para cada hidrozona       - dict{H}
                  H: numero de hidrozonas
          tipos = tipos de regulacion hidrologica de cada hidrozona - numpy.ndarray(H, 1)
          hz_lista = Hidrozonas relevantes para la cuenca de aforo
          m         = mes inicial para la simulacion
          y         = anio inicial para la simulacion
          factorh   = factor H de lavado de suelos (0:ene, 11:dic)  - list: 12
          ndias     = numero de dias de cada mes   (0:ene, 11:dic)  - list: 12
          y_obs  = series de tiempo de caudal observado             - numpy.ndarray(T, )
          warmup = numero de pasos de tiempo de calentamiento       - scalar
          n         = factor exponencial de escorrentia (def.: 0.4) - scalar
          cont      = True: Se modelan contaminantes,               - boolean
                      False: No se modelan contaminantes

        Output:
          f      = vector de funciones objetivo                  - numpy.ndarray(5, )
                   0:NSE, 1:RMSE, 2:RSR, 3:PBIAS, 4:KGE

    '''

    y_sim = modelo_iterativo(param, rain, evap, temp, demand_m3_s, area_aporte, areas, tipos, hz_lista, m, y, factorh, ndias, n, cont)

    # Check inputs
    Ny = y_sim.shape
    T = Ny[0]

    if not isinstance(y_obs, np.ndarray):
        raise ValueError('y_obs debe ser un numpy.array.')
    if y_obs.dtype.kind != 'f' and y_obs.dtype.kind != 'i' and y_obs.dtype.kind != 'u':
        raise ValueError('y_obs debe contener numeros.')
    Nflow = y_obs.shape
    if len(Nflow) != 1:
        raise ValueError('y_obs debe tener la forma (T, ).')
    if len(y_obs) != T:
        raise ValueError('y_sim and y_obs deben tener el mismo numero de columnas.')

    # Eliminar los datos de calentamiento
    Qs = y_sim[warmup:len(y_sim) + 1]
    Qo = y_obs[warmup:len(y_sim) + 1]

    # Calcular funciones objetivos
    f = np.nan * np.ones((5,))
    f[0] = NSE(Qs, Qo)      # NSE
    f[1] = RMSE(Qs, Qo)     # RMSE
    f[2] = RSR(Qs, Qo)      # RSR
    f[3] = PBIAS(Qs, Qo)    # PBIAS
    f[4] = KGE(Qs, Qo)      # KGE

    return f

'''
    Module to execute the model

    This module is part of the SAFE Toolbox by F. Pianosi, F. Sarrazin and
    T. Wagener at Bristol University (2015).
    SAFE is provided without any warranty and for non-commercial use only.
    For more details, see the Licence file included in the root directory
    of this distribution.
    For any comment and feedback, or to discuss a Licence agreement for
    commercial use, please contact: francesca.pianosi@bristol.ac.uk
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info

    Package version: SAFEpython_v0.0.0
'''

def model_execution(fun_test, X, *args):

    """Executes the model coded in the matlab function 'fun_test' against
    each sample input vector in matrix X, and returns the associated output
    vectors (in matrix Y).

    Usage:
    Y = model_execution.model_execution(fun_test, X, *args, ExtraArgOut=False)

    Input:
     fun_test = function implementing the model.           - python function
                The first output argument of
                'fun_test' must be a numpy.ndarray of
                shape (P, ), (1,P) or (P,1).
           X = matrix of N input sample                    - numpy.ndarray(N,M)
              (each input sample has M components)

    Optional input:
        *args = extra arguments needed to execute 'fun_test'

    ExtraArgOut = specifies if extra output arguments must - boolean
                  be returned beyond Y in case
                  'fun_test' provides extra output
                  arguments.
                  (default: False, i.e. no extra output
                  arguments are returned)

    Output:
            Y = vector (NxP) of associated output samples, - numpy.ndarray(N,P)
                P being the number of model outputs
                associated to each sampled input
                combination (corresponds to the first
                output argument of 'fun_test')

    Optional output:
       argout = extra output arguments provided by         - tuple
                'fun_test' if ExtraArgOut is True. argout
                is a tuple and each element of argout
                corresponds to an output argument of fun_test.

    NOTES:
    1) If the 'fun_test' function requires other arguments besides 'X',
    or produce other output besides 'Y', they can be passed as optional
    arguments after 'X' and recovered as optional output after 'Y'.
    2) The assignment of the 'argout' variable must be customised by the user
    for the specific case study (see L141-145)

    Example:

    import numpy as np
    from SAFEpython.model_execution import model_execution
    from SAFEpython.sobol_g import sobol_g_function

    fun_test = sobol_g_function
    X =  np.random.random((3, 4))
    a = np.ones((4,))
    Y = model_execution(fun_test, X, a) # Or:
    Y, tmp = model_execution(fun_test, X, a, ExtraArgOut=True)
    V = tmp[0]
    Si_ex = tmp[1]

    This function is part of the SAFE Toolbox by F. Pianosi, F. Sarrazin
    and T. Wagener at Bristol University (2015).
    SAFE is provided without any warranty and for non-commercial use only.
    For more details, see the Licence file included in the root directory
    of this distribution.
    For any comment and feedback, or to discuss a Licence agreement for
    commercial use, please contact: francesca.pianosi@bristol.ac.uk
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info"""

    ###########################################################################
    # Check inputs
    ###########################################################################
    if not isinstance(X, np.ndarray):
        raise ValueError('"X" must be a numpy.array.')
    if X.dtype.kind != 'f' and X.dtype.kind != 'i' and X.dtype.kind != 'u':
        raise ValueError('"X" must contain floats or integers.')
    Nx = X.shape
    N = Nx[0]
    if len(Nx) != 2:
        raise ValueError('"X" must have at least two rows.')

    ###########################################################################
    # Recover the type and shapes of the output arguments of my_fun
    ###########################################################################

    # Perform one model run to determine P (number output to be saved ) and the
    # number of extra arguments given by 'fun_test':
    tmp = fun_test(X[0, :], *args)  # modified

    if isinstance(tmp, tuple): # my_fun provides extra output arguments
        # Recover the total number of extra arguments:
        NumExtraArgOut = len(tmp) - 1 # number of extra arguments
        # Check format of first argument of the function
        if not isinstance(tmp[0], np.ndarray):
            raise ValueError('the first output argument returned by ' +
                             '"fun_test" must be a numpy.ndarray')
        if tmp[0].dtype.kind != 'f' and tmp[0].dtype.kind != 'i' and \
        tmp[0].dtype.kind != 'u':
            raise ValueError('the first output argument returned by ' +
                             '"fun_test" must contains float or integers.')
        N1 = tmp[0].shape
        if len(N1) > 2:
            raise ValueError('the first output argument returned by ' +
                             '"fun_test" must be of shape (P, ), (P,1) or (1,P).')
        elif len(N1) == 2:
            if N1[0] != 1 and N1[1] != 1:
                raise ValueError('the first output argument returned by ' +
                                 '"fun_test" must be of shape (P, ), (P,1) or (1,P).')
        P = len(tmp[0].flatten())

    else: # no extra arguments
        NumExtraArgOut = 0
        if not isinstance(tmp, np.ndarray):
            raise ValueError('the first output argument returned by ' +
                             '"fun_test" must be a numpy.ndarray')
        if tmp.dtype.kind != 'f' and tmp.dtype.kind != 'i' and tmp.dtype.kind != 'u':
            raise ValueError('the first output argument returned by '  +
                             '"fun_test" must contains float or integers.')
        N1 = tmp.shape
        if len(N1) > 2:
            raise ValueError('the first output argument returned by ' +
                             '"fun_test" must be of shape (P, ), (P,1) or (1,P).')
        elif len(N1) == 2:
            if N1[0] != 1 and N1[1] != 1:
                raise ValueError('the first output argument returned by ' +
                                 '"fun_test" must be of shape (P, ), (P,1) or (1,P).')
        P = len(tmp.flatten())

    # Perform the model runs

    Y = np.nan * np.ones((N, P)) # variable initialization
    for j in range(N):
        if NumExtraArgOut == 0:
            Y[j, :] = fun_test(X[j, :], *args).flatten()
        else: # save extra output arguments in a tuple
            tmp = fun_test(X[j, :], *args)
            Y[j, :] = tmp[0].flatten()
            # Assign extra output argument (these lines should be customised by
            # the user for the specific case study):
            argout = ()
            for i in range(NumExtraArgOut):
                argout = argout + (tmp[i+1],)

    # Determine the output arguments to be returned
    return Y

def NSE(y_sim, y_obs):

    """Computes the Nash-Sutcliffe Efficiency (NSE) coefficient.

    Usage:
        nse = util.NSE(Y_sim, y_obs)

    Input:
    y_sim = time series of modelled variable              - numpy.ndarray (N, )
            (N > 1 different time series can be        or - numpy.ndarray (N,T)
            evaluated at once)
    y_obs = time series of observed variable              - numpy.ndarray (T, )
                                                       or - numpy.ndarray (1,T)

    Output:
      nse = vector of NSE coefficients                    - numpy.ndarray (N, )

    References:

    Nash, J. E. and J. V. Sutcliffe (1970),
    River flow forecasting through conceptual models part I
    A discussion of principles, Journal of Hydrology, 10 (3), 282-290.

    This function is part of the SAFE Toolbox by F. Pianosi, F. Sarrazin
    and T. Wagener at Bristol University (2015).
    SAFE is provided without any warranty and for non-commercial use only.
    For more details, see the Licence file included in the root directory
    of this distribution.
    For any comment and feedback, or to discuss a Licence agreement for
    commercial use, please contact: francesca.pianosi@bristol.ac.uk
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info"""

    Nsim = y_sim.shape
    if len(Nsim) > 1:
        N = Nsim[0]
        T = Nsim[1]
    elif len(Nsim) == 1:
        T = Nsim[0]
        N = 1
        y_sim_tmp = np.nan * np.ones((1, T))
        y_sim_tmp[0, :] = y_sim
        y_sim = y_sim_tmp

    Nobs = y_obs.shape
    if len(Nobs) > 1:
        if Nobs[0] != 1:
            raise ValueError('"y_obs" be of shape (T, ) or (1,T).')
        if Nobs[1] != T:
            raise ValueError('the number of elements in "y_obs" must be equal'+
                             'to the number of columns in "y_sim"')
    elif len(Nobs) == 1:
        if Nobs[0] != T:
            raise ValueError('the number of elements in "y_obs" must be equal'+
                             'to the number of columns in "y_sim"')
        y_obs_tmp = np.nan * np.ones((1, T))
        y_obs_tmp[0, :] = y_obs
        y_obs = y_obs_tmp

    # Eliminar valores nan
    filtro = np.ndarray.tolist(~np.isnan(y_obs))[0]
    y_sim = y_sim[:, filtro]
    y_obs = y_obs[~np.isnan(y_obs)]
    No = len(y_obs)

    Err = y_sim - repmat(y_obs, N, 1)
    Err0 = y_obs - np.mean(y_obs)
    nse = 1 - np.sum(Err**2, axis=1) / np.sum(Err0**2)

    return nse


def RMSE(y_sim, y_obs):

    """Computes the Root Mean Squared Error

    Usage:
    rmse = util.RMSE(Y_sim, y_obs)

    Input:
    y_sim = time series of modelled variable              - numpy.ndarray (N, )
            (N > 1 different time series can be        or - numpy.ndarray (N,T)
            evaluated at once)
            at once)
    y_obs = time series of observed variable              - numpy.ndarray (T, )
                                                       or - numpy.ndarray (1,T)

    Output:
     rmse = vector of RMSE coefficients                   - numpy.ndarray (N, )

    This function is part of the SAFE Toolbox by F. Pianosi, F. Sarrazin
    and T. Wagener at Bristol University (2015).
    SAFE is provided without any warranty and for non-commercial use only.
    For more details, see the Licence file included in the root directory
    of this distribution.
    For any comment and feedback, or to discuss a Licence agreement for
    commercial use, please contact: francesca.pianosi@bristol.ac.uk
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info"""

    Nsim = y_sim.shape
    if len(Nsim) > 1:
        N = Nsim[0]
        T = Nsim[1]
    elif len(Nsim) == 1:
        T = Nsim[0]
        N = 1
        y_sim_tmp = np.nan * np.ones((1, T))
        y_sim_tmp[0, :] = y_sim
        y_sim = y_sim_tmp

    Nobs = y_obs.shape
    if len(Nobs) > 1:
        if Nobs[0] != 1:
            raise ValueError('"y_obs" be of shape (T, ) or (1,T).')
        if Nobs[1] != T:
            raise ValueError('the number of elements in "y_obs" must be' +
                             'equal to the number of columns in "y_sim"')
    elif len(Nobs) == 1:
        if Nobs[0] != T:
            raise ValueError('the number of elements in "y_obs" must be' +
                             'equal to the number of columns in "y_sim"')
        y_obs_tmp = np.nan * np.ones((1, T))
        y_obs_tmp[0, :] = y_obs
        y_obs = y_obs_tmp

    # Eliminar valores nan
    filtro = np.ndarray.tolist(~np.isnan(y_obs))[0]
    y_sim = y_sim[:, filtro]
    y_obs = y_obs[~np.isnan(y_obs)]
    No = len(y_obs)

    Err = y_sim - repmat(y_obs, N, 1)
    rmse = np.sqrt(np.mean(Err**2, axis=1) / No)

    return rmse

def RSR(y_sim, y_obs):

    """Computes the RSR = RMSE/STDEV

    Usage:
    rsr = util.RSR(Y_sim, y_obs)

    Input:
    y_sim = time series of modelled variable              - numpy.ndarray (N, )
            (N > 1 different time series can be        or - numpy.ndarray (N,T)
            evaluated at once)
            at once)
    y_obs = time series of observed variable              - numpy.ndarray (T, )
                                                       or - numpy.ndarray (1,T)

    Output:
     rsr = vector of RSR coefficients                     - numpy.ndarray (N, )

    This is a custom function made by the user based on the SAFE Toolbox.
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info"""

    Nsim = y_sim.shape
    if len(Nsim) > 1:
        N = Nsim[0]
        T = Nsim[1]
    elif len(Nsim) == 1:
        T = Nsim[0]
        N = 1
        y_sim_tmp = np.nan * np.ones((1, T))
        y_sim_tmp[0, :] = y_sim
        y_sim = y_sim_tmp

    Nobs = y_obs.shape
    if len(Nobs) > 1:
        if Nobs[0] != 1:
            raise ValueError('"y_obs" be of shape (T, ) or (1,T).')
        if Nobs[1] != T:
            raise ValueError('the number of elements in "y_obs" must be' +
                             'equal to the number of columns in "y_sim"')
    elif len(Nobs) == 1:
        if Nobs[0] != T:
            raise ValueError('the number of elements in "y_obs" must be' +
                             'equal to the number of columns in "y_sim"')
        y_obs_tmp = np.nan * np.ones((1, T))
        y_obs_tmp[0, :] = y_obs
        y_obs = y_obs_tmp

    # Eliminar valores nan
    filtro = np.ndarray.tolist(~np.isnan(y_obs))[0]
    y_sim = y_sim[:, filtro]
    y_obs = y_obs[~np.isnan(y_obs)]
    No = len(y_obs)

    Err = y_sim - repmat(y_obs, N, 1)
    rmse = np.sqrt(np.mean(Err**2, axis=1) / No)
    stdev = np.std(y_obs)
    rsr = rmse / stdev

    return rsr

def PBIAS(y_sim, y_obs):

    """Computes the Percent Bias

    Usage:
    pbias = util.PBIAS(Y_sim, y_obs)

    Input:
    y_sim = time series of modelled variable              - numpy.ndarray (N, )
            (N > 1 different time series can be        or - numpy.ndarray (N,T)
            evaluated at once)
            at once)
    y_obs = time series of observed variable              - numpy.ndarray (T, )
                                                       or - numpy.ndarray (1,T)

    Output:
     pbias = vector of PBIAS coefficients                 - numpy.ndarray (N, )

    This is a custom function made by the user based on the SAFE Toolbox.
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info"""

    Nsim = y_sim.shape
    if len(Nsim) > 1:
        N = Nsim[0]
        T = Nsim[1]
    elif len(Nsim) == 1:
        T = Nsim[0]
        N = 1
        y_sim_tmp = np.nan * np.ones((1, T))
        y_sim_tmp[0, :] = y_sim
        y_sim = y_sim_tmp

    Nobs = y_obs.shape
    if len(Nobs) > 1:
        if Nobs[0] != 1:
            raise ValueError('"y_obs" be of shape (T, ) or (1,T).')
        if Nobs[1] != T:
            raise ValueError('the number of elements in "y_obs" must be' +
                             'equal to the number of columns in "y_sim"')
    elif len(Nobs) == 1:
        if Nobs[0] != T:
            raise ValueError('the number of elements in "y_obs" must be' +
                             'equal to the number of columns in "y_sim"')
        y_obs_tmp = np.nan * np.ones((1, T))
        y_obs_tmp[0, :] = y_obs
        y_obs = y_obs_tmp

    # Eliminar valores nan
    filtro = np.ndarray.tolist(~np.isnan(y_obs))[0]
    y_sim = y_sim[:, filtro]
    y_obs = y_obs[~np.isnan(y_obs)]
    No = len(y_obs)

    Err = y_sim - repmat(y_obs, N, 1)
    pbias = np.sum(Err, axis=1) * 100 / np.sum(repmat(y_obs, N, 1), axis=1)

    return pbias

def KGE(y_sim, y_obs, scale=[1, 1, 1]):

    """Computes the Kling-Gupta Efficiency (KGE) coefficient.

    Usage:
        kge = util.KGE(Y_sim, y_obs)

    Input:
    y_sim = time series of modelled variable              - numpy.ndarray (N, )
            (N > 1 different time series can be        or - numpy.ndarray (N,T)
            evaluated at once)
    y_obs = time series of observed variable              - numpy.ndarray (T, )
                                                       or - numpy.ndarray (1,T)
    scale = scaling factors for r, a, and b               - vector (1,3)

    Output:
      kge = vector of KGE coefficients                    - numpy.ndarray (N, )

    References:

    Gupta, Kling, Yilmaz, Martinez. (2009),
    Decomposition of the mean squared error and NSE performance criteria:
    Implications for improving hydrological modelling, Journal of Hydrology, 377, 80-91.

    This is a custom function made by the user based on the SAFE Toolbox.
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info"""

    Nsim = y_sim.shape
    if len(Nsim) > 1:
        N = Nsim[0]
        T = Nsim[1]
    elif len(Nsim) == 1:
        T = Nsim[0]
        N = 1
        y_sim_tmp = np.nan * np.ones((1, T))
        y_sim_tmp[0, :] = y_sim
        y_sim = y_sim_tmp

    Nobs = y_obs.shape
    if len(Nobs) > 1:
        if Nobs[0] != 1:
            raise ValueError('"y_obs" be of shape (T, ) or (1,T).')
        if Nobs[1] != T:
            raise ValueError('the number of elements in "y_obs" must be equal'+
                             'to the number of columns in "y_sim"')
    elif len(Nobs) == 1:
        if Nobs[0] != T:
            raise ValueError('the number of elements in "y_obs" must be equal'+
                             'to the number of columns in "y_sim"')
        y_obs_tmp = np.nan * np.ones((1, T))
        y_obs_tmp[0, :] = y_obs
        y_obs = y_obs_tmp

    if len(scale) != 3:
        raise ValueError('input scale must have 3 parameters.')

    # Eliminar valores nan
    filtro = np.ndarray.tolist(~np.isnan(y_obs))[0]
    y_sim = y_sim[:, filtro]
    y_obs = y_obs[~np.isnan(y_obs)]
    No = len(y_obs)

    # Bias
    muO = np.mean(y_obs)
    muS = np.mean(y_sim, axis=1)
    b = muS / muO

    # Variability
    stdO = np.std(y_obs)
    stdS = np.std(y_sim, axis=1)
    a = stdS / stdO

    # Correlation
    ErrO = (y_obs - muO) / stdO
    ErrS = (y_sim - np.transpose(repmat(muS, No, 1))) / np.transpose(repmat(stdS, No, 1))
    Err = repmat(ErrO, N, 1) * ErrS
    r = (1 / float(T)) * np.sum(Err, axis=1)

    kge = 1 - np.sqrt(scale[0] * (r - 1)**2 + scale[1] * (a - 1)**2 + scale[2] * (b - 1)**2)

    return kge

def funcionobjetivo(E, E_cond, E_Labels):
    # CALCULAR COMBINACION DE FUNCIONES OBJETIVO

    Nsim = E.shape
    if len(Nsim) > 1:
        N = Nsim[0]
        T = Nsim[1]
    elif len(Nsim) == 1:
        T = Nsim[0]
        N = 1
        E_tmp = np.nan * np.ones((1, T))
        E_tmp[0, :] = E
        E = E_tmp

    if len(E_cond) != T:
        raise ValueError('el numero de elementos en "E_cond" debe ser igual' +
                         'al numero de columnas en "E"')

    E_temp = np.zeros(shape=(N, T + 1))
    E_temp[:, :-1] = E
    E_temp[:, 0] = 1 - E_temp[:, 0]  # 1-NSE
    E_temp[:, 3] = abs(E_temp[:, 3])  # abs(PBIAS)
    E_temp[:, 4] = 1 - E_temp[:, 4]  # 1-KGE
    E_norm = np.zeros(shape=(N, T))
    for cond_index in range(T):
        E_norm[:, cond_index] = (E_temp[:, cond_index] - min(E_temp[:, cond_index])) / \
                                (max(E_temp[:, cond_index]) - min(E_temp[:, cond_index]))
    E_norm = E_norm * repmat(E_cond, N, 1)
    E_temp[:, T] = np.sqrt(np.sum(E_norm ** 2, axis=1))

    E_mod = np.zeros(shape=(N, T + 1))
    E_mod[:, :-1] = E
    E_mod[:, -1] = E_temp[:, -1]

    E_Labels_mod = E_Labels
    E_Labels.append('OF')

    E_cond_mod = E_cond
    E_cond.append(True)

    return E_mod, E_cond_mod, E_Labels_mod

def AAT_sampling(samp_strat, M, distr_fun, distr_par, N, nrep=5):

    """ Generates a sample X composed of N random samples of M uncorrelated
    variables.

    Usage:
        X = sampling.AAT_sampling(samp_strat, M, distr_fun, distr_par, N, nrep=5)

    Input:
    samp_strat = sampling strategy                                     - string
                 Options: 'rsu': random uniform
                          'lhs': latin hypercube
             M = number of variables                                  - integer
     distr_fun = probability distribution function for ech input
                     - function (eg: 'scipy.stats.uniform') if all
                       variables have the same pdf
                     - list of M functions (e.g.:
                       ['scipy.stats.uniform','scipy.stats.norm']) otherwise
     distr_par = parameters of the probability distribution function
                     - list of parameters if all input variables have the same
                     - list of M lists otherwise
             N = number of samples                                    - integer

    Optional input:
          nrep = number of replicate to select the maximin            - integer
                 hypercube(default value: 5)

    Output:
             X = matrix of samples                        - numpy.ndarray (N,M)
                 Each row is a point in the input space.
                 In contrast to OAT_sampling, rows are not sorted in any
                 specific order, and all elements in a row usually
                 differ from the elements in the following row.

    Supported probability distribution function :

         scipy.stats.beta        (Beta)
         scipy.stats.binom       (Binomial)
         scipy.stats.chi2        (Chisquare)
         scipy.stats.dweibull    (Double Weibull)
         scipy.stats.expon       (Exponential)
         scipy.stats.f           (F)
         scipy.stats.gamma       (Gamma)
         scipy.stats.genextreme  (Generalized Extreme Value)
         scipy.stats.genpareto   (Generalized Pareto)
         scipy.stats.geom        (Geometric)
         scipy.stats.hypergeom   (Hypergeometric)
         scipy.stats.lognorm     (Lognormal)
         scipy.stats.nbinom      (Negative Binomial)
         scipy.stats.ncf         (Noncentral F)
         scipy.stats.nct         (Noncentral t)
         scipy.stats.ncx2        (Noncentral Chi-square)
         scipy.stats.norm        (Normal)
         scipy.stats.poisson     (Poisson)
         scipy.stats.randint     (Discrete Uniform)
         scipy.stats.rayleigh    (Rayleigh)
         scipy.stats.t           (T)
         scipy.stats.uniform     (Uniform)
         scipy.stats.weibull_max (Weibull maximum)
         scipy.stats.weibull_min (Weibull minimum)

    Examples:

    import scipy.stats as st
    import matplotlib.pyplot as plt

    from SAFEpython.sampling import AAT_sampling

    # Example 1: 2 inputs, both from Unif[0,3]
    N = 1000
    M = 2
    distr_fun = st.uniform
    distr_par = [0, 3]
    samp_strat = 'lhs'
    X = AAT_sampling(samp_strat, M, distr_fun, distr_par, N)

    # Plot results:
    plt.figure()
    plt.plot(X[:, 0], X[:, 1], '.k')
    plt.xlabel('x_1')
    plt.ylabel('x_2')

    # Example 2: 2 inputs, one from Unif[0,3], one from Unif[1,5]
    distr_fun = st.uniform
    distr_par = [[0, 3], [1, 4]]
    X = AAT_sampling(samp_strat, M, distr_fun, distr_par, N)
    # (use above code to plot results)

    # Example 3: 2 inputs, one from Unif[0,3], one from discrete, uniform in [1,5]
    distr_fun = [st.uniform, st.randint]
    distr_par = [[0, 3], [1, 6]]
    X = AAT_sampling(samp_strat, M, distr_fun, distr_par, N)

    # Example 4: investigate the difference between 'rsu' and 'lhs':
    N = 20
    X1 = AAT_sampling('rsu', 2, st.uniform, [0, 1], N)
    X2 = AAT_sampling('lhs', 2, st.uniform,[0, 1], N)
    plt.figure()
    plt.subplot(121)
    plt.plot(X1[:, 0],X1[:, 1], 'ok')
    plt.title('Random Uniform')
    plt.subplot(122)
    plt.plot(X2[:, 0],X2[:, 1], 'ok')
    plt.title('Latin Hypercube')

    Note: In sampling.AAT_sampling, the function lhcube.lhcube is used to derive
    latin hypercube sampling (L126). Alternatively, the python package pyDOE
    (pyDOE.lhs) could be used to perform latin hypercube sampling.

    This function is part of the SAFE Toolbox by F. Pianosi, F. Sarrazin
    and T. Wagener at Bristol University (2015).
    SAFE is provided without any warranty and for non-commercial use only.
    For more details, see the Licence file included in the root directory
    of this distribution.
    For any comment and feedback, or to discuss a Licence agreement for
    commercial use, please contact: francesca.pianosi@bristol.ac.uk
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info """

    ###########################################################################
    # Check inputs
    ###########################################################################

    if not isinstance(samp_strat, str):
        raise ValueError('"samp_strat" must be a string.')

    if not isinstance(M, (int, np.int8, np.int16, np.int32, np.int64)):
        raise ValueError('"M" must be scalar and integer.')
    if M <= 0:
        raise ValueError('"M" must be positive.')

    if callable(distr_fun):
        distr_fun = [distr_fun] * M
    elif isinstance(distr_fun, list):
        if len(distr_fun) != M:
            raise ValueError('If "distr_fun" is a list, it must have M components.')
    else:
        raise ValueError('"distr_fun" must be a list of functions or a function.')

    if isinstance(distr_par, list):
        if all(isinstance(i, float) or isinstance(i, int) for i in distr_par):
            distr_par = [distr_par] * M
        elif not all(isinstance(i, list) for i in distr_par):
            raise ValueError('"distr_par" be a list of M lists of parameters' +
                             'or a list of parameters is all input have the same.')
    else:
        raise ValueError('Wrong data type for input "distr_par".')

    if not isinstance(N, (int, np.int8, np.int16, np.int32, np.int64)):
        raise ValueError('"N" must be scalar and integer.')
    if N <= 0:
        raise ValueError('"N" must be positive.')

    ###########################################################################
    # Uniformly sample the unit square
    ###########################################################################
    if samp_strat == 'rsu':
        X = np.random.random((N, M))
    elif samp_strat == 'lhs':
        X, _ = lhcube(N, M, nrep)
    else:
        raise ValueError("""Sampling_strategy should be either ''rsu'' or ''lhs'""")

    ###########################################################################
    # Map back into the specified distribution by inverting the CDF
    ###########################################################################
    for i in range(M):

        pars = distr_par[i]
        num_par = len(pars)
        name = distr_fun[i]

        if name in [st.chi2, st.expon, st.geom, st.poisson, st.rayleigh,
                    st.t,st.weibull_max, st.weibull_min]:
            if num_par != 1:
                raise ValueError('Input ' + '%d' % (i+1)+ ': Number of PDF' +
                                 'parameters not consistent with PDF type')
            else:
                X[:, i] = name.ppf(X[:, i], pars)

        elif name in [st.beta, st.binom, st.f, st.gamma, st.lognorm, st.nbinom,
                      st.nct, st.ncx2, st.norm, st.uniform, st.randint]:
            if num_par != 2:
                raise ValueError('Input ' + '%d' % (i+1)+ ': Number of PDF' +
                                 'parameters not consistent with PDF type')
            else:
                X[:, i] = name.ppf(X[:, i], pars[0], pars[1])

        elif name in [st.genextreme, st.genpareto, st.hypergeom, st.ncf]:
            if num_par != 3:
                raise ValueError('Input ' + '%d' % (i+1)+ ': Number of PDF' +
                                 'parameters not consistent with PDF type')
            else:
                X[:, i] = name.ppf(X[:, i], pars[0], pars[1], pars[2])
        else:
            raise ValueError('Input ' + '%d' % (i+1)+ ': Unknown PDF type')

    return X

def lhcube(N, M, nrep=5):

    """Generate a latin hypercube of N datapoints in the M-dimensional hypercube
    [0,1]x[0,1]x...x[0,1]. If required, generation can be repeated for a
    prescribed number of times and the maximin latin hypercube is returned.

    Usage:
        X, d = lhcube.lhcube(N, M, nrep=5)

    Input:
       N = number of samples                              - positive int
       M = number of inputs                               - positive int
    nrep = number of repetition (default: 5)              - positive int

    Output:
       X = sample points                                  - numpy.ndarray (N,M)
       d = minimum distance between two points (rows) in X- scalar

    Example:

    import numpy as np
    import matplotlib.pyplot as plt
    from SAFEpython.lhcube import lhcube
    N = 10
    M = 2
    X, _ = lhcube(N, M)
    plt.figure()
    plt.plot(X[:, 0], X[:, 1], '.')
    plt.xticks(np.arange(0, 1+1/N, 1/N), '')
    plt.yticks(np.arange(0, 1+1/N, 1/N), '')
    plt.grid(linestyle='--')

    References:

    this is a python version of the code in:
            J.C. Rougier, calibrate package
            http://www.maths.bris.ac.uk/~mazjcr/#software

    This function is part of the SAFE Toolbox by F. Pianosi, F. Sarrazin
    and T. Wagener at Bristol University (2015).
    SAFE is provided without any warranty and for non-commercial use only.
    For more details, see the Licence file included in the root directory
    of this distribution.
    For any comment and feedback, or to discuss a Licence agreement for
    commercial use, please contact: francesca.pianosi@bristol.ac.uk
    For details on how to cite SAFE in your publication, please see:
    https://www.safetoolbox.info"""

    ###########################################################################
    # Check inputs
    ###########################################################################
    if not isinstance(N, (int, np.int8, np.int16, np.int32, np.int64)):
        raise ValueError('"N" must be scalar and integer.')
    if N <= 0:
        raise ValueError('"N" must be positive.')

    if not isinstance(M, (int, np.int8, np.int16, np.int32, np.int64)):
        raise ValueError('"M" must be scalar and integer.')
    if M <= 0:
        raise ValueError('"M" must be positive.')

    if not isinstance(nrep, (int, np.int8, np.int16, np.int32, np.int64)):
        raise ValueError('"nrep" must be scalar and integer.')
    if nrep <= 0:
        raise ValueError('"nrep" must be positive.')

    ###########################################################################
    # Generate latin hypercube sample
    ###########################################################################
    d = 0

    # Generate nrep hypercube sample X and keep the one that maximises the
    # minimum inter-point Euclidean distance between any two sampled points:
    for k in range(nrep):

        # Generate a latin-hypercube:
        ran = np.random.random((N, M))
        Xk = np.zeros((N, M))
        for i in range(M):
            idx = np.random.choice(np.arange(1, N+1, 1), size=(N, ), replace=False)
            Xk[:, i] = (idx - ran[:, i])/N

        # Compute the minimum distance between points in X:
        dk = np.min(pdist(Xk, metric='euclidean'))

        # If the current latin hypercube has minimum distance higher than
        # the best so far, it will be retained as the best.
        if dk > d:
            X = Xk
            d = d

    return X, d
