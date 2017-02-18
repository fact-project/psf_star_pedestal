# coding: utf-8
from astropy.io import fits
from fact.plotting import camera
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import numpy as np
from scipy.stats import norm
from scipy.optimize import curve_fit
from matplotlib.backends.backend_pdf import PdfPages
from tqdm import tqdm


def gauss(x, mu, sigma, A, off):
    return A * norm(mu, sigma).pdf(x) + off


f = fits.open('./ursa_star_pedestal.fits')

ped_var = f[1].data['ped_var'].byteswap().newbyteorder()
unixtime = f[1].data['UnixTimeUTC'].byteswap().newbyteorder()

unixtime = unixtime[:, 0] + unixtime[:, 1] / 1e6


fig_cam = plt.figure(figsize=(8, 8))
ax = fig_cam.add_axes([0, 0, 1, 1])
ax.set_axis_off()

camera(ped_var.sum(axis=0), ax=ax)

fig_cam.savefig('camera_pedvar.png', dpi=300)

fig, ax = plt.subplots()

x_mm = unixtime / 3600 * (360 / 24) * (9.5 / 0.1)


sigmas = []
with PdfPages('star_pedvar.pdf') as pdf:
    for pix in tqdm(range(1440)):
        y = pd.Series(ped_var[:, pix]).rolling(200, center=True).mean()
        if y.dropna().max() < 2e5:
            continue


        mask = np.isfinite(y).values

        x0 = x_mm[np.argmax(y[mask])]
        params, cov = curve_fit(gauss, x_mm[mask], y[mask], p0=(x0, 5.5, 200e5, 20e4))

        ax.cla()

        ax.plot(x_mm[mask], y[mask])
        ax.plot(x_mm[mask], gauss(x_mm[mask], *params))

        ax.set_xlabel('x / mm')
        ax.set_ylabel('ped_var rolling mean')
        ax.set_title('Pixel {}'.format(pix))

        fig.tight_layout()
        pdf.savefig(fig)
        sigmas.append(params[1])

print(np.mean(sigmas), '+-', np.std(sigmas), sep='')
