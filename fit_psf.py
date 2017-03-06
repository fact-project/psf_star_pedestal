# coding: utf-8
from astropy.io import fits
import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.optimize import curve_fit
from joblib import Parallel, delayed
import astropy.units as u
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('outputfile')


pixel_width = 9.5 * u.mm
focal_length = 4.889 * u.m
sidereal_day = 1 * u.sday
pixel_fov = np.arctan(pixel_width / focal_length)


def gauss(x, mu, sigma, A, off):
    return A * norm(mu, sigma).pdf(x) + off


def fit(x, y, chid):

    y_smooth = pd.Series(y).rolling(200, center=True).mean()

    idx = y_smooth.argmax()
    x0 = x_mm[idx]
    amp = y_smooth[idx]

    mask = np.isfinite(y_smooth.values)

    if amp < 3e5:
        return {
            'chid': chid,
            'mu': np.nan,
            'sigma': np.nan,
            'A': np.nan,
            'off': np.nan,
        }

    try:
        params, cov = curve_fit(
            gauss, x_mm[mask], y_smooth.values[mask], p0=(x0, 5.5, amp, 20e4)
        )
    except RuntimeError:
        return {
            'chid': chid,
            'mu': np.nan,
            'sigma': np.nan,
            'A': np.nan,
            'off': np.nan,
        }

    return {
        'chid': chid,
        'mu': params[0],
        'sigma': params[1],
        'A': params[2],
        'off': params[3],
    }


if __name__ == '__main__':

    args = parser.parse_args()

    f = fits.open(args.inputfile)

    ped_var = f[1].data['ped_var'].byteswap().newbyteorder()
    unixtime = f[1].data['UnixTimeUTC'].byteswap().newbyteorder()

    unixtime = (unixtime[:, 0] + unixtime[:, 1] / 1e6) * u.s

    time = unixtime - unixtime.min()

    x = (time * 360 * u.deg / sidereal_day * pixel_width / pixel_fov)

    x_mm = x.to(u.mm).value

    with Parallel(n_jobs=-1, verbose=10) as pool:

        result = pd.DataFrame(
            pool(
                delayed(fit)(x_mm, ped_var[:, chid], chid)
                for chid in range(1440)
            )
        )

    result.to_csv(args.outputfile, index=False)
