# coding: utf-8
from astropy.io import fits
import pandas as pd
import numpy as np
from scipy.stats import norm
import astropy.units as u
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm

parser = ArgumentParser()
parser.add_argument('datafile')
parser.add_argument('fitresults')
parser.add_argument('outputfile')


pixel_width = 9.5 * u.mm
focal_length = 4.889 * u.m
sidereal_day = 1 * u.sday
pixel_fov = 2 * np.arctan(0.5 * pixel_width / focal_length)


def gauss(x, mu, sigma, A, off):
    return A * norm(mu, sigma).pdf(x) + off


if __name__ == '__main__':

    args = parser.parse_args()

    f = fits.open(args.datafile)
    df = pd.read_csv(args.fitresults).dropna()

    print(df.sigma.describe())

    ped_var = f[1].data['ped_var']

    unixtime = f[1].data['UnixTimeUTC']
    unixtime = (unixtime[:, 0] + unixtime[:, 1] / 1e6) * u.s
    time = unixtime - unixtime.min()

    x = (time * 360 * u.deg / sidereal_day * pixel_width / pixel_fov)
    x_mm = x.to(u.mm).value

    fig, ax = plt.subplots()

    y = np.zeros_like(x_mm)
    # data, = ax.plot(x_mm, y, '.', alpha=0.1, ms=2)
    data_smooth, = ax.plot(x_mm, y)
    fit, = ax.plot(x_mm, y)

    ax.set_xlabel(r'$x \,\, / \,\, \, \mathrm{mm}$')
    ax.set_ylabel(r'$\mathtt{ped\_var}$')
    ax.set_title('Pixel 0, $\sigma = 0.00\,\mathrm{mm}$')

    fig.tight_layout()

    with PdfPages(args.outputfile) as pdf:

        for idx, r in tqdm(df.iterrows()):

            y = ped_var[:, r.chid]
            y_smooth = pd.Series(y).rolling(200, center=True).mean()

            ax.set_ylim(0, 1.1 * y_smooth.max())
            ax.set_title('Pixel {}, $\sigma = {:.2f}\,\mathrm{{mm}}$'.format(r.chid, r.sigma))

            # data.set_ydata(y)
            data_smooth.set_ydata(y_smooth.values)
            fit.set_ydata(gauss(x_mm, r.mu, r.sigma, r.A, r.off))

            pdf.savefig(fig)
