import pandas as pd

from joblib import Parallel, delayed
import click

from astropy.io import fits
import astropy.units as u

from ..fitting import fit
from ..smoothing import butter_lowpass
from ..utils import time_to_distance, unixtime_tuple_to_time


def smooth(y):
    return butter_lowpass(y, 1e-3, 1)


@click.command()
@click.argument('inputfile')
@click.argument('outputfile')
def main(inputfile, outputfile):

    f = fits.open(inputfile)

    ped_var = f[1].data['ped_var'][:].byteswap().newbyteorder()
    unixtime = f[1].data['UnixTimeUTC'][:].byteswap().newbyteorder()

    time = unixtime_tuple_to_time(unixtime)
    x = time_to_distance(time)

    x_mm = x.to(u.mm).value

    with Parallel(n_jobs=-1, verbose=10) as pool:

        result = pd.DataFrame(
            pool(
                delayed(fit)(x_mm, smooth(ped_var[:, chid]))
                for chid in range(1440)
            )
        )

    result.index.name = 'chid'
    result.to_csv(outputfile, index=True)


if __name__ == '__main__':
    main()
