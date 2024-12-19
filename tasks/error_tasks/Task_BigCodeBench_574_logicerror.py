import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def task_func(array_length=100, noise_level=0.5):
    x = np.linspace(0, 4 * np.pi, array_length)
    y = np.sin(x) + noise_level * np.random.rand(array_length)

    def func(x, a, b):
        return a * np.sin(b * x)

    popt, pcov = curve_fit(func, x, y, p0=[1, 2])

    fig, ax = plt.subplots()
    ax.plot(x, y, 'b-', label='data')
    ax.plot(x, func(x, *popt), 'r-', label='fit: a=%5.3f, b=%5.3f' % tuple(popt))
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.legend()
    
    return ax
