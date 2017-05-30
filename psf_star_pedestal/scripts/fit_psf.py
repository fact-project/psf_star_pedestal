import pandas as pd

from joblib import Parallel, delayed
from argparse import ArgumentParser

from astropy.io import fits
import astropy.units as u

import fact.instrument.constants as const

from ..fitting import fit
from ..smoothing import butter_lowpass


parser = ArgumentParser()
parser.add_argument('inputfile')
parser.add_argument('outputfile')


pixel_width = const.PIXEL_SPACING_IN_MM * u.mm
focal_length = const.FOCAL_LENGTH_MM * u.mm
sidereal_day = 1 * u.sday
pixel_fov = const.FOV_PER_PIXEL_DEG * u.deg


def smooth(y):
    return butter_lowpass(y, 1e-3, 1)


def main():
    args = parser.parse_args()

    f = fits.open(args.inputfile)

    ped_var = f[1].data['ped_var'][:].byteswap().newbyteorder()
    unixtime = f[1].data['UnixTimeUTC'][:].byteswap().newbyteorder()

    unixtime = (unixtime[:, 0] + unixtime[:, 1] / 1e6) * u.s

    time = unixtime - unixtime.min()

    x = (time * 360 * u.deg / sidereal_day * pixel_width / pixel_fov)

    x_mm = x.to(u.mm).value

    with Parallel(n_jobs=-1, verbose=10) as pool:

        result = pd.DataFrame(
            pool(
                delayed(fit)(x_mm, smooth(ped_var[:, chid]))
                for chid in range(1440)
            )
        )

    result.index.name = 'chid'
    result.to_csv(args.outputfile, index=True)


if __name__ == '__main__':
    main()
