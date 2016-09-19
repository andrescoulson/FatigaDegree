import numpy as np
import rainflow

x = np.linspace(0, 4, 200)
y = 0.2 + 0.5 * np.sin(x) + 0.2 * np.cos(10*x) + 0.2 * np.sin(4*x)

print rainflow.extract_cycles(y)