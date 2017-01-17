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

            plt.show()

        else:
            m = Message(self.master, text="Error open file")

    def rainflow(self):
        print rainflow.extract_cycles(self.filebase)


ventanaPrincipal = Tk()
app = App(ventanaPrincipal)
ventanaPrincipal.wm_title("Embedding in TK")
ventanaPrincipal.geometry("800x500")
ventanaPrincipal.mainloop()
