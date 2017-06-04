# coding: utf-8
from astropy.io import fits
import pandas as pd
import numpy as np
import astropy.units as u
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm
import click

from psf_star_pedestal.smoothing import butter_lowpass

from ..fitting import gaussian_and_constant
from ..utils import time_to_distance, unixtime_tuple_to_time


@click.command()
@click.argument('datafile')
@click.argument('fitresults')
@click.argument('outputfile')
def main(datafile, fitresults, outputfile):
    f = fits.open(datafile)
    df = pd.read_csv(fitresults).dropna()

    ped_var = f[1].data['ped_var']

    unixtime = f[1].data['UnixTimeUTC']

    time = unixtime_tuple_to_time(unixtime)
    x = time_to_distance(time)
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

    with PdfPages(outputfile) as pdf:
        for idx, r in tqdm(df.iterrows()):

            y = ped_var[:, r.chid]
            y_smooth = butter_lowpass(y, 1e-3, 1)

            ax.set_ylim(0, 1.1 * y_smooth.max())
            ax.set_title('Pixel {}, $\sigma = {:.2f}\,\mathrm{{mm}}$'.format(
                r.chid, r.sigma
            ))

            # data.set_ydata(y)
            data_smooth.set_ydata(y_smooth)
            fit.set_ydata(
                gaussian_and_constant(x_mm, r.mu, r.sigma, r.A, r.off)
            )

            pdf.savefig(fig)


if __name__ == '__main__':
    main()
