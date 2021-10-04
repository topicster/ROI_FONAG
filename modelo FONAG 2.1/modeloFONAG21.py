# -*- coding: utf-8 -*-
#############################################################################
#                                                                           #
#  Script:      Modelo FONAG 2.1 by atuk                                    #
#  Description: Modelo Hidrologico FONAG actualizado                        #
#  Created By:  ATUK Consultoria Estrategica & Katarisoft                   #
#  Date:        30-Abr-2020                                                 #
#                                                                           #
#############################################################################

print("""

          ############################################################
          #                                                          #
          #   Modelo Hidrologico FONAG 2.1 by atuk                   #
          #   Creado por: ATUK Consultoria Estrategica & Katarisoft  #
          #                                                          #
          ############################################################

  Cargando ...
    
    """)

# Import ArcPy site-package and os modules
import arcpy
import os
from arcpy import env
from arcpy.sa import *
import csv
import math
import numpy as np
import dbfread

# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
# Check out the ArcGIS Geostatistical Analyst extension license
arcpy.CheckOutExtension("GeoStats")

# Permitir sobreescritura de archivos
env.overwriteOutput = True

class modelinit():

    # Selecciona la ubicacion actual del directorio
    path = os.getcwd()

    # Lectura de inputs
    # inputs_usuario = raw_input('Ingrese el nombre del archivo con la tabla de inputs: ')
    # print("Lectura de inputs")

    def inputs(self):
        inputs = open(r"%s\modeloFONAG\inputs\t_inputs.csv" % self.path, "r")
        t_inputs = inputs.read().split("\n")[1].split("\r")[0].split(",")
        inputs.close()
        return t_inputs
        
    #def __init__(self):
        #print ""
        #path = path
        #t_inputs = t_inputs

    def f2r_c(self, in_features, field, out_raster, inMaskData):
        # FeatureToRaster_conversion
        arcpy.PointToRaster_conversion(in_features, field, out_raster, "SUM", field)
        out_rastser_zeros = Con(IsNull(out_raster), 0, out_raster)
        out_raster_mask = ExtractByMask(out_rastser_zeros, inMaskData)
        return out_raster_mask

    def asignacion(self, lista, raster, col1, col2):
        # Asignacion de tabla a raster (float)
        rasterlist = []
        sumraster = 0
        for i in lista[1:]:
            if type(i) != list:
                i = i.split(',')
            if len(i) <= 1:
                continue
            rasterlist.append(Con(raster == float(i[col1]),float(i[col2]),0))
        for j in rasterlist:
            sumraster += j
        return sumraster

    def asignacion_int(self, lista, raster, col1, col2):
        # Asignacion de tabla a raster (enteros)
        rasterlist = []
        sumraster = 0
        for i in lista[1:]:
            if type(i) != list:
                i = i.split(',')
            if len(i) <= 1:
                continue
            rasterlist.append(Con(raster == int(i[col1]), int(i[col2]), 0))
        for j in rasterlist:
            sumraster += j
        return sumraster

    def angleAccum(self, flowdir, angle):
        # Acumulacion de numeros positivos y negativos
        pos_angle = Con(angle > 0, angle, 0)
        neg_angle = Abs(Con(angle < 0, angle, 0))
        pos_accum = FlowAccumulation(flowdir, pos_angle, "FLOAT")
        neg_accum = FlowAccumulation(flowdir, neg_angle, "FLOAT")
        diff_accum = pos_accum - neg_accum
        return diff_accum

    def terreno(self,path):
        # Paso 1:
        # TERRENO: DEM, DIRECCION DE FLUJO, ACUMULACION, LONGITUD
        t_inputs = self.inputs()
        print("TERRENO: DEM, DIRECCION DE FLUJO, ACUMULACION, LONGITUD")

        # Crear carpeta de salidas
        print("Crear carpeta de salidas")
        os.system("md modeloFONAG\\%s" % t_inputs[16])
        os.system("md modeloFONAG\\%s\\tables" % t_inputs[16])
        env.workspace = "%s/modeloFONAG/%s" % (path, t_inputs[16])

        # Lectura de DEM y relleno de vacios
        r_DEM = arcpy.Raster("%s/modeloFONAG/inputs/%s" % (path, t_inputs[0]))
        print("Lectura DEM")
        print("%s/modeloFONAG/inputs/%s" % (path, t_inputs[0]))

        # Leer Mascara
        inMaskData = "%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[1], t_inputs[2])
        print("Lectura Mascara")
        print(inMaskData)

        # Extraer por mascara
        r_DEM_mask = ExtractByMask(r_DEM, inMaskData)
        r_DEM_mask.save("%s/modeloFONAG/%s/r_DEM_mask.tif" % (path, t_inputs[16]))
        print("Extraer por mascara")

        # Relleno de vacios
        r_SurfaceRaster = Fill(r_DEM_mask)
        r_SurfaceRaster.save("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))
        print("Relleno de vacios")

        #Variables de entorno
        env.cellSize = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        env.extent = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        print("Variables de entorno")

        # Generar raster de ceros y de unos para ciertos procesos
        r_DEM_ceros = r_SurfaceRaster * 0
        r_DEM_unos = r_SurfaceRaster / r_SurfaceRaster
        r_DEM_ceros.save("%s/modeloFONAG/%s/r_DEM_ceros.tif" % (path, t_inputs[16]))
        r_DEM_unos.save("%s/modeloFONAG/%s/r_DEM_unos.tif" % (path, t_inputs[16]))
        print("Extraer por mascara")


        # Genera hillshade
        r_Hillshade = "%s/modeloFONAG/%s/r_DEM_shd.tif" % (path, t_inputs[16])
        arcpy.HillShade_3d(r_SurfaceRaster, r_Hillshade, z_factor=3)
        print("Generar hillshade")

        # Direccion de flujo
        r_FlowDirection = FlowDirection(r_SurfaceRaster, "NORMAL")
        r_FlowDirection.save("%s/modeloFONAG/%s/r_DEM_dir.tif" % (path, t_inputs[16]))
        print("Direccion de flujo")

        # Acumulacion de flujo
        inWeightRaster = ""
        r_FlowAccumulation = FlowAccumulation(r_FlowDirection, inWeightRaster) + 1
        r_FlowAccumulation.save("%s/modeloFONAG/%s/r_DEM_acc.tif" % (path, t_inputs[16]))
        print("Acumulacion de flujo")

        # Area de aporte
        cellXResult = arcpy.GetRasterProperties_management(r_DEM_mask, "CELLSIZEX")
        cellYResult = arcpy.GetRasterProperties_management(r_DEM_mask, "CELLSIZEY")
        cellX = float(cellXResult.getOutput(0))
        cellY = float(cellYResult.getOutput(0))
        cellArea = cellX * cellY
        r_area = r_FlowAccumulation * cellArea
        r_area.save("%s/modeloFONAG/%s/r_DEM_area.tif" % (path, t_inputs[16]))
        print("Area de aporte")

        # Longitud de flujo
        r_FlowLength = FlowLength(r_FlowDirection, "UPSTREAM", inWeightRaster)
        r_FlowLength.save("%s/modeloFONAG/%s/r_DEM_length.tif" % (path, t_inputs[16]))
        print("Longitud de flujo")
        r_LengthAccumulation = FlowAccumulation(r_FlowDirection, r_FlowLength)
        r_Length_mean = r_LengthAccumulation / r_FlowAccumulation
        r_Length_norm = (r_FlowLength + 1) / (r_Length_mean + 1)
        c_factordist = Exp(-1 * r_Length_norm)
        c_factordist.save("%s/modeloFONAG/%s/r_factordist.tif" % (path, t_inputs[16]))
        print("Factor de ponderacion por distancia")

        print("FIN DE MODULO DE TERRENO")

    def usos_agua(self,path):
        # Paso 2:
        # USOS DE AGUA: ABSTRACCIONES Y RETORNOS
        print("USOS DE AGUA: ABSTRACCIONES Y RETORNOS")
        t_inputs = self.inputs()

        # Variables de entorno
        env.cellSize = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        env.extent = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        print("Variables de entorno")

        # Leer Raster de entrada
        inMaskData = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))
        r_area = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_area.tif" % (path, t_inputs[16]))
        r_FlowDirection = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_dir.tif" % (path, t_inputs[16]))
        r_FlowAccumulation = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_acc.tif" % (path, t_inputs[16]))

        # Generar raster de ceros y de unos para ciertos procesos
        r_SurfaceRaster = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))
        r_DEM_ceros = r_SurfaceRaster * 0
        # r_DEM_unos = r_SurfaceRaster / r_SurfaceRaster

        # Lectura de tabla de abstracciones y retornos
        f_coefret = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[4]), "r")
        lines_coefret = f_coefret.read().split("\n")
        f_coefret.close()

        dicwd = {}
        dicrf = {}
        dicsum = {}
        print("Lectura de tabla abstracciones")
        print(lines_coefret)

        if (len(lines_coefret) <= 1) or (len(lines_coefret[1]) == 0):
            # No existen usos de agua para modelar
            cont = False
            print("No existen usos de agua para modelar")
        else:
            # Creacion de rasters de abstracciones y retornos
            print("Inicio bucle de creacion de rasters de abstracciones")

            for i in lines_coefret[1:]:
                i = i.split(",")
                if len(i) <= 1:
                    continue
                # Abstracciones de agua
                print("%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[3], i[0]))
                print(i)
                if i[0][0] == 'v':
                    print("Transformar abstraccion a raster")
                    dicwd[i[0]] = self.f2r_c("%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[3], i[0]), i[3],
                                             "%s/modeloFONAG/%s/r%s.tif" % (path, t_inputs[16], i[0][1:]), inMaskData)
                elif i[0][0] == 'r':
                    print("Lectura de abstraccion raster")
                    dicwd[i[0]] = arcpy.Raster("%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[3], i[0]))
                    dicwd[i[0]] = Con(IsNull(dicwd[i[0]]), 0, dicwd[i[0]])
                    dicwd[i[0]] = ExtractByMask(dicwd[i[0]], inMaskData)
                elif not i[0][0]:
                    print("Abstraccion vacia")
                    dicwd[i[0]] = r_DEM_ceros
                else:
                    print("Abstraccion inexistente")
                    dicwd[i[0]] = r_DEM_ceros

                # Retornos de agua
                print("%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[3], i[1]))
                if i[1][0] == 'v':
                    print("Transformar retorno a raster")
                    dicrf[i[1]] = self.f2r_c("%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[3], i[1]), i[3],
                                             "%s/modeloFONAG/%s/r%s.tif" % (path, t_inputs[16], i[1][1:]), inMaskData)
                elif i[1][0] == 'r':
                    print("Lectura de retorno raster")
                    dicrf[i[1]] = arcpy.Raster("%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[3], i[1]))
                    dicrf[i[1]] = Con(IsNull(dicrf[i[1]]), 0, dicrf[i[1]])
                    dicrf[i[1]] = ExtractByMask(dicrf[i[1]], inMaskData)
                elif i[1][0] == 'd':
                    print("Retorno aguas abajo del punto de abstraccion")
                    dicrf[i[1]] = SnapPourPoint("%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[3], i[0]),
                                                      r_FlowAccumulation, float(i[1][2:]), i[3])
                elif not i[1][0]:
                    print("Retorno vacio")
                    dicrf[i[1]] = r_DEM_ceros
                else:
                    print("Retorno inexistente")
                    dicrf[i[1]] = r_DEM_ceros

                # Suma de retorno de agua con el coeficiente de retorno y resta de la abstraccion de agua
                dicsum[i[0]] = (dicrf[i[1]] * float(i[2])) - dicwd[i[0]]
            print("Fin bucle")

        # Suma de todos los usos de agua
        r_demand_m3s = r_DEM_ceros
        for i in dicsum:
            r_demand_m3s = r_demand_m3s + dicsum[i]
        r_demand_m3s.save("%s/modeloFONAG/%s/r_demand_m3s.tif" % (path, t_inputs[16]))
        print("Combinacion de abstracciones y retornos de agua")

        # Transformacion de unidades de usos de agua (queda pendiente el numero de dias al mes)
        r_demand_mmdia = r_demand_m3s * 60*60*24 *1000 / r_area
        r_demand_mmdia.save("%s/modeloFONAG/%s/r_demand_mmdia.tif" % (path, t_inputs[16]))
        print("Transformacion de unidades de usos de agua")

        # Acumulacion de usos de agua para estres hidrico
        r_wateruse_m3s = r_DEM_ceros
        for i in dicwd:
            r_wateruse_m3s = r_wateruse_m3s + dicwd[i]
        r_UsosAccumulation = self.angleAccum(r_FlowDirection,r_wateruse_m3s)
        r_UsosAccumulation.save("%s/modeloFONAG/%s/r_wateruse_acc.tif"%(path,t_inputs[16]))
        print("Acumulacion de usos de agua para estres hidrico")

        print("FIN DE MODULO DE USOS DE AGUA")

    def usos_suelo(self,path):
        # Paso 3:
        # USOS DE SUELO: ASIGNACION DE USOS DE HIDROZONAS
        print("USOS DE SUELO: ASIGNACION DE USOS DE HIDROZONAS")
        t_inputs = self.inputs()

        # Variables de entorno
        env.cellSize = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        env.extent = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        print("Variables de entorno")

        # Leer Raster de entrada
        inMaskData = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))

        # Lectura de la tabla de usos de suelo e hidrozonas
        f_landuse = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[6]), "r")
        lines_landuse = f_landuse.read().split("\n")
        f_landuse.close()
        print("Lectura de tabla de usos")

        # Lectura del raster de usos de suelo
        r_landuse = arcpy.Raster("%s/modeloFONAG/inputs/%s"%(path, t_inputs[5]))
        r_landuse_mask = ExtractByMask(r_landuse, inMaskData)
        print("Lectura raster usos suelo")

        # Asignacion de hidrozonas a usos de suelo
        r_hidrozonas = self.asignacion(lines_landuse, r_landuse_mask ,0, 1)
        r_hidrozonas.save("%s/modeloFONAG/%s/r_hidrozonas.tif" % (path, t_inputs[16]))
        print("Asignacion de hidrozonas a usos de suelo")

        print("FIN DE MODULO DE USOS DE SUELO")

    def contaminantes(self,path):
        # Coeficientes de contaminantes
        t_inputs = self.inputs()

        # Variables de entorno
        env.cellSize = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        env.extent = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        print("Variables de entorno")

        # Generar raster de ceros y de unos para ciertos procesos
        r_SurfaceRaster = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))
        # r_DEM_ceros = r_SurfaceRaster * 0
        r_DEM_unos = r_SurfaceRaster / r_SurfaceRaster

        # Lectura de tabla de coeficientes de hidrozonas
        r_hidrozonas = arcpy.Raster("%s/modeloFONAG/%s/r_hidrozonas.tif" % (path, t_inputs[16]))
        f_coefhz = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[7]), "r")
        lines_coefhz = f_coefhz.read().split("\n")
        f_coefhz.close()
        print("Lectura tabla de coeficientes")

        # Lectura de tabla de contaminantes
        f_cnt = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[10]), "r")
        lines_cnt = f_cnt.read().split("\n")
        f_cnt.close()
        print("Lectura de tabla de contaminantes")
        print(lines_cnt)

        # Leer puntos de aforo
        in_data = "%s/modeloFONAG/inputs/%s" % (path, t_inputs[15])
        print("Leer puntos de aforo")

        # Asignacion de coeficientes de transporte a hidrozonas
        diccnt = {}
        print("Inicia bucle de asignacion de coeficientes de transporte a hidrozonas")
        for i in lines_cnt[1:]:
            i = i.split(',')
            r_as = self.asignacion(lines_coefhz, r_hidrozonas, 0, 2 *int(i[ 0]) + 2)
            r_at = self.asignacion(lines_coefhz, r_hidrozonas, 0, 2 * int(i[0]) + 3)
            if not i[2]:
                print("No existe ponderacion por amenazas")
                # No existe ponderacion por amenazas
                r_amn = r_DEM_unos
            else:
                print("Leer raster de ponderacion por amenazas")
                # Leer raster de ponderacion por amenazas
                r_amn = arcpy.Raster("%s/modeloFONAG/inputs/%s/%s" % (path, t_inputs[9], i[2]))
            
            # Crear carpetas para resultados de contaminantes
            print("Crear carpeta para resultados de contaminante")
            os.system("md modeloFONAG\\%s\\cnt%s" % (t_inputs[16], i[0]))
            r_as.save("%s/modeloFONAG/%s/cnt%s/r_as.tif" % (path, t_inputs[16],i[0]))
            r_at.save("%s/modeloFONAG/%s/cnt%s/r_at.tif" % (path, t_inputs[16],i[0]))

            # Duplicar puntos de aforo para crear tablas de resultados
            out_data_cnt = "%s/modeloFONAG/%s/tables/v1_aforo_cnt%s.shp"%(path,t_inputs[16], i[0])
            arcpy.Copy_management(in_data, out_data_cnt)
            print("Crea punto de aforo para contaminante")
            print(out_data_cnt)

            # Crear almacen de datos mensuales
            cntset = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}

            # Guardar coeficientes de transporte de contaminantes
            diccnt['cnt%s' % i[0]] = {'r_as': r_as, 'r_at': r_at, 'r_amn': r_amn, 'decay': i[1], 'out_data_cnt': out_data_cnt, 'cntset': cntset}
        print("Fin bucle")

        # Duplicar puntos de aforo para crear tablas de resultados
        out_data_qr = "%s/modeloFONAG/%s/tables/v_aforo_qr.shp" % (path, t_inputs[16])
        arcpy.Copy_management(in_data, out_data_qr)
        print("Crea punto de aforo de escorrentia")
        print(out_data_qr)

        return diccnt

    def coeficientes(self,path):
        # Paso 4:
        # COEFICIENTES DE REGULACION HIDRLOGICA
        print("COEFICIENTES DE REGULACION HIDRLOGICA")
        t_inputs = self.inputs()

        # Variables de entorno
        env.cellSize = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        env.extent = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        print("Variables de entorno")

        # Lectura de tabla de coeficientes de hidrozonas
        f_coefhz = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[7]), "r")
        lines_coefhz = f_coefhz.read().split("\n")
        f_coefhz.close()
        print("Lectura tabla de coeficientes")

        # Asignacion de coeficientes hidrologicos a hidrozonas
        r_hidrozonas = arcpy.Raster("%s/modeloFONAG/%s/r_hidrozonas.tif" % ( path, t_inputs[16]))
        r_hz_kc = self.asignacion(lines_coefhz,r_hidrozonas,0,2)
        r_hz_kc.save("%s/modeloFONAG/%s/r_hz_kc.tif" % (path, t_inputs[16]))
        print("Asignacion de coeficientes hidrologicos a hidrozonas")

        # Crear un archivo de salida csv con los coeficientes determinados
        csvfile = open('t_coefhz_output.csv', 'w')
        field = ['hz', 'tipo', 'coef', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6',
                 'm7', 'm8', 'm9', 'm10', 'm11', 'm12', 'spt']
        writefile = csv.DictWriter(csvfile,field)
        writefile.writeheader()

        print("Inicia bucle de asignacion de coeficientes de regulacion hidrologica")
        for hz in lines_coefhz[1:]:
            hz = hz.split(",")
            if len(hz) > 1 and hz[1] == '1':
                print("Caso de hidrozona con comportamiento lineal")
                # Caso de hidrozona con comportamiento lineal
                yl = np.zeros(shape=(13,))
                m = np.zeros(shape=(12,))
                yl[0] = -1 * (float(hz[3])) * 0 + (2 * float(hz[3])) ** 0.5
                for j in range(1, 13):
                    yl[j] = -1 * (float(hz[3])) * j + (2 * float(hz[3])) ** 0.5
                    m[j - 1] = (yl[j] + yl[j - 1]) / 2
                # Eliminar coeficientes negativos y escalarlos
                m[m < 0] = 0
                M = sum(m)
                m = m / M
                writefile.writerow({'hz':hz[0],
                                    'tipo':hz[1],
                                    'coef':hz[2],
                                    'm1': m[0],
                                    'm2': m[1],
                                    'm3': m[2],
                                    'm4': m[3],
                                    'm5': m[4],
                                    'm6': m[5],
                                    'm7': m[6],
                                    'm8': m[7],
                                    'm9': m[8],
                                    'm10': m[9],
                                    'm11': m[10],
                                    'm12': m[11],
                                    'spt' : -999})

            elif len(hz) > 1 and hz[1] == '2':
                print("Caso de hidrozona con comportamiento no lineal")
                # Caso de hidrozona con comportamiento no lineal
                yl = np.zeros(shape=(13,))
                m = np.zeros(shape=(12,))
                yl[0] = float(hz[3]) * math.exp((-1 * float(hz[3])) * 0)
                for j in range(1, 13):
                    yl[j] = float(hz[3]) * math.exp((-1 * float(hz[3])) * j)
                    m[j - 1] = (yl[j] + yl[j - 1]) / 2
                # Eliminar coeficientes negativos y escalarlos
                m[m < 0] = 0
                M = sum(m)
                m = m / M
                writefile.writerow({'hz': hz[0],
                                    'tipo': hz[1],
                                    'coef': hz[2],
                                    'm1': m[0],
                                    'm2': m[1],
                                    'm3': m[2],
                                    'm4': m[3],
                                    'm5': m[4],
                                    'm6': m[5],
                                    'm7': m[6],
                                    'm8': m[7],
                                    'm9': m[8],
                                    'm10': m[9],
                                    'm11': m[10],
                                    'm12': m[11],
                                    'spt': -999})

            elif len(hz) > 1 and hz[1] == '3':
                print("Caso de hidrozona glaciar")
	            # Caso de hidrozona glaciar
                writefile.writerow({'hz': hz[0],
                                    'tipo': hz[1],
                                    'coef': hz[2],
                                    'm1': 0.000001, # 1./12.,
                                    'm2': 0.0, # 1./12.,
                                    'm3': 0.0, # 1./12.,
                                    'm4': 0.0, # 1./12.,
                                    'm5': 0.0, # 1./12.,
                                    'm6': 0.0, # 1./12.,
                                    'm7': 0.0, # 1./12.,
                                    'm8': 0.0, # 1./12.,
                                    'm9': 0.0, # 1./12.,
                                    'm10': 0.0, # 1./12.,
                                    'm11': 0.0, # 1./12.,
                                    'm12': 0.0, # 1./12.,
                                    'spt': hz[3]})
        print("Fin bucle")

        # Asignacion de coeficientes de regulacion a hidrozonas
        csvfile.close()
        writefileasig = open("t_coefhz_output.csv", "r")
        writefileasig = writefileasig.read().split("\n")
        r_mes = []
        for j in range(12):
            r_mes.append(self.asignacion(writefileasig, r_hidrozonas, 0, j + 3))
            r_mes[j].save("%s/modeloFONAG/%s/r_mes%s.tif" % (path, t_inputs[16], j + 1))
        r_spt = self.asignacion(writefileasig, r_hidrozonas, 0, 15)
        r_spt.save("%s/modeloFONAG/%s/r_spt.tif" % (path, t_inputs[16]))
        try:
            os.remove("%s/modeloFONAG/%s/tables/t_coefhz_output.csv" % (path, t_inputs[16]))
        except OSError as error:
            print(error)
            print("No existe archivo t_coefhz_output.csv anterior. Avanzar.")
        os.rename("t_coefhz_output.csv", "%s/modeloFONAG/%s/tables/t_coefhz_output.csv" % (path, t_inputs[16]))
        print("Asignacion de coeficientes de regulacion a hidrozonas")
        # Guardar coeficientes de regulacion hidrologica

        print("FIN DE MODULO DE CONTAMINANTES")

    def balance(self,path):
        # Paso 5:
        # MODELO HIDROLOGICO: BALANCE HIDRICO MENSUAL
        print("MODELO HIDROLOGICO: BALANCE HIDRICO MENSUAL")
        t_inputs = self.inputs()

        # Variables de entorno
        env.cellSize = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        env.extent = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        print("Variables de entorno")

        # Leer Raster de entrada
        r_FlowDirection = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_dir.tif" % (path, t_inputs[16]))
        r_FlowAccumulation = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_acc.tif" % (path, t_inputs[16]))
        r_SurfaceRaster = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))
        inMaskData = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))

        # Generar raster de ceros y de unos para ciertos procesos
        r_DEM_ceros = r_SurfaceRaster * 0
        # r_DEM_unos = r_SurfaceRaster / r_SurfaceRaster

        # Area de aporte
        cellXResult = arcpy.GetRasterProperties_management(r_SurfaceRaster, "CELLSIZEX")
        cellYResult = arcpy.GetRasterProperties_management(r_SurfaceRaster, "CELLSIZEY")
        cellX = float(cellXResult.getOutput(0))
        cellY = float(cellYResult.getOutput(0))
        cellArea = cellX * cellY

        # Factor exponencial de escorrentia para transporte de contaminantes
        n = 0.4
        print("Factor exponencial de escorrentia para transporte de contaminantes: %s" % n)

        # Factor H de lavado de suelos
        f_factorh = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[8]), "r")
        c_factorh = f_factorh.read().split("\n")
        factorh = c_factorh[1].split(',')
        ndias = c_factorh[2].split(',')
        f_factorh.close()
        print("Factor H de lavado de suelos")

        # Lectura de la tabla de fechas de inicio y fin de modelacion
        f_fechas = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[11]), "r")
        lista_fechas = f_fechas.read().split("\n")
        f_fechas.close()
        print("Lectura de la tabla de fechas de inicio y fin de modelacion")

        # Determina el numero de iteraciones en base a las fechas indicadas
        iterdata = lista_fechas[1].split(',')
        iter = ((int(iterdata[2])-int(iterdata[0]))*12)+(int(iterdata[3])-int(iterdata[1]))+1
        print("Determina el numero de iteraciones en base a las fechas indicadas")

        # Definir el anio inicial
        y = int(iterdata[0])
        # Determinar el mes inicial
        m = int(iterdata[1])
        # Inicializar escorrentia mensual
        q = {}
        for j in range(1, 13):
            q['q%s' % j] = r_DEM_ceros

        # Leer puntos de aforo
        in_data = "%s/modeloFONAG/inputs/%s" % (path, t_inputs[15])
        print("Leer puntos de aforo")

        # Crear carpetas para resultados de caudales
        print("Crear carpetas para resultados de caudales")
        os.system("md modeloFONAG\\%s\\Qn" % t_inputs[16])
        os.system("md modeloFONAG\\%s\\Qd" % t_inputs[16])
        os.system("md modeloFONAG\\%s\\qnt" % t_inputs[16])
        os.system("md modeloFONAG\\%s\\qds" % t_inputs[16])

        # Duplicar puntos de aforo para crear tablas de resultados
        out_data_prc = "%s/modeloFONAG/%s/tables/v_aforo_prc.shp" % (path, t_inputs[16])
        out_data_eto = "%s/modeloFONAG/%s/tables/v_aforo_eto.shp" % (path, t_inputs[16])
        out_data_eta = "%s/modeloFONAG/%s/tables/v_aforo_eta.shp" % (path, t_inputs[16])
        out_data_tmp = "%s/modeloFONAG/%s/tables/v_aforo_tmp.shp" % (path, t_inputs[16])
        out_data_gla = "%s/modeloFONAG/%s/tables/v_aforo_gla.shp" % (path, t_inputs[16])
        out_data_Qn = "%s/modeloFONAG/%s/tables/v_aforo_Qn.shp" % (path, t_inputs[16])
        out_data_qnt = "%s/modeloFONAG/%s/tables/v_aforo_qnt.shp" % (path, t_inputs[16])
        out_data_Qd = "%s/modeloFONAG/%s/tables/v_aforo_Qd.shp" % (path, t_inputs[16])
        out_data_qds = "%s/modeloFONAG/%s/tables/v_aforo_qds.shp" % (path, t_inputs[16])

        # Copiar los shp files correspondientes
        arcpy.Copy_management(in_data, out_data_prc)
        arcpy.Copy_management(in_data, out_data_eto)
        arcpy.Copy_management(in_data, out_data_eta)
        arcpy.Copy_management(in_data, out_data_tmp)
        arcpy.Copy_management(in_data, out_data_gla)
        arcpy.Copy_management(in_data, out_data_Qn)
        arcpy.Copy_management(in_data, out_data_qnt)
        arcpy.Copy_management(in_data, out_data_Qd)
        arcpy.Copy_management(in_data, out_data_qds)
        print("Crea punto de aforo de caudales")

        # Crear almacenes de datos mensuales
        qntset = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
        Qnset = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}

        # Leer coeficientes de hidrozonas
        r_mes = []
        for j in range(12):
            r_mes.append(arcpy.Raster("%s/modeloFONAG/%s/r_mes%s.tif" % (path, t_inputs[16], j + 1)))
        r_spt = arcpy.Raster("%s/modeloFONAG/%s/r_spt.tif" % (path, t_inputs[16]))
        r_hz_kc = arcpy.Raster("%s/modeloFONAG/%s/r_hz_kc.tif" % (path, t_inputs[16]))

        # Determinar coeficientes de contaminantes si es que existen
        f_cnt = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[10]), "r")
        lines_cnt = f_cnt.read().split("\n")
        f_cnt.close()
        if lines_cnt[1] and lines_cnt[1][0]:
            diccnt = self.contaminantes(path)
            cont = True
        else:
            cont = False

        print("Inicia bucle de modelacion hidrologica")
        for i in range(iter):
            # Completar el numero de mes a dos digitos
            mes = int(m)
            if m < 10:
                m = "0%s" % m
            print("PROCESANDO ANIO %s MES %s" % (y, m))

            print("  Calcular el caudal para el mes actual")
            # Calcular deshielo glaciar del mes actual
            # Usar temperatura minima:
            # r_tmp = arcpy.Raster("%s/modeloFONAG/inputs/%s/r_tmpmin_%s_%s.tif" % (path, t_inputs[13], y, m))
            # Si no se tiene temperatura minima, usar la temperatura promedio escalada:
            r_tmpavg = arcpy.Raster("%s/modeloFONAG/inputs/%s/r_tmp_%s_%s.tif" % (path, t_inputs[13], y, m))
            r_tmp = r_tmpavg / 3 - 1 # Esta relacion deberia ser calibrada
            r_gla = Con(r_spt == -999, 0, r_tmp * (1.52 + 0.54 * r_spt) / int(ndias[mes]))

            # Reasignar los caudales arrastrados de meses anteriores
            for j in range(12, 1, -1):
                q['q%s' % j] = q['q%s' % (j - 1)]

            # Leer datos climaticos mensuales
            r_prc = arcpy.Raster("%s/modeloFONAG/inputs/%s/r_prc_%s_%s.tif"%(path,t_inputs[12],y,m))
            r_eto = arcpy.Raster("%s/modeloFONAG/inputs/%s/r_eto_%s_%s.tif"%(path,t_inputs[14],y,m))

            # Calcular evapotranspiracion real
            r_eta = r_hz_kc * r_eto

            # Calcular la lluvia efectiva del mes actual
            q['q1'] = Con(r_prc - r_eta < 0, 0, r_prc - r_eta)

            # Calcular el caudal natural del mes actual
            Qn = r_gla
            for j in range(1, 13):
                Qn += r_mes[j - 1] * q['q%s' % j]
            Qn.save("%s/modeloFONAG/%s/Qn/r_Qn_%s_%s.tif" % (path, t_inputs[16], y, m))

            # Transformar unidades de caudal natural
            Qn_m3s = Qn * cellArea / (60*60*24*1000) / float(ndias[mes])
            r_qnt_m3s = FlowAccumulation(r_FlowDirection, Qn_m3s)
            r_qnt_m3s.save("%s/modeloFONAG/%s/qnt/r_qnt_%s_%s.tif" % (path, t_inputs[16], y, m))

            # Almacenar rasters mensuales
            qntset[mes].append(r_qnt_m3s)
            Qnset[mes].append(Qn)

            # Calcular el caudal disponible del mes actual
            r_demand_mmdia = arcpy.Raster("%s/modeloFONAG/%s/r_demand_mmdia.tif" % (path, t_inputs[16]))
            Qd = Con(Qn + (r_demand_mmdia * int(ndias[mes])) < 0, 0, Qn + (r_demand_mmdia * int(ndias[mes])))
            Qd.save("%s/modeloFONAG/%s/Qd/r_Qd_%s_%s.tif" % (path, t_inputs[16], y, m))

            # Transformar unidades de caudal dispinible
            Qd_m3s = Qd * cellArea / (60*60*24*1000) / float(ndias[mes])
            r_qds_m3s = self.angleAccum(r_FlowDirection, Qd_m3s)
            r_qds_m3s.save("%s/modeloFONAG/%s/qds/r_qds_%s_%s.tif" % (path, t_inputs[16], y, m))
            print("  Guardar resultado de calculo de caudales")

            # Calcular acumulados en el punto de aforo
            r_prc_acc = FlowAccumulation(r_FlowDirection, r_prc) / r_FlowAccumulation
            r_eto_acc = FlowAccumulation(r_FlowDirection, r_eto) / r_FlowAccumulation
            r_eta_acc = FlowAccumulation(r_FlowDirection, r_eta) / r_FlowAccumulation
            r_tmp_acc = self.angleAccum(r_FlowDirection, r_tmp) / r_FlowAccumulation
            r_gla_acc = FlowAccumulation(r_FlowDirection, r_gla) / r_FlowAccumulation
            r_Qn_acc = FlowAccumulation(r_FlowDirection, Qn) / r_FlowAccumulation
            r_Qd_acc = self.angleAccum(r_FlowDirection, Qd) / r_FlowAccumulation

            # Ingresar los resultados en las tablas de atributos
            ExtractMultiValuesToPoints(out_data_prc, [[r_prc_acc, "%s_%s" % (y, m)]])
            ExtractMultiValuesToPoints(out_data_eto, [[r_eto_acc, "%s_%s" % (y, m)]])
            ExtractMultiValuesToPoints(out_data_eta, [[r_eta_acc, "%s_%s" % (y, m)]])
            ExtractMultiValuesToPoints(out_data_tmp, [[r_tmp_acc, "%s_%s" % (y, m)]])
            ExtractMultiValuesToPoints(out_data_gla, [[r_gla_acc, "%s_%s" % (y, m)]])
            ExtractMultiValuesToPoints(out_data_Qn, [[r_Qn_acc, "%s_%s" % (y, m)]])
            ExtractMultiValuesToPoints(out_data_qnt, [[r_qnt_m3s, "%s_%s" % (y, m)]])
            ExtractMultiValuesToPoints(out_data_Qd, [[r_Qd_acc, "%s_%s" % (y, m)]])
            ExtractMultiValuesToPoints(out_data_qds, [[r_qds_m3s, "%s_%s" % (y, m)]])
            print("  Extraer valores en el punto de aforo")

            if cont:
                diccnt, out_data_qr = self.transporte(q, n, ndias, mes, y, m, diccnt, factorh, r_qds_m3s, r_mes,
                                              inMaskData, cellArea, r_FlowDirection, path)

            # Determinar el valor de anio y mes de la siguiente iteracion
            if int(m) == 12:
                m = 0
                y = y + 1
            m = int(m) + 1

        print("Fin bucle")

        # Exportar los resultados a csv
        arcpy.TableToTable_conversion(out_data_prc, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_prc.csv")
        arcpy.TableToTable_conversion(out_data_eto, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_eto.csv")
        arcpy.TableToTable_conversion(out_data_eta, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_eta.csv")
        arcpy.TableToTable_conversion(out_data_tmp, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_tmp.csv")
        arcpy.TableToTable_conversion(out_data_gla, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_gla.csv")
        arcpy.TableToTable_conversion(out_data_Qn, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_Qn.csv")
        arcpy.TableToTable_conversion(out_data_qnt, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_qnt.csv")
        arcpy.TableToTable_conversion(out_data_Qd, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_Qd.csv")
        arcpy.TableToTable_conversion(out_data_qds, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_qds.csv")
        # Exportar matrices mensuales a csv
        with open("%s/modeloFONAG/%s/tables/%s" % (path, t_inputs[16], "Qnset.csv"), 'w') as f:
            for key in Qnset.keys():
                f.write("%s,%s\n" % (key, Qnset[key]))
        with open("%s/modeloFONAG/%s/tables/%s" % (path, t_inputs[16], "qntset.csv"), 'w') as f:
            for key in qntset.keys():
                f.write("%s,%s\n" % (key, qntset[key]))
        if cont:
            arcpy.TableToTable_conversion(out_data_qr, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_qr.csv")
            for j in diccnt:
                arcpy.TableToTable_conversion(diccnt[j]['out_data_cnt'], "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_%s.csv" % j)
                with open("%s/modeloFONAG/%s/tables/%s" % (path, t_inputs[16], "%sset.csv" % j), 'w') as f:
                    for key in diccnt[j]['cntset'].keys():
                        f.write("%s,%s\n" % (key, diccnt[j]['cntset'][key]))
        print("Exportar los resultados a csv")

        print("FIN DE MODULO DE BALANCE HIDRICO")

    def transporte(self, q, n, ndias, mes, y, m, diccnt, factorh, r_qds_m3s, r_mes, inMaskData, cellArea, r_FlowDirection, path):
        # CALCULO DE TRANSPORTE DE CONTAMINANTES
        print("  Calcular el transporte de cada contaminante para el mes actual")
        t_inputs = self.inputs()
        # Leer Raster de entrada
        c_factordist = arcpy.Raster("%s/modeloFONAG/%s/r_factordist.tif" % (path, t_inputs[16]))

        # Calcular la escorrentia superficial del mes actual
        qr = r_mes[0] * q['q1'] * cellArea / (60*60*24*1000) / float(ndias[mes])

        # Ingresar los resultados en las tablas de atributos
        out_data_qr = "%s/modeloFONAG/%s/tables/v_aforo_qr.shp" % (path, t_inputs[16])
        ExtractMultiValuesToPoints(out_data_qr, [[qr, "%s_%s" % (y, m)]])

        # Calcular el transporte de cada contaminante para el mes actual
        for j in diccnt:
            # diccnt['cnt%s'%i[0]] = {'r_as': r_as, 'r_at': r_at, 'r_amn': r_amn, 'decay': i[1], 'out_data_cnt': out_data_cnt, 'cntset': cntset}

            # Calcular la concentracion inicial del contaminante
            r_cnt = (diccnt[j]['r_as'] + float(factorh[mes]) * (diccnt[j]['r_at']-diccnt[j]['r_as']))*pow(qr,1+n)

            # Escalar la concentracion por el coeficiente de ponderacion de amenazas
            r_cnt_pon = r_cnt * diccnt[j]['r_amn']

            # Escalar la concentracion por el coeficiente de ponderacion de distancia
            if diccnt[j]['decay'] != '0':
                # Contaminante no conservativo
                print("    Contaminante no conservativo")
                r_cnt_pon = r_cnt_pon * (c_factordist ** float(diccnt[j]['decay']))
            else:
                # Contaminante conservativo
                print("    Contaminante conservativo")

            # Calcular la acumulacion de carga
            Y = FlowAccumulation(r_FlowDirection, r_cnt_pon)

            # Calcular la concentracion total del contaminante
            r_act = Con(IsNull(Y / r_qds_m3s), 0, Y / r_qds_m3s)
            r_act = ExtractByMask(r_act, inMaskData)
            r_act.save("%s/modeloFONAG/%s/%s/r_%s_%s_%s.tif" % (path, t_inputs[16], j, j, y, m))

            # Almacenar rasters mensuales
            diccnt[j]['cntset'][mes].append(r_act)

            # Ingresar los resultados en las tablas de atributos
            ExtractMultiValuesToPoints(diccnt[j]['out_data_cnt'], [[r_act, "%s_%s" % (y, m)]])
        print("  Guardar resultado de concentracion de contaminantes")

        return diccnt, out_data_qr

    def estres(self, path):
        # Paso 6:
        # ESTRES HIDRICO
        print("ESTRES HIDRICO")
        t_inputs = self.inputs()

        # Variables de entorno
        env.cellSize = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        env.extent = "%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16])
        print("Variables de entorno")

        # Leer Raster de Entrada
        r_UsosAccumulation = arcpy.Raster("%s/modeloFONAG/%s/r_wateruse_acc.tif" % (path, t_inputs[16]))
        # Generar raster de ceros y de unos para ciertos procesos
        r_SurfaceRaster = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))
        r_DEM_ceros = r_SurfaceRaster * 0
        # r_DEM_unos = r_SurfaceRaster / r_SurfaceRaster

        # Reconstruir las matrices mensuales
        qntset = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
        Qnset = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
        t_qntset = open("%s/modeloFONAG/%s/tables/qntset.csv"%(path,t_inputs[16]), 'r')
        t_Qnset = open("%s/modeloFONAG/%s/tables/Qnset.csv" % (path, t_inputs[16]), 'r')
        for est in t_Qnset:
            #import pdb
            #pdb.set_trace()
            line = est.split('\n')[0].split(",")
            for i in line[1:]:
                Qnset[int(line[0])].append(arcpy.Raster(i.replace('\\', '/').replace('\r', '/r').strip('[]')))
        for est in t_qntset:
            # import pdb
            # pdb.set_trace()
            line = est.split('\n')[0].split(",")
            for i in line[1:]:
                qntset[int(line[0])].append(arcpy.Raster(i.replace('\\', '/').replace('\r', '/r').strip('[]')))
        t_qntset.close()
        t_Qnset.close()

        # Crear carpetas para resultados de caudales
        print("Crear carpetas para caudales mensuales interanuales")
        os.system("md modeloFONAG\\%s\\%s" % (t_inputs[16], 'Qm'))
        os.system("md modeloFONAG\\%s\\%s" % (t_inputs[16], 'Q80'))

        # Inicializar el indicador de estres hidrico
        NQm = r_DEM_ceros
        NQ80 = r_DEM_ceros

        # Calcular  promedios mensuales
        print("Inicia bucle de promedios mensuales")
        for i in qntset:
            if i < 10:
                mes = "0%s" % i
            else:
                mes = i

            if len(qntset[i]) == 0:
                print("  No hay datos suficientes para el mes %s" % mes)

            elif len(qntset[i]) == 1:
                print("  Raster unico para el mes %s" % mes)
                out_Qm = qntset[i][0]
                out_Qm.save('%s/modeloFONAG/%s/Qm/r_Qm_%s.tif' % (path, t_inputs[16], mes))
                out_Qn = Qnset[i][0]
                out_Qn.save('%s/modeloFONAG/%s/Qm/r_Qn_mean_%s.tif' % (path, t_inputs[16], mes))
                print("  Asumir promedio mensual interanual")

                # Determinar el indicador de estres hidrico
                NQm = Con(out_Qm < r_UsosAccumulation, NQm + 1, NQm)

                out_q80 = 0.50 * qntset[i][0]
                out_q80.save('%s/modeloFONAG/%s/Q80/r_q80_%s.tif'%(path, t_inputs[16],mes))
                print("  Asumir percentil Q80 mensual interanual")

                # Determinar el indicador de estres hidrico
                NQ80 = Con(out_q80 < r_UsosAccumulation, NQ80 + 1, NQ80)

            else:
                print("  Calculo de promedio mensual del mes %s" % mes)
                out_Qm = CellStatistics(qntset[i], "MEAN")
                out_Qm.save('%s/modeloFONAG/%s/Qm/r_Qm_%s.tif' % (path, t_inputs[16], mes))
                out_Qn = CellStatistics(Qnset[i], "MEAN")
                out_Qn.save('%s/modeloFONAG/%s/Qm/r_Qn_mean_%s.tif' % (path, t_inputs[16], mes))
                print("  Guardar raster de promedio mensual interanual")

                # Determinar el indicador de estres hidrico
                NQm = Con(out_Qm < r_UsosAccumulation, NQm + 1, NQm)

                print("  Calculo de percentil Q80 mensual del mes %s" % mes)
                arrs = []
                for j in qntset[i]:
                    # Obtener variables del raster
                    lowerLeft = arcpy.Point(j.extent.XMin, j.extent.YMin)
                    cellSize = j.meanCellWidth

                    # Convertir Raster a Array
                    a = arcpy.RasterToNumPyArray(j, nodata_to_value = -9999)

                    # Reconvertir Array a Raster
                    # b = arcpy.NumPyArrayToRaster(a,lowerLeft,cellSize,value_to_nodata=-9999)
                    # b.save('%s.tif'%mes)

                    # Acumular arrays para proceso posterior
                    arrs.append(a)

                a = np.array(arrs)
                # ---- create the masked arrays assuming 0.0 is the null/nodata value ----
                arrs_m = []
                for j in arrs:
                    m = np.where(a[0] == -9999, 1, 0)
                    am = np.ma.MaskedArray(j, mask = m)
                    arrs_m.append(am)
                a_m = np.array(arrs_m)

                # Calcular el percentil Q80
                n_80 = np.nanpercentile(a_m, q=20., axis=0)

                out_q80 = arcpy.NumPyArrayToRaster(n_80, lowerLeft, cellSize, value_to_nodata=-9999)
                out_q80.save('%s/modeloFONAG/%s/Q80/r_q80_%s.tif' % (path, t_inputs[16], mes))
                print("  Guardar raster de percentil Q80 mensual interanual")

                # Determinar el indicador de estres hidrico
                NQ80 = Con(out_q80 < r_UsosAccumulation, NQ80 + 1, NQ80)
        print("Fin bucle")

        # Guardar resultados del estres hidrico
        NQm.save('%s/modeloFONAG/%s/Qm/r_NQm.tif' % (path, t_inputs[16]))
        NQ80.save('%s/modeloFONAG/%s/Q80/r_NQ80.tif' % (path, t_inputs[16]))
        print("Guardar indicadores de estres hidrico")

        # Calcular el estres hidrico en base al indicador
        r_estres = Con((NQm > 2) & (NQ80 > 5), 4, Con((NQm > 2) & (NQ80 > 3), 3, Con((NQm > 0) & (NQ80 > 3), 2, Con((NQ80 > 0), 1, 0))))
        print("Calculo de estres hidrico")
        r_estres.save('%s/modeloFONAG/%s/r_estres.tif'%(path,t_inputs[16]))
        print("  Guardar resultados de estres hidrico")

        # Determinar coeficientes de contaminantes si es que existen
        f_cnt = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[10]), "r")
        lines_cnt = f_cnt.read().split("\n")
        f_cnt.close()
        if lines_cnt[1] and lines_cnt[1][0]:
            self.promedio_contaminantes()
            
        # Leer puntos de aforo
        in_data = "%s/modeloFONAG/inputs/%s" % (path, t_inputs[15])
        print("Leer puntos de aforo")
        
        # Duplicar puntos de aforo para crear tablas de resultados
        out_data_estres = "%s/modeloFONAG/%s/tables/v_aforo_estres.shp" % (path, t_inputs[16])
        
        # Copiar los shp files correspondientes
        arcpy.Copy_management(in_data, out_data_estres)
        
        # Ingresar los resultados en las tablas de atributos
        ExtractMultiValuesToPoints(out_data_estres, [[r_estres, "estres puntual"]])
        

        # Exportar los resultados a csv
        arcpy.TableToTable_conversion(out_data_estres, "%s/modeloFONAG/%s/tables/" % (path, t_inputs[16]), "t_out_data_estres.csv")
        

        # Leer punto de aforo para la calibracion
        v_aforo = '%s/modeloFONAG/inputs/%s' % (path, t_inputs[18])
        print('Lectura de coordenadas de puntos de aforo')
        
        # Determinar el area de la cuenca de aporte
        r_FlowDirection = arcpy.Raster('%s/modeloFONAG/%s/r_DEM_dir.tif' % (path,t_inputs[16]))
        r_outWatershed = Watershed(r_FlowDirection, v_aforo)
        r_outWatershed.save('%s/modeloFONAG/%s/tables/r_outWatershed.tif' % (path, t_inputs[16]))
        print('Determinar el area de la cuenca de aporte')
        
        # Crear tablas de estadisticas (calcular el area de cada categoria de estres)
        estres_OutTable = r'%s\modeloFONAG\%s\tables' % (path, t_inputs[16]) + r'\t_tab_estres.dbf'
        TabulateArea(r_estres, 'Value', r_outWatershed, 'Value', estres_OutTable, 1)
        
        # Leer tabla creada
        estres_table = dbfread.DBF(estres_OutTable, load=True)
            
        print("FIN DE MODULO DE ESTRES HIDRICO")

        print(" ")
        print("""
    
        #################################################################
        #                                                               #
        #   Modelo Hidrologico FONAG 2.0 by atuk                        #
        #   Created By: ATUK strategic consultancy & Katarisoft         #
        #                                                               #
        #################################################################
    
        """)

    def promedio_contaminantes(self, path):
        # Paso 6b:
        # PROMEDIO DE CONTAMINANTES
        print("PROMEDIO DE CONTAMINANTES")
        t_inputs = self.inputs()
        # Leer Raster de Entrada
        # r_UsosAccumulation = arcpy.Raster("%s/modeloFONAG/%s/r_wateruse_acc.tif" % (path, t_inputs[16]))
        # Generar raster de ceros y de unos para ciertos procesos
        r_SurfaceRaster = arcpy.Raster("%s/modeloFONAG/%s/r_DEM_fill.tif" % (path, t_inputs[16]))
        # r_DEM_ceros = r_SurfaceRaster * 0
        # r_DEM_unos = r_SurfaceRaster / r_SurfaceRaster

        # Crear carpetas para resultados de contaminantes
        print("Crear carpetas para contaminantes mensuales interanuales")
        os.system("md modeloFONAG\\%s\\%s" % (t_inputs[16], 'Cntm'))

        # Lectura de tabla de contaminantes
        f_cnt = open("%s/modeloFONAG/inputs/%s" % (path, t_inputs[10]), "r")
        lines_cnt = f_cnt.read().split("\n")
        f_cnt.close()

        for j in lines_cnt[1:]:
            j = j.split(',')

            # Reconstruir las matrices mensuales
            cntset = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []}
            t_cntset = open("%s/modeloFONAG/%s/tables/%s" % (path, t_inputs[16], "cnt%sset.csv" % j[0]), 'r')
            for est in t_cntset:
                # import pdb
                # pdb.set_trace()
                line = est.split('\n')[0].split(",")
                for k in line[1:]:
                    cntset[int(line[0])].append(arcpy.Raster(k.replace('\\', '/').replace('\r', '/r').strip('[]')))
            t_cntset.close()

            # Calcular  promedios mensuales
            print("Inicia bucle de promedios mensuales para contaminate cnt%s" % j[0])
            for i in cntset:
                if i < 10:
                    mes = "0%s" % i
                else:
                    mes = i

                if len(cntset[i]) == 0:
                    print("  No hay datos suficientes para el mes %s" % mes)

                elif len(cntset[i]) == 1:
                    print("  Raster unico para el mes %s" % mes)
                    out_Cntm = cntset[i][0]
                    out_Cntm.save('%s/modeloFONAG/%s/Cntm/r_cnt%s_mean_%s.tif' % (path, t_inputs[16], j[0], mes))
                    print("  Asumir promedio mensual interanual")
                else:
                    print("  Calculo de promedio mensual del mes %s" % mes)
                    out_Cntm = CellStatistics(cntset[i], "MEAN")
                    out_Cntm.save('%s/modeloFONAG/%s/Cntm/r_cnt%s_mean_%s.tif' % (path, t_inputs[16], j[0], mes))
                    print("  Guardar raster de promedio mensual interanual")
            print("Fin bucle")
