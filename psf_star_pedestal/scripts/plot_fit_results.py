import pandas as pd
import numpy as np
from fact.instrument.camera import get_pixel_coords
from fact.plotting import camera
import matplotlib.pyplot as plt
import click


@click.command()
@click.argument('inputfile')
@click.option('-o', '--output', help='Outputfile for the plot')
@click.option(
    '-t', '--threshold', default=4e6,
    help='Only show pixels above threhold',
)
def main(inputfile, output, threshold):
    df = pd.read_csv(inputfile)

    x, y = get_pixel_coords()
    df['x'] = x
    df['y'] = y
    df['r'] = np.sqrt(df.x**2 + df.y**2)

    psf = df.sigma.values
    psf[df.A.values < threshold] = np.nan

    sigma = np.ma.masked_invalid(df.sigma.values)
    cmap = plt.get_cmap('viridis')
    cmap.set_bad('lightgray')
    camera(sigma, cmap=cmap)

    df = df.query('A >= @args.threshold')

    plt.show()

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
    if output:
        fig.savefig(output, dpi=300)
    else:
        plt.show()


if __name__ == '__main__':
    main()
