import numpy as np
import rainflow
from matplotlib.pylab import hist, show
import matplotlib.pyplot as plt
import math
import Tkinter
from Tkinter import *


ventanaPrincipal = Tk()
ventanaPrincipal.geometry("800x500")

def ejecutar(f): ventanaPrincipal.after(200,f)

btnLoad = Button(ventanaPrincipal, text="Load").grid(row=1, column=1)
btnRcc = Button(ventanaPrincipal, text="RCC Analisys").grid(row=1, column=3)
btnSlf = Button(ventanaPrincipal, text="SLF Analisys").grid(row=1, column=4)
btnReset = Button(ventanaPrincipal, text="Reset").grid(row=1, column=5)
btnExit = Button(ventanaPrincipal, text="Exit").grid(row=1, column=6)


ventanaPrincipal.mainloop()


# f = open('25_547_31.pres')
#
# data = [line.replace("\n", " ")[0:] for line in f.readlines()[0:]]
#
# all_data =  np.zeros(len(data))
# for i in range(len(data)):
#     all_data[i] = float(data[i])
# all_data.sort()
#
# f.close()
#
# plt.hist(all_data, bins= int(math.sqrt(len(all_data))) , normed=True)
# plt.show()
#
#
# dt = 0.01
# Fs = 1/dt
# t = np.arange(0, 10, dt)
# nse = np.random.randn(len(t))
# r = np.exp(-t/0.05)
#
# cnse = np.convolve(nse, r)*dt
# cnse = cnse[:len(t)]
# s = 0.1*np.sin(2*np.pi*t) + cnse
#
#
#
#
# plt.angle_spectrum(s, Fs=Fs)
#
# plt.show()
