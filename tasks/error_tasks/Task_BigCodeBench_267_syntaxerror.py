import numpy as np
import matplotlib.pyplot as plt
from scipy import fftpack

def task_func(data, sample_rate=100):
    # Add new key 'a' with value 1
    data['a'] = 1

    # Generate a signal based on the values in `data`
    signal = np.array(list(data.values()))
    time = np.linspace(0, 2, 2 * sample_rate, False)
    signal = np.sin(np.outer(time, signal) * np.pi)

    # Perform a Fast Fourier Transform (FFT) on the signal
    fft = fftpack.fft(signal)

    # Plot the FFT
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(np.abs(fft))
    ax.set_title('FFT of the Signal')
    ax.set_xlabel('Frequency [Hz]')
    ax.set_ylabel('Frequency Spectrum Magnitude')
    

    return fft

