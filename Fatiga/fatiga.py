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
        self.btnRcc = Button(master, text="RCC Analisys", command=self.rainflow).grid(row=1, column=3)
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
            all_data.sort()

            f.close()

            plt.hist(all_data, bins=int(math.sqrt(len(all_data))), normed=True)

            self.filebase = all_data

            # falta el espectro de frecuencia
            plt.title("Histograma de Presion")
            plt.show()

        else:
            m = Message(self.master, text="Error open file")

    def findext(self):
        matrix_in = self.filebase
        #extrae los máximos y ptos de inflexion
        wi = self.diff(matrix_in)
        data = []
        data[0] = matrix_in[0]
        no = 0
        current = 0  # tamaño actual del resultado
        for i in range(len(matrix_in) - 2):
            if wi[i] * wi[i + 1] <= 0:
                no = no + 1
                data[no] = matrix_in[i + 1]

        data[no + 1] = matrix_in[len(matrix_in) - 1]
        no = no + 2

        #elimina puntos de inflexión
        if no != 0:
            current = no
            no = 0

        matrix_in = data

        wi = self.diff(data)

        for i in range(current-1):
            if ~((wi[i] == 0) & (wi[i + 1] == 0)):
                no = no + 1
                data[no] = matrix_in[i + 1]

        no = no + 1  # se agrega por el ultimo

        # retira los repetidos
        if no != 0:
            current = no
            no = 0

        matrix_in = data

        for i in range(current):
            if ~ matrix_in[i] == matrix_in[i + 1]:
                data[no] = matrix_in[i]
                no = no + 1

        # extrae los maximos

        if no != 0:
            current = no
            no = 0

        if len(data) > 2:
            wi = self.diff(data)

            for i in range(current):
                if wi[i] * wi[i + 1] < 0:
                    no = no + 1
                    data[no] = matrix_in[i + 1]
        #almacena datos en MATRIX_OUT
        matrix_out = data

        return matrix_out

    def diff(self, filebase):
        wi = np.zeros(len(filebase))
        for i in range(len(filebase) - 1):
            wi[i] = filebase[i + 1] - filebase[i]


        return wi

    def rainflow(self, dataIn, filebase):
        wi = []




ventanaPrincipal = Tk()
app = App(ventanaPrincipal)
ventanaPrincipal.wm_title("Fatiga")
ventanaPrincipal.geometry("800x500")
ventanaPrincipal.mainloop()
