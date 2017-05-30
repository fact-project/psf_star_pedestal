from scipy.signal import butter, lfilter
from scipy.signal import gaussian
import numpy as np


def butter_lowpass(data, cutoff, order=5):
    b, a = butter(order, cutoff, btype='low', analog=False)
    smooth = lfilter(b, a, data)
    return smooth


def rolling_mean(data, n):
    window_size = 2 * n + 1
    kernel = np.full(window_size, 1.0 / window_size)
    return np.convolve(data, kernel, mode='same')


def gaussian_filter(data, std):
    kernel = gaussian(int(10 * std), std)
    return np.convolve(data, kernel, mode='same')
