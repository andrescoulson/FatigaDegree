# coding=utf-8
import numpy as np

try:
    # Python 3.x
    from tkinter import *
except ImportError:
    # Python 2.x
    from Tkinter import *
import matplotlib
from matplotlib import cm
import utils
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import math
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import LinearLocator, FormatStrFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
try:
    # Python 3.x
    from tkinter.filedialog import askopenfilename
except ImportError:
    # Python 2.x
    from tkFileDialog import askopenfilename

try:
    # Python 3.x
    from tkinter import messagebox as TkMessage
except ImportError:
    # Python 2.x
    import tkMessageBox as TkMessage
import operator
import os




class App:
    def __init__(self, master):
        self.master = master
        self.filebase = None  # variable que posee vector de archivo de presion
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
            #fig.savefig('hist_pressure.eps', format='eps', dpi=1000)
            fig.canvas.draw()

            # espectro de presion
            figu = plt.figure(figsize=(10, 5), dpi=60)
            figura = FigureCanvasTkAgg(figu, master=self.master)
            figura.get_tk_widget().place(x=560, y=50)
            esp = figu.add_subplot(111)
            figu.subplots_adjust(top=0.90)
            esp.set_title("Espectro de Presion")
            esp.set_xlabel('Time [Hours]')
            esp.set_ylabel('Pressure [Psi]')
            y = np.arange(len(all_data))
            esp.plot(y, all_data)
            #figu.savefig('espect_pressure.eps', format='eps', dpi=1000)
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
        if ~(self.filebase is None):
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
            fig_sa = plt.figure(figsize=(10, 4), dpi=60)
            Figure_sa = FigureCanvasTkAgg(fig_sa, master=self.master)
            Figure_sa.get_tk_widget().place(x=10, y=360)
            hist_sa = fig_sa.add_subplot(111)
            fig_sa.subplots_adjust(top=0.90)
            hist_sa.hist(esfuerzo_alternante, bins=int(math.sqrt(len(esfuerzo_alternante))), normed=False)
            hist_sa.set_title("Histograma de Esfuerzo Alternante")
            hist_sa.plot()
            #fig_sa.savefig('hist_SA.eps', format='eps', dpi=1000)
            fig_sa.canvas.draw()

            # histograma SM (esfuerzo medio)
            fig_sm = plt.figure(figsize=(10, 4), dpi=60)
            Figure_sm = FigureCanvasTkAgg(fig_sm, master=self.master)
            Figure_sm.get_tk_widget().place(x=560, y=360)
            hist_sm = fig_sm.add_subplot(111)
            fig_sm.subplots_adjust(top=0.90)
            hist_sm.hist(esfuerzo_medio, bins=int(math.sqrt(len(esfuerzo_medio))), normed=False)
            hist_sm.set_title("Histograma de Esfuerzo Medio")
            hist_sm.plot()
            #fig_sm.savefig('hist_SM.eps', format='eps', dpi=1000)
            fig_sm.canvas.draw()

            # histograma en 3d rainflow



            # se añada una nueva figura a esa ventana creada
            fig_sm_3d = plt.figure(figsize=(9, 5), dpi=70)
            fig_sm_3d.suptitle("Histograma 3D Rainflow")
            Figure_sm_3d = FigureCanvasTkAgg(fig_sm_3d, master=self.master)
            Figure_sm_3d.get_tk_widget().place(x=10, y=620)
            fig_sm_3d.subplots_adjust(top=0.90)

            ax2 = fig_sm_3d.add_subplot(111)

            # se obtiene los rangos para los ejes
            gridx = np.linspace(min(esfuerzo_medio), max(esfuerzo_medio), 11)
            gridy = np.linspace(min(esfuerzo_alternante), max(esfuerzo_alternante), 11)
            #  se crea un histograma en 2d a partir de los datos SA SM Cycles
            hist, xedges, yedges = np.histogram2d(esfuerzo_medio, esfuerzo_alternante, bins=[gridx, gridy])

            # pintamos el grafico dado en hist
            myextent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
            im = ax2.imshow(hist.T, origin='low', extent=myextent, interpolation='nearest', aspect='auto')

            # se coloca la barra al lado derecho corresponde al numero de ciclos

            divider3 = make_axes_locatable(ax2)
            cbar_ax = divider3.append_axes("right", size="8%", pad=0.05)
            ax2.plot(esfuerzo_medio, esfuerzo_alternante, 'ro')
            ax2.set_xlabel("Esfuerzo medio")
            ax2.set_ylabel("Esfuerzo alternante")

            # se muestra el widget creado
            fig_sm_3d.colorbar(im, cax=cbar_ax)
            #fig_sm_3d.savefig('hist_3d_rainflow.eps', format='eps', dpi=1000)
            fig_sm_3d.canvas.draw()



        else:
            TkMessage.showinfo("Error file", "Press file error ")

    def slfAnilisis(self):
        # calcula funcion de transferencia para cada nodo en el modelo
        pload = self.filebase
        if ~(self.filebase is None) :
            meses = 5.0
            time = meses / 12.0
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
            n = int(len(smin[1]) / 3)

            #print n
            s1min = smin[2][0:n]
            s2min = smin[2][n + 1:2 * n]
            s3min = smin[2][2 * n + 1:3 * n]
            s1max = smax[2][0:n]
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

            #print len(TF1), len(TF2), len(TF3)

            tp = self.findext()
            rf, col = self.rainflow(tp)  # rainflow
            #print col
            ni = []
            k=0
            for i in range(int(col / 3)):
                for j in range(3):
                    if j == 2:
                        ni.append(rf[k])
                    k += 1

            # Palt = 1/2(pmax-pmin)
            k=0
            DP =[]
            for i in range(int(col / 3)):
                for j in range(3):
                    if j == 0:
                        DP.append(2*rf[k])
                    k += 1

            # Pmean = 1/2(pmax-pmin)
            MP=[]
            k=0
            for i in range(int(col / 3)):
                for j in range(3):
                    if j == 2:
                        MP.append(rf[k])
                    k += 1


            # calcula daño para cada ciclo y daño acumulado
            # constantes tomadas de la tabla F.13 API 579
            C1a = 2.254510E+00
            C2a = -4.642236E-01
            C3a = -8.312745E-01
            C4a = 8.634660E-02
            C5a = 2.020834E-01
            C6a = -6.940535E-03
            C7a = -2.079726E-02
            C8a = 2.010235E-04
            C9a = 7.137717E-04
            C10a = 0.0
            C11a = 0.0

            C1b = 7.999502E+00
            C2b = 5.832491E-02
            C3b = 1.500851E-01
            C4b = 1.273659E-04
            C5b = -5.263661E-05
            C6b = 0.0
            C7b = 0.0
            C8b = 0.0
            C9b = 0.0
            C10b = 0.0
            C11b = 0.0

            # calculando daño acumulado
            # factores para modificacion de resistencia a la fatiga

            Cus = 1.0
            Et = 29.4e6
            Efc = 28.3e6
            Kff = 1.0
            Kee = 1.0
            Ka = 0.45  # factor acabado superficial
            Kb = 1.00  # Factor de Tamaño
            Kc = 1.00  # Factor de carga
            Kd = 1.00  # Factor de temperatura
            Ke = 1.00  # Factor de confiabilidad
            Kf = 1.00  # Factores misceláneos
            # Sf = Ka*Kb*Kc*Kd*Ke*Kf*Sf;

            ndp = len(DP)
            Sa = np.zeros((ndp, n))
            Dk = np.zeros(n)
            #print Sa

            kkk = 0
            X = 0
            i=0
            for i in range(ndp):
                for j in range(n-1):
                    Sa[i][j] = 1 / math.sqrt(2) * math.sqrt(
                        ((TF1[j] - TF2[j]) ** 2) + ((TF2[j] - TF3[j]) ** 2) + ((TF3[j] - TF1[j]) ** 2)) * DP[i]
                    Sa[i][j] = (Kff * Kee * Sa[i][j]) / 2
                    Sa[i][j] = Sa[i][j] / 1e3  # convierte a kpsi

                    # las siguientes ecuacuones estan en kpsi

                    sc = Sa[i][j] / Cus
                    if Sa[i][j] <= 31 and Sa[i][j] >= 7:
                        X = (C1a + C3a * sc + C5a * sc ** 2 + C7a * sc ** 3 + C9a * sc ** 4 + C11a * sc ** 5) / (
                            1 + C2a * sc + C4a * sc ** 2 + C6a * sc ** 3 + C8a * sc ** 4 + C10a * sc ** 5)
                    else:

                        X = (C1b + C3b * sc + C5b * sc ** 2 + C7b * sc ** 3 + C9b * sc ** 4 + C11b * sc ** 5) / (
                            1 + C2b * sc + C4b * sc ** 2 + C6b * sc ** 3 + C8b * sc ** 4 + C10b * sc ** 5)

                    # calcula el daño acumulado y vida para cada nodo para cada grupo de carga

                    Nkji = (10 ** X) * (Et / Efc)  # vida acumulada en el cicli Dpi en el nodo "j"
                    dkji = ni[i] / Nkji  # daño generado en el ciclo Dpi en el nodo "j"
                    Dk[j] += dkji  # daño acumulado en el nodo "j"
            # determina el nodo con major daño acumulado (vida minima)
            nd, val = max(enumerate(Dk), key=operator.itemgetter(1))

            # calculando curva de sensibilidad
            # grafica de sensibilidad de la vida a la variacion de DP
            k = 0
            Dfac = []
            print "ndp", ndp," ni", len(ni)

            for j in self.frange(0.5, 1.5, 0.05):
                Dfac.append(0)

            for fac in self.frange(0.5, 1.5, 0.05):

                for i in range(ndp):
                    sc = Sa[i][nd] * fac / Cus
                    if 7 <= Sa[i][j] <= 31:
                        X = (C1a + C3a * sc + C5a * sc ** 2 + C7a * sc ** 3 + C9a * sc ** 4 + C11a * sc ** 5) / (
                            1 + C2a * sc + C4a * sc ** 2 + C6a * sc ** 3 + C8a * sc ** 4 + C10a * sc ** 5)
                    else:
                        X = (C1b + C3b * sc + C5b * sc ** 2 + C7b * sc ** 3 + C9b * sc ** 4 + C11b * sc ** 5) / (
                            1 + C2b * sc + C4b * sc ** 2 + C6b * sc ** 3 + C8b * sc ** 4 + C10b * sc ** 5)

                    # calcula el daño acumuluado para un factor de presion
                    # dado para el nodo mas critico
                    Dfac[k] += ni[i] / ((10 ** X) * (Et / Efc))
                k += 1
            # grafica de sensibilidad de la vida a la variacion de DP
            fig_slf = plt.figure(figsize=(10, 5), dpi=60)
            Figure_slf = FigureCanvasTkAgg(fig_slf, master=self.master)
            Figure_slf.get_tk_widget().place(x=560, y=360)
            slf_curve = fig_slf.add_subplot(111)
            fig_slf.subplots_adjust(top=0.90)

            ydata =[]
            for i in self.frange(0.5, 1.5, 0.05):
                ydata.append(i)

            for i in range(len(Dfac)):
                print float(time/Dfac[i])
                Dfac[i] = float(time/Dfac[i])

            #slf_curve.set_title("Espectro de Presion")
            slf_curve.set_xlabel('P-Factor')
            slf_curve.set_ylabel('Available Life [Years]')
            slf_curve.plot(ydata, Dfac)

            fig_slf.canvas.draw()


        else:

            TkMessage.showinfo("Error file", "Press file error ")

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

    def getFileMin_Max(self, options) :
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

    def frange(self, start, stop, step):
        i = start
        while i <= stop:
            yield i
            i += step


ventanaPrincipal = Tk()
app = App(ventanaPrincipal)
ventanaPrincipal.wm_title("Fatiga")
ventanaPrincipal.geometry("1150x980")
utils.center(ventanaPrincipal)
ventanaPrincipal.deiconify()
ventanaPrincipal.mainloop()
