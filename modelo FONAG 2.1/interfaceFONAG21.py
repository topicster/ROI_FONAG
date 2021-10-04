# -*- coding: utf-8 -*-

print('''
###################################################################################
###      ######  ######   ####  ###### ########      #######      ########    #####
###  #######  ####  ###    ###  ##### # ######  ####  #####  ####  #########  #####
###     ###  ######  ##  #  ##  #### ### ####   #################  #########  #####
###  ######  ######  ##  ### #  ###       ###  ###    ########   ###########  #####
###  #######  ####  ###  ####   ##  #####  ###   ##   #######   ############  #####
###  ##########  ######  ####   #  #######  ####    ########        ###  ###  #####
###################################################################################
''')


from Tkinter import *
import os
from tkFileDialog import askopenfiles
from tkFileDialog import  askdirectory
from Tkinter import PhotoImage as pim
from tkinter import ttk
from PIL import Image,ImageTk
import tkMessageBox
import threading
import dbfread

os.chdir(os.path.dirname(os.path.abspath(__file__)))
path = os.getcwd() 

class SplashScreen:
    def __init__(self, parent):
        self.parent = parent
 
        self.aturSplash()
        self.aturWindow()
 
    def aturSplash(self):
        # import image menggunakan Pillow
        self.gambar = Image.open('%s/img/logo1.gbr'%path)
        self.imgSplash = ImageTk.PhotoImage(self.gambar)
 
    def aturWindow(self):
        # ambil ukuran dari file image
        lebar, tinggi = self.gambar.size
 
        setengahLebar = (self.parent.winfo_screenwidth()-lebar)//2
        setengahTinggi = (self.parent.winfo_screenheight()-tinggi)//2
 
        # atur posisi window di tengah-tengah layar
        self.parent.geometry("%ix%i+%i+%i" %(lebar, tinggi,
                                             setengahLebar,setengahTinggi))
 
        # atur Image via Komponen Label
        Label(self.parent, image=self.imgSplash).pack()

def splash(root):
    # menghilangkan judul dan batas frame Window
    root.overrideredirect(True)
    progressbar = ttk.Progressbar(orient=HORIZONTAL, length=10000, mode='determinate')
    progressbar.pack(side="bottom")
    app = SplashScreen(root)
    progressbar.start()
    
    # menutup window setelah 5 detik
    root.after(5000, root.destroy)  #6010
    root.mainloop()

root = Tk()
splash(root)
#threading.Thread(target=splash, args=(root,)).start()

import csv
import time
#import modeloFONAG21
#import modeloFONAG21light
#import arcpy
#from arcpy.sa import *
#from arcpy import env
from tkFileDialog import asksaveasfilename
from tkFileDialog import asksaveasfile
from pyexcel import merge_all_to_a_book

# Check out the ArcGIS Spatial Analyst extension license
#arcpy.CheckOutExtension('Spatial')
# Check out the ArcGIS Geostatistical Analyst extension license
#arcpy.CheckOutExtension('GeoStats')
# Permitir sobreescritura de archivos
#env.overwriteOutput = True

#fonag = modeloFONAG21.modelinit()
#fonaglight = modeloFONAG21light.modelinit()

root = Tk()
root.geometry('1100x780+0+0')
root.title('Modelo FONAG')
nbfonag = ttk.Notebook(root)
pgmodel = ttk.Frame(nbfonag)

canvas = Canvas(pgmodel, width=1100, height=780)
canvas.pack(expand=YES, fill=BOTH)
canvas.create_rectangle(600, 150, 1075, 370, fill='')
canvas.create_rectangle(600, 380, 1075, 735, fill='')

typecsv = [('CSV Files', '*.csv')]
typetif = [('Raster Files', '*.tif')]
typeshp = [('Shapes Files', '*.shp')]
typetxt = [('Text Files', '*.txt')]
typemask = [('Shapes Files', '*.shp'), ('Raster Files', '*.tif')]

img = Image.open('%s/img/openfile.png'%path)
img = img.resize((20, 20), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)

imgi = Image.open('%s/img/openfile.png'%path)
imgi = imgi.resize((40, 40), Image.ANTIALIAS)
imgi = ImageTk.PhotoImage(imgi)

imgf = Image.open('%s/img/openfolder.png'%path)
imgf = imgf.resize((20, 20), Image.ANTIALIAS)
imgf = ImageTk.PhotoImage(imgf)

imgp = Image.open('%s/img/play.png'%path)
imgp = imgp.resize((40, 40), Image.ANTIALIAS)
imgp = ImageTk.PhotoImage(imgp)

imgps = Image.open('%s/img/process.png'%path)
imgps = imgps.resize((40, 40), Image.ANTIALIAS)
imgps = ImageTk.PhotoImage(imgps)

imgs = Image.open('%s/img/stop.png'%path)
imgs = imgs.resize((40, 40), Image.ANTIALIAS)
imgs = ImageTk.PhotoImage(imgs)

imge = Image.open('%s/img/export.png'%path)
imge = imge.resize((40, 40), Image.ANTIALIAS)
imge = ImageTk.PhotoImage(imge)

imgpo = Image.open('%s/img/process.png'%path)
imgpo = imgpo.resize((40, 40), Image.ANTIALIAS)
imgpo = ImageTk.PhotoImage(imgpo)

imgl = Image.open('%s/img/limpiar.png'%path)
imgl = imgl.resize((40, 40), Image.ANTIALIAS)
imgl = ImageTk.PhotoImage(imgl)

imgc = Image.open('%s/img/calib.png'%path)
imgc = imgc.resize((40, 40), Image.ANTIALIAS)
imgc = ImageTk.PhotoImage(imgc)

imgo = Image.open('%s/img/of.png'%path)
imgo = imgo.resize((40, 40), Image.ANTIALIAS)
imgo = ImageTk.PhotoImage(imgo)

imgse = Image.open('%s/img/sensi.png'%path)
imgse = imgse.resize((40, 40), Image.ANTIALIAS)
imgse = ImageTk.PhotoImage(imgse)

imgeh = Image.open('%s/img/estres.png'%path)
imgeh = imgeh.resize((40, 40), Image.ANTIALIAS)
imgeh = ImageTk.PhotoImage(imgeh)

logo = Image.open('%s/img/logo.png'%path)
logo = logo.resize((130, 130), Image.ANTIALIAS)
logo = ImageTk.PhotoImage(logo)

panel = Label(pgmodel, image = logo)
panel.pack(side = 'bottom', fill = 'both', expand = 'yes')
panel.place(x=10,y=10)

#ejemod = Label(pgmodel, image = imgp)
#ejemod.pack(side = 'bottom', fill = 'both', expand = 'yes')
#ejemod.place(x=610,y=160)

def condlight():
    if chklight.get():
        light = True
    else:
        light = False

    return light

chklight = IntVar()

tejmod = Label(pgmodel, text = 'Ejecución por módulos')
tejmod.pack(side = 'bottom', fill = 'both', expand = 'yes')
tejmod.place(x=620,y=165)
tejmod.configure(font='helvetica 15')

bckbtncont = Checkbutton(pgmodel, text='Light', variable=chklight)
bckbtncont.pack(side=LEFT)
bckbtncont.place(x=910,y=165)
bckbtncont.configure(font='helvetica 15')

btnexp = Button(pgmodel, text='Exportar', image=imge, command=lambda:export_up_xls())
btnexp.pack(side=LEFT,padx=70, pady=20)
btnexp.place(x=993,y=165)

btnterreno = Button(pgmodel, text='1. Terreno',command=lambda:terreno(),  height = 1, width = 20)
btnterreno.pack(side=LEFT, padx=70, pady=20)
btnterreno.place(x=620,y=210)
btnterreno.configure(font='helvetica 12')

btnagua = Button(pgmodel, text='2. Usos de Agua',command=lambda:usoagua(),  height = 1, width = 20)
btnagua.pack(side=LEFT, padx=70, pady=20)
btnagua.place(x=620,y=250)
btnagua.configure(font='helvetica 12')

btnsuelo = Button(pgmodel, text='3. Usos de Suelo',command=lambda:usosuelo(),  height = 1, width = 20)
btnsuelo.pack(side=LEFT, padx=70, pady=20)
btnsuelo.place(x=620,y=290)
btnsuelo.configure(font='helvetica 12')

btncoef = Button(pgmodel, text='4. Coeficientes',command=lambda:coeficiente(),  height = 1, width = 20)
btncoef.pack(side=LEFT, padx=70, pady=20)
btncoef.place(x=620,y=330)
btncoef.configure(font='helvetica 12')

btnbalance = Button(pgmodel, text='5. Balance Hídrico',command=lambda:balance(),  height = 1, width = 20)
btnbalance.pack(side=LEFT, padx=70, pady=20)
btnbalance.place(x=850,y=250)
btnbalance.configure(font='helvetica 12')

btnestres = Button(pgmodel, text='6. Estrés Hídrico',command=lambda:estres(),  height = 1, width = 20)
btnestres.pack(side=LEFT, padx=70, pady=20)
btnestres.place(x=850,y=290)
btnestres.configure(font='helvetica 12')

btnestres = Button(pgmodel, text='7. Postproceso',command=lambda:estres(),  height = 1, width = 20)
btnestres.pack(side=LEFT, padx=70, pady=20)
btnestres.place(x=850,y=330)
btnestres.configure(font='helvetica 12')


### calibración por pasos
#ejemod = Label(pgmodel, image = imgc)
#ejemod.pack(side = 'bottom', fill = 'both', expand = 'yes')
#ejemod.place(x=610,y=390)

tejmod = Label(pgmodel, text = 'Calibración y análisis de sensibilidad')
tejmod.pack(side = 'bottom', fill = 'both', expand = 'yes')
tejmod.place(x=620,y=395)
tejmod.configure(font='helvetica 15')

lblsim = Label(pgmodel, text = 'Número de simulaciones')
lblsim.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblsim.place(x=620,y=443)
lblsim.configure(font='helvetica 10')

txtsim = Text(pgmodel, height=1, width=10)
txtsim.pack(side=LEFT)
txtsim.place(x=790,y=440)
txtsim.insert(END, '1000')
def cond():
    E_cond = []
    if chkNSE.get():
        E_cond.append(True)
    else:
        E_cond.append(False)
    if chkRMSE.get():
        E_cond.append(True)
    else:
        E_cond.append(False)
    if chkRSR.get():
        E_cond.append(True)
    else:
        E_cond.append(False)
    if chkPBIAS.get():
        E_cond.append(True)
    else:
        E_cond.append(False)
    if chkKGE.get():
        E_cond.append(True)
    else:
        E_cond.append(False)
    if chkcont.get():
        cont = True
    else:
        cont = False
    return cont, E_cond

def umbral():
    res = [float(txtumbral1.get('1.0',END)[:-1]),
           float(txtumbral2.get('1.0',END)[:-1]),
           float(txtumbral3.get('1.0',END)[:-1]),
           float(txtumbral4.get('1.0',END)[:-1]),
           float(txtumbral5.get('1.0',END)[:-1]),
           1,]
    return res

chkNSE = IntVar()
chkRMSE = IntVar()
chkRSR = IntVar()
chkPBIAS = IntVar()
chkKGE = IntVar()
chkcont = IntVar()

bckbtncont = Checkbutton(pgmodel, text='Contaminantes', variable=chkcont)
bckbtncont.pack(side=LEFT)
bckbtncont.place(x=900,y=440)
bckbtncont.configure(font='helvetica 10')

btnexp2 = Button(pgmodel, text='Exportar', image=imge, command=lambda:export_xls())
btnexp2.pack(side=LEFT, padx=70, pady=20)
btnexp2.place(x=993,y=395)

bckbtnnse = Checkbutton(pgmodel, text='NSE', variable=chkNSE)
bckbtnnse.pack(side=LEFT)
bckbtnnse.place(x=620,y=470)
bckbtnnse.configure(font='helvetica 15')
bckbtnnse.select()

bckbtnrmse = Checkbutton(pgmodel, text='RMSE', variable=chkRMSE)
bckbtnrmse.pack(side=LEFT)
bckbtnrmse.place(x=690,y=470)
bckbtnrmse.configure(font='helvetica 15')

bckbtnrsr = Checkbutton(pgmodel, text='RSR', variable=chkRSR)
bckbtnrsr.pack(side=LEFT)
bckbtnrsr.place(x=780,y=470)
bckbtnrsr.configure(font='helvetica 15')
bckbtnrsr.select()

bckbtnpbias = Checkbutton(pgmodel, text='PBIAS', variable=chkPBIAS)
bckbtnpbias.pack(side=LEFT)
bckbtnpbias.place(x=855,y=470)
bckbtnpbias.configure(font='helvetica 15')
bckbtnpbias.select()

bckbtnkge = Checkbutton(pgmodel, text='KGE', variable=chkKGE)
bckbtnkge.pack(side=LEFT)
bckbtnkge.place(x=950,y=470)
bckbtnkge.configure(font='helvetica 15')

txtumbral1 = Text(pgmodel, height=1, width=5)
txtumbral1.pack(side=LEFT)
txtumbral1.place(x=640,y=505)
txtumbral1.insert(END, '0.60')

txtumbral2 = Text(pgmodel, height=1, width=5)
txtumbral2.pack(side=LEFT)
txtumbral2.place(x=710,y=505)
txtumbral2.insert(END, '1.00')

txtumbral3 = Text(pgmodel, height=1, width=5)
txtumbral3.pack(side=LEFT)
txtumbral3.place(x=800,y=505)
txtumbral3.insert(END, '0.70')

txtumbral4 = Text(pgmodel, height=1, width=5)
txtumbral4.pack(side=LEFT)
txtumbral4.place(x=875,y=505)
txtumbral4.insert(END, '25')

txtumbral5 = Text(pgmodel, height=1, width=5)
txtumbral5.pack(side=LEFT)
txtumbral5.place(x=970,y=505)
txtumbral5.insert(END, '0.60')


#calc = Checkbar(pgmodel, ['NSE', 'RMSE', 'RSR', 'PBIAS','KGE'])
#lng.pack(side=TOP,  fill=X)
#lng.config(relief=GROOVE, bd=2)

btnconf = Button(pgmodel, text='1. Configuración',command=lambda:configuracion(),  height = 1, width = 20)
btnconf.pack(side=LEFT, padx=70, pady=20)
btnconf.place(x=620,y=535)
btnconf.configure(font='helvetica 12')

btnagua = Button(pgmodel, text='2. Datos de Clima',command=lambda:clima(),  height = 1, width = 20)
btnagua.pack(side=LEFT, padx=70, pady=20)
btnagua.place(x=620,y=575)
btnagua.configure(font='helvetica 12')

btnsuelo = Button(pgmodel, text='3. Muestreo de Coef.',command=lambda:muescoef(),  height = 1, width = 20)
btnsuelo.pack(side=LEFT, padx=70, pady=20)
btnsuelo.place(x=620,y=615)
btnsuelo.configure(font='helvetica 12')

btncoef = Button(pgmodel, text='4. Modelo de Caudal',command=lambda:modcaud(),  height = 1, width = 20)
btncoef.pack(side=LEFT, padx=70, pady=20)
btncoef.place(x=620,y=655)
btncoef.configure(font='helvetica 12')

btnbalance = Button(pgmodel, text='5. Muestreo de Cont.',command=lambda:muescont(),  height = 1, width = 20)
btnbalance.pack(side=LEFT, padx=70, pady=20)
btnbalance.place(x=620,y=695)
btnbalance.configure(font='helvetica 12')

btnestres = Button(pgmodel, text='6. Modelo de Cont.',command=lambda:modcont(),  height = 1, width = 20)
btnestres.pack(side=LEFT, padx=70, pady=20)
btnestres.place(x=850,y=535)
btnestres.configure(font='helvetica 12')

btnestres = Button(pgmodel, text='7. Sensibilidad Regional.',command=lambda:senreg(),  height = 1, width = 20)
btnestres.pack(side=LEFT, padx=70, pady=20)
btnestres.place(x=850,y=575)
btnestres.configure(font='helvetica 12')

btnestres = Button(pgmodel, text='8. Sensibilidad OF.',command=lambda:senregof(),  height = 1, width = 20)
btnestres.pack(side=LEFT, padx=70, pady=20)
btnestres.place(x=850,y=615)
btnestres.configure(font='helvetica 12')

btnestres = Button(pgmodel, text='9. Sensibilidad PAWN.',command=lambda:senpawn(),  height = 1, width = 20)
btnestres.pack(side=LEFT, padx=70, pady=20)
btnestres.place(x=850,y=655)
btnestres.configure(font='helvetica 12')

btnestres = Button(pgmodel, text='10. Sensibilidad PAWN OF.',command=lambda:senpawnof(),  height = 1, width = 20)
btnestres.pack(side=LEFT, padx=70, pady=20)
btnestres.place(x=850,y=695)
btnestres.configure(font='helvetica 12')
###fin calibracion por pasos

title = Label(pgmodel, text = 'Modelo Hidrológico FONAG 2.1')
title.pack(side = 'bottom', fill = 'both', expand = 'yes')
title.place(x=180,y=25)
title.configure(font='helvetica 20')

btnexec = Button(pgmodel, text='Ejecutar', image=imgp,command=lambda:run_model())
btnexec.pack(side=LEFT, padx=70, pady=20)
btnexec.place(x=516,y=80)

btninput = Button(pgmodel, text='Inputs', image=imgi, command=lambda:load_inputs())
btninput.pack(side=LEFT, padx=70, pady=20)
btninput.place(x=186,y=80)

btncalib = Button(pgmodel, text='Calibrar', image=imgc, command=lambda:calibrar())
btncalib.pack(side=LEFT, padx=70, pady=20)
btncalib.place(x=296,y=80)

btnpost = Button(pgmodel, text='PostProceso', image=imgpo, command=lambda:postprocess())
btnpost.pack(side=LEFT, padx=70, pady=20)
btnpost.place(x=736,y=80)

btnsensi = Button(pgmodel, text='Sensibilidad', image=imgse, command=lambda:sensibilidad())
btnsensi.pack(side=LEFT, padx=70, pady=20)
btnsensi.place(x=406,y=80)

btnclean = Button(pgmodel, text='Limpiar', image=imgl, command=lambda:clean_txt())
btnclean.pack(side=LEFT, padx=70, pady=20)
btnclean.place(x=846,y=80)

btnestres = Button(pgmodel, text='Estres', image=imgeh, command=lambda:run_estres())
btnestres.pack(side=LEFT, padx=70, pady=20)
btnestres.place(x=626,y=80)

btnexit = Button(pgmodel, text='Salir', image=imgs, command=pgmodel.quit)
btnexit.pack(side=LEFT, padx=70, pady=20)
btnexit.place(x=993,y=80)

inputs = {'elevation': '',
          'mask': '',
          'vmask': '',
          'demand': '',
          'tdemand': '',
          'rland': '',
          'tland': '',
          'tcoef': '',
          'tfactor': '',
          'cnt': '',
          'tcnt': '',
          'tdates': '',
          'rain': '',
          'temp': '',
          'evap': '',
          'vcoord': '',
          'outputs': '',
          'outputs': '',
          'maxmin':'',
          'aforo':'',
          'obs':''}

def generarinputs():
    global inputs
    csvfile = open('t_inputs.csv', 'wb')
    field = ['elevation','mask','vmask','demand','tdemand','rland','tland','tcoef','tfactor','cnt','tcnt','tdates','rain','temp','evap','vcoord','outputs','maxmin','aforo','obs']
    writefile = csv.DictWriter(csvfile,field)
    writefile.writeheader()
    writefile.writerow(inputs)
    csvfile.close()
    try:
        os.remove('%s/modeloFONAG/inputs/t_inputs.csv' % path)
    except OSError as error:
        print(error)
        print('No existe archivo t_inputs.csv anterior. Avanzar.')
    os.rename('t_inputs.csv', '%s/modeloFONAG/inputs/t_inputs.csv' % path)

def configuracion():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_cal_FONAG21 as wcf
        cont, E_cond = cond()
        wcf.configuracion(path,int(txtsim.get('1.0',END)[:-1]),E_cond,cont)

def clima():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_cal_FONAG21 as wcf
        cont, E_cond = cond()
        try:
            wcf.clima(path, int(txtsim.get('1.0', END)[:-1]), E_cond, cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Debe ejecutar el paso 1. Configuración')
            
def muescoef():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_cal_FONAG21 as wcf
        cont, E_cond = cond()
        try:
            wcf.muescoef(path,int(txtsim.get('1.0',END)[:-1]),E_cond,cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Debe ejecutar el paso 2. clima')

def modcaud():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_cal_FONAG21 as wcf
        cont, E_cond = cond()
        try:
            wcf.modcaud(path,int(txtsim.get('1.0',END)[:-1]),E_cond,cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Debe ejecutar el paso 2. clima y/o paso 3 Mestreo de Coef')
            
def muescont():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_cal_FONAG21 as wcf
        cont, E_cond = cond()
        if cont:
            try:
                wcf.muescont(path,int(txtsim.get('1.0',END)[:-1]),E_cond,cont)
            except RuntimeError:
                tkMessageBox.showinfo('Error', 'Debe ejecutar el paso 2. Clima')

def modcont():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_cal_FONAG21 as wcf
        cont, E_cond = cond()
        if cont:
            try:
                wcf.modcont(path,int(txtsim.get('1.0',END)[:-1]),E_cond,cont)
            except RuntimeError:
                tkMessageBox.showinfo('Error', 'Debe ejecutar el paso 2. clima y/o paso 5 Muestreo de Contaminantes')

def cdfrsa():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafcdfrsa(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def smvd():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafsmvd(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def cdfrsaof():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafcdfrsaof(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def smvdof():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafsmvdof(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def cdfpawn():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafcdfpawn(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def spawn():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafspawn(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def dpawn():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafdpawn(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')


def cdfpawnof():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafcdfpawnof(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def spawnof():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafspawnof(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def dpawnof():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafdpawnof(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def gep():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafep(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def gst():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        #cont, E_cond = cond()
        try:
            gf.grafst(path)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')
def gepc():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        cont, E_cond = cond()
        try:
            gf.grafepc(path,cont=cont,N=1000)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def gstc():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        cont, E_cond = cond()
        try:
            gf.grafstc(path,cont=cont,N=1000)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')
            
def gnse():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        cont, E_cond = cond()
        try:
            gf.grafFunObj(path, E_cond_mod=[True,False,False,False,False,False],N=1000, cont=cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def grmse():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        cont, E_cond = cond()
        try:
            gf.grafFunObj(path, E_cond_mod=[False,True,False,False,False,False],N=1000, cont=cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def grsr():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        cont, E_cond = cond()
        try:
            gf.grafFunObj(path, E_cond_mod=[False,False,True,False,False,False],N=1000, cont=cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def gpbias():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        cont, E_cond = cond()
        try:
            gf.grafFunObj(path, E_cond_mod=[False,False,False,True,False,False],N=1000, cont=cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def gkge():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        cont, E_cond = cond()
        try:
            gf.grafFunObj(path, E_cond_mod=[False,False,False,False,True,False],N=1000, cont=cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def gof():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        cont, E_cond = cond()
        try:
            gf.grafFunObj(path, E_cond_mod=[False,False,False,False,False,True],N=1000, cont=cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')
            
            
def senreg():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_sensi_FONAG21 as wsf
        cont, E_cond = cond()
        E_umbral = umbral()
        try:
            wsf.rsa(path,E_cond=E_cond,cont=cont,E_umbral=E_umbral)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad regional')

def senregof():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_sensi_FONAG21 as wsf
        cont, E_cond = cond()
        try:
            wsf.rsa_OF(path,cont=cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'Sensibilidad Regional OF')

def senpawn():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_sensi_FONAG21 as wsf
        cont, E_cond = cond()
        try:
            wsf.pawn(path,cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'PANW')

def senpawnof():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_sensi_FONAG21 as wsf
        cont, E_cond = cond()
        try:
            wsf.pawn_OF(path,cont=cont)
        except RuntimeError:
            tkMessageBox.showinfo('Error', 'PWN OF')
                
def calibrar():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_cal_iter_FONAG21 as wcif
        cont, E_cond = cond()
        wcif.calibrar(path,int(txtsim.get('1.0',END)[:-1]),E_cond,cont)

def graflineal(t,output):
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        gf.grafser(path,t,output)

def grafmensual(t,output):
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import GRAFONAG as gf
        gf.grafmensual(path,t)
        
def postprocess():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_post_FONAG21 as wpf
        wpf.percentiles(path, ['qds','prc','qnt'])
 
def sensibilidad():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import workflow_sensi_FONAG21 as wsf
        cont, E_cond = cond()
        wsf.rsa(path,E_cond=E_cond,cont=cont)
        wsf.rsa_OF(path,cont=cont)
        wsf.pawn(path,cont)
        wsf.pawn_OF(path,cont=cont)
        
def validar(inputs):
    bol = 0
    load_inputstxt()
    for j in inputs:
        if not inputs[j]:
            bol = 1
    return bol

def terreno():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import modeloFONAG21
        fonag = modeloFONAG21.modelinit()
        fonag.terreno(path)
    
def usoagua():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import modeloFONAG21
        fonag = modeloFONAG21.modelinit()
        fonag.usos_agua(path)

def usosuelo():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import modeloFONAG21
        fonag = modeloFONAG21.modelinit()
        fonag.usos_suelo(path)

def coeficiente():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        import modeloFONAG21
        fonag = modeloFONAG21.modelinit()
        fonag.coeficientes(path)

def balance():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        start_balance = time.time()
        light = condlight()
        if light:
            print('Modelo light')
            import modeloFONAG21light
            fonaglight = modeloFONAG21light.modelinit()
            fonaglight.balance(path)
        else:
            import modeloFONAG21
            fonag = modeloFONAG21.modelinit()
            fonag.balance(path)
        elapsed_time = (time.time() - start_balance) / 60
        print('El proceso de balance hidrico para caudal tomo %s minutos.' % elapsed_time)

def estres():
    global path
    global inputs
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        start_estres = time.time()
        light = condlight()
        if light:
            print('No se puede ejecutar el estres hidrico en modo light.')
            #import modeloFONAG21light
            #fonaglight = modeloFONAG21light.modelinit()
            # fonaglight.estres(path)
        else:
            import modeloFONAG21
            fonag = modeloFONAG21.modelinit()
            fonag.estres(path)
        elapsed_time = (time.time() - start_estres) / 60
        print('El proceso de estres hidrico tomo %s minutos.' % elapsed_time)

def enable_txt():
    txtrdem.configure(state='normal')
    txtmask.configure(state='normal')
    txtvmask.configure(state='normal')
    txtdemand.configure(state='normal')
    txttdemand.configure(state='normal')
    txtrland.configure(state='normal')
    txttland.configure(state='normal')
    txttcoef.configure(state='normal')
    txttfactor.configure(state='normal')
    txtcnt.configure(state='normal')
    txttcnt.configure(state='normal')
    txttdates.configure(state='normal')
    txtrain.configure(state='normal')
    txttemp.configure(state='normal')
    txtevap.configure(state='normal')
    txtvcoord.configure(state='normal')
    txtoutputs.configure(state='normal')

def load_inputstxt():
    global inputs
    print(txtrdem.get('1.0',END)[:-1])
    inputs = {'elevation': txtrdem.get('1.0',END)[:-1],
              'mask': txtmask.get('1.0',END)[:-1],
              'vmask': txtvmask.get('1.0',END)[:-1],
              'demand': txtdemand.get('1.0',END)[:-1],
              'tdemand': txttdemand.get('1.0',END)[:-1],
              'rland': txtrland.get('1.0',END)[:-1],
              'tland': txttland.get('1.0',END)[:-1],
              'tcoef': txttcoef.get('1.0',END)[:-1],
              'tfactor': txttfactor.get('1.0',END)[:-1],
              'cnt': txtcnt.get('1.0',END)[:-1],
              'tcnt': txttcnt.get('1.0',END)[:-1],
              'tdates': txttdates.get('1.0',END)[:-1],
              'rain': txtrain.get('1.0',END)[:-1],
              'temp': txttemp.get('1.0',END)[:-1],
              'evap': txtevap.get('1.0',END)[:-1],
              'vcoord': txtvcoord.get('1.0',END)[:-1],
              'outputs': txtoutputs.get('1.0',END)[:-1],
              'maxmin': txtmaxmin.get('1.0',END)[:-1],
              'aforo': txtaforo.get('1.0',END)[:-1],
              'obs': txtobs.get('1.0',END)[:-1]}

def clean_txt():
    global inputs
    #enable_txt()
    txtrdem.delete('1.0', END)
    txtmask.delete('1.0', END)
    txtvmask.delete('1.0', END)
    txtdemand.delete('1.0', END)
    txttdemand.delete('1.0', END)
    txtrland.delete('1.0', END)
    txttland.delete('1.0', END)
    txttcoef.delete('1.0', END)
    txttfactor.delete('1.0', END)
    txtcnt.delete('1.0', END)
    txttcnt.delete('1.0', END)
    txttdates.delete('1.0', END)
    txtrain.delete('1.0', END)
    txttemp.delete('1.0', END)
    txtevap.delete('1.0', END)
    txtvcoord.delete('1.0', END)
    txtoutputs.delete('1.0', END)
    txtmaxmin.delete('1.0', END)
    txtaforo.delete('1.0', END)
    txtobs.delete('1.0', END)
    inputs = {'elevation': '',
              'mask': '',
              'vmask': '',
              'demand': '',
              'tdemand': '',
              'rland': '',
              'tland': '',
              'tcoef': '',
              'tfactor': '',
              'cnt': '',
              'tcnt': '',
              'tdates': '',
              'rain': '',
              'temp': '',
              'evap': '',
              'vcoord': '',
              'outputs': '',
              'maxmin':'',
              'aforo':'',
              'obs':''}
    
def load_inputs():
    global inputs
    #enable_txt()
    file = askopenfiles(mode ='r', filetypes = typecsv,title = 'Cargar inputs csv')
    if file is not None and len(file) > 0:
        file = file[0].read()
        file = file.split('\n')
        file = file[1].split(',')
        clean_txt()
        txtrdem.insert(END, file[0][file[0].rfind('/')+1:])
        txtmask.insert(END, file[1][file[1].rfind('/')+1:])
        txtvmask.insert(END, file[2][file[2].rfind('/')+1:])
        txtdemand.insert(END, file[3][file[3].rfind('/')+1:])
        txttdemand.insert(END, file[4][file[4].rfind('/')+1:])
        txtrland.insert(END, file[5][file[5].rfind('/')+1:])
        txttland.insert(END, file[6][file[6].rfind('/')+1:])
        txttcoef.insert(END, file[7][file[7].rfind('/')+1:])
        txttfactor.insert(END, file[8][file[8].rfind('/')+1:])
        txtcnt.insert(END, file[9][file[9].rfind('/')+1:])
        txttcnt.insert(END, file[10][file[10].rfind('/')+1:])
        txttdates.insert(END, file[11][file[11].rfind('/')+1:])
        txtrain.insert(END, file[12][file[12].rfind('/')+1:])
        txttemp.insert(END, file[13][file[13].rfind('/')+1:])
        txtevap.insert(END, file[14][file[14].rfind('/')+1:])
        txtvcoord.insert(END, file[15][file[15].rfind('/')+1:])
        txtoutputs.insert(END, file[16][file[16].rfind('/')+1:])
        txtmaxmin.insert(END, file[17][file[17].rfind('/')+1:])
        txtaforo.insert(END, file[18][file[18].rfind('/')+1:])
        txtobs.insert(END, file[19][file[19].rfind('/')+1:])
        inputs = {'elevation': file[0][file[0].rfind('/')+1:],
                  'mask': file[1][file[1].rfind('/')+1:],
                  'vmask': file[2][file[2].rfind('/')+1:],
                  'demand': file[3][file[3].rfind('/')+1:],
                  'tdemand': file[4][file[4].rfind('/')+1:],
                  'rland': file[5][file[5].rfind('/')+1:],
                  'tland': file[6][file[6].rfind('/')+1:],
                  'tcoef': file[7][file[7].rfind('/')+1:],
                  'tfactor': file[8][file[8].rfind('/')+1:],
                  'cnt': file[9][file[9].rfind('/')+1:],
                  'tcnt': file[10][file[10].rfind('/')+1:],
                  'tdates': file[11][file[11].rfind('/')+1:],
                  'rain': file[12][file[12].rfind('/')+1:],
                  'temp': file[13][file[13].rfind('/')+1:],
                  'evap': file[14][file[14].rfind('/')+1:],
                  'vcoord': file[15][file[15].rfind('/')+1:],
                  'outputs': file[16][file[16].rfind('/')+1:],
                  'maxmin': file[17][file[17].rfind('/')+1:],
                  'aforo': file[18][file[18].rfind('/')+1:],
                  'obs': file[19][file[19].rfind('/')+1:]}
        #disable_txt()

def export_xls():
    # Ejecutar modelo
    global inputs
    global path
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        f = asksaveasfile(mode='w', defaultextension=".xls")
        if f is None:
            return
        print(f)
        import GRAFONAG as gf
        gf.unirsensi(path)
        merge_all_to_a_book([r'%s\modeloFONAG\%s\calibracion\sortedX.csv'%(path,inputs['outputs']),
                             r'%s\modeloFONAG\%s\calibracion\sortedY.csv'%(path,inputs['outputs']),
                             r'%s\modeloFONAG\%s\calibracion\sortedE.csv'%(path,inputs['outputs']),
                             r'%s\modeloFONAG\%s\calibracion\var_sensibilidad.csv'%(path,inputs['outputs'])],
                            f.name)
        print("El archivo se exporto con exito")

def export_up_xls():
    # Ejecutar modelo
    global inputs
    global path
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        f = asksaveasfile(mode='w', defaultextension=".xls")
        if f is None:
            return
        print(f)
        #import GRAFONAG as gf
        #gf.unirsensi(path)
        estres = ['Sin estrés hídrico','Estrés hídrico ligero','Estrés hídrico moderado','Estrés hídrico alto','Estrés hídrico severo']
        try:
            outestres = open(r'%s\modeloFONAG\%s\tables\t_out_data_estres.csv' % (path, inputs['outputs']), 'r')
            dictestres = csv.DictReader(outestres, delimiter=';')
            label = ['Punto','Nivel Estrés','Valor']
            with open(r'%s\modeloFONAG\%s\tables\t_out_estres_all.csv' %(path, inputs['outputs']), 'wb') as myfile:
                wr = csv.writer(myfile)
                wr.writerow(label)
                for est in dictestres:
                    if est.get('NOMBRE'):
                        nom = est['NOMBRE']
                    elif est.get('Nombre'):
                        nom = est['Nombre']
                    else:
                        nom = est['name']
                    wr.writerow([nom,estres[int(est['estres_pun'])],est['estres_pun']])
                
            estres_OutTable = r'%s\modeloFONAG\%s\tables' % (path, inputs['outputs']) + r'\t_tab_estres.dbf'
            estres_table = dbfread.DBF(estres_OutTable, load=True)
            tot = 0
            label = estres_table.field_names
            label.insert(0,'Nivel Estrés')
            label.append('Porcentaje')
            print(label)
            for i in estres_table.records:
                tot += i[estres_table.field_names[2]]
            with open(r'%s\modeloFONAG\%s\tables\t_estres_all.csv' %(path, inputs['outputs']), 'wb') as myfile:
                wr = csv.writer(myfile)
                wr.writerow(['Nivel Estrés','Valor','Celdas','Porcentaje'])
                for i in estres_table.records:
                    wr.writerow([estres[i[estres_table.field_names[1]]],i[estres_table.field_names[1]],i[estres_table.field_names[2]],(i[estres_table.field_names[2]]*100)/tot])
        
            merge_all_to_a_book([r'%s\modeloFONAG\%s\postproceso\series_prc.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\series_qnt.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\series_qds.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\percentil_prc.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\percentil_qnt.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\percentil_qds.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\promedio_out_prc.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\promedio_out_qnt.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\promedio_out_qds.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\tables\t_estres_all.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\tables\t_out_estres_all.csv' %(path, inputs['outputs'])],
                                f.name)
        except:
            merge_all_to_a_book([r'%s\modeloFONAG\%s\postproceso\series_prc.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\series_qnt.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\series_qds.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\percentil_prc.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\percentil_qnt.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\percentil_qds.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\promedio_out_prc.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\promedio_out_qnt.csv'%(path,inputs['outputs']),
                                 r'%s\modeloFONAG\%s\postproceso\promedio_out_qds.csv'%(path,inputs['outputs'])],
                                f.name)
        print("El archivo se exporto con exito")
        
def run_model():
    # Ejecutar modelo
    global inputs
    global path
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        start = time.time()
        light = condlight()
        if light:
            print('Modelo FONAG 2.1 light')
            import modeloFONAG21light
            fonaglight = modeloFONAG21light.modelinit()
            # print('Paso 1: Analisis de terreno')
            # Analisis de terreno
            fonaglight.terreno(path)

            # print('Paso 2: Usos de agua')
            # Usos de agua
            fonaglight.usos_agua(path)

            # print('Paso 3: Usos de suelo')
            # Usos de suelo
            fonaglight.usos_suelo(path)

            # print('Paso 4: Coeficientes de hidrozonas')
            # Coeficientes de hidrozonas
            fonaglight.coeficientes(path)

            # print('Paso 5: Balance hidrico')
            # Balance hidrico
            fonaglight.balance(path)

            # print('Paso 6: Estres hidrico')
            # Estres hidrico
            # fonaglight.estres(path)

        else:
            print('Modelo FONAG 2.1 completo')
            import modeloFONAG21
            fonag = modeloFONAG21.modelinit()
            # print('Paso 1: Analisis de terreno')
            # Analisis de terreno
            fonag.terreno(path)

            # print('Paso 2: Usos de agua')
            # Usos de agua
            fonag.usos_agua(path)

            # print('Paso 3: Usos de suelo')
            # Usos de suelo
            fonag.usos_suelo(path)

            # print('Paso 4: Coeficientes de hidrozonas')
            # Coeficientes de hidrozonas
            fonag.coeficientes(path)

            # print('Paso 5: Balance hidrico')
            # Balance hidrico
            fonag.balance(path)

            # print('Paso 6: Estres hidrico')
            # Estres hidrico
            fonag.estres(path)

        elapsed_time = (time.time() - start) / 60
        print('La corrida del modelo tomo %s minutos.' % elapsed_time)

def run_estres():
    # Ejecutar modelo
    global inputs
    global path
    bol = validar(inputs)
    if bol == 1:
        tkMessageBox.showinfo('Error', 'Debe cargar todos lo archivos y carpetas para ejecutar el modelo')
    else:
        generarinputs()
        start = time.time()
        light = condlight()
        if light:
            tkMessageBox.showinfo('Error', 'No se puede correr el estrés Hídrico cuando está activada la opción "Ligth" ')
        else:
            import modeloFONAG21
            fonag = modeloFONAG21.modelinit()
            # print('Paso 6: Estres hidrico')
            # Estres hidrico
            fonag.estres(path)
        
def open_dir(obj,title, index):
    # Funcion para carga de carpeta
    global inputs
    #enable_txt()
    dir = askdirectory(title = title)
    obj.delete('1.0', END)
    obj.insert(END, dir[dir.rfind('/')+1:])
    inputs[index] = dir[dir.rfind('/')+1:]
    #disable_txt()

def open_file(obj, title,index, types):
    # Funcion para carga de archivo csv
    global inputs
    #enable_txt()
    file = askopenfiles(mode ='r', filetypes = types,title = title)   
    if file is not None and len(file) > 0:
        file = file[0]
        obj.delete('1.0', END)
        obj.insert(END, file.name[file.name.rfind('/')+1:])
        inputs[index] = file.name[file.name.rfind('/')+1:]
        #disable_txt()
   
#construir GUI#
#01Ráster de elevación#
lblrdem = Label(pgmodel, text='Ráster de elevación')
lblrdem.pack(side=LEFT)
lblrdem.place(x=0,y=150)
txtrdem = Text(pgmodel, height=1, width=20)
txtrdem.pack(side=LEFT)
txtrdem.place(x=350,y=150)
btnrdem = Button(pgmodel, text ='Abrir raster', image=img, command = lambda:open_file(txtrdem, 'Ráster de elevación', 'elevation', typetif))
btnrdem.pack(side=LEFT, pady = 10)
btnrdem.place(x=550,y=150)


#02Carpeta de archivos de máscara#
lblmask = Label(pgmodel, text='Carpeta de archivos de máscara')
lblmask.pack(side=LEFT)
lblmask.place(x=0,y=180)
txtmask = Text(pgmodel, height=1, width=20)
txtmask.pack(side=LEFT)
txtmask.place(x=350,y=180)
btnmask = Button(pgmodel, text ='Open', image=imgf, command = lambda:open_dir(txtmask, 'Seleccione carpeta de mascaras', 'mask'))
btnmask.pack(side=LEFT, pady = 10)
btnmask.place(x=550,y=180)

#03Archivo de máscara#
lblvmask = Label(pgmodel, text='Archivo de máscara')
lblvmask.pack(side=LEFT)
lblvmask.place(x=0,y=210)
txtvmask = Text(pgmodel, height=1, width=20)
txtvmask.pack(side=LEFT)
txtvmask.place(x=350,y=210)
btnvmask = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txtvmask, 'Archivo de máscara', 'vmask', typemask))
btnvmask.pack(side=LEFT, pady = 10)
btnvmask.place(x=550,y=210)

#04Carpeta de archivos de usos de agua#
lbldemand = Label(pgmodel, text='Carpeta de archivos de usos de agua')
lbldemand.pack(side=LEFT)
lbldemand.place(x=0,y=240)
txtdemand = Text(pgmodel, height=1, width=20)
txtdemand.pack(side=LEFT)
txtdemand.place(x=350,y=240)
btndemand = Button(pgmodel, text ='Open', image=imgf, command = lambda:open_dir(txtdemand, 'Carpeta de archivos de usos de agua', 'demand'))
btndemand.pack(side=LEFT, pady = 10)
btndemand.place(x=550,y=240)

#05Tabla de usos de agua#
lbltdemand = Label(pgmodel, text='Tabla de usos de agua')
lbltdemand.pack(side=LEFT)
lbltdemand.place(x=0,y=270)
txttdemand = Text(pgmodel, height=1, width=20)
txttdemand.pack(side=LEFT)
txttdemand.place(x=350,y=270)
btntdemand = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txttdemand, 'Tabla de usos de agua', 'tdemand',typecsv))
btntdemand.pack(side=LEFT, pady = 10)
btntdemand.place(x=550,y=270)

#06Ráster de usos de suelo#
lblrland = Label(pgmodel, text='Ráster de usos de suelo')
lblrland.pack(side=LEFT)
lblrland.place(x=0,y=300)
txtrland = Text(pgmodel, height=1, width=20)
txtrland.pack(side=LEFT)
txtrland.place(x=350,y=300)
btnrland = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txtrland, 'Ráster de usos de suelo', 'rland', typetif))
btnrland.pack(side=LEFT, pady = 10)
btnrland.place(x=550,y=300)

#07Tabla de usos de suelo#
lbltland = Label(pgmodel, text='Tabla de usos de suelo')
lbltland.pack(side=LEFT)
lbltland.place(x=0,y=330)
txttland = Text(pgmodel, height=1, width=20)
txttland.pack(side=LEFT)
txttland.place(x=350,y=330)
btntland = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txttland, 'Tabla de usos de suelo', 'tland', typecsv))
btntland.pack(side=LEFT, pady = 10)
btntland.place(x=550,y=330)

#08Tabla de coeficientes de hidrozonas#
lbltcoef = Label(pgmodel, text='Tabla de coeficientes de hidrozonas')
lbltcoef.pack(side=LEFT)
lbltcoef.place(x=0,y=360)
txttcoef = Text(pgmodel, height=1, width=20)
txttcoef.pack(side=LEFT)
txttcoef.place(x=350,y=360)
btntcoef = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txttcoef, 'Tabla de coeficientes de hidrozonas', 'tcoef', typecsv))
btntcoef.pack(side=LEFT, pady = 10)
btntcoef.place(x=550,y=360)

#09Tabla de factor de lavado de suelos H#
lbltfactor = Label(pgmodel, text='Tabla de factor de lavado de suelos H')
lbltfactor.pack(side=LEFT)
lbltfactor.place(x=0,y=390)
txttfactor = Text(pgmodel, height=1, width=20)
txttfactor.pack(side=LEFT)
txttfactor.place(x=350,y=390)
btntfactor = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txttfactor, 'Tabla de factor de lavado de suelos H', 'tfactor', typecsv))
btntfactor.pack(side=LEFT, pady = 10)
btntfactor.place(x=550,y=390)

#10Carpeta de ráster de ponderación de contaminantes#
lblcnt = Label(pgmodel, text='Carpeta de ráster de ponderación de contaminantes')
lblcnt.pack(side=LEFT)
lblcnt.place(x=0,y=420)
txtcnt = Text(pgmodel, height=1, width=20)
txtcnt.pack(side=LEFT)
txtcnt.place(x=350,y=420)
btncnt = Button(pgmodel, text ='Open', image=imgf, command = lambda:open_dir(txtcnt, 'Carpeta de ráster de ponderación de contaminantes', 'cnt'))
btncnt.pack(side=LEFT, pady = 10)
btncnt.place(x=550,y=420)

#11Tabla de contaminantes#
lbltcnt = Label(pgmodel, text='Tabla de contaminantes')
lbltcnt.pack(side=LEFT)
lbltcnt.place(x=0,y=450)
txttcnt = Text(pgmodel, height=1, width=20)
txttcnt.pack(side=LEFT)
txttcnt.place(x=350,y=450)
btntcnt = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txttcnt, 'Tabla de contaminantes', 'tcnt', typecsv))
btntcnt.pack(side=LEFT, pady = 10)
btntcnt.place(x=550,y=450)

#12Tabla de fechas de corrida#
lbltdates = Label(pgmodel, text='Tabla de fechas de corrida')
lbltdates.pack(side=LEFT)
lbltdates.place(x=0,y=480)
txttdates = Text(pgmodel, height=1, width=20)
txttdates.pack(side=LEFT)
txttdates.place(x=350,y=480)
btntdates = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txttdates, 'Tabla de fechas de corridaa', 'tdates', typecsv))
btntdates.pack(side=LEFT, pady = 10)
btntdates.place(x=550,y=480)

#13Carpeta de ráster de lluvia#
lblrain = Label(pgmodel, text='Carpeta de ráster de lluvia')
lblrain.pack(side=LEFT)
lblrain.place(x=0,y=510)
txtrain = Text(pgmodel, height=1, width=20)
txtrain.pack(side=LEFT)
txtrain.place(x=350,y=510)
btnrain = Button(pgmodel, text ='Open', image=imgf, command = lambda:open_dir(txtrain, 'Carpeta de ráster de lluvia', 'rain'))
btnrain.pack(side=LEFT, pady = 10)
btnrain.place(x=550,y=510)

#14Carpeta de ráster de temperatura#
lbltemp = Label(pgmodel, text='Carpeta de ráster de temperatura')
lbltemp.pack(side=LEFT)
lbltemp.place(x=0,y=540)
txttemp = Text(pgmodel, height=1, width=20)
txttemp.pack(side=LEFT)
txttemp.place(x=350,y=540)
btntemp = Button(pgmodel, text ='Open', image=imgf, command = lambda:open_dir(txttemp, 'Carpeta de ráster de temperatura', 'temp'))
btntemp.pack(side=LEFT, pady = 10)
btntemp.place(x=550,y=540)

#15Carpeta de ráster de evapotranspiración#
lblevap = Label(pgmodel, text='Carpeta de ráster de evapotranspiración')
lblevap.pack(side=LEFT)
lblevap.place(x=0,y=570)
txtevap = Text(pgmodel, height=1, width=20)
txtevap.pack(side=LEFT)
txtevap.place(x=350,y=570)
btnevap = Button(pgmodel, text ='Open', image=imgf, command = lambda:open_dir(txtevap, 'Carpeta de ráster de evapotranspiración', 'evap'))
btnevap.pack(side=LEFT, pady = 10)
btnevap.place(x=550,y=570)

#16Puntos de coordenadas de salida#
lblvcoord = Label(pgmodel, text='Puntos de coordenadas de salida')
lblvcoord.pack(side=LEFT)
lblvcoord.place(x=0,y=600)
txtvcoord = Text(pgmodel, height=1, width=20)
txtvcoord.pack(side=LEFT)
txtvcoord.place(x=350,y=600)
btnvcoord = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txtvcoord, 'Puntos de coordenadas de salida', 'vcoord', typeshp))
btnvcoord.pack(side=LEFT, pady = 10)
btnvcoord.place(x=550,y=600)

#17Carpeta de salidas del modelo#
lbloutputs = Label(pgmodel, text='Carpeta de salidas del modelo')
lbloutputs.pack(side=LEFT)
lbloutputs.place(x=0,y=630)
txtoutputs = Text(pgmodel, height=1, width=20)
txtoutputs.pack(side=LEFT)
txtoutputs.place(x=350,y=630)
btnoutputs = Button(pgmodel, text ='Open', image=imgf, command = lambda:open_dir(txtoutputs, 'Carpeta de salidas del modelo', 'outputs'))
btnoutputs.pack(side=LEFT, pady = 10)
btnoutputs.place(x=550,y=630)

#18Tala rangos minimos maximos#
lblmaxmin = Label(pgmodel, text='Tabla de rangos minimos y maximos')
lblmaxmin.pack(side=LEFT)
lblmaxmin.place(x=0,y=660)
txtmaxmin = Text(pgmodel, height=1, width=20)
txtmaxmin.pack(side=LEFT)
txtmaxmin.place(x=350,y=660)
btnmaxmin = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txtmaxmin, 'Tabla de rangos minimos y maximos', 'maxmin',typecsv))
btnmaxmin.pack(side=LEFT, pady = 10)
btnmaxmin.place(x=550,y=660)

#19Carpeta de salidas del modelo#
lblaforo = Label(pgmodel, text='Punto de aforo para calibración')
lblaforo.pack(side=LEFT)
lblaforo.place(x=0,y=690)
txtaforo = Text(pgmodel, height=1, width=20)
txtaforo.pack(side=LEFT)
txtaforo.place(x=350,y=690)
btnaforo = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txtaforo, 'Punto de aforo para calibración', 'aforo',typeshp))
btnaforo.pack(side=LEFT, pady = 10)
btnaforo.place(x=550,y=690)

#20Carpeta de salidas del modelo#
lblobs = Label(pgmodel, text='Archivo de datos observados')
lblobs.pack(side=LEFT)
lblobs.place(x=0,y=720)
txtobs = Text(pgmodel, height=1, width=20)
txtobs.pack(side=LEFT)
txtobs.place(x=350,y=720)
btnobs = Button(pgmodel, text ='Open', image=img, command = lambda:open_file(txtobs, 'Archivo de datos observados', 'obs',typetxt))
btnobs.pack(side=LEFT, pady = 10)
btnobs.place(x=550,y=720)

#Pestaña para resultados
pgresult = ttk.Frame(nbfonag)

canvasres = Canvas(pgresult, width=1100, height=780)
canvasres.pack(expand=YES, fill=BOTH)
canvasres.create_rectangle(20, 150, 270, 390, fill='')
canvasres.create_rectangle(290, 150, 540, 470, fill='')
canvasres.create_rectangle(560, 150, 810, 630, fill='')
canvasres.create_rectangle(830, 150, 1080, 590, fill='')

logores = Image.open('%s/img/logo.png'%path)
logores = logores.resize((130, 130), Image.ANTIALIAS)
logores = ImageTk.PhotoImage(logores)

panelres = Label(pgresult, image = logo)
panelres.pack(side = 'bottom', fill = 'both', expand = 'yes')
panelres.place(x=10,y=10)

titleres = Label(pgresult, text = 'Modelo Hidrológico FONAG 2.1')
titleres.pack(side = 'bottom', fill = 'both', expand = 'yes')
titleres.place(x=180,y=25)
titleres.configure(font='helvetica 25')

titlergraf = Label(pgresult, text = 'Interfaz Gráfica')
titlergraf.pack(side = 'bottom', fill = 'both', expand = 'yes')
titlergraf.place(x=180,y=70)
titlergraf.configure(font='helvetica 20')

#btnexportres = Button(pgresult, text='Exportar', image=imge, command=lambda:export_xls())
#btnexportres.pack(side=LEFT, padx=70, pady=20)
#btnexportres.place(x=800,y=80)

btnexitres = Button(pgresult, text='Salir', image=imgs, command=pgmodel.quit)
btnexitres.pack(side=LEFT, padx=70, pady=20)
btnexitres.place(x=1014,y=80)

#cuadro Graficos de Calibracion
lblresultcalib = Label(pgresult, image = imgc)
lblresultcalib.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblresultcalib.place(x=30,y=160)

lblresultcalibi = Label(pgresult, text = 'Calibración')
lblresultcalibi.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblresultcalibi.place(x=75,y=165)
lblresultcalibi.configure(font='helvetica 15')

btnresgep = Button(pgresult, text='Gáfico de ejes paralelos',command=lambda:gep(),  height = 1, width = 20)
btnresgep.pack(side=LEFT, padx=70, pady=20)
btnresgep.place(x=45,y=220)
btnresgep.configure(font='helvetica 11')

btnresepc = Button(pgresult, text='Ejes paralelos calibrado',command=lambda:gepc(),  height = 1, width = 20)
btnresepc.pack(side=LEFT, padx=70, pady=20)
btnresepc.place(x=45,y=260)
btnresepc.configure(font='helvetica 11')

btnresst = Button(pgresult, text='Series de tiempo',command=lambda:gst(),  height = 1, width = 20)
btnresst.pack(side=LEFT, padx=70, pady=20)
btnresst.place(x=45,y=300)
btnresst.configure(font='helvetica 11')

btnressc = Button(pgresult, text='Series calibradas',command=lambda:gstc(),  height = 1, width = 20)
btnressc.pack(side=LEFT, padx=70, pady=20)
btnressc.place(x=45,y=340)
btnressc.configure(font='helvetica 11')

#cuadro Graficos de Funciones Objetivo
lblresultof = Label(pgresult, image = imgo)
lblresultof.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblresultof.place(x=300,y=160)

lblresultfo = Label(pgresult, text = 'Funciones Objetivo')
lblresultfo.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblresultfo.place(x=345,y=165)
lblresultfo.configure(font='helvetica 15')

btnresnse = Button(pgresult, text='NSE',command=lambda:gnse(),  height = 1, width = 20)
btnresnse.pack(side=LEFT, padx=70, pady=20)
btnresnse.place(x=325,y=220)
btnresnse.configure(font='helvetica 11')

btnresrmse = Button(pgresult, text='RMSE',command=lambda:grmse(),  height = 1, width = 20)
btnresrmse.pack(side=LEFT, padx=70, pady=20)
btnresrmse.place(x=325,y=260)
btnresrmse.configure(font='helvetica 11')

btnresrsr = Button(pgresult, text='RSR',command=lambda:grsr(),  height = 1, width = 20)
btnresrsr.pack(side=LEFT, padx=70, pady=20)
btnresrsr.place(x=325,y=300)
btnresrsr.configure(font='helvetica 11')

btnrespbias = Button(pgresult, text='PBIAS',command=lambda:gpbias(),  height = 1, width = 20)
btnrespbias.pack(side=LEFT, padx=70, pady=20)
btnrespbias.place(x=325,y=340)
btnrespbias.configure(font='helvetica 11')

btnreskge = Button(pgresult, text='KGE',command=lambda:gkge(),  height = 1, width = 20)
btnreskge.pack(side=LEFT, padx=70, pady=20)
btnreskge.place(x=325,y=380)
btnreskge.configure(font='helvetica 11')

btnresfo = Button(pgresult, text='OF',command=lambda:gof(),  height = 1, width = 20)
btnresfo.pack(side=LEFT, padx=70, pady=20)
btnresfo.place(x=325,y=420)
btnresfo.configure(font='helvetica 11')


#cuadro Graficos de Analisis Sensibilidad
lblresultsensi = Label(pgresult, image = imgse)
lblresultsensi.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblresultsensi.place(x=570,y=160)

lblresultsensii = Label(pgresult, text = 'Análisis sensibilidad')
lblresultsensii.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblresultsensii.place(x=615,y=165)
lblresultsensii.configure(font='helvetica 15')

btnresdc = Button(pgresult, text='CDFs de Análisis Regional',command=lambda:cdfrsa(),  height = 1, width = 22)
btnresdc.pack(side=LEFT, padx=70, pady=20)
btnresdc.place(x=580,y=220)
btnresdc.configure(font='helvetica 11')

btnresoc = Button(pgresult, text='Sensibilidad MVD',command=lambda:smvd(),  height = 1, width = 22)
btnresoc.pack(side=LEFT, padx=70, pady=20)
btnresoc.place(x=580,y=260)
btnresoc.configure(font='helvetica 11')

btnresmvd = Button(pgresult, text='CDFs de Análisis Regional OF',command=lambda:cdfrsaof(),  height = 1, width = 22)
btnresmvd.pack(side=LEFT, padx=70, pady=20)
btnresmvd.place(x=580,y=300)
btnresmvd.configure(font='helvetica 11')

btnressp = Button(pgresult, text='Sensibilidad MVD para OF',command=lambda:smvdof(),  height = 1, width = 22)
btnressp.pack(side=LEFT, padx=70, pady=20)
btnressp.place(x=580,y=340)
btnressp.configure(font='helvetica 11')

btnrescpqm = Button(pgresult, text='CDFs de PAWN Qmedio',command=lambda:cdfpawn(),  height = 1, width = 22)
btnrescpqm.pack(side=LEFT, padx=70, pady=22)
btnrescpqm.place(x=580,y=380)
btnrescpqm.configure(font='helvetica 11')

btnresspqm = Button(pgresult, text='Sensibilidad PAWN Qmedio',command=lambda:spawn(),  height = 1, width = 22)
btnresspqm.pack(side=LEFT, padx=70, pady=20)
btnresspqm.place(x=580,y=420)
btnresspqm.configure(font='helvetica 11')

btnresdpqm = Button(pgresult, text='Dummy PAWN Qmedio',command=lambda:dpawn(),  height = 1, width = 22)
btnresdpqm.pack(side=LEFT, padx=70, pady=20)
btnresdpqm.place(x=580,y=460)
btnresdpqm.configure(font='helvetica 11')

btnrescqof = Button(pgresult, text='CDFs de PAWN para OF',command=lambda:cdfpawnof(),  height = 1, width = 22)
btnrescqof.pack(side=LEFT, padx=70, pady=20)
btnrescqof.place(x=580,y=500)
btnrescqof.configure(font='helvetica 11')

btnresspof = Button(pgresult, text='Sensibilidad PAWN para OF',command=lambda:spawnof(),  height = 1, width = 22)
btnresspof.pack(side=LEFT, padx=70, pady=20)
btnresspof.place(x=580,y=540)
btnresspof.configure(font='helvetica 11')

btnresdpof = Button(pgresult, text='Dummy PAWN para OF',command=lambda:dpawnof(),  height = 1, width = 22)
btnresdpof.pack(side=LEFT, padx=70, pady=20)
btnresdpof.place(x=580,y=580)
btnresdpof.configure(font='helvetica 11')

#cuadro Graficos de Post Proceso
lblresultpost = Label(pgresult, image = imgps)
lblresultpost.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblresultpost.place(x=840,y=160)

lblresultpp = Label(pgresult, text = 'Post proceso')
lblresultpp.pack(side = 'bottom', fill = 'both', expand = 'yes')
lblresultpp.place(x=885,y=165)
lblresultpp.configure(font='helvetica 15')

btnressdp = Button(pgresult, text='Series precipitación',command=lambda:graflineal('prc','tables'),  height = 1, width = 20)
btnressdp.pack(side=LEFT, padx=70, pady=20)
btnressdp.place(x=870,y=220)
btnressdp.configure(font='helvetica 11')

btnrespscn = Button(pgresult, text='Serie caudal natural',command=lambda:graflineal('qnt','tables'),  height = 1, width = 20)
btnrespscn.pack(side=LEFT, padx=70, pady=20)
btnrespscn.place(x=870,y=260)
btnrespscn.configure(font='helvetica 11')

btnresscd = Button(pgresult, text='Serie caudal disponible',command=lambda:graflineal('qds','tables'),  height = 1, width = 20)
btnresscd.pack(side=LEFT, padx=70, pady=20)
btnresscd.place(x=870,y=300)
btnresscd.configure(font='helvetica 11')

btnrespll = Button(pgresult, text='Percentil lluvia',command=lambda:graflineal('prc','postproceso'),  height = 1, width = 20)
btnrespll.pack(side=LEFT, padx=70, pady=20)
btnrespll.place(x=870,y=340)
btnrespll.configure(font='helvetica 11')

btnrescdcn = Button(pgresult, text='Curva duración caudal nat.',command=lambda:graflineal('qnt','postproceso'),  height = 1, width = 20)
btnrescdcn.pack(side=LEFT, padx=70, pady=20)
btnrescdcn.place(x=870,y=380)
btnrescdcn.configure(font='helvetica 11')

btnrescdcd= Button(pgresult, text='Curva duración caudal disp.',command=lambda:graflineal('qds','postproceso'),  height = 1, width = 20)
btnrescdcd.pack(side=LEFT, padx=70, pady=20)
btnrescdcd.place(x=870,y=420)
btnrescdcd.configure(font='helvetica 11')

btnresppm = Button(pgresult, text='Precip. prom. mensual',command=lambda:graflineal('prc','menusual'),  height = 1, width = 20)
btnresppm.pack(side=LEFT, padx=70, pady=20)
btnresppm.place(x=870,y=460)
btnresppm.configure(font='helvetica 11')

btnresqnpm = Button(pgresult, text='Q natural prom. mensual',command=lambda:graflineal('qnt','mensual'),  height = 1, width = 20)
btnresqnpm.pack(side=LEFT, padx=70, pady=20)
btnresqnpm.place(x=870,y=500)
btnresqnpm.configure(font='helvetica 11')

btnresqdpm = Button(pgresult, text='Q disp. prom. mensual',command=lambda:graflineal('qds','mensual'),  height = 1, width = 20)
btnresqdpm.pack(side=LEFT, padx=70, pady=20)
btnresqdpm.place(x=870,y=540)
btnresqdpm.configure(font='helvetica 11')


#llenado de las pestanias
nbfonag.add(pgmodel, text="Modelo")
nbfonag.add(pgresult, text="Resultados")
nbfonag.pack(expand=1, fill="both")
#Lanzar GUI#
root.mainloop()
