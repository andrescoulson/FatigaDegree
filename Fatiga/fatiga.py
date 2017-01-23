# coding=utf-8
import numpy as np
try:
    # Python 3.x
    from tkinter import *
except ImportError:
    # Python 2.x
    from Tkinter import *
import matplotlib

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import math
try:
    # Python 3.x
    from tkinter.filedialog import askopenfilename
except ImportError:
    # Python 2.x
    from tkFileDialog import askopenfilename



class App:
    def __init__(self, master):
        self.master = master
        self.filebase = 0
        self.btnLoad = Button(master, text="Load", command=self.loadPres).place(x=10, y=10)
        self.btnRcc = Button(master, text="RCC Analisys", command=self.onRccBtn).place(x=70, y=10)
        self.btnSlf = Button(master, text="SLF Analisys", command=self.slfAnilisis).place(x=180, y=10)
        self.btnReset = Button(master, text="Reset").place(x=290, y=10)
        self.btnExit = Button(master, text="Exit", command=quit).place(x=360, y=10)

        self.file_opt = options = {}

        options['defaultextension'] = '.pres'
        options['filetypes'] = [('all files', '.*'), ('pressure files', '.pres')]
        options['initialdir'] = 'C:\\'
        options['parent'] = master
        options['title'] = 'Presssure'

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

            dt = 0.01
            Fs = 1 / dt
            t = np.arange(0, 10, dt)
            nse = np.random.randn(len(t))
            r = np.exp(-t / 0.05)
            cnse = np.convolve(nse, r) * dt
            cnse = cnse[:len(t)]
            s = 0.1 * np.sin(2 * np.pi * t) + cnse

            figu = plt.figure(figsize=(10, 5), dpi=60)
            figura = FigureCanvasTkAgg(figu, master=self.master)
            figura.get_tk_widget().place(x=10, y=380)
            esp = figu.add_subplot(111)
            figu.subplots_adjust(top=0.90)
            esp.angle_spectrum(s, Fs=Fs)
            esp.set_title("Espectro de Presion")
            esp.plot()
            figu.canvas.draw()

            # seteando el archivo obtenido
            self.filebase = all_data

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

            for i in range(current - 1):
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
        data_out = np.zeros(len(data) * 3)
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
                        current_vector_salida += 1
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
                current_vector_salida += 1
                data_out[current_vector_salida] = ampl
                current_vector_salida += 1
                data_out[current_vector_salida] = mean
                current_vector_salida += 1
                data_out[current_vector_salida] = 0.50
                k += 1
        col = k

        data_out = data_out[:col - 1]
        return data_out, col

    def onRccBtn(self):
        dataout = self.findext()
        fatiga, col = self.rainflow(dataout)


    def slfAnilisis(self):
        fig = plt.figure(1)
        plt.ion()
        t = np.arange(0.0, 3.0, 0.01)
        s = np.sin(np.pi * t)
        plt.plot(t, s)

        canvas = FigureCanvasTkAgg(fig, master=self.master)
        plot_widget = canvas.get_tk_widget()
        plot_widget.grid(row=0, column=0)

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


ventanaPrincipal = Tk()
app = App(ventanaPrincipal)
ventanaPrincipal.wm_title("Fatiga")
ventanaPrincipal.geometry("1024x700")
ventanaPrincipal.mainloop()
