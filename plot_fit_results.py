import pandas as pd
import numpy as np
from fact.pixels import get_pixel_coords
from fact.plotting import camera
import matplotlib.pyplot as plt
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('outputfile')


if __name__ == '__main__':
    args = parser.parse_args()

    df = pd.read_csv(args.inputfile)

    sigma = np.ma.masked_invalid(df.sigma.values)

    cmap = plt.get_cmap('viridis')
    cmap.set_bad('lightgray')

    camera(sigma, cmap=cmap)
    plt.show()

    x, y = get_pixel_coords()
    df['x'] = x.values
    df['y'] = y.values
    df['r'] = np.sqrt(df.x**2 + df.y**2)

    xplot = np.linspace(0, 190, 2)

    # only fit the main star going through the camera center
    df = df.loc[(df.y < 30) & (df.y > -30)].dropna()

    a, b = np.polyfit(df.r.values, df.sigma.values, deg=1)

    fig, ax = plt.subplots()

    ax.scatter('r', 'sigma', data=df)
    ax.plot(xplot, a * xplot + b, color='C1', label='Linear regression')

    ax.set_xlabel(r'$d \,\, / \,\, \mathrm{mm}$')
    ax.set_ylabel(r'$\sigma \,\, / \,\, \mathrm{mm}$')

    fig.tight_layout()
    fig.savefig(args.outputfile, dpi=300)
