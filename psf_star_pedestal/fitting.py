from scipy.stats import norm
import numpy as np
from scipy.optimize import curve_fit


def gaussian_and_constant(x, mu, sigma, A, off):
    return A * norm(mu, sigma).pdf(x) + off


def fit(x, y):

    mask = np.isfinite(y)

    y = y[mask]
    x = x[mask]

    idx = y.argmax()
    x0 = x[idx]
    amp = y[idx]

    if amp < 150e3:
        return {
            'mu': np.nan,
            'sigma': np.nan,
            'A': np.nan,
            'off': np.nan,
            'status': 'low_amplitude',
        }

    try:
        params, cov = curve_fit(
            gaussian_and_constant, x, y, p0=(x0, 5.5, amp, 20e4)
        )
    except RuntimeError:
        return {
            'mu': np.nan,
            'sigma': np.nan,
            'A': np.nan,
            'off': np.nan,
            'status': 'fit_failed',
        }

    return {
        'mu': params[0],
        'sigma': params[1],
        'A': params[2],
        'off': params[3],
        'status': 'success',
    }
