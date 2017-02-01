# coding=utf-8
import numpy as np
import rainflow

try:
    # Python 3.x
    from tkinter import *
except ImportError:
    # Python 2.x
    from Tkinter import *
import matplotlib
from matplotlib import cm

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter

try:
    # Python 3.x
    from tkinter.filedialog import askopenfilename
except ImportError:
    # Python 2.x
    from tkFileDialog import askopenfilename


class App:
    def __init__(self, master):
        self.master = master
        self.filebase = 0  # variable que posee vector de archivo de presion
        self.btnLoad = Button(master, text="Load", command=self.loadPres).place(x=10, y=10)
        self.btnRcc = Button(master, text="RCC Analisys", command=self.onRccBtn).place(x=70, y=10)
        self.btnSlf = Button(master, text="SLF Analisys", command=self.slfAnilisis).place(x=180, y=10)
        self.btnReset = Button(master, text="Reset").place(x=290, y=10)
        self.btnExit = Button(master, text="Exit", command=quit).place(x=360, y=10)

        self.file_opt = options = {}
        # opciones usadas para abrir archivos de extension .pres
        options['defaultextension'] = '.pres'
        options['filetypes'] = [('all files', '.*'), ('pressure files', '.pres')]
        options['initialdir'] = 'C:\\'
        options['parent'] = master
        options['title'] = 'Presssure'

        self.file_min = options = {}
        # opciones usadas para abrir archivos de extension .min
        options['defaultextension'] = '.min'
        options['filetypes'] = [('all files', '.*'), ('min psi', '.min')]
        options['initialdir'] = 'C:\\'
        options['parent'] = master
        options['title'] = 'MinPressure'

        self.file_max = options = {}
        # opciones usadas para abrir archivos de extension .max
        options['defaultextension'] = '.max'
        options['filetypes'] = [('all files', '.*'), ('max psi', '.max')]
        options['initialdir'] = 'C:\\'
        options['parent'] = master
        options['title'] = 'MaxPressure'

    def loadPres(self):
        all_data = self.getFile(self.file_opt)
        if len(all_data) > 0:
            # histograma de presion

            fig = plt.figure(figsize=(10, 5), dpi=60)
            Figure = FigureCanvasTkAgg(fig, master=self.master)
            Figure.get_tk_widget().place(x=10, y=50)
            ax = fig.add_subplot(111)
            fig.subplots_adjust(top=0.90)
            ax.hist(all_data, bins=int(math.sqrt(len(all_data))), normed=False)
            ax.set_title("Histograma de Presion")
            ax.plot()
            fig.canvas.draw()

            # espectro de presion
            figu = plt.figure(figsize=(10, 5), dpi=60)
            figura = FigureCanvasTkAgg(figu, master=self.master)
            figura.get_tk_widget().place(x=10, y=380)
            esp = figu.add_subplot(111)
            figu.subplots_adjust(top=0.90)
            esp.set_title("Espectro de Presion")
            esp.set_xlabel('Time [Hours]')
            esp.set_ylabel('Pressure [Psi]')
            y = np.arange(len(all_data))
            esp.plot(y, all_data)
            figu.canvas.draw()

            # seteando el archivo obtenido el archivo se setea para posterior utlizacion en algoritmo rainflow
            self.filebase = all_data

        else:
            m = Message(self.master, text="Error open file")  # mensaje lanzado si el archivo no pudo abrirse

    def findext(self):
        matrix_in = self.filebase
        # extrae los máximos y ptos de inflexion
        wi = self.diff(matrix_in)
        data = np.zeros(len(matrix_in))
        data[0] = matrix_in[0]
        no = 0
        current = len(matrix_in)  # tamaño actual del resultado
        for i in range(current - 2):
            if (wi[i] * wi[i + 1]) <= 0:
                no += 1
                data[no] = matrix_in[i + 1]

        data[no + 1] = matrix_in[current - 1]
        no += 2
        data = data[:no]

        # print "primer no ", no
        # elimina puntos de inflexión
        if no != 0:
            current = no
            no = 0

        matrix_in = data

        wi = self.diff(data)

        for i in range(current - 1):
            if ~((wi[i] == 0) and (wi[i + 1] == 0)):
                no += 1
                data[no] = matrix_in[i + 1]

        no += 1  # se agrega por el ultimo
        data = data[:no]

        # retira los repetidos
        if no != 0:
            current = no
            no = 0

        matrix_in = data
        for i in range(current - 1):
            if ~ (matrix_in[i] == matrix_in[i + 1]):
                data[no] = matrix_in[i]
                no += 1

        # extrae los maximos

        if no != 0:
            current = no
            no = 0

        if len(data) > 2:
            wi = self.diff(data)
            for i in range(current - 1):
                if wi[i] * wi[i + 1] < 0:
                    no += 1
                    data[no] = matrix_in[i + 1]
        # almacena datos en MATRIX_OUT
        # redimensionando datos de salida
        data = data[:no]
        matrix_out = data
        return matrix_out

    def diff(self, filebase):
        wi = []
        for i in range(len(filebase) - 1):
            wi.append(filebase[i + 1] - filebase[i])

        return wi

    def rainflow(self, datain):
        # inicializando variables
        data = datain
        tot_num = len(data)
        data_out = np.zeros(len(data) * 3)
        j = -1
        cNr = 1
        k = 0
        a = np.zeros(len(data) * 5)
        ampl = 0
        mean = 0
        current_vector = 0
        current_vector_salida = -1
        # fin de inicializacion

        for i in range(tot_num):
            j += 1
            a[j] = data[current_vector]
            current_vector += 1
            while j >= 2 and (math.fabs(a[j - 1] - a[j - 2]) <= math.fabs(a[j] - a[j - 1])):
                ampl = math.fabs((a[j - 1] - a[j - 2]) / 2)
                if j == 0:
                    nada = 0
                elif j == 1:
                    nada = 0
                elif j == 2:
                    mean = (a[0] + a[1]) / 2
                    a[0] = a[1]
                    a[1] = a[2]
                    j = 1
                    if ampl > 0:
                        current_vector_salida += 1
                        data_out[current_vector_salida] = ampl
                        current_vector_salida += 1
                        data_out[current_vector_salida] = mean
                        current_vector_salida += 1
                        data_out[current_vector_salida] = 0.50
                        k += 1
                else:
                    mean = (a[j - 1] + a[j - 2]) / 2
                    a[j - 2] = a[j]
                    j -= 2
                    if ampl > 0:
                        current_vector_salida += 1
                        data_out[current_vector_salida] = ampl
                        current_vector_salida += 1
                        data_out[current_vector_salida] = mean
                        current_vector_salida += 1
                        data_out[current_vector_salida] = 1.00
                        cNr += 1
                        k += 1
        for l in range(j):
            ampl = math.fabs(a[l] - a[l + 1]) / 2
            mean = (a[l] + a[l + 1]) / 2
            if ampl > 0:
                current_vector_salida += 1
                data_out[current_vector_salida] = ampl
                current_vector_salida += 1
                data_out[current_vector_salida] = mean
                current_vector_salida += 1
                data_out[current_vector_salida] = 0.50
                k += 1
        col = k

        data_out = data_out[:col]
        return data_out, col

    def onRccBtn(self):
        dataout = self.findext()
        fatiga, col = self.rainflow(dataout)
        # obteniendo datos esfuerzos
        esfuerzo_alternante = []
        esfuerzo_medio = []
        k = 0
        # obteniendo los datos de esfuerzo alternante y esfuerzo medio
        for i in range(int(col / 3)):
            for j in range(3):
                if j == 0:
                    esfuerzo_alternante.append(fatiga[k])
                elif j == 1:
                    esfuerzo_medio.append(fatiga[k])
                k += 1

        # histograma SA (esfuerzo alternante)
        fig_sa = plt.figure(figsize=(8, 5), dpi=60)
        Figure_sa = FigureCanvasTkAgg(fig_sa, master=self.master)
        Figure_sa.get_tk_widget().place(x=560, y=50)
        hist_sa = fig_sa.add_subplot(111)
        fig_sa.subplots_adjust(top=0.90)
        hist_sa.hist(esfuerzo_alternante, bins=int(math.sqrt(len(esfuerzo_alternante))), normed=False)
        hist_sa.set_title("Histograma de Esfuerzo Alternante")
        hist_sa.plot()
        fig_sa.canvas.draw()

        # histograma SM e(sfuerzo medio)
        fig_sm = plt.figure(figsize=(8, 5), dpi=60)
        Figure_sm = FigureCanvasTkAgg(fig_sm, master=self.master)
        Figure_sm.get_tk_widget().place(x=560, y=380)
        hist_sm = fig_sm.add_subplot(111)
        fig_sm.subplots_adjust(top=0.90)
        hist_sm.hist(esfuerzo_medio, bins=int(math.sqrt(len(esfuerzo_medio))), normed=False)
        hist_sm.set_title("Histograma de Esfuerzo Medio")
        hist_sm.plot()
        fig_sm.canvas.draw()

    def slfAnilisis(self):
        meses = 5
        time = meses / 12
        pload = self.filebase
        s1min = self.getFileMin_Max(self.file_min)
        s2min = self.getFileMin_Max(self.file_min)
        s3min = self.getFileMin_Max(self.file_min)
        s1max = self.getFileMin_Max(self.file_max)
        s2max = self.getFileMin_Max(self.file_max)
        s3max = self.getFileMin_Max(self.file_max)
        smin = []
        smax = []
        smin.append(s1min)
        smin.append(s2min)
        smin.append(s3min)
        smax.append(s1max)
        smax.append(s2max)
        smax.append(s3max)

        # calculando la matriz de transferencia
        n = len(smin[1]) / 3
        s1min = smin[2][1:n]
        s2min = smin[2][n + 1:2 * n]
        s3min = smin[2][2 * n + 1:3 * n]
        s1max = smax[2][1:n]
        s2max = smax[2][n + 1:2 * n]
        s3max = smax[2][2 * n + 1:3 * n]
        ds1 = s1max - s1min
        ds2 = s2max - s2min
        ds3 = s3max - s3min

        # calculan funcion de transferencia
        prmin = min(pload)
        prmax = max(pload)
        TF1 = ds1 / (prmax - prmin)
        TF2 = ds2 / (prmax - prmin)
        TF3 = ds3 / (prmax - prmin)

        amp, mean, cyc = rainflow._rainflow(pload)

    def getFile(self, options):
        filename = askopenfilename(**options)
        if filename:
            f = open(filename)
            data = [line.replace("\n", " ")[0:] for line in f.readlines()[0:]]

            all_data = np.zeros(len(data))
            for i in range(len(data)):
                all_data[i] = float(data[i])

            f.close()
        return all_data

    def getFileMin_Max(self, options):
        filename = askopenfilename(**options)
        if filename:
            f = open(filename)
            data = [line.replace("\n", " ")[0:] for line in f.readlines()[0:]]

            all_data = np.zeros(len(data))
            for i in range(len(data)):
                datos = data[i].split()
                all_data[i] = float(datos[1])

            f.close()
        return all_data


ventanaPrincipal = Tk()
app = App(ventanaPrincipal)
ventanaPrincipal.wm_title("Fatiga")
ventanaPrincipal.geometry("1024x700")
ventanaPrincipal.deiconify()
ventanaPrincipal.mainloop()
