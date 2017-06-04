import astropy.units as u

from .constants import pixel_fov, pixel_width, sidereal_day


def time_to_distance(time):
    return (time * 360 * u.deg / sidereal_day * pixel_width / pixel_fov)


def unixtime_tuple_to_time(unixtime):
    unixtime = (unixtime[:, 0] + unixtime[:, 1] / 1e6) * u.s
    return unixtime - unixtime.min()
