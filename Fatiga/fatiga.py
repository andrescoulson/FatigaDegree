# coding=utf-8
import numpy as np
import rainflow
import matplotlib.pyplot as plt
import math
import Tkinter
from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from tkFileDialog import askopenfilename


class App:
    def __init__(self, master):
        self.master = master
        self.filebase = 0
        self.btnLoad = Button(master, text="Load", command=self.loadPres).grid(row=1, column=1)
        self.btnRcc = Button(master, text="RCC Analisys", command=self.onRccBtn).grid(row=1, column=3)
        self.btnSlf = Button(master, text="SLF Analisys").grid(row=1, column=4)
        self.btnReset = Button(master, text="Reset").grid(row=1, column=5)
        self.btnExit = Button(master, text="Exit", command=quit).grid(row=1, column=6)

        self.file_opt = options = {}

        options['defaultextension'] = '.pres'
        options['filetypes'] = [('all files', '.*'), ('pressure files', '.pres')]
        options['initialdir'] = 'C:\\'
        options['parent'] = master
        options['title'] = 'Presssure'

    def loadPres(self):
        filename = askopenfilename(**self.file_opt)
        if filename:
            f = open(filename)
            data = [line.replace("\n", " ")[0:] for line in f.readlines()[0:]]

            all_data = np.zeros(len(data))
            for i in range(len(data)):
                all_data[i] = float(data[i])

            f.close()

            plt.hist(all_data, bins=int(math.sqrt(len(all_data))), normed=False)

            self.filebase = all_data

            # falta el espectro de frecuencia
            plt.title("Histograma de Presion")
            plt.show()

        else:
            m = Message(self.master, text="Error open file")

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

        data[no + 1] = matrix_in[len(matrix_in) - 1]
        no += 2
        data = data[:no]

        # print "primer no ", no
        # elimina puntos de inflexión
        if no != 0:
            current = no
            no = 0

        matrix_in = data

        wi = self.diff(data)

        for i in range(current - 2):
            if ~((wi[i] == 0) & (wi[i + 1] == 0)):
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

            for i in range(current-1):
                if wi[i] * wi[i + 1] < 0:
                    no += 1
                    data[no] = matrix_in[i + 1]
        # almacena datos en MATRIX_OUT

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
        data_out = np.zeros(len(data)*3)
        j = -1
        cNr = 1
        k = 0
        a = np.zeros(len(data))
        ampl = 0
        mean = 0
        current_vector = 0
        current_vector_salida = 0
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
                        data_out[current_vector_salida] = ampl
                        current_vector_salida += 1
                        data_out[current_vector_salida] = mean
                        current_vector_salida += 1
                        data_out[current_vector_salida] = 1.00
                        cNr += 1
                        k += 1
                for l in range(j - 1):
                    ampl = math.fabs(a[l] - a[l + 1]) / 2
                    mean = (a[l] + a[l + 1]) / 2
                    if ampl > 0:
                        data_out[current_vector_salida] = ampl
                        current_vector_salida += 1
                        data_out[current_vector_salida] = mean
                        current_vector_salida += 1
                        data_out[current_vector_salida] = 0.50
                        k += 1
                col = k
                print len(data_out)
                return data_out, col

    def onRccBtn(self):
        dataout = self.findext()
        fatiga, col = self.rainflow(dataout)
        print fatiga


ventanaPrincipal = Tk()
app = App(ventanaPrincipal)
ventanaPrincipal.wm_title("Fatiga")
ventanaPrincipal.geometry("800x500")
ventanaPrincipal.mainloop()
